import os
from typing import Any, AsyncGenerator, Type, TypeVar

from pydantic import BaseModel

from ait.core.domain.interfaces import CompletionResponse
from ait.factories import (
    create_llm_client,
    create_model_handler,
    create_prompt_formatter,
)

T = TypeVar("T", bound=BaseModel)
N = TypeVar("N")
C = TypeVar("C")


class AITools:
    """
    A class that bundles methods for easily interacting with LLMs and manipulating pydantic BaseModels.
    """

    def __init__(
        self,
        model: str | None = None,
        embedding_model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        """
        Initialize AIT with LLM client and prompt formatter.

        Args:
            model (str): The model to use for completions
            embedding_model (str): The model to use for embeddings
            api_key (str): The API key for authentication
        """
        if not model:
            model = os.getenv("LLM_MODEL", "")
        if not embedding_model:
            embedding_model = os.getenv("EMBEDDING_MODEL", "")
        if not api_key:
            api_key = os.getenv("LLM_API_KEY", "")

        self.llm_client = create_llm_client(
            model=model,
            embedding_model=embedding_model,
            api_key=api_key,
            base_url=base_url,
        )
        self.prompt_formatter = create_prompt_formatter()
        self.model_handler = create_model_handler()

    def inject_types(
        self,
        model: Type[T],
        fields: list[tuple[str, Any]],
    ) -> Type[T]:
        """
        Injects field types into a response model.

        Args:
            model (Type[T]): The model to inject types into
            fields (list[tuple[str, Any]]): The fields to inject types into

        Returns:
            Type[T]: The model with injected types

        Example:
            >>> ait.inject_types(Fruit, [("name", Literal[tuple(available_fruits)])])
        """
        return self.model_handler.inject_types(model, fields)

    def reduce_model_schema(
        self, model: Type[T], include_description: bool = True
    ) -> str:
        """
        Reduces a response model schema into version with less tokens. Helpful for reducing prompt noise.

        Args:
            model (Type[T]): The model to reduce the schema of
            include_description (bool): Whether to include the description in the schema

        Returns:
            str: The reduced schema
        """
        return self.model_handler.reduce_model_schema(model, include_description)

    def _prepare_messages(self, path: str, **kwargs: Any) -> list:
        prompt = self.prompt_formatter.render(
            path=path,
            input=kwargs,
        )
        return [
            {"role": "system", "content": prompt},
        ]

    async def chat(
        self,
        path: str,
        **kwargs: Any,
    ) -> CompletionResponse:
        """
        Execute a chat task and return a text response.

        Args:
            path (str): The path to the prompt template file
            **kwargs: Additional arguments to pass to the prompt formatter

        Returns:
            CompletionResponse: The response from the LLM with text content
        """
        messages = self._prepare_messages(path, **kwargs)
        return await self.llm_client.chat(messages=messages)

    async def stream(
        self,
        path: str,
        **kwargs: Any,
    ) -> AsyncGenerator[CompletionResponse, None]:
        """
        Execute a streaming task and return a stream of text responses.

        Args:
            path (str): The path to the prompt template file
            **kwargs: Additional arguments to pass to the prompt formatter

        Returns:
            AsyncGenerator[CompletionResponse, None]: Stream of responses from the LLM
        """
        messages = self._prepare_messages(path, **kwargs)
        async for response in await self.llm_client.stream(messages=messages):
            yield response

    async def asend(
        self,
        response_model: Type[T],
        path: str,
        **kwargs: Any,
    ) -> CompletionResponse[T]:
        """
        Execute a structured task and return a typed response.

        Args:
            response_model (Type[T]): The model to return the response as
            path (str): Path to the prompt template file
            **kwargs: Additional arguments to pass to the prompt formatter

        Returns:
            CompletionResponse[T]: The response from the LLM with structured content
        """
        messages = self._prepare_messages(path, **kwargs)
        response = await self.llm_client.asend(
            messages=messages,
            response_model=response_model,
        )
        if not isinstance(response.content, response_model):
            raise ValueError(
                f"Response content is not an instance of {response_model.__name__}"
            )
        return response
