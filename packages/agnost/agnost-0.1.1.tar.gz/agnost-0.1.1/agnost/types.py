from typing import Callable, Optional

class AgnostConfig:
    """Configuration class for Agnost API client."""
    
    def __init__(
        self,
        endpoint: str = "https://api.agnost.ai/api/v1/",
        disable_input: bool = False,
        disable_output: bool = False,
    ):
        """
        Initialize Agnost configuration.
        
        Args:
            endpoint: API endpoint URL, defaults to "https://api.agnost.ai"
            disable_input: Flag to disable input processing, defaults to False
            disable_output: Flag to disable output processing, defaults to False
        """
        self.endpoint = endpoint
        self.disable_input = disable_input
        self.disable_output = disable_output