from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import sentry_sdk
from datetime import datetime
import uvicorn

app = FastAPI(
    title="Sentry API Service",
    description="API service for retrieving and analyzing Sentry issues",
    version="0.6.2"
)

# Add CORS middleware
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

# Global variable to store the Sentry configuration
sentry_config: Optional[SentryConfig] = None

@app.post("/config")
async def set_config(config: SentryConfig):
    """Set Sentry configuration including authentication token"""
    global sentry_config
    sentry_config = config
    # Initialize Sentry SDK
    sentry_sdk.init(dsn=config.auth_token)
    return {"message": "Configuration updated successfully"}

@app.get("/config")
async def get_config():
    """Get current Sentry configuration (without sensitive data)"""
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

@app.post("/sentry/issue", response_model=SentryResponse)
async def get_sentry_issue(
    request: SentryIssueRequest,
    config: SentryConfig = Depends(get_current_config)
):
    """
    Retrieve issue details from Sentry
    """
    try:
        # Extract issue ID from URL if needed
        issue_id = _extract_issue_id(request.issue_id_or_url)
        
        # Get issue details from Sentry
        issue = await sentry_sdk.get_issue(issue_id)
        
        return SentryResponse(
            title=issue.title,
            id=issue.id,
            status=issue.status,
            level=issue.level,
            first_seen=issue.first_seen,
            last_seen=issue.last_seen,
            count=issue.count,
            stacktrace=issue.get_latest_event().get_stacktrace()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def _extract_issue_id(issue_id_or_url: str) -> str:
    """Extract issue ID from a Sentry URL or return the ID directly"""
    if issue_id_or_url.startswith(("http://", "https://")):
        return issue_id_or_url.split("/")[-1]
    return issue_id_or_url

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "0.6.2"
    }

def start_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the FastAPI server"""
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start_server()