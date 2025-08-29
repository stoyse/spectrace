"""
Simple OpenAI client for making API calls
"""

import openai
import json
import time
import os
import logging
from typing import Dict, Any
from schemas import OpenAIRequest, OpenAIResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class OpenAIClient:
    """Simple OpenAI client wrapper"""
    
    def __init__(self):
        """Initialize with API key"""
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            logger.warning("OPENAI_API_KEY not found in environment")
            print("Warning: OPENAI_API_KEY not found in environment")
            print(f"Available env vars: {list(os.environ.keys())[:10]}...")  # Debug info
        else:
            # Log partial key for debugging (first 10 chars only)
            logger.info(f"OpenAI API key found: {api_key[:10]}...")
            
        try:
            self.client = openai.OpenAI(api_key=api_key) if api_key else None
            if self.client:
                logger.info("OpenAI client initialized successfully")
            else:
                logger.error("OpenAI client not initialized - missing API key")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            self.client = None
    
    async def process_text(self, request: OpenAIRequest) -> OpenAIResponse:
        """Send text to OpenAI and get response"""
        start_time = time.time()
        
        if not self.client:
            return OpenAIResponse(
                success=False,
                data=None,
                message="OpenAI client not initialized - missing API key",
                model_used=request.model.value,
                response_time=time.time() - start_time
            )
        
        try:
            # Simple message structure
            messages = [
                {"role": "system", "content": "You are a helpful assistant. Always respond with valid JSON when requested."},
                {"role": "user", "content": request.text}
            ]
            
            logger.info(f"Making OpenAI request with model: {request.model.value}")
            
            # Call OpenAI
            response = self.client.chat.completions.create(
                model=request.model.value,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            
            logger.info("OpenAI request completed successfully")
            
            # Get response content
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else 0
            response_time = time.time() - start_time
            
            # Return successful response
            return OpenAIResponse(
                success=True,
                data={"response": content},
                message="Analysis completed successfully",
                model_used=request.model.value,
                tokens_used=tokens_used,
                response_time=response_time
            )
            
        except openai.RateLimitError as e:
            logger.error(f"Rate limit error: {str(e)}")
            return OpenAIResponse(
                success=False,
                data=None,
                message="Rate limit exceeded - try again later",
                model_used=request.model.value,
                response_time=time.time() - start_time
            )
            
        except openai.AuthenticationError as e:
            logger.error(f"Authentication error: {str(e)}")
            return OpenAIResponse(
                success=False,
                data=None,
                message="Authentication failed - check API key",
                model_used=request.model.value,
                response_time=time.time() - start_time
            )
            
        except openai.BadRequestError as e:
            logger.error(f"Bad request error: {str(e)}")
            return OpenAIResponse(
                success=False,
                data=None,
                message=f"Bad request - check input parameters: {str(e)}",
                model_used=request.model.value,
                response_time=time.time() - start_time
            )
            
        except Exception as e:
            logger.error(f"Unexpected OpenAI error: {str(e)}")
            return OpenAIResponse(
                success=False,
                data=None,
                message=f"OpenAI error: {str(e)}",
                model_used=request.model.value,
                response_time=time.time() - start_time
            )

# Global instance
openai_client = OpenAIClient()