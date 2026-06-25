"""Tests for FastAPI API routes."""

import json
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.api.server import create_app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    app = create_app()
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def mock_recommendation(sample_recommendation_dict):
    """A mock Recommendation object for testing."""
    mock = MagicMock()
    mock.to_dict.return_value = sample_recommendation_dict
    mock.recommendation = sample_recommendation_dict["recommendation"]
    mock.tender_id = sample_recommendation_dict["tender_id"]
    return mock


class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        """GET /health returns 200 with status ok."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestAnalyzeEndpoint:
    def test_analyze_returns_200_with_valid_input(
        self, client, mock_recommendation, sample_recommendation_dict
    ):
        """POST /analyze returns 200 with a valid recommendation."""
        company_profile = {
            "company_id": "TEST-001",
            "name": "Test Co",
            "annual_turnover_inr_crores": [30, 35, 40],
            "years_in_operation": 10,
            "certifications": [],
            "completed_projects": [],
        }

        with patch("src.api.routes.PipelineRunner") as mock_runner_cls:
            mock_runner = MagicMock()
            mock_runner.run.return_value = mock_recommendation
            mock_runner_cls.return_value = mock_runner

            # Create a minimal fake PDF bytes
            fake_pdf = b"%PDF-1.4 fake content"

            response = client.post(
                "/analyze",
                files={"tender_pdf": ("test.pdf", fake_pdf, "application/pdf")},
                data={"company_profile_json": json.dumps(company_profile)},
            )

        assert response.status_code == 200
        body = response.json()
        assert body["recommendation"] in ("BID", "REVIEW", "NO_BID")
        assert "qualification_score" in body

    def test_analyze_returns_422_for_invalid_json(self, client):
        """POST /analyze returns 422 when company_profile_json is not valid JSON."""
        fake_pdf = b"%PDF-1.4 fake"
        response = client.post(
            "/analyze",
            files={"tender_pdf": ("test.pdf", fake_pdf, "application/pdf")},
            data={"company_profile_json": "not json at all"},
        )
        assert response.status_code == 422

    def test_analyze_returns_422_missing_company_id(self, client):
        """POST /analyze returns 422 when company_id is missing from profile."""
        company_profile = {"name": "No ID Company"}
        fake_pdf = b"%PDF-1.4 fake"
        response = client.post(
            "/analyze",
            files={"tender_pdf": ("test.pdf", fake_pdf, "application/pdf")},
            data={"company_profile_json": json.dumps(company_profile)},
        )
        assert response.status_code == 422


class TestLedgerEndpoints:
    def test_ledger_returns_list(self, client):
        """GET /ledger returns a list (possibly empty)."""
        with patch("src.api.routes.DecisionLedger") as mock_ledger_cls:
            mock_ledger = MagicMock()
            mock_ledger.read_paginated.return_value = ([], 0)
            mock_ledger_cls.return_value = mock_ledger

            response = client.get("/ledger")

        assert response.status_code == 200
        body = response.json()
        assert "results" in body
        assert "total" in body
        assert isinstance(body["results"], list)

    def test_ledger_pagination_params(self, client):
        """GET /ledger accepts page and page_size params."""
        with patch("src.api.routes.DecisionLedger") as mock_ledger_cls:
            mock_ledger = MagicMock()
            mock_ledger.read_paginated.return_value = ([], 0)
            mock_ledger_cls.return_value = mock_ledger

            response = client.get("/ledger?page=2&page_size=10")

        assert response.status_code == 200

    def test_ledger_single_found(self, client, sample_recommendation_dict):
        """GET /ledger/{id} returns the decision if found."""
        with patch("src.api.routes.DecisionLedger") as mock_ledger_cls:
            mock_ledger = MagicMock()
            mock_ledger.find_by_id.return_value = sample_recommendation_dict
            mock_ledger_cls.return_value = mock_ledger

            response = client.get("/ledger/rec_test001")

        assert response.status_code == 200
        assert response.json()["recommendation"] == "BID"

    def test_ledger_single_not_found(self, client):
        """GET /ledger/{id} returns 404 when ID not found."""
        with patch("src.api.routes.DecisionLedger") as mock_ledger_cls:
            mock_ledger = MagicMock()
            mock_ledger.find_by_id.return_value = None
            mock_ledger_cls.return_value = mock_ledger

            response = client.get("/ledger/nonexistent_id")

        assert response.status_code == 404
