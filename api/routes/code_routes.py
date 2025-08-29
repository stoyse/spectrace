"""
Code Analysis Routes Module

This module contains FastAPI routes for code comparison and security analysis endpoints.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from schemas import (
    CodeComparisonRequest, 
    CodeComparisonResponse,
    SpecificationComparisonRequest,
    SpecificationComparisonResponse,
    ComplianceValidationRequest,
    ComplianceValidationResponse,
    DecompileResponse,
    BinaryMetadata
)
from services.code_analyzer import CodeAnalyzer
from services.spec_analyzer import SpecificationAnalyzer
from services.compliance_analyzer import ComplianceAnalyzer
from services.ghidra_service import GhidraDecompiler
import tempfile
import os
import time
import logging

# Create router instance
router = APIRouter()

# Initialize analyzers
code_analyzer = CodeAnalyzer()
spec_analyzer = SpecificationAnalyzer()
compliance_analyzer = ComplianceAnalyzer()
ghidra_decompiler = GhidraDecompiler()

# Set up logging
logger = logging.getLogger(__name__)

@router.post("/decompile", response_model=DecompileResponse)
async def decompile_binary(
    file: UploadFile = File(..., description="Binary file to decompile"),
    architecture: str = Form(None, description="Target architecture hint")
):
    """
    Decompile a binary file using Ghidra headless analyzer.
    
    This endpoint accepts binary files and returns both assembly and decompiled C code.
    Supports common binary formats like ELF, PE, Mach-O, and various embedded formats.
    
    Args:
        file: Binary file to analyze (max 100MB)
        architecture: Optional architecture hint (e.g., x86, ARM, MIPS)
        
    Returns:
        DecompileResponse containing:
        - assembly_code: Disassembled assembly code
        - decompiled_code: High-level C decompilation
        - metadata: Binary analysis metadata
        - success: Whether decompilation succeeded
        - error: Error message if failed
        
    Raises:
        HTTPException: If file validation fails or decompilation errors occur
    """
    start_time = time.time()
    temp_file_path = None
    
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="Filename is required")
        
        if file.size and file.size > 100 * 1024 * 1024:  # 100MB limit
            raise HTTPException(status_code=400, detail="File too large (max 100MB)")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='_' + file.filename) as temp_file:
            temp_file_path = temp_file.name
            content = await file.read()
            temp_file.write(content)
        
        # Validate binary file
        is_valid, validation_error = ghidra_decompiler.validate_binary_file(temp_file_path)
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid binary file: {validation_error}")
        
        logger.info(f"Starting decompilation of {file.filename} ({len(content)} bytes)")
        
        # Decompile using Ghidra
        result = await ghidra_decompiler.decompile_binary(temp_file_path, file.filename)
        
        if not result['success']:
            logger.error(f"Decompilation failed: {result.get('error', 'Unknown error')}")
            return DecompileResponse(
                success=False,
                assembly_code="",
                decompiled_code="",
                metadata=BinaryMetadata(filename=file.filename, file_size=len(content)),
                error=result.get('error', 'Decompilation failed')
            )
        
        # Create metadata
        analysis_time = time.time() - start_time
        metadata = BinaryMetadata(
            filename=file.filename,
            file_size=len(content),
            analysis_time=analysis_time,
            **{k: v for k, v in result['metadata'].items() if k != 'filename'}
        )
        
        logger.info(f"Decompilation completed successfully in {analysis_time:.2f}s")
        
        return DecompileResponse(
            success=True,
            assembly_code=result['assembly_code'],
            decompiled_code=result['decompiled_code'],
            metadata=metadata,
            warnings=[validation_error] if validation_error and "caution" in validation_error else []
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error during decompilation: {str(e)}")
        return DecompileResponse(
            success=False,
            assembly_code="",
            decompiled_code="",
            metadata=BinaryMetadata(filename=file.filename if file.filename else "unknown"),
            error=f"Internal server error: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.warning(f"Failed to clean up temp file {temp_file_path}: {str(e)}")


@router.post("/compare-code", response_model=CodeComparisonResponse)
async def compare_code(request: CodeComparisonRequest):
    """
    Compare two firmware/assembly code versions and perform security analysis.
    
    This endpoint analyzes differences between two code versions and identifies
    potential security issues, focusing on:
    - Hardcoded Credentials: Detect embedded passwords, API keys, certificates
    - Network Calls: Identify new network functionality, suspicious URLs/IPs  
    - Memory Operations: Flag unsafe memory access patterns
    - Privilege Escalation: Detect attempts to gain higher privileges
    - Obfuscation: Identify code obfuscation techniques
    - Backdoors: Flag suspicious jump patterns, hidden functionality
    
    Args:
        request: CodeComparisonRequest containing:
            - old_code: Original firmware code
            - new_code: Updated firmware code  
            - analysis_depth: Level of analysis detail (basic, detailed, comprehensive)
            - firmware_type: Type of firmware being analyzed (optional context)
            
    Returns:
        CodeComparisonResponse with:
            - differences: List of detected differences between code versions
            - security_findings: List of security-related findings
            - risk_assessment: Overall risk level assessment
            - change_summary: Summary of changes detected
            - recommendations: List of recommended actions
            - analysis_metadata: Metadata about the analysis process
            
    Raises:
        HTTPException: If analysis fails or invalid input provided
    """
    # Validate input
    if not request.old_code or not request.new_code:
        raise HTTPException(
            status_code=400, 
            detail="Both old_code and new_code are required"
        )
    
    if not request.old_code.strip() or not request.new_code.strip():
        raise HTTPException(
            status_code=400,
            detail="Both old_code and new_code must contain non-empty content"
        )
    
    try:
        # Perform comparison and analysis
        result = await code_analyzer.compare_codes(request)
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Analysis failed: {result.change_summary.get('error', 'Unknown error')}"
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during code comparison: {str(e)}")


@router.post("/compare-specs", response_model=SpecificationComparisonResponse)
async def compare_specs(request: SpecificationComparisonRequest):
    """
    Compare two specification versions and analyze changes.
    
    This endpoint analyzes differences between two specification versions focusing on:
    - Content changes and additions/removals
    - New features mentioned in specifications
    - Behavioral changes described
    - Impact on functionality and security
    
    Args:
        request: SpecificationComparisonRequest containing:
            - old_spec: Original specification content
            - new_spec: Updated specification content
            
    Returns:
        SpecificationComparisonResponse with:
            - differences: List of changes between versions
            - new_features: Features added in new version
            - removed_features: Features removed in new version
            - behavioral_changes: Changes in described behavior
            - change_summary: Summary of all changes
            - recommendations: Suggested actions
            
    Raises:
        HTTPException: If analysis fails or invalid input provided
    """
    # Validate input
    if not request.old_spec or not request.new_spec:
        raise HTTPException(
            status_code=400, 
            detail="Both old_spec and new_spec are required"
        )
    
    if not request.old_spec.strip() or not request.new_spec.strip():
        raise HTTPException(
            status_code=400,
            detail="Both old_spec and new_spec must contain non-empty content"
        )
    
    try:
        # Perform comparison and analysis
        result = await spec_analyzer.compare_specs(request)
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Analysis failed: {result.change_summary.get('error', 'Unknown error')}"
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during specification comparison: {str(e)}")


@router.post("/validate-compliance", response_model=ComplianceValidationResponse)
async def validate_compliance(request: ComplianceValidationRequest):
    """
    Validate compliance between code analysis and specification analysis results.
    
    This endpoint analyzes if the code changes match the specification changes by comparing
    the results from both /compare-code and /compare-specs endpoints to identify:
    - Code changes not mentioned in specifications
    - Specification changes not reflected in code
    - Inconsistencies between code and specifications
    - Overall compliance score and status
    
    Args:
        request: ComplianceValidationRequest containing:
            - code_analysis: Results from code comparison endpoint
            - spec_analysis: Results from specification comparison endpoint
            
    Returns:
        ComplianceValidationResponse with:
            - compliance_status: compliant, partially_compliant, or non_compliant
            - mismatches: List of found inconsistencies
            - matches: List of correctly aligned changes
            - compliance_score: Numerical score (0.0 to 1.0)
            - summary: Overall compliance assessment
            - recommendations: Suggested actions
            
    Raises:
        HTTPException: If validation fails or invalid input provided
    """
    # Basic validation
    if not request.code_analysis or not request.spec_analysis:
        raise HTTPException(
            status_code=400, 
            detail="Both code_analysis and spec_analysis are required"
        )
    
    try:
        # Perform compliance validation
        result = await compliance_analyzer.validate_compliance(request)
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=f"Validation failed: {result.summary.get('error', 'Unknown error')}"
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during compliance validation: {str(e)}")

