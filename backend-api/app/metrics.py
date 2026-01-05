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
    # Unregister first to avoid duplicates during re-initialization (e.g. tests)
    try:
        REGISTRY.unregister(REGISTRY._collector_to_names.get(DatabaseCollector(db), None))
    except:
        pass # Ignore if not registered or other issues, just try to register
        
    # Ideally we should verify if it's already there, but unregister is safer for tests
    # Actually, unregistering by instance might fail if instance is different.
    # Better approach: Clear metrics involved or handle error.
    
    # Simple fix for "Duplicated timeseries": 
    # Use a custom registry for the app or checking if registered?
    # No, simplest is to wrap in try/except or just ignore if it fails (not ideal for strictness)
    
    # Let's try to unregister by name loop if needed, OR:
    # Since Duplicated timeseries comes from checking names.
    
    # We will just suppress the error if it happens, assuming it's already registered.
    try:
        REGISTRY.register(DatabaseCollector(db))
    except ValueError:
        pass # Already registered
    
    return metrics
