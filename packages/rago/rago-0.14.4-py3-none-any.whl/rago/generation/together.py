"""TogetherGen class for text generation using Together AI's API."""

from __future__ import annotations

from typing import cast

import instructor
import openai

from pydantic import BaseModel
from typeguard import typechecked

from rago._optional import require_dependency
from rago.generation.base import GenerationBase


@typechecked
class TogetherGen(GenerationBase):
    """Together AI generation model for text generation."""

    default_model_name: str = 'mistralai/Mixtral-8x7B-Instruct-v0.1'
    default_api_params = {
        'top_p': 0.9,
        'frequency_penalty': 0.0,
        'presence_penalty': 0.0,
    }

    def _load_optional_modules(self) -> None:
        self._together = require_dependency(
            'together',
            extra='together',
            context='together',
        )

    def _setup(self) -> None:
        """Set up the object with the initial parameters."""
        # if we have to get structured output instructor uses doesn't
        # have support for together yet but we can access the model
        # and use openai sdk if we need to get structured output
        if self.structured_output:
            model = openai.OpenAI(
                base_url='https://api.together.xyz/v1',
                api_key=self.api_key,
            )
            self.model = (
                instructor.from_openai(
                    client=model,
                    mode=instructor.Mode.TOOLS,
                )
                if self.structured_output
                else model
            )

        else:
            self._together.api_key = self.api_key
            self.model = self._together.Together()

    def generate(self, query: str, context: list[str]) -> str | BaseModel:
        """Generate text using Together AI's API."""
        input_text = self.prompt_template.format(
            query=query, context=' '.join(context)
        )

        api_params = self.api_params or self.default_api_params

        messages = []
        if self.system_message:
            messages.append({'role': 'system', 'content': self.system_message})
        messages.append({'role': 'user', 'content': input_text})

        model_params = {
            'model': self.model_name,
            'messages': messages,
            'max_tokens': self.output_max_length,
            'temperature': self.temperature,
            **api_params,
        }

        if self.structured_output:
            model_params['response_model'] = self.structured_output
            response = self.model.chat.completions.create(**model_params)
            self.logs['model_params'] = model_params
            return cast(BaseModel, response)

        response = self.model.chat.completions.create(**model_params)
        self.logs['model_params'] = model_params
        return cast(str, response.choices[0].message.content.strip())
