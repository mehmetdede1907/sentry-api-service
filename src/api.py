from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import httpx
from datetime import datetime
from .utils import extract_issue_id, create_stacktrace

SENTRY_API_BASE = "https://sentry.io/api/0/"

app = FastAPI(
    title="Sentry API Service",
    description="API service for retrieving and analyzing Sentry issues",
    version="0.6.2"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SentryConfig(BaseModel):
    auth_token: str

class SentryIssueRequest(BaseModel):
    issue_id_or_url: str

class SentryResponse(BaseModel):
    title: str
    id: str
    status: str
    level: str
    first_seen: datetime
    last_seen: datetime
    count: int
    stacktrace: Dict[str, Any]

# Global configuration
sentry_config: Optional[SentryConfig] = None

@app.post("/config")
async def set_config(config: SentryConfig):
    """Set Sentry configuration including authentication token"""
    global sentry_config
    sentry_config = config
    return {"message": "Configuration updated successfully"}

@app.get("/config")
async def get_config():
    """Get current Sentry configuration status"""
    if sentry_config:
        return {"configured": True}
    return {"configured": False}

def get_current_config():
    """Dependency to check if Sentry is configured"""
    if not sentry_config:
        raise HTTPException(
            status_code=400,
            detail="Sentry not configured. Please set configuration first using /config endpoint"
        )
    return sentry_config

async def fetch_sentry_issue(issue_id: str, auth_token: str) -> Dict[str, Any]:
    """Fetch issue details from Sentry API"""
    async with httpx.AsyncClient(base_url=SENTRY_API_BASE) as client:
        response = await client.get(
            f"issues/{issue_id}/",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        if response.status_code == 401:
            raise HTTPException(
                status_code=401,
                detail="Unauthorized. Please check your Sentry authentication token."
            )
        response.raise_for_status()
        return response.json()

@app.post("/sentry/issue", response_model=SentryResponse)
async def get_sentry_issue(
    request: SentryIssueRequest,
    config: SentryConfig = Depends(get_current_config)
):
    """
    Retrieve issue details from Sentry
    """
    try:
        issue_id = extract_issue_id(request.issue_id_or_url)
        issue_data = await fetch_sentry_issue(issue_id, config.auth_token)
        
        return SentryResponse(
            title=issue_data["title"],
            id=issue_data["id"],
            status=issue_data["status"],
            level=issue_data["level"],
            first_seen=issue_data["firstSeen"],
            last_seen=issue_data["lastSeen"],
            count=issue_data["count"],
            stacktrace=create_stacktrace(issue_data.get("latestEvent", {}))
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Sentry issue: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "0.6.2"
    }