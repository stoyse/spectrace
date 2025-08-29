"""
Simple Code Analyzer using LLM

This module compares firmware code using OpenAI and provides security analysis.
"""

import json
import asyncio
from typing import List, Dict, Any
from schemas import (
    CodeDifference, 
    SecurityFinding, 
    RiskLevel, 
    CodeComparisonResponse,
    CodeComparisonRequest,
    OpenAIRequest
)
from client import openai_client
from prompts import get_code_comparison_prompt


class CodeAnalyzer:
    """Simple code analyzer that uses LLM for analysis"""
    
    def __init__(self):
        """Initialize the analyzer"""
        self.client = openai_client
    
    async def compare_codes(self, request: CodeComparisonRequest) -> CodeComparisonResponse:
        """
        Compare two code versions using LLM.
        
        Args:
            request: Contains old_code, new_code, firmware_type etc.
            
        Returns:
            Response with differences and security analysis
        """
        try:
            # Create the prompt
            prompt = get_code_comparison_prompt(
                request.old_code,
                request.new_code, 
                request.firmware_type or "Unknown"
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
            differences = self._make_differences(analysis.get("differences", []))
            findings = self._make_findings(analysis.get("security_findings", []))
            risk = self._parse_risk(analysis.get("risk_assessment", "low"))
            
            # Build metadata
            metadata = {
                'old_code_lines': len(request.old_code.splitlines()),
                'new_code_lines': len(request.new_code.splitlines()),
                'total_differences': len(differences),
                'security_findings_count': len(findings),
                'analysis_method': "llm_based",
                'analysis_depth': request.analysis_depth,
                'firmware_type': request.firmware_type
            }
            
            return CodeComparisonResponse(
                success=True,
                differences=differences,
                security_findings=findings,
                risk_assessment=risk,
                change_summary=analysis.get("change_summary", {}),
                recommendations=analysis.get("recommendations", []),
                analysis_metadata=metadata
            )
            
        except Exception as e:
            return CodeComparisonResponse(
                success=False,
                differences=[],
                security_findings=[],
                risk_assessment=RiskLevel.LOW,
                change_summary={'error': str(e)},
                recommendations=[f"Analysis failed: {str(e)}"],
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
                "differences": [],
                "security_findings": [],
                "risk_assessment": "low",
                "change_summary": {"total_changes": 0},
                "recommendations": ["Could not parse LLM response"]
            }
    
    def _make_differences(self, diff_list: List[Dict]) -> List[CodeDifference]:
        """Convert LLM differences to our objects"""
        differences = []
        
        for diff in diff_list:
            try:
                differences.append(CodeDifference(
                    line_number=diff.get("line_number", 1),
                    change_type=diff.get("change_type", "modified"),
                    old_content=diff.get("old_content"),
                    new_content=diff.get("new_content"),
                    context=diff.get("description", "")
                ))
            except:
                continue  # Skip bad entries
                
        return differences
    
    def _make_findings(self, finding_list: List[Dict]) -> List[SecurityFinding]:
        """Convert LLM findings to our objects"""
        findings = []
        
        for finding in finding_list:
            try:
                severity = self._parse_risk(finding.get("severity", "low"))
                findings.append(SecurityFinding(
                    type=finding.get("type", "unknown"),
                    severity=severity,
                    location=finding.get("location", "unknown"),
                    description=finding.get("description", ""),
                    code_snippet=finding.get("code_snippet", ""),
                    recommendation=finding.get("recommendation", "")
                ))
            except:
                continue  # Skip bad entries
                
        return findings
    
    def _parse_risk(self, risk_str: str) -> RiskLevel:
        """Convert risk string to enum"""
        risk_map = {
            "critical": RiskLevel.CRITICAL,
            "high": RiskLevel.HIGH,
            "medium": RiskLevel.MEDIUM,
            "low": RiskLevel.LOW
        }
        return risk_map.get(risk_str.lower(), RiskLevel.LOW)