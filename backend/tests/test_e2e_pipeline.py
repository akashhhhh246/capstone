import pytest

def test_full_end_to_end_investigative_workflow(test_client):
    """
    End-to-End Workflow Verification:
    1. Analyst submits suspicious real-world/synthetic text
    2. Backend preprocesses text and runs TF-IDF + GLTR + Watermark
    3. DetectionResult and Content are registered in database
    4. SimilarityService compares against historical repository
    5. ProvenanceService reconstructs multi-platform lineage DAG
    6. PropagationService calculates NetworkX velocity and PyG GNN risk
    7. Campaign & RiskScoringService generates itemized explainability reasons
    8. Dashboard stats reflect updated counts and threat alerts
    """
    # Step 1: Text submission & Detection
    submission_text = "LEAKED INTEL: High-frequency cognitive modulation transmitters secretly active on aviation flights tonight! #AeroTruth"
    det_res = test_client.post("/api/v1/detection/analyze", json={
        "text": submission_text,
        "domain": "disinformation",
        "register_content": True
    })
    assert det_res.status_code == 200
    det_data = det_res.json()
    assert det_data["classification"] in ["HUMAN", "AI_GENERATED"]
    assert "gltr_result" in det_data
    assert "watermark_result" in det_data
    
    content_id = det_data["content_id"]
    assert content_id is not None

    # Step 2: Content Registry retrieval
    content_res = test_client.get(f"/api/v1/content/{content_id}")
    assert content_res.status_code == 200
    c_data = content_res.json()
    assert c_data["id"] == content_id
    assert c_data["word_count"] > 5

    # Step 3: Provenance reconstruction
    prov_res = test_client.get(f"/api/v1/provenance/{content_id}")
    assert prov_res.status_code == 200
    prov_data = prov_res.json()
    assert "nodes" in prov_data
    assert "edges" in prov_data
    assert prov_data["is_acyclic"] is True

    # Step 4: Propagation Graph & GNN metrics
    prop_res = test_client.get(f"/api/v1/propagation/{content_id}")
    assert prop_res.status_code == 200
    prop_data = prop_res.json()
    assert "propagation_velocity_per_hour" in prop_data
    assert "gnn_analysis" in prop_data

    # Step 5: Campaign exploration
    camps_res = test_client.get("/api/v1/campaigns")
    assert camps_res.status_code == 200
    camps = camps_res.json()
    assert len(camps) > 0
    target_camp_id = camps[0]["id"]

    camp_detail_res = test_client.get(f"/api/v1/campaigns/{target_camp_id}")
    assert camp_detail_res.status_code == 200
    camp_detail = camp_detail_res.json()
    assert len(camp_detail["explainability_reasons"]) > 0

    # Step 6: Dashboard Stats verification
    dash_res = test_client.get("/api/v1/dashboard/stats")
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert dash_data["total_analyzed_content"] >= 20
    assert dash_data["active_campaigns_count"] >= 2
    assert len(dash_data["recent_alerts"]) > 0
