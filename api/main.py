from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import code_routes
from middleware import ErrorHandlingMiddleware, setup_logging
import uvicorn
import logging

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI instance
app = FastAPI(
    title="Spectrace API - Firmware Security Analysis Platform",
    description="A FastAPI application with AI and Ghidra integration for firmware security analysis",
    version="2.0.0"
)

# Add error handling middleware
app.add_middleware(ErrorHandlingMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers from routes folder

app.include_router(code_routes.router, prefix="/api/v1", tags=["code_analysis"])

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint providing API information and documentation link.
    
    Returns:
        Dictionary with welcome message and documentation URL
    """
    return {
        "message": "Welcome to Spectrace API - Firmware Security Analysis Platform", 
        "docs": "/docs",
        "version": "1.0.0",
        "features": [
            "Code Comparison & Security Analysis",
            "Specification Comparison", 
            "Change Analysis & Risk Assessment",
            "Specification Compliance Validation"
        ]
    }

# Run the application
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)