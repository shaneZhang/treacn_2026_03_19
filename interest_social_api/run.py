import os
import sys
import logging
from datetime import datetime

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app import create_app
from config import get_config

def setup_logging():
    log_level = os.environ.get('LOG_LEVEL', 'INFO').upper()
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.getLogger('werkzeug').setLevel(logging.WARNING)

setup_logging()
logger = logging.getLogger(__name__)

app = create_app()

@app.route('/health')
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "interest-social-api",
        "version": os.environ.get('APP_VERSION', '1.0.0')
    }

@app.route('/ready')
def readiness_check():
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

if __name__ == '__main__':
    config = get_config()
    host = config.HOST
    port = config.PORT
    debug = config.DEBUG
    
    logger.info(f"Starting Interest Social API on {host}:{port}")
    logger.info(f"Environment: {config.APP_ENV}")
    logger.info(f"Debug mode: {debug}")
    
    app.run(host=host, port=port, debug=debug)
