"""
Fast unit tests for compare-specs endpoint using mocks
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from schemas import (
    SpecificationComparisonResponse, 
    SpecificationDifference, 
    SpecificationFeature,
    SpecificationBehaviorChange
)

client = TestClient(app)

class TestCompareSpecsEndpoint:
    """Fast tests for /api/v1/compare-specs endpoint"""
    
    @patch('services.spec_analyzer.SpecificationAnalyzer.compare_specs')
    def test_basic_specs_comparison_success(self, mock_compare):
        """Test successful specification comparison"""
        mock_compare.return_value = SpecificationComparisonResponse(
            success=True,
            differences=[
                SpecificationDifference(
                    section="Introduction",
                    change_type="modified",
                    old_content="Version 1",
                    new_content="Version 2",
                    description="Version number updated"
                )
            ],
            new_features=[
                SpecificationFeature(
                    feature="Timer support",
                    description="Hardware timer functionality",
                    impact="Improved efficiency"
                )
            ],
            removed_features=[],
            behavioral_changes=[],
            change_summary={"total_changes": 1},
            recommendations=["Review timer implementation"],
            analysis_metadata={"analysis_method": "mocked"}
        )
        
        payload = {
            "old_spec": "# Version 1\nBasic LED blink",
            "new_spec": "# Version 2\nTimer-based LED blink"
        }
        
        response = client.post("/api/v1/compare-specs", json=payload)
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert len(result["differences"]) == 1
        assert len(result["new_features"]) == 1
    
    @patch('services.spec_analyzer.SpecificationAnalyzer.compare_specs')
    def test_behavioral_changes_detection(self, mock_compare):
        """Test behavioral changes in specification"""
        mock_compare.return_value = SpecificationComparisonResponse(
            success=True,
            differences=[],
            new_features=[],
            removed_features=[],
            behavioral_changes=[
                SpecificationBehaviorChange(
                    change="LED control method",
                    old_behavior="Software delay loop",
                    new_behavior="Hardware timer-based",
                    security_impact="Reduced CPU usage, more predictable timing"
                )
            ],
            change_summary={"behavioral_changes": 1},
            recommendations=["Test timing accuracy"],
            analysis_metadata={"analysis_method": "mocked"}
        )
        
        payload = {
            "old_spec": "Uses software delay for timing",
            "new_spec": "Uses hardware timer for timing"
        }
        
        response = client.post("/api/v1/compare-specs", json=payload)
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert len(result["behavioral_changes"]) == 1
        assert result["behavioral_changes"][0]["change"] == "LED control method"
    
    def test_empty_specs_validation(self):
        """Test validation of empty inputs"""
        payload = {"old_spec": "", "new_spec": "# New spec"}
        response = client.post("/api/v1/compare-specs", json=payload)
        assert response.status_code == 400
        
        payload = {"old_spec": "# Old spec", "new_spec": ""}
        response = client.post("/api/v1/compare-specs", json=payload)
        assert response.status_code == 400
    
    def test_malformed_json_payload(self):
        """Test malformed payloads"""
        payload = {"old_spec": "# Old spec"}  # missing new_spec
        response = client.post("/api/v1/compare-specs", json=payload)
        assert response.status_code == 422


class TestSpecificationAnalyzerService:
    """Fast tests for SpecificationAnalyzer service"""
    
    def test_spec_analyzer_initialization(self):
        """Test analyzer initializes"""
        from services.spec_analyzer import SpecificationAnalyzer
        analyzer = SpecificationAnalyzer()
        assert analyzer.client is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])