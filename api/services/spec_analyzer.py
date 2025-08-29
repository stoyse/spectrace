"""
Simple Specification Analyzer using LLM

This module compares specifications using OpenAI and provides change analysis.
"""

import json
from typing import List, Dict, Any
from schemas import (
    SpecificationDifference,
    SpecificationFeature, 
    SpecificationBehaviorChange,
    SpecificationComparisonResponse,
    SpecificationComparisonRequest,
    OpenAIRequest
)
from client import openai_client
from prompts import get_specification_comparison_prompt


class SpecificationAnalyzer:
    """Simple specification analyzer that uses LLM for analysis"""
    
    def __init__(self):
        """Initialize the analyzer"""
        self.client = openai_client
    
    async def compare_specs(self, request: SpecificationComparisonRequest) -> SpecificationComparisonResponse:
        """
        Compare two specification versions using LLM.
        
        Args:
            request: Contains old_spec, new_spec
            
        Returns:
            Response with differences and analysis
        """
        try:
            # Create the prompt
            prompt = get_specification_comparison_prompt(
                request.old_spec,
                request.new_spec
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
            new_features = self._make_features(analysis.get("new_features", []))
            removed_features = self._make_features(analysis.get("removed_features", []))
            behavioral_changes = self._make_behavior_changes(analysis.get("behavioral_changes", []))
            
            # Build metadata
            metadata = {
                'old_spec_length': len(request.old_spec),
                'new_spec_length': len(request.new_spec),
                'total_differences': len(differences),
                'new_features_count': len(new_features),
                'removed_features_count': len(removed_features),
                'behavioral_changes_count': len(behavioral_changes),
                'analysis_method': "llm_based"
            }
            
            return SpecificationComparisonResponse(
                success=True,
                differences=differences,
                new_features=new_features,
                removed_features=removed_features,
                behavioral_changes=behavioral_changes,
                change_summary=analysis.get("change_summary", {}),
                recommendations=analysis.get("recommendations", []),
                analysis_metadata=metadata
            )
            
        except Exception as e:
            return SpecificationComparisonResponse(
                success=False,
                differences=[],
                new_features=[],
                removed_features=[],
                behavioral_changes=[],
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
                "new_features": [],
                "removed_features": [],
                "behavioral_changes": [],
                "change_summary": {"total_changes": 0},
                "recommendations": ["Could not parse LLM response"]
            }
    
    def _make_differences(self, diff_list: List[Dict]) -> List[SpecificationDifference]:
        """Convert LLM differences to our objects"""
        differences = []
        
        for diff in diff_list:
            try:
                differences.append(SpecificationDifference(
                    section=diff.get("section", "unknown"),
                    change_type=diff.get("change_type", "modified"),
                    old_content=diff.get("old_content"),
                    new_content=diff.get("new_content"),
                    description=diff.get("description", "")
                ))
            except:
                continue  # Skip bad entries
                
        return differences
    
    def _make_features(self, feature_list: List[Dict]) -> List[SpecificationFeature]:
        """Convert LLM features to our objects"""
        features = []
        
        for feature in feature_list:
            try:
                features.append(SpecificationFeature(
                    feature=feature.get("feature", "unknown"),
                    description=feature.get("description", ""),
                    impact=feature.get("impact", "")
                ))
            except:
                continue  # Skip bad entries
                
        return features
    
    def _make_behavior_changes(self, change_list: List[Dict]) -> List[SpecificationBehaviorChange]:
        """Convert LLM behavior changes to our objects"""
        changes = []
        
        for change in change_list:
            try:
                changes.append(SpecificationBehaviorChange(
                    change=change.get("change", "unknown"),
                    old_behavior=change.get("old_behavior", ""),
                    new_behavior=change.get("new_behavior", ""),
                    security_impact=change.get("security_impact", "")
                ))
            except:
                continue  # Skip bad entries
                
        return changes