from typing import Optional
from fastapi import APIRouter
from wa.metrics import compute_summary_metrics

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/summary")
def get_metrics_summary(site_id: Optional[str] = None):
    return compute_summary_metrics(site_id=site_id)
