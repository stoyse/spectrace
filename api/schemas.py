"""
Simple schemas for Spectrace API

Only includes the models we actually use.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class OpenAIModel(str, Enum):
    """OpenAI model options"""
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_3_5_TURBO = "gpt-3.5-turbo"


class OpenAIRequest(BaseModel):
    """Request to OpenAI API"""
    text: str = Field(..., description="Input text to process")
    model: OpenAIModel = Field(default=OpenAIModel.GPT_4, description="OpenAI model to use")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: Optional[int] = Field(default=1000, gt=0, description="Maximum tokens to generate")


class OpenAIResponse(BaseModel):
    """Response from OpenAI API"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: str
    model_used: str
    tokens_used: Optional[int] = None
    response_time: Optional[float] = None


class RiskLevel(str, Enum):
    """Risk level for security analysis"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


## ================ CODE =================

class SecurityFinding(BaseModel):
    """A security issue found in code"""
    type: str = Field(..., description="Type of security finding")
    severity: RiskLevel = Field(..., description="Risk level")
    location: str = Field(..., description="Where found in code")
    description: str = Field(..., description="What was found")
    code_snippet: str = Field(..., description="Relevant code")
    recommendation: str = Field(..., description="How to fix")


class CodeDifference(BaseModel):
    """A difference between two code versions"""
    line_number: int = Field(..., description="Line number of change")
    change_type: str = Field(..., description="Type: added, removed, or modified")
    old_content: Optional[str] = Field(None, description="Original content")
    new_content: Optional[str] = Field(None, description="New content")
    context: str = Field(..., description="Surrounding code context")


class CodeComparisonRequest(BaseModel):
    """Request to compare two code versions"""
    old_code: str = Field(..., description="Original code")
    new_code: str = Field(..., description="Updated code") 
    analysis_depth: str = Field(default="detailed", description="Analysis depth level")
    firmware_type: Optional[str] = Field(None, description="Type of firmware (e.g., ATmega328P)")


class CodeComparisonResponse(BaseModel):
    """Response from code comparison analysis"""
    success: bool = Field(..., description="Whether comparison was successful")
    differences: List[CodeDifference] = Field(..., description="List of code differences")
    security_findings: List[SecurityFinding] = Field(..., description="Security analysis findings")
    risk_assessment: RiskLevel = Field(..., description="Overall risk level")
    change_summary: Dict[str, Any] = Field(..., description="Summary of detected changes")
    recommendations: List[str] = Field(..., description="Recommended actions")
    analysis_metadata: Dict[str, Any] = Field(..., description="Analysis process metadata")


## ================ SPECS =================

class SpecificationComparisonRequest(BaseModel):
    """Request to compare two specification versions"""
    old_spec: str = Field(..., description="Original specification")
    new_spec: str = Field(..., description="Updated specification")


class SpecificationDifference(BaseModel):
    """A difference between two specification versions"""
    section: str = Field(..., description="Section name or reference")
    change_type: str = Field(..., description="Type: added, removed, or modified")
    old_content: Optional[str] = Field(None, description="Original content")
    new_content: Optional[str] = Field(None, description="New content")
    description: str = Field(..., description="Description of change")


class SpecificationFeature(BaseModel):
    """A feature mentioned in specification"""
    feature: str = Field(..., description="Feature name")
    description: str = Field(..., description="What this feature does")
    impact: str = Field(..., description="Impact on security/functionality")


class SpecificationBehaviorChange(BaseModel):
    """A behavioral change described in specification"""
    change: str = Field(..., description="Behavior that changed")
    old_behavior: str = Field(..., description="How it worked before")
    new_behavior: str = Field(..., description="How it works now")
    security_impact: str = Field(..., description="Security implications")


class SpecificationComparisonResponse(BaseModel):
    """Response from specification comparison analysis"""
    success: bool = Field(..., description="Whether comparison was successful")
    differences: List[SpecificationDifference] = Field(..., description="List of specification differences")
    new_features: List[SpecificationFeature] = Field(..., description="New features found")
    removed_features: List[SpecificationFeature] = Field(..., description="Removed features")
    behavioral_changes: List[SpecificationBehaviorChange] = Field(..., description="Behavioral changes")
    change_summary: Dict[str, Any] = Field(..., description="Summary of changes")
    recommendations: List[str] = Field(..., description="Recommended actions")
    analysis_metadata: Dict[str, Any] = Field(..., description="Analysis metadata")


## ================ COMPLIANCE =================

class ComplianceValidationRequest(BaseModel):
    """Request to validate compliance between code and specification analysis"""
    code_analysis: Dict[str, Any] = Field(..., description="Results from code comparison")
    spec_analysis: Dict[str, Any] = Field(..., description="Results from specification comparison")


class ComplianceMismatch(BaseModel):
    """A mismatch between code and documentation"""
    type: str = Field(..., description="Type: missing_in_docs, missing_in_code, inconsistent")
    description: str = Field(..., description="What doesn't match")
    code_reference: str = Field(..., description="Reference to code change")
    spec_reference: Optional[str] = Field(None, description="Reference to spec change")
    severity: str = Field(..., description="Severity: high, medium, low")


class ComplianceMatch(BaseModel):
    """A match between code and documentation"""
    description: str = Field(..., description="What matches correctly")
    code_reference: str = Field(..., description="Reference to code change")
    spec_reference: str = Field(..., description="Reference to spec change")


class ComplianceValidationResponse(BaseModel):
    """Response from compliance validation analysis"""
    success: bool = Field(..., description="Whether validation was successful")
    compliance_status: str = Field(..., description="compliant, partially_compliant, or non_compliant")
    mismatches: List[ComplianceMismatch] = Field(..., description="List of mismatches found")
    matches: List[ComplianceMatch] = Field(..., description="List of matches found")
    compliance_score: float = Field(..., description="Compliance score (0.0 to 1.0)")
    summary: Dict[str, Any] = Field(..., description="Summary of compliance analysis")
    recommendations: List[str] = Field(..., description="Recommended actions")
    analysis_metadata: Dict[str, Any] = Field(..., description="Analysis metadata")


## ================ BINARY DECOMPILATION =================

class DecompileRequest(BaseModel):
    """Request to decompile a binary file"""
    filename: str = Field(..., description="Original filename of the binary")
    architecture: Optional[str] = Field(None, description="Target architecture hint (e.g., x86, ARM)")
    timeout: Optional[int] = Field(default=300, description="Analysis timeout in seconds")


class BinaryMetadata(BaseModel):
    """Metadata about the analyzed binary"""
    filename: str = Field(..., description="Original filename")
    program: Optional[str] = Field(None, description="Program name from Ghidra")
    language: Optional[str] = Field(None, description="Detected language/architecture")
    compiler: Optional[str] = Field(None, description="Detected compiler")
    architecture: Optional[str] = Field(None, description="Target architecture")
    address_size: Optional[str] = Field(None, description="Address size (32-bit/64-bit)")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    analysis_time: Optional[float] = Field(None, description="Time taken for analysis")


class DecompileResponse(BaseModel):
    """Response from binary decompilation"""
    success: bool = Field(..., description="Whether decompilation was successful")
    assembly_code: str = Field(..., description="Disassembled assembly code")
    decompiled_code: str = Field(..., description="High-level decompiled C code")
    metadata: BinaryMetadata = Field(..., description="Binary analysis metadata")
    error: Optional[str] = Field(None, description="Error message if decompilation failed")
    warnings: List[str] = Field(default_factory=list, description="Non-fatal warnings")


class BinaryAnalysisRequest(BaseModel):
    """Request for binary-based firmware analysis"""
    old_binary_decompiled: str = Field(..., description="Decompiled code from old binary")
    new_binary_decompiled: str = Field(..., description="Decompiled code from new binary")
    old_binary_metadata: BinaryMetadata = Field(..., description="Metadata from old binary")
    new_binary_metadata: BinaryMetadata = Field(..., description="Metadata from new binary")
    analysis_depth: str = Field(default="detailed", description="Analysis depth level")
    firmware_type: Optional[str] = Field(None, description="Type of firmware")


class BinaryComparisonResponse(BaseModel):
    """Response from binary-based code comparison"""
    success: bool = Field(..., description="Whether comparison was successful")
    differences: List[CodeDifference] = Field(..., description="List of code differences")
    security_findings: List[SecurityFinding] = Field(..., description="Security analysis findings")
    risk_assessment: RiskLevel = Field(..., description="Overall risk level")
    change_summary: Dict[str, Any] = Field(..., description="Summary of detected changes")
    recommendations: List[str] = Field(..., description="Recommended actions")
    analysis_metadata: Dict[str, Any] = Field(..., description="Analysis process metadata")
    binary_metadata: Dict[str, BinaryMetadata] = Field(..., description="Metadata from both binaries")