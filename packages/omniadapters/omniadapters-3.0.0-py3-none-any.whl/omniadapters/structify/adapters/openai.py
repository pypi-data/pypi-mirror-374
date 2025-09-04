from __future__ import annotations

import instructor
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

from omniadapters.structify.adapters.base import BaseAdapter
from omniadapters.structify.models import OpenAIProviderConfig


class OpenAIAdapter(BaseAdapter[OpenAIProviderConfig, AsyncOpenAI, ChatCompletion]):
    def _create_client(self) -> AsyncOpenAI:
        return AsyncOpenAI(**self.provider_config.model_dump())

    def _with_instructor(self) -> instructor.AsyncInstructor:
        client: AsyncOpenAI = self.client
        return instructor.from_openai(client, mode=self.instructor_config.mode)
