"""Claude API Desktop - A modern desktop client for the Anthropic Claude API.

A feature-rich desktop application with streaming support, extended context capabilities,
conversation branching, and comprehensive conversation management.
"""

__version__ = "1.0.0"
__author__ = "Anthony Maio"
__email__ = "anthony.maio@gmail.com"
__license__ = "MIT"

from .client import ClaudeClient

__all__ = ["ClaudeClient"]