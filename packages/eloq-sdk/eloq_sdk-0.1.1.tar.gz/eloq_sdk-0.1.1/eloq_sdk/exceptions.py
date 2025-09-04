import json
from typing import Optional, Dict, Any


class EloqAPIError(Exception):
    """Base exception for Eloq API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        super().__init__(self._format_message())
    
    def _format_message(self) -> str:
        """Format the error message in a user-friendly way."""
        if self.status_code == 401:
            return self._format_auth_error()
        elif self.status_code == 403:
            return self._format_permission_error()
        elif self.status_code == 404:
            return self._format_not_found_error()
        elif self.status_code == 429:
            return self._format_rate_limit_error()
        elif self.status_code >= 500:
            return self._format_server_error()
        else:
            return self._format_generic_error()
    
    def _format_auth_error(self) -> str:
        """Format authentication error messages."""
        error_msg = self.response_data.get('message', 'Authentication failed')
        if 'invalid token' in error_msg.lower():
            return (
                "Authentication failed: Invalid token\n"
                "Please check your API token and ensure:\n"
                "• Token format is correct\n"
                "• Token is not expired\n"
                "• Token has sufficient permissions\n\n"
                "💡 Tip: You can regenerate your token in the Eloq console"
            )
        elif 'expired' in error_msg.lower():
            return (
                "Authentication failed: Token expired\n"
                "Please generate a new API token"
            )
        else:
            return f"Authentication failed: {error_msg}"
    
    def _format_permission_error(self) -> str:
        """Format permission error messages."""
        error_msg = self.response_data.get('message', 'Permission denied')
        return (
            f"Insufficient permissions: {error_msg}\n"
            "Please check if your account has permission to perform this operation"
        )
    
    def _format_not_found_error(self) -> str:
        """Format not found error messages."""
        error_msg = self.response_data.get('message', 'Resource not found')
        return f"Not found: {error_msg}"
    
    def _format_rate_limit_error(self) -> str:
        """Format rate limit error messages."""
        return (
            "Rate limit exceeded\n"
            "Please try again later or contact support to increase your API rate limit"
        )
    
    def _format_server_error(self) -> str:
        """Format server error messages."""
        return (
            "Server error\n"
            "Eloq servers are temporarily unavailable. Please try again later.\n"
            "If the problem persists, please contact Eloq support."
        )
    
    def _format_generic_error(self) -> str:
        """Format generic error messages."""
        error_msg = self.response_data.get('message', self.message)
        code = self.response_data.get('code', self.status_code)
        return f"API Error (Code: {code}): {error_msg}"


class EloqAuthenticationError(EloqAPIError):
    """Exception raised for authentication errors (401)."""
    pass


class EloqPermissionError(EloqAPIError):
    """Exception raised for permission errors (403)."""
    pass


class EloqNotFoundError(EloqAPIError):
    """Exception raised for not found errors (404)."""
    pass


class EloqRateLimitError(EloqAPIError):
    """Exception raised for rate limit errors (429)."""
    pass


class EloqServerError(EloqAPIError):
    """Exception raised for server errors (5xx)."""
    pass


class EloqValidationError(EloqAPIError):
    """Exception raised for validation errors (400)."""
    pass
