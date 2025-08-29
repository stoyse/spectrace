"""
Fast unit tests for compliance validation endpoint using mocks
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from schemas import (
    ComplianceValidationResponse, 
    ComplianceMismatch, 
    ComplianceMatch
)

client = TestClient(app)

class TestComplianceValidationEndpoint:
    """Fast tests for /api/v1/validate-compliance endpoint"""
    
    @patch('services.compliance_analyzer.ComplianceAnalyzer.validate_compliance')
    def test_basic_compliance_validation_success(self, mock_validate):
        """Test successful compliance validation"""
        mock_validate.return_value = ComplianceValidationResponse(
            success=True,
            compliance_status="compliant",
            mismatches=[],
            matches=[
                ComplianceMatch(
                    description="Timer implementation matches specification",
                    code_reference="line 22: timer setup",
                    spec_reference="Timer section"
                )
            ],
            compliance_score=0.9,
            summary={"total_matches": 1, "total_mismatches": 0},
            recommendations=["Good alignment between code and specs"],
            analysis_metadata={"analysis_method": "mocked"}
        )
        
        code_analysis = {
            "success": True,
            "differences": [{"line_number": 22, "change_type": "added", "description": "Added timer"}],
            "change_summary": {"total_changes": 1}
        }
        
        spec_analysis = {
            "success": True,
            "new_features": [{"feature": "Timer", "description": "Hardware timer"}],
            "change_summary": {"total_changes": 1}
        }
        
        payload = {
            "code_analysis": code_analysis,
            "spec_analysis": spec_analysis
        }
        
        response = client.post("/api/v1/validate-compliance", json=payload)
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert result["compliance_status"] == "compliant"
        assert result["compliance_score"] == 0.9
        assert len(result["matches"]) == 1
    
    @patch('services.compliance_analyzer.ComplianceAnalyzer.validate_compliance')
    def test_compliance_mismatches_detection(self, mock_validate):
        """Test mismatch detection"""
        mock_validate.return_value = ComplianceValidationResponse(
            success=True,
            compliance_status="partially_compliant",
            mismatches=[
                ComplianceMismatch(
                    type="missing_in_specs",
                    description="Code change not specified",
                    code_reference="line 15: new register usage",
                    spec_reference=None,
                    severity="medium"
                )
            ],
            matches=[],
            compliance_score=0.4,
            summary={"total_matches": 0, "total_mismatches": 1},
            recommendations=["Specify new register usage"],
            analysis_metadata={"analysis_method": "mocked"}
        )
        
        code_analysis = {
            "success": True,
            "differences": [{"line_number": 15, "change_type": "added", "description": "New register"}],
            "change_summary": {"total_changes": 1}
        }
        
        spec_analysis = {
            "success": True,
            "differences": [],
            "change_summary": {"total_changes": 0}
        }
        
        payload = {
            "code_analysis": code_analysis,
            "spec_analysis": spec_analysis
        }
        
        response = client.post("/api/v1/validate-compliance", json=payload)
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert result["compliance_status"] == "partially_compliant"
        assert len(result["mismatches"]) == 1
        assert result["mismatches"][0]["type"] == "missing_in_specs"
    
    def test_empty_analysis_validation(self):
        """Test validation of empty inputs"""
        payload = {"code_analysis": {}, "spec_analysis": {"differences": []}}
        response = client.post("/api/v1/validate-compliance", json=payload)
        assert response.status_code == 400
        
        payload = {"code_analysis": {"differences": []}, "spec_analysis": {}}
        response = client.post("/api/v1/validate-compliance", json=payload)
        assert response.status_code == 400
    
    def test_malformed_json_payload(self):
        """Test malformed payloads"""
        payload = {"code_analysis": {"differences": []}}  # missing spec_analysis
        response = client.post("/api/v1/validate-compliance", json=payload)
        assert response.status_code == 422


class TestComplianceAnalyzerService:
    """Fast tests for ComplianceAnalyzer service"""
    
    def test_compliance_analyzer_initialization(self):
        """Test analyzer initializes"""
        from services.compliance_analyzer import ComplianceAnalyzer
        analyzer = ComplianceAnalyzer()
        assert analyzer.client is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])