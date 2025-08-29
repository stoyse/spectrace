"""
Simple OpenAI client for making API calls
"""

import openai
import json
import time
import os
from typing import Dict, Any
from schemas import OpenAIRequest, OpenAIResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class OpenAIClient:
    """Simple OpenAI client wrapper"""
    
    def __init__(self):
        """Initialize with API key"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("Warning: OPENAI_API_KEY not found in environment")
            # For testing, we'll allow initialization without key
        
        self.client = openai.OpenAI(api_key=api_key) if api_key else None
    
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
            
            # Call OpenAI
            response = self.client.chat.completions.create(
                model=request.model.value,
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            
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
            
        except openai.RateLimitError:
            return OpenAIResponse(
                success=False,
                data=None,
                message="Rate limit exceeded - try again later",
                model_used=request.model.value,
                response_time=time.time() - start_time
            )
            
        except openai.AuthenticationError:
            return OpenAIResponse(
                success=False,
                data=None,
                message="Authentication failed - check API key",
                model_used=request.model.value,
                response_time=time.time() - start_time
            )
            
        except Exception as e:
            return OpenAIResponse(
                success=False,
                data=None,
                message=f"OpenAI error: {str(e)}",
                model_used=request.model.value,
                response_time=time.time() - start_time
            )

# Global instance
openai_client = OpenAIClient()