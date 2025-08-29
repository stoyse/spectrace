"""
Simple Compliance Analyzer using LLM

This module validates compliance between code analysis and specification analysis results.
"""

import json
from typing import List, Dict, Any
from schemas import (
    ComplianceMismatch,
    ComplianceMatch,
    ComplianceValidationResponse,
    ComplianceValidationRequest,
    OpenAIRequest
)
from client import openai_client
from prompts import get_compliance_validation_prompt


class ComplianceAnalyzer:
    """Simple compliance analyzer that uses LLM for validation"""
    
    def __init__(self):
        """Initialize the analyzer"""
        self.client = openai_client
    
    async def validate_compliance(self, request: ComplianceValidationRequest) -> ComplianceValidationResponse:
        """
        Validate compliance between code and specification analysis results.
        
        Args:
            request: Contains code_analysis and spec_analysis results
            
        Returns:
            Response with compliance validation results
        """
        try:
            # Convert analysis results to JSON strings for the prompt
            code_analysis_str = json.dumps(request.code_analysis, indent=2)
            spec_analysis_str = json.dumps(request.spec_analysis, indent=2)
            
            # Create the prompt
            prompt = get_compliance_validation_prompt(
                code_analysis_str,
                spec_analysis_str
            )
            
            # Make OpenAI request
            openai_request = OpenAIRequest(
                text=prompt,
                model="gpt-4",
                temperature=0.2,
                max_tokens=2000
            )
            
            # Get LLM response
            llm_response = await self._call_openai(openai_request)
            
            if not llm_response.success:
                raise Exception(f"OpenAI failed: {llm_response.message}")
            
            # Parse the JSON response
            analysis = self._parse_response(llm_response.data.get("response", ""))
            
            # Convert to our objects
            mismatches = self._make_mismatches(analysis.get("mismatches", []))
            matches = self._make_matches(analysis.get("matches", []))
            compliance_status = analysis.get("compliance_status", "unknown")
            compliance_score = float(analysis.get("compliance_score", 0.0))
            
            # Build metadata
            metadata = {
                'code_changes_count': len(request.code_analysis.get('differences', [])),
                'spec_changes_count': len(request.spec_analysis.get('differences', [])),
                'mismatches_count': len(mismatches),
                'matches_count': len(matches),
                'analysis_method': "llm_based"
            }
            
            return ComplianceValidationResponse(
                success=True,
                compliance_status=compliance_status,
                mismatches=mismatches,
                matches=matches,
                compliance_score=compliance_score,
                summary=analysis.get("summary", {}),
                recommendations=analysis.get("recommendations", []),
                analysis_metadata=metadata
            )
            
        except Exception as e:
            return ComplianceValidationResponse(
                success=False,
                compliance_status="error",
                mismatches=[],
                matches=[],
                compliance_score=0.0,
                summary={'error': str(e)},
                recommendations=[f"Validation failed: {str(e)}"],
                analysis_metadata={'error': True}
            )
    
    async def _call_openai(self, request: OpenAIRequest):
        """Call OpenAI API"""
        return await self.client.process_text(request)
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON response from LLM"""
        try:
            # Find JSON in response
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = response_text[start:end]
                return json.loads(json_str)
            else:
                return json.loads(response_text)
                
        except json.JSONDecodeError:
            # Return empty analysis if parsing fails
            return {
                "compliance_status": "error",
                "mismatches": [],
                "matches": [],
                "compliance_score": 0.0,
                "summary": {"total_code_changes": 0, "total_doc_changes": 0},
                "recommendations": ["Could not parse LLM response"]
            }
    
    def _make_mismatches(self, mismatch_list: List[Dict]) -> List[ComplianceMismatch]:
        """Convert LLM mismatches to our objects"""
        mismatches = []
        
        for mismatch in mismatch_list:
            try:
                mismatches.append(ComplianceMismatch(
                    type=mismatch.get("type", "unknown"),
                    description=mismatch.get("description", ""),
                    code_reference=mismatch.get("code_reference", ""),
                    doc_reference=mismatch.get("doc_reference"),
                    severity=mismatch.get("severity", "medium")
                ))
            except:
                continue  # Skip bad entries
                
        return mismatches
    
    def _make_matches(self, match_list: List[Dict]) -> List[ComplianceMatch]:
        """Convert LLM matches to our objects"""
        matches = []
        
        for match in match_list:
            try:
                matches.append(ComplianceMatch(
                    description=match.get("description", ""),
                    code_reference=match.get("code_reference", ""),
                    doc_reference=match.get("doc_reference", "")
                ))
            except:
                continue  # Skip bad entries
                
        return matches