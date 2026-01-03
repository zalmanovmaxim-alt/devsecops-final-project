from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client.core import GaugeMetricFamily, REGISTRY
import sqlalchemy

class DatabaseCollector(object):
    def __init__(self, db):
        self.db = db

    def collect(self):
        # Create a metric family
        gauge = GaugeMetricFamily('db_connection_status', 'Status of database connection (1=Up, 0=Down)')
        
        status = 0
        try:
            # Short timeout to avoid blocking metrics if DB hangs
            # Note: SQLAlchemy execute doesn't easily support timeout per-query unless configured in engine
            # We assume a quick check. 
            with self.db.engine.connect() as connection:
                connection.execute(sqlalchemy.text("SELECT 1"))
                status = 1
        except Exception:
            status = 0
            
        gauge.add_metric([], status)
        yield gauge

def init_metrics(app, db):
    metrics = PrometheusMetrics(app)
    
    # Register custom collector
    REGISTRY.register(DatabaseCollector(db))
    
    return metrics
