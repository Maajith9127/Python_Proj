"""HTTP client for the partner FitMetrics API (23MIC0060)."""
from __future__ import annotations
import httpx
from .. import config


class PartnerUnavailable(Exception):
    pass


async def fetch_partner_workout(payload: dict) -> dict:
    """POST /metrics/workout-analysis on FitMetrics partner API (with local fallback if partner is sleeping)."""
    headers = {"X-API-Key": config.FITMETRICS_API_KEY} if config.FITMETRICS_API_KEY else {}
    try:
        async with httpx.AsyncClient(timeout=config.FITMETRICS_TIMEOUT) as client:
            r = await client.post(f"{config.FITMETRICS_BASE_URL}/metrics/workout-analysis", json=payload, headers=headers)
            r.raise_for_status()
            body = r.json()
            return body.get("data", body)
    except Exception:
        # Fallback to partner contract calculation if remote Render instance is sleeping
        from ..engine import training
        w = training.analyse_workout(
            payload.get("activity", "running"),
            float(payload.get("duration", 45)),
            float(payload.get("weight", 74)),
            int(payload.get("age", 21)),
            int(payload.get("restingHr", 62)),
            int(payload.get("avgHr", 172)),
            payload.get("gender", "male"),
            payload.get("climate", "normal"),
        )
        return {
            "activity": w["activity"],
            "durationMin": w["durationMin"],
            "caloriesBurned": w["caloriesBurned"],
            "percentHrr": w["percentHrr"],
            "zone": w["zone"],
            "trainingLoad": w["trainingLoad"],
            "recoveryHours": w["recoveryHours"],
        }
