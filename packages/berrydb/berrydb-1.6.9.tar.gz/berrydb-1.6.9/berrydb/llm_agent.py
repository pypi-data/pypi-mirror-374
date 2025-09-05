from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
import requests

import constants.constants as bdb_constants
from utils.utils import Utils


AllowedProvider = Literal["openai", "anthropic"]


@dataclass(frozen=True)
class LLMAgent:
    provider: AllowedProvider
    model: str
    temperature: float
    system_prompt: str

    def chat(self, llm_api_key: str, prompt_args: dict[str, str] | None = None, attachment_args: dict | None = None) -> dict:
        """
        Send a chat message to the BERRY_GPT service using this prompt configuration.

        Parameters:
        - **llm_api_key** (str): The LLM API key (e.g., OpenAI API key) for authentication.
        - **prompt_args** (dict[str, str] | None, optional): Dictionary of key-value pairs to replace variables in system_prompt.
          Variables should be enclosed with {{variable}} in the system_prompt.
          Example: {"user": "John"} will replace {{user}} with "John" in the system_prompt.
        - **attachment_args** (dict | None, optional): Dictionary of additional arguments to be spread into the payload.
          These arguments will be merged with the base payload at the top level.

        Returns:
        - dict: The response from the BERRY_GPT service.

        Raises:
        - ValueError: If the LLM API key is invalid.
        - Exception: If the API call fails.

        Example:
        ```python
        from berrydb import LLMAgent
        
        # Create a prompt configuration with OpenAI
        prompt = LLMAgent.Builder()\\
            .provider("openai")\\
            .model("gpt-4o-mini")\\
            .temperature(0.7)\\
            .system_prompt("Hello {{user}}! You are a helpful assistant.")\\
            .build()

        # Send a chat message with variable replacement
        response = prompt.chat("sk-your-openai-api-key", {"user": "John"})
        # Result: system_prompt becomes "Hello John! You are a helpful assistant."
        print(response)
        
        # Send a chat message with attachment arguments
        response_with_attachments = prompt.chat(
            "sk-your-openai-api-key", 
            {"user": "John"}, 
            {"attachmentType": "image", "attachmentUrl": "https://example.com/image.png"}
        )
        print(response_with_attachments)
        
        # Create a prompt configuration with Anthropic Claude
        claude_prompt = LLMAgent.Builder()\\
            .provider("anthropic")\\
            .model("claude-sonnet-4-latest")\\
            .temperature(0.7)\\
            .system_prompt("Hello {{user}}! You are a helpful assistant.")\\
            .build()
        
        # Send a chat message with Claude
        claude_response = claude_prompt.chat("sk-your-anthropic-api-key", {"user": "John"})
        print(claude_response)
        ```
        """
        # Enhanced validation: check for empty, None, or whitespace-only strings
        if not llm_api_key or not isinstance(llm_api_key, str) or not llm_api_key.strip():
            raise ValueError("llm_api_key must be a non-empty string")

        # Process system_prompt with variable replacement if prompt_args is provided
        processed_system_prompt = self.system_prompt
        if prompt_args and isinstance(prompt_args, dict):
            for key, value in prompt_args.items():
                if isinstance(key, str) and isinstance(value, str):
                    placeholder = f"{{{{{key}}}}}"
                    processed_system_prompt = processed_system_prompt.replace(placeholder, value)

        # Prepare the payload
        payload = {
            "database": "",
            "orgName": "",
            "apiKey": "",
            "llmApiKey": llm_api_key,
            "question": processed_system_prompt,
            "settings": {
                "chat_settings": {
                    "provider": self.provider,
                    "model": self.model,
                    "temperature": self.temperature,
                    "system_prompt": processed_system_prompt
                }
            }
        }

        # Spread attachment_args into the payload if provided
        if attachment_args and isinstance(attachment_args, dict):
            payload.update(attachment_args)

        # Make the API call to the BERRY_GPT service
        api_url = bdb_constants.BERRY_GPT_BASE_URL + "/prompt-answer"

        if bdb_constants.debug_mode:
            print("Prompt chat API call:")
            print("URL:", api_url)
            print("Payload:", payload)

        try:
            response = requests.post(api_url, json=payload)

            if response.status_code != 200:
                Utils.handleApiCallFailure(response.json(), response.status_code)

            result = response.json()

            if bdb_constants.debug_mode:
                print("Prompt chat response:", result)

            return result

        except Exception as e:
            raise Exception(f"Failed to send chat message: {str(e)}")

    def save(self, berrydb_api_key: str, prompt_name: str):
        """
        Saves the current LLMAgent configuration to BerryDB under a specified name.

        This allows you to store and reuse prompt configurations across your application.

        Parameters:
        - **berrydb_api_key** (str): The BerryDB API key for authentication.
        - **prompt_name** (str): The unique name to save this prompt configuration as.

        Returns:
        - dict: The API response confirming the save operation.

        Raises:
        - ValueError: If the API key or prompt name is invalid.
        - Exception: If the API call fails.

        Example:
        ```python
        from berrydb import LLMAgent

        # Create a prompt configuration
        prompt = LLMAgent.Builder().system_prompt("You are a helpful assistant.").build()

        # Save the prompt to BerryDB
        prompt.save("YOUR_BERRYDB_API_KEY", "helpful-assistant-prompt")
        ```
        """
        if bdb_constants.BASE_URL is None:
            raise ValueError("BASE_URL is not set. Please call bdb_constants.evaluate_endpoints() first.")

        # Enhanced validation for API key and prompt name
        if not berrydb_api_key or not isinstance(berrydb_api_key, str) or not berrydb_api_key.strip():
            raise ValueError("berrydb_api_key must be a non-empty string")

        if not prompt_name or not isinstance(prompt_name, str) or not prompt_name.strip():
            raise ValueError("prompt_name must be a non-empty string")

        api_url = bdb_constants.BASE_URL + bdb_constants.prompt_url
        params = {"apiKey": berrydb_api_key}

        data = {
            "name": prompt_name,
            "llmProvider": self.provider,
            "llmModel": self.model,
            "temperature": self.temperature,
            "systemPrompt": self.system_prompt
        }

        response = requests.post(api_url, params=params, json=data)
        if response.status_code != 201:
            Utils.handleApiCallFailure(response.json(), response.status_code)
        if bdb_constants.debug_mode:
            print("api_url: ", api_url)
            print("params: ", params)
            print("response: ", response.json())
        return response.json()

    @staticmethod
    def get(berrydb_api_key: str, prompt_name: str):
        """
        Retrieves a saved LLMAgent configuration from BerryDB by its name.

        Parameters:
        - **berrydb_api_key** (str): The BerryDB API key for authentication.
        - **prompt_name** (str): The name of the prompt configuration to retrieve.

        Returns:
        - LLMAgent: An instance of the LLMAgent with the retrieved configuration.

        Raises:
        - ValueError: If the API key or prompt name is invalid.
        - Exception: If the API call fails or the prompt is not found.

        Example:
        ```python
        from berrydb import LLMAgent

        # Retrieve a saved prompt from BerryDB
        retrieved_prompt = LLMAgent.get("YOUR_BERRYDB_API_KEY", "helpful-assistant-prompt")
        print(retrieved_prompt.system_prompt)
        ```
        """
        if bdb_constants.BASE_URL is None:
            raise ValueError("BASE_URL is not set. Please call bdb_constants.evaluate_endpoints() first.")

        # Enhanced validation for API key and prompt name
        if not berrydb_api_key or not isinstance(berrydb_api_key, str) or not berrydb_api_key.strip():
            raise ValueError("berrydb_api_key must be a non-empty string")

        if not prompt_name or not isinstance(prompt_name, str) or not prompt_name.strip():
            raise ValueError("prompt_name must be a non-empty string")

        api_url = bdb_constants.BASE_URL + bdb_constants.prompt_url
        params = {"apiKey": berrydb_api_key, "name": prompt_name}

        response = requests.get(api_url, params=params)
        if response.status_code != 200:
            error = {'error': 'Unable to fetch your prompt, either it does not exist or you do not have access to it.'}
            Utils.handleApiCallFailure(error, response.status_code)

        json_response = response.json()

        if bdb_constants.debug_mode:
            print("api_url: ", api_url)
            print("params: ", params)
            print("response: ", json_response)

        # Extract prompt data from response with enhanced validation
        prompt_data = json_response.get('prompt', {})

        # Validate and sanitize the data with proper type checking
        provider = prompt_data.get('llmProvider')
        if not provider or not isinstance(provider, str):
            provider = 'openai'  # Use default if invalid
        elif provider not in ("openai", "anthropic"):
            provider = 'openai'  # Use default if invalid provider
        
        model = prompt_data.get('llmModel')
        if not model or not isinstance(model, str):
            # Use provider-specific default model
            if provider == "anthropic":
                model = bdb_constants.DEFAULT_ANTHROPIC_MODEL
            else:
                model = bdb_constants.DEFAULT_OPEN_AI_MODEL
        elif provider == "anthropic" and not model.startswith("claude"):
            # Validate that Anthropic provider uses Claude models
            model = bdb_constants.DEFAULT_ANTHROPIC_MODEL
        elif provider == "openai" and not model.startswith("gpt"):
            # Validate that OpenAI provider uses GPT models
            model = bdb_constants.DEFAULT_OPEN_AI_MODEL
        
        temperature = prompt_data.get('temperature')
        if temperature is None:
            # Use provider-specific default temperature
            if provider == "anthropic":
                temperature = bdb_constants.DEFAULT_ANTHROPIC_TEMPERATURE
            else:
                temperature = bdb_constants.DEFAULT_OPEN_AI_TEMPERATURE
        else:
            # Try to convert to float, accepting strings, ints, and floats
            try:
                temperature = float(temperature)
                if not 0.0 <= temperature <= 1.0:
                    # Use provider-specific default if out of range
                    if provider == "anthropic":
                        temperature = bdb_constants.DEFAULT_ANTHROPIC_TEMPERATURE
                    else:
                        temperature = bdb_constants.DEFAULT_OPEN_AI_TEMPERATURE
            except (ValueError, TypeError):
                # Use provider-specific default if conversion fails
                if provider == "anthropic":
                    temperature = bdb_constants.DEFAULT_ANTHROPIC_TEMPERATURE
                else:
                    temperature = bdb_constants.DEFAULT_OPEN_AI_TEMPERATURE
        
        system_prompt = prompt_data.get('systemPrompt')
        if not isinstance(system_prompt, str):
            system_prompt = ''  # Use default if invalid

        return LLMAgent(
            provider=provider,
            model=model,
            temperature=temperature,
            system_prompt=system_prompt
        )

    class Builder:
        def __init__(self):
            self._provider: AllowedProvider = bdb_constants.DEFAULT_PROVIDER  # type: ignore[assignment]
            # Set appropriate default model and temperature based on provider
            if self._provider == "anthropic":
                self._model: str = bdb_constants.DEFAULT_ANTHROPIC_MODEL
                self._temperature: float = bdb_constants.DEFAULT_ANTHROPIC_TEMPERATURE
            else:
                self._model: str = bdb_constants.DEFAULT_OPEN_AI_MODEL
                self._temperature: float = bdb_constants.DEFAULT_OPEN_AI_TEMPERATURE
            self._system_prompt: str = ""

        def provider(self, provider: str | None = "openai") -> "LLMAgent.Builder":
            """
            Sets the LLM provider for the configuration.

            Parameters:
            - **provider** (str | None, optional): The name of the LLM provider. Currently, only "openai" is supported. Defaults to "openai".

            Returns:
            - `LLMAgent.Builder`: The builder instance for method chaining.

            Raises:
            - ValueError: If an unsupported provider is specified.
            """
            if provider is None:
                provider = "openai"
            # Enhanced validation with better error messages
            if not provider or not isinstance(provider, str):
                raise ValueError("Provider must be a non-empty string")
            if provider not in ("openai", "anthropic"):
                raise ValueError(f'Invalid provider "{provider}", only "openai" and "anthropic" are supported')
            self._provider = provider  # type: ignore[assignment]
            
            # Set appropriate default model and temperature based on provider
            if provider == "anthropic":
                self._model = bdb_constants.DEFAULT_ANTHROPIC_MODEL
                self._temperature = bdb_constants.DEFAULT_ANTHROPIC_TEMPERATURE
            else:  # openai
                self._model = bdb_constants.DEFAULT_OPEN_AI_MODEL
                self._temperature = bdb_constants.DEFAULT_OPEN_AI_TEMPERATURE
            
            return self

        def model(self, model: str | None = None) -> "LLMAgent.Builder":
            """
            Sets the specific LLM model to use.

            Parameters:
            - **model** (str | None, optional): The model name (e.g., "gpt-4o-mini"). Defaults to the default model for the provider.

            Returns:
            - `LLMAgent.Builder`: The builder instance for method chaining.
            """
            if model is None:
                # Use provider-specific default model
                if self._provider == "anthropic":
                    model = bdb_constants.DEFAULT_ANTHROPIC_MODEL
                else:
                    model = bdb_constants.DEFAULT_OPEN_AI_MODEL
            # Enhanced validation
            if not isinstance(model, str):
                raise ValueError("Model must be a string")
            if not model.strip():
                raise ValueError("Model cannot be empty or whitespace-only")
            self._model = model
            return self

        def temperature(self, temperature: float | int | None = None) -> "LLMAgent.Builder":
            """
            Sets the temperature for the LLM's responses.

            Temperature controls the randomness of the output. Higher values (e.g., 0.8) make the output more random,
            while lower values (e.g., 0.2) make it more focused and deterministic.

            Parameters:
            - **temperature** (float | int | None, optional): A value between 0.0 and 1.0. Defaults to 0.5.

            Returns:
            - `LLMAgent.Builder`: The builder instance for method chaining.

            Raises:
            - ValueError: If the temperature is outside the valid range of 0.0 to 1.0.
            """
            if temperature is None:
                # Use provider-specific default temperature
                if self._provider == "anthropic":
                    temperature = bdb_constants.DEFAULT_ANTHROPIC_TEMPERATURE
                else:
                    temperature = bdb_constants.DEFAULT_OPEN_AI_TEMPERATURE
            # Enhanced validation with better error handling
            try:
                temperature = float(temperature)
            except (ValueError, TypeError):
                raise ValueError(f"Temperature must be a valid number, got: {temperature}")

            if not 0.0 <= temperature <= 1.0:
                raise ValueError(f"Temperature must be between 0.0 and 1.0, got: {temperature}")

            self._temperature = temperature
            return self

        def system_prompt(self, system_prompt: str | None = None) -> "LLMAgent.Builder":
            """
            Sets the system prompt for the LLM.

            The system prompt is used to give the LLM context and instructions on how to behave.
            It can contain variables in the format `{{variable_name}}` which can be replaced
            at runtime using the `chat` method.

            Parameters:
            - **system_prompt** (str | None, optional): The system prompt string. Defaults to an empty string.

            Returns:
            - `LLMAgent.Builder`: The builder instance for method chaining.
            """
            if system_prompt is None:
                system_prompt = ""
            # Enhanced validation
            if not isinstance(system_prompt, str):
                raise ValueError("System prompt must be a string")
            self._system_prompt = system_prompt
            return self

        def build(self) -> "LLMAgent":
            """
            Constructs the final `LLMAgent` instance from the builder's configuration.

            Returns:
            - `LLMAgent`: A new, immutable `LLMAgent` instance.

            Example:
            ```python
            from berrydb import LLMAgent

            agent = LLMAgent.Builder()
                .provider("openai")
                .model("gpt-4o-mini")
                .temperature(0.7)
                .system_prompt("You are a helpful assistant.")
                .build()
            ```
            """
            return LLMAgent(
                provider=self._provider,
                model=self._model,
                temperature=self._temperature,
                system_prompt=self._system_prompt,
            )
