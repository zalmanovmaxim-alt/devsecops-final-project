
from prometheus_flask_exporter import PrometheusMetrics

def init_metrics(app):
    metrics = PrometheusMetrics(app)
    # Common metrics are exported automatically by the library
    return metrics
