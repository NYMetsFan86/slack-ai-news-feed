"""Health check endpoint for monitoring Cloud Function health"""
import json
import logging
from typing import Dict, Any
from datetime import datetime
import functions_framework
from flask import Request, Response

from .config import Config
from .firestore_client import FirestoreClient
from .llm_client import LLMClient
from .slack_client import SlackClient

logger = logging.getLogger(__name__)


@functions_framework.http
def health_check(request: Request) -> Response:
    """
    HTTP endpoint for health checking the AI News Summarizer
    
    Args:
        request: Flask Request object
        
    Returns:
        Flask Response with health status
    """
    health_status: Dict[str, Any] = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "ai-news-summarizer",
        "checks": {}
    }
    
    # Check configuration
    try:
        config_valid = Config.is_valid()
        health_status["checks"]["config"] = {
            "status": "pass" if config_valid else "fail",
            "valid": config_valid
        }
        if not config_valid:
            health_status["status"] = "unhealthy"
    except Exception as e:
        health_status["checks"]["config"] = {
            "status": "fail",
            "error": str(e)
        }
        health_status["status"] = "unhealthy"
    
    # Check Firestore connectivity
    try:
        db_client = FirestoreClient()
        # Try to read a non-existent document (should not throw)
        db_client.is_url_processed("health-check-test-url")
        health_status["checks"]["firestore"] = {
            "status": "pass",
            "collection": Config.FIRESTORE_COLLECTION
        }
    except Exception as e:
        health_status["checks"]["firestore"] = {
            "status": "fail",
            "error": str(e)
        }
        health_status["status"] = "unhealthy"
    
    # Check OpenRouter API (optional - only if requested)
    if request.args.get('check_llm') == 'true':
        try:
            llm_client = LLMClient()
            if llm_client.test_connection():
                health_status["checks"]["openrouter"] = {
                    "status": "pass",
                    "model": Config.OPENROUTER_MODEL
                }
            else:
                health_status["checks"]["openrouter"] = {
                    "status": "fail",
                    "error": "Connection test failed"
                }
                health_status["status"] = "degraded"
        except Exception as e:
            health_status["checks"]["openrouter"] = {
                "status": "fail",
                "error": str(e)
            }
            health_status["status"] = "degraded"
    
    # Check Slack webhook (optional - only if requested)
    if request.args.get('check_slack') == 'true':
        try:
            slack_client = SlackClient()
            # Don't actually send a test message
            if Config.SLACK_WEBHOOK_URL:
                health_status["checks"]["slack"] = {
                    "status": "pass",
                    "webhook_configured": True
                }
            else:
                health_status["checks"]["slack"] = {
                    "status": "fail",
                    "error": "Webhook URL not configured"
                }
                health_status["status"] = "unhealthy"
        except Exception as e:
            health_status["checks"]["slack"] = {
                "status": "fail",
                "error": str(e)
            }
            health_status["status"] = "degraded"
    
    # Determine HTTP status code
    if health_status["status"] == "healthy":
        status_code = 200
    elif health_status["status"] == "degraded":
        status_code = 200  # Still return 200 for degraded
    else:
        status_code = 503
    
    return Response(
        json.dumps(health_status, indent=2),
        status=status_code,
        mimetype='application/json'
    )


@functions_framework.http
def readiness_check(request: Request) -> Response:
    """
    Kubernetes-style readiness probe
    
    Args:
        request: Flask Request object
        
    Returns:
        Flask Response indicating readiness
    """
    try:
        # Quick checks only
        if not Config.is_valid():
            return Response("Not Ready - Invalid Configuration", status=503)
        
        # Check Firestore is accessible
        db_client = FirestoreClient()
        db_client.is_url_processed("readiness-check")
        
        return Response("Ready", status=200)
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return Response(f"Not Ready - {str(e)}", status=503)


@functions_framework.http
def liveness_check(request: Request) -> Response:
    """
    Kubernetes-style liveness probe
    
    Args:
        request: Flask Request object
        
    Returns:
        Flask Response indicating liveness
    """
    # Simple check - if we can respond, we're alive
    return Response("Alive", status=200)