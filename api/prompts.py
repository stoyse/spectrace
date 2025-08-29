"""
Simple prompts for code analysis
"""

def get_code_comparison_prompt(old_code, new_code, firmware_type="Unknown"):
    """
    Get a simple prompt for comparing two code versions.
    
    Args:
        old_code: Original code
        new_code: New code  
        firmware_type: Type of firmware
        
    Returns:
        Formatted prompt string
    """
    return f"""You are a firmware security expert. Compare these two code versions and provide analysis in JSON format.

OLD CODE:
{old_code}

NEW CODE:
{new_code}

FIRMWARE TYPE: {firmware_type}

Please analyze:
1. What changed between the versions
2. Any security concerns (hardcoded passwords, network calls, memory issues, etc.)
3. Risk level (low, medium, high, critical)

Respond with this JSON structure:
{{
    "differences": [
        {{
            "line_number": 1,
            "change_type": "added|removed|modified",
            "old_content": "original line or null",
            "new_content": "new line or null", 
            "description": "what changed"
        }}
    ],
    "security_findings": [
        {{
            "type": "hardcoded_credentials|network_calls|memory_operations|other",
            "severity": "critical|high|medium|low",
            "location": "where found",
            "description": "what was found", 
            "code_snippet": "problematic code",
            "recommendation": "how to fix"
        }}
    ],
    "risk_assessment": "critical|high|medium|low",
    "change_summary": {{
        "total_changes": 0,
        "major_changes": ["list of important changes"],
        "security_impact": "description"
    }},
    "recommendations": ["recommendation 1", "recommendation 2"]
}}"""


def get_specification_comparison_prompt(old_spec, new_spec):
    """
    Get a simple prompt for comparing two specification versions.
    
    Args:
        old_spec: Original specification
        new_spec: New specification
        
    Returns:
        Formatted prompt string
    """
    return f"""You are a technical specification expert. Compare these two specification versions and provide analysis in JSON format.

OLD SPECIFICATION:
{old_spec}

NEW SPECIFICATION:
{new_spec}

Please analyze:
1. What changed between the specification versions
2. New features or functionality mentioned
3. Removed features or deprecated items
4. Changes in behavior, security, or implementation details

Respond with this JSON structure:
{{
    "differences": [
        {{
            "section": "section name or line reference",
            "change_type": "added|removed|modified",
            "old_content": "original content or null",
            "new_content": "new content or null",
            "description": "what changed"
        }}
    ],
    "new_features": [
        {{
            "feature": "feature name",
            "description": "what this feature does",
            "impact": "impact on security/functionality"
        }}
    ],
    "removed_features": [
        {{
            "feature": "feature name", 
            "description": "what was removed",
            "impact": "impact of removal"
        }}
    ],
    "behavioral_changes": [
        {{
            "change": "behavior that changed",
            "old_behavior": "how it worked before",
            "new_behavior": "how it works now",
            "security_impact": "security implications if any"
        }}
    ],
    "change_summary": {{
        "total_changes": 0,
        "major_changes": ["list of important changes"],
        "risk_level": "low|medium|high|critical"
    }},
    "recommendations": ["recommendation 1", "recommendation 2"]
}}"""


def get_compliance_validation_prompt(code_analysis, spec_analysis):
    """
    Get a simple prompt for validating if code changes match specification changes.
    
    Args:
        code_analysis: Results from code comparison analysis
        spec_analysis: Results from specification comparison analysis
        
    Returns:
        Formatted prompt string
    """
    return f"""You are a quality assurance expert. Compare these code analysis results with specification analysis results to check if they match and make sense together.

CODE ANALYSIS RESULTS:
{code_analysis}

SPECIFICATION ANALYSIS RESULTS:
{spec_analysis}

Please analyze:
1. Do the code changes match what's described in the specification changes?
2. Are there code changes not mentioned in the specification?
3. Are there specification changes not reflected in code?
4. Overall compliance between code and specification

Respond with this JSON structure:
{{
    "compliance_status": "compliant|partially_compliant|non_compliant",
    "mismatches": [
        {{
            "type": "missing_in_spec|missing_in_code|inconsistent",
            "description": "what doesn't match",
            "code_reference": "reference to code change",
            "spec_reference": "reference to spec change or null",
            "severity": "high|medium|low"
        }}
    ],
    "matches": [
        {{
            "description": "what matches correctly",
            "code_reference": "reference to code change",
            "spec_reference": "reference to spec change"
        }}
    ],
    "compliance_score": 0.0,
    "summary": {{
        "total_code_changes": 0,
        "total_spec_changes": 0,
        "matched_changes": 0,
        "unmatched_changes": 0,
        "overall_assessment": "assessment description"
    }},
    "recommendations": ["recommendation 1", "recommendation 2"]
}}"""