"""
Metrics endpoint for Prometheus scraping.
"""

from fastapi import APIRouter, Response
from app.core.metrics import get_metrics, get_metrics_content_type

router = APIRouter()


@router.get("")
async def metrics():
    """
    Expose Prometheus metrics for scraping.
    
    This endpoint returns metrics in Prometheus exposition format.
    Configure your Prometheus server to scrape this endpoint.
    
    Example prometheus.yml:
    ```yaml
    scrape_configs:
      - job_name: 'easeemail'
        scrape_interval: 15s
        static_configs:
          - targets: ['api:8000']
        metrics_path: '/metrics'
    ```
    """
    return Response(
        content=get_metrics(),
        media_type=get_metrics_content_type()
    )
