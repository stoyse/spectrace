"""
Error handling middleware for the Spectrace API.
"""

import logging
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import traceback
from typing import Callable

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle errors and provide consistent error responses.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except HTTPException:
            # Re-raise HTTP exceptions as they're handled by FastAPI
            raise
        except Exception as e:
            # Log unexpected errors
            logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
            
            # Return a generic error response
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "Internal server error",
                    "message": "An unexpected error occurred. Please try again later.",
                    "details": str(e) if logger.level <= logging.DEBUG else None
                }
            )

class GhidraErrorHandler:
    """
    Specialized error handler for Ghidra-related operations.
    """
    
    @staticmethod
    def handle_ghidra_error(error: Exception, context: str = "Ghidra operation") -> dict:
        """
        Handle Ghidra-specific errors and return formatted error response.
        
        Args:
            error: The exception that occurred
            context: Context description for the error
            
        Returns:
            Formatted error response dictionary
        """
        error_msg = str(error).lower()
        
        # Common Ghidra error patterns
        if "java" in error_msg and "not found" in error_msg:
            return {
                "success": False,
                "error": "Java runtime not found",
                "message": "Java 17+ is required for Ghidra operations. Please ensure Java is installed and JAVA_HOME is set correctly.",
                "suggestion": "Install Java 17+ and set JAVA_HOME environment variable"
            }
        
        elif "ghidra" in error_msg and ("not found" in error_msg or "no such file" in error_msg):
            return {
                "success": False,
                "error": "Ghidra installation not found",
                "message": "Ghidra installation directory not found. Please ensure Ghidra is properly installed.",
                "suggestion": "Set GHIDRA_INSTALL_DIR environment variable to your Ghidra installation path"
            }
        
        elif "timeout" in error_msg or "timed out" in error_msg:
            return {
                "success": False,
                "error": "Analysis timeout",
                "message": "Binary analysis took too long and was terminated. This may happen with very large or complex binaries.",
                "suggestion": "Try with a smaller binary or increase timeout limits"
            }
        
        elif "permission" in error_msg or "denied" in error_msg:
            return {
                "success": False,
                "error": "Permission denied",
                "message": "Insufficient permissions to access required files or directories.",
                "suggestion": "Check file permissions and ensure the application has write access to temporary directories"
            }
        
        elif "memory" in error_msg or "heap" in error_msg:
            return {
                "success": False,
                "error": "Insufficient memory",
                "message": "Not enough memory available for binary analysis. This can happen with very large binaries.",
                "suggestion": "Try with a smaller binary or increase available memory for the Java process"
            }
        
        elif "unsupported" in error_msg or "unknown format" in error_msg:
            return {
                "success": False,
                "error": "Unsupported binary format",
                "message": "The uploaded file format is not supported by Ghidra for analysis.",
                "suggestion": "Ensure the file is a valid binary (ELF, PE, Mach-O, or raw binary)"
            }
        
        else:
            # Generic error handling
            logger.error(f"{context} failed: {str(error)}")
            return {
                "success": False,
                "error": f"{context} failed",
                "message": f"An error occurred during {context.lower()}: {str(error)}",
                "suggestion": "Please check the binary file and try again"
            }

def setup_logging():
    """
    Set up logging configuration for the application.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('spectrace_api.log', mode='a')
        ]
    )
    
    # Set specific log levels
    logging.getLogger('uvicorn').setLevel(logging.WARNING)
    logging.getLogger('fastapi').setLevel(logging.INFO)
    logging.getLogger('ghidra_service').setLevel(logging.DEBUG)