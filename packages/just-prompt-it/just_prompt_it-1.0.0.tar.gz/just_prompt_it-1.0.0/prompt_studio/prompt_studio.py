"""Main SDK class for Prompt Studio."""

import os
from typing import Optional

import httpx

from .exceptions import APIKeyError, PromptNotFoundError


class PromptStudio:
    """
    SDK for interacting with prompts API.

    This class provides methods to fetch and render prompts using a given API.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api-studio.dev.trustsoft.ai",
    ):
        """
        Initialize the PromptStudio.

        Args:
            api_key: API key for authentication. If not provided, will look for PROMPT_STUDIO_API_KEY environment variable.
            base_url: Base URL for the API.
        """
        self.api_key = api_key or os.getenv("PROMPT_STUDIO_API_KEY")
        if not self.api_key:
            raise APIKeyError(
                "API key must be provided either as parameter or PROMPT_STUDIO_API_KEY environment variable"
            )
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def get_prompt(
        self, project_name: str, prompt_name: str, alias: Optional[str] = None
    ) -> str:
        """
        Fetch a prompt from the API.

        Args:
            project_name: Name of the project.
            prompt_name: Name of the prompt.
            alias: Optional alias for the prompt, could be number or label of prompt version. If not provided, the latest active prompt is fetched..

        Returns:
            The prompt body as a string.

        Raises:
            ValueError: If the API request fails.
        """
        url = f"{self.base_url}/sdk-api/prompt"
        params = {
            "projectName": project_name,
            "promptName": prompt_name,
        }
        if alias:
            params["alias"] = alias
        with httpx.Client() as client:
            response = client.get(url=url, params=params, headers=self.headers)
            if response.status_code == 404:
                raise PromptNotFoundError(
                    f"Prompt '{prompt_name}' not found in project '{project_name}'"
                )
            if response.status_code != 200:
                raise PromptNotFoundError(f"Failed to fetch prompt: {response.text}")
            return response.json()["body"]

    async def a_get_prompt(
        self, project_name: str, prompt_name: str, alias: Optional[str] = None
    ) -> str:
        """
        Asynchronously fetch a prompt from the API.

        Args:
            project_name: Name of the project.
            prompt_name: Name of the prompt.
            alias: Optional alias for the prompt, could be number or label of prompt version. If not provided, the latest active prompt is fetched..

        Returns:
            The prompt body as a string.

        Raises:
            ValueError: If the API request fails.
        """
        url = f"{self.base_url}/sdk-api/prompt"
        params = {
            "projectName": project_name,
            "promptName": prompt_name,
        }
        if alias:
            params["alias"] = alias

        async with httpx.AsyncClient() as client:
            response = await client.get(url=url, params=params, headers=self.headers)
            if response.status_code == 404:
                raise PromptNotFoundError(
                    f"Prompt '{prompt_name}' not found in project '{project_name}'"
                )
            if response.status_code != 200:
                raise PromptNotFoundError(f"Failed to fetch prompt: {response.text}")
            return response.json()["body"]
