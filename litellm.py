from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import os

# Event class to log LLM interactions
@dataclass
class LLMEvent:
    """
    Records a single interaction between the agent and the LLM.
    """
    event_type: str = "llms"
    prompt: Optional[Union[str, List]] = None
    completion: Optional[Union[str, Dict]] = None
    model: Optional[str] = None
    timestamp: str = None

    def log_event(self, file_path: str):
        """Logs the details of the event to a file."""
        with open(file_path, "a") as f:
            f.write(f"[LLMEvent] Logged event:\n")
            f.write(f"  Prompt: {self.prompt or 'N/A'}\n")
            f.write(f"  Completion: {self.completion or 'N/A'}\n")
            f.write(f"  Model: {self.model or 'unknown'}\n")
            f.write(f"  Timestamp: {self.timestamp}\n\n")

class LiteLLMProvider:
    """
    A provider to patch LLM method calls for LiteLLM, capturing and logging events.
    """
    def __init__(self, log_file="demo.txt"):
        self.log_file = log_file
        self.original_create = None
        self.original_create_async = None
        self.conversation_history = []  # To store full conversation history

        # Initialize log file
        with open(self.log_file, "w") as f:
            f.write(f"Log File Initialized: {datetime.now().isoformat()}\n\n")

    def override(self):
        """
        Overrides LiteLLM sync and async completion methods to log events.
        """
        import litellm

        # Store original methods for restoration
        self.original_create = litellm.completion
        self.original_create_async = litellm.acompletion

        # Define patched sync method
        def patched_sync(*args, **kwargs):
            response = self.original_create(*args, **kwargs)
            return self._log_interaction(kwargs, response)

        # Define patched async method
        async def patched_async(*args, **kwargs):
            response = await self.original_create_async(*args, **kwargs)
            return self._log_interaction(kwargs, response)

        # Apply patches
        litellm.completion = patched_sync
        litellm.acompletion = patched_async

    def _log_interaction(self, kwargs: dict, response: Any):
        """
        Logs and stores the interaction between the user and the LLM.
        """
        prompt = kwargs.get("prompt", "N/A")
        model = response.get("model", "unknown") if isinstance(response, dict) else "unknown"
        completion = response.get("completion", "N/A") if isinstance(response, dict) else str(response)

        llm_event = LLMEvent(
            prompt=prompt,
            completion=completion,
            model=model,
            timestamp=datetime.now().isoformat(),
        )
        llm_event.log_event(self.log_file)

        # Store in conversation history
        self.conversation_history.append(llm_event)
        return response

    def undo_override(self):
        """
        Restores LiteLLM's original methods.
        """
        import litellm

        if self.original_create and self.original_create_async:
            litellm.completion = self.original_create
            litellm.acompletion = self.original_create_async

    def get_conversation_history(self):
        """Returns the full conversation history."""
        return [
            {
                "prompt": event.prompt,
                "completion": event.completion,
                "timestamp": event.timestamp,
            }
            for event in self.conversation_history
        ]

# Example usage
if __name__ == "__main__":
    provider = LiteLLMProvider()
    provider.override()
    # Example call to the patched method (simulate completion call)
    # litellm.completion(prompt="Hello, how are you?")
    # Fetch full conversation history
    # print(provider.get_conversation_history())
    # To unpatch:
    # provider.undo_override()