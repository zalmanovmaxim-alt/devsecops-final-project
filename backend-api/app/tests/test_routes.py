def test_health_check(client):
    response = client.get('/health', follow_redirects=True)
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'

def test_metrics_endpoint(client):
    # Prometheus metrics usually expose /metrics
    response = client.get('/metrics')
    assert response.status_code == 200
    # Check for any prometheus content
    assert b'# HELP' in response.data or b'# TYPE' in response.data
