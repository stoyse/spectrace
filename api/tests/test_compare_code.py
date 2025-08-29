"""
Fast unit tests for compare-code endpoint using mocks
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from schemas import CodeComparisonResponse, SecurityFinding, CodeDifference, RiskLevel

client = TestClient(app)

class TestCompareCodeEndpoint:
    """Fast tests for /api/v1/compare-code endpoint"""
    
    @patch('services.code_analyzer.CodeAnalyzer.compare_codes')
    def test_basic_code_comparison_success(self, mock_compare):
        """Test successful code comparison"""
        # Mock response
        mock_compare.return_value = CodeComparisonResponse(
            success=True,
            differences=[
                CodeDifference(
                    line_number=1,
                    change_type="modified",
                    old_content="ldi r16, 0x01",
                    new_content="ldi r16, 0x02",
                    context="LED value change"
                )
            ],
            security_findings=[],
            risk_assessment=RiskLevel.LOW,
            change_summary={"total_changes": 1, "modified": 1},
            recommendations=["Review LED value change"],
            analysis_metadata={"analysis_method": "mocked"}
        )
        
        payload = {
            "old_code": "ldi r16, 0x01\nout PORTB, r16",
            "new_code": "ldi r16, 0x02\nout PORTB, r16"
        }
        
        response = client.post("/api/v1/compare-code", json=payload)
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert len(result["differences"]) == 1
        assert result["risk_assessment"] == "low"
    
    @patch('services.code_analyzer.CodeAnalyzer.compare_codes')
    def test_security_findings_detection(self, mock_compare):
        """Test security findings in response"""
        mock_compare.return_value = CodeComparisonResponse(
            success=True,
            differences=[],
            security_findings=[
                SecurityFinding(
                    type="hardcoded_credentials",
                    severity=RiskLevel.HIGH,
                    location="line 2",
                    description="Hardcoded password detected",
                    code_snippet="password = 'admin123'",
                    recommendation="Use environment variables"
                )
            ],
            risk_assessment=RiskLevel.HIGH,
            change_summary={"total_changes": 1, "security_issues": 1},
            recommendations=["Fix hardcoded credentials"],
            analysis_metadata={"analysis_method": "mocked"}
        )
        
        payload = {
            "old_code": "mov r1, #0x00",
            "new_code": "password = 'admin123'"
        }
        
        response = client.post("/api/v1/compare-code", json=payload)
        
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert len(result["security_findings"]) == 1
        assert result["security_findings"][0]["type"] == "hardcoded_credentials"
        assert result["risk_assessment"] == "high"
    
    def test_empty_code_validation(self):
        """Test validation of empty inputs"""
        payload = {"old_code": "", "new_code": "ldi r16, 0x01"}
        response = client.post("/api/v1/compare-code", json=payload)
        assert response.status_code == 400
        
        payload = {"old_code": "ldi r16, 0x01", "new_code": ""}
        response = client.post("/api/v1/compare-code", json=payload)
        assert response.status_code == 400
    
    def test_malformed_json_payload(self):
        """Test malformed payloads"""
        payload = {"old_code": "ldi r16, 0x01"}  # missing new_code
        response = client.post("/api/v1/compare-code", json=payload)
        assert response.status_code == 422
    
    @patch('services.code_analyzer.CodeAnalyzer.compare_codes')
    def test_analysis_depth_parameter(self, mock_compare):
        """Test different analysis depth levels"""
        mock_compare.return_value = CodeComparisonResponse(
            success=True,
            differences=[],
            security_findings=[],
            risk_assessment=RiskLevel.LOW,
            change_summary={"total_changes": 0},
            recommendations=[],
            analysis_metadata={"analysis_depth": "detailed"}
        )
        
        payload = {
            "old_code": "ldi r16, 0x01",
            "new_code": "ldi r16, 0x02",
            "analysis_depth": "detailed"
        }
        
        response = client.post("/api/v1/compare-code", json=payload)
        assert response.status_code == 200
        result = response.json()
        assert result["analysis_metadata"]["analysis_depth"] == "detailed"


class TestCodeAnalyzerService:
    """Fast tests for CodeAnalyzer service"""
    
    def test_code_analyzer_initialization(self):
        """Test analyzer initializes"""
        from services.code_analyzer import CodeAnalyzer
        analyzer = CodeAnalyzer()
        assert analyzer.client is not None
    
    def test_risk_level_parsing(self):
        """Test risk level string parsing"""
        from services.code_analyzer import CodeAnalyzer
        analyzer = CodeAnalyzer()
        
        assert analyzer._parse_risk("critical") == RiskLevel.CRITICAL
        assert analyzer._parse_risk("HIGH") == RiskLevel.HIGH
        assert analyzer._parse_risk("Medium") == RiskLevel.MEDIUM
        assert analyzer._parse_risk("low") == RiskLevel.LOW
        assert analyzer._parse_risk("unknown") == RiskLevel.LOW

if __name__ == "__main__":
    pytest.main([__file__, "-v"])