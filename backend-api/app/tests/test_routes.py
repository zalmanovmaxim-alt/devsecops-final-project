def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'

def test_homepage_redirect(client):
    # Homepage should render or return something. Even if it renders template, status should be 200.
    response = client.get('/')
    assert response.status_code == 200
    # In our modified version, it still renders homepage.html, which expects 'players_grouped'
    # But fixture creates empty DB, so it should handle empty data gracefully.

def test_metrics_endpoint(client):
    # Prometheus metrics usually expose /metrics
    response = client.get('/metrics')
    assert response.status_code == 200
    assert b'flask_http_request_duration_seconds_bucket' in response.data
