import os
from typing import Any, Dict
from django.http import HttpRequest


def analytics_context(request: HttpRequest) -> Dict[str, Any]:
    """
    Exposes Google Analytics 4 Measurement ID and Google Search Console
    verification token to templates dynamically via environment variables.
    """
    return {
        "GA4_MEASUREMENT_ID": os.environ.get("GA4_MEASUREMENT_ID", ""),
        "GSC_VERIFICATION_CODE": os.environ.get("GSC_VERIFICATION_CODE", ""),
    }
