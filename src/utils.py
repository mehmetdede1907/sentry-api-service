from urllib.parse import urlparse
from typing import Dict, Any

class SentryError(Exception):
    pass

def extract_issue_id(issue_id_or_url: str) -> str:
    """
    Extract the Sentry issue ID from either a full URL or a standalone ID.
    
    Args:
        issue_id_or_url: A Sentry issue ID or full Sentry URL
        
    Returns:
        The extracted issue ID
        
    Raises:
        ValueError: If the input is invalid
    """
    if not issue_id_or_url:
        raise ValueError("Missing issue ID or URL")

    if issue_id_or_url.startswith(("http://", "https://")):
        parsed_url = urlparse(issue_id_or_url)
        if not parsed_url.hostname or not parsed_url.hostname.endswith(".sentry.io"):
            raise ValueError("Invalid Sentry URL. Must be a URL ending with .sentry.io")

        path_parts = parsed_url.path.strip("/").split("/")
        if len(path_parts) < 2 or path_parts[0] != "issues":
            raise ValueError(
                "Invalid Sentry issue URL. Path must contain '/issues/{issue_id}'"
            )

        issue_id = path_parts[-1]
    else:
        issue_id = issue_id_or_url

    if not issue_id.isdigit():
        raise ValueError("Invalid Sentry issue ID. Must be a numeric value.")

    return issue_id

def create_stacktrace(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a formatted stacktrace from event data.
    
    Args:
        event_data: The Sentry event data containing exception information
        
    Returns:
        A dictionary containing formatted stacktrace information
    """
    stacktrace_info = {
        "exceptions": [],
        "frames": []
    }

    for entry in event_data.get("entries", []):
        if entry["type"] != "exception":
            continue

        for exception in entry["data"]["values"]:
            exception_info = {
                "type": exception.get("type", "Unknown"),
                "value": exception.get("value", ""),
                "module": exception.get("module", "Unknown")
            }
            stacktrace_info["exceptions"].append(exception_info)

            if "stacktrace" in exception:
                for frame in exception["stacktrace"].get("frames", []):
                    frame_info = {
                        "filename": frame.get("filename", "Unknown"),
                        "function": frame.get("function", "Unknown"),
                        "lineno": frame.get("lineNo", "?"),
                        "context": frame.get("context", []),
                        "variables": frame.get("vars", {})
                    }
                    stacktrace_info["frames"].append(frame_info)

    return stacktrace_info