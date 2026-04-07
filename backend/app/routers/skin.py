from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Optional

from ..ml.skin_ai import assess

router = APIRouter()


class WaterReading(BaseModel):
    ph:          float
    tds:         float
    turbidity:   float
    temperature: float
    orp:         Optional[float] = None   # v0.5 hardware may not send ORP


class SkinProfile(BaseModel):
    skin_type:              str        = Field("normal", description="normal|dry|oily|combination|sensitive")
    conditions:             List[str]  = Field(default_factory=list, description="eczema|psoriasis|rosacea|acne|none")
    eye_sensitive:          bool       = False
    respiratory_sensitive:  bool       = False


class SkinAssessRequest(BaseModel):
    reading:      WaterReading
    skin_profile: SkinProfile


@router.post("/skin/assess")
def assess_skin_safety(body: SkinAssessRequest):
    """
    POST /api/v1/skin/assess

    Stateless endpoint — takes a water reading + user skin profile and
    returns a personalised safety score, concerns, and advice.

    Works for both:
    - Pool mode (reading from ESP32 via WebSocket)
    - Portable mode (any water body)
    """
    reading_dict = body.reading.dict()
    profile_dict = body.skin_profile.dict()

    result = assess(reading_dict, profile_dict)
    return result
