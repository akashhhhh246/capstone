import pytest

def test_api_detection_analyze(test_client):
    res = test_client.post("/api/v1/detection/analyze", json={
        "text": "Confidential whistleblowers confirm coordinated emergency power grid shutdown tonight at midnight!",
        "domain": "disinformation",
        "register_content": True
    })
    assert res.status_code == 200
    data = res.json()
    assert "classification" in data
    assert "confidence" in data
    assert "gltr_result" in data
    assert "watermark_result" in data
    assert data["content_id"] is not None

def test_api_campaigns_list_and_detail(test_client):
    res = test_client.get("/api/v1/campaigns")
    assert res.status_code == 200
    campaigns = res.json()
    assert len(campaigns) > 0
    
    first_id = campaigns[0]["id"]
    res_detail = test_client.get(f"/api/v1/campaigns/{first_id}")
    assert res_detail.status_code == 200
    detail = res_detail.json()
    assert detail["id"] == first_id
    assert "explainability_reasons" in detail

def test_api_dashboard_stats(test_client):
    res = test_client.get("/api/v1/dashboard/stats")
    assert res.status_code == 200
    stats = res.json()
    assert "total_analyzed_content" in stats
    assert "active_campaigns_count" in stats
    assert "platforms_count" in stats

def test_api_models_governance(test_client):
    res = test_client.get("/api/v1/models")
    assert res.status_code == 200
    models = res.json()
    assert len(models) >= 4
    for m in models:
        assert "operational_status" in m
        assert "limitations" in m
