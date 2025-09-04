import asyncio
import dataclasses
import logging
import os
import random
from typing import Any, Callable, Dict, Mapping, Optional, Type, TypeVar

from openai import APIError, AsyncAzureOpenAI
from openai._exceptions import APITimeoutError

from .models import TextAnalysis

logger = logging.getLogger(__name__)

T = TypeVar("T")


class AzureOpenAITextAnalyzer:
    """
    Encapsulates an AsyncAzureOpenAI client configured via environment variables,
    and provides a retrying _analyze_text(...) method.
    """

    TRANSIENT_ERROR_CODES = {"DeploymentNotFound", "ServiceUnavailable", "content_filter"}
    MAX_BACKOFF_SECONDS = 60
    DEFAULT_MAX_RETRIES = 10
    DEFAULT_INITIAL_BACKOFF = 1

    def __init__(
        self,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        api_version: Optional[str] = None,
        deployment_name: Optional[str] = None,
    ):
        self.endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT", "")
        self.api_key = api_key or os.getenv("AZURE_OPENAI_KEY", "")
        self.api_version = api_version or os.getenv("AZURE_OPENAI_API_VERSION", "")
        self.deployment_name = deployment_name or os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "")
        if not all([self.endpoint, self.api_key, self.api_version, self.deployment_name]):
            raise RuntimeError(
                "Azure OpenAI configuration error: "
                "AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY, AZURE_OPENAI_API_VERSION, "
                "and AZURE_OPENAI_DEPLOYMENT_NAME must all be set."
            )
        self.client = AsyncAzureOpenAI(
            azure_endpoint=self.endpoint, api_key=self.api_key, api_version=self.api_version
        )

    @staticmethod
    def _to_dict(obj: Any) -> Dict[str, Any]:
        if obj is None:
            return {}
        if hasattr(obj, "model_dump"):
            try:
                return obj.model_dump()
            except TypeError:
                return obj.model_dump(mode="python")
        if hasattr(obj, "dict"):
            try:
                return obj.dict()
            except TypeError:
                return obj.dict()
        if dataclasses.is_dataclass(obj):
            return dataclasses.asdict(obj)
        if isinstance(obj, Mapping):
            return dict(obj)
        if hasattr(obj, "__dict__"):
            return dict(vars(obj))
        return {"value": obj}

    async def _analyze_text(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: Type[T],
        max_retries: int,
        initial_backoff: int,
    ) -> Optional[T]:
        last_exception: Optional[Exception] = None
        backoff = initial_backoff
        for attempt in range(1, max_retries + 1):
            try:
                resp = await self.client.beta.chat.completions.parse(
                    model=self.deployment_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    response_format=response_format,
                )
                choices = getattr(resp, "choices", None) or []
                if not choices:
                    raise RuntimeError("_analyze_text: Azure returned no choices")
                return choices[0].message.parsed
            except APITimeoutError as e:
                logger.warning(
                    "timeout on attempt %d/%d, retrying…",
                    attempt,
                    max_retries,
                    exc_info=e,
                )
                last_exception = e
            except APIError as e:
                code = getattr(e, "code", "") or ""
                if code in self.TRANSIENT_ERROR_CODES:
                    logger.warning(
                        "transient APIError '%s' on attempt %d/%d, retrying…",
                        code,
                        attempt,
                        max_retries,
                        exc_info=e,
                    )
                    last_exception = e
                else:
                    logger.error("non-transient APIError '%s', aborting", code, exc_info=e)
                    raise

            except Exception as e:
                logger.exception("unexpected error on attempt %d, aborting", attempt, exc_info=e)
                raise

            if attempt < max_retries:
                sleep_secs = min(backoff, self.MAX_BACKOFF_SECONDS) * (0.5 + random.random() / 2)
                logger.info("sleeping %.1fs before next retry", sleep_secs)
                await asyncio.sleep(sleep_secs)
                backoff *= 2
            else:
                logger.error("reached max retries (%d), giving up", max_retries)
        if last_exception:
            raise last_exception
        raise RuntimeError("_analyze_text: exhausted all retries with no exception details")

    async def analyze_text(
        self,
        id: str,
        system_prompt: str,
        user_prompt: str,
        response_format: Type[T],
        max_retries: int = DEFAULT_MAX_RETRIES,
        initial_backoff: int = DEFAULT_INITIAL_BACKOFF,
    ) -> Dict[str, Any]:
        try:
            logger.debug(f"analyze_text: Processing text {id}")
            parsed = await self._analyze_text(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                response_format=response_format,
                max_retries=max_retries,
                initial_backoff=initial_backoff,
            )
            if not parsed:
                return {"id": id}
            row = self._to_dict(parsed)
            if not isinstance(row, dict):
                row = {"result": row}
            row.pop("id", None)
            return {"id": id, **row}
        except Exception as e:
            logger.error(f"Error in analyze_text - id {id}: {e}")
            return {"id": id}

    async def close(self) -> None:
        await self.client.close()
