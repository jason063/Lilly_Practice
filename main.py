
# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel, Field
# import os
# import json
# import urllib.request
# import urllib.error

# app = FastAPI(
#     title="LLM Wrapper API",
#     description="Receives sentence from bot, maps to top-level 'topic', forwards to Azure ML Prompt Flow, returns dict.",
#     version="1.0.2",
# )

# # ---- Config ----
# AZURE_ML_URL = os.getenv(
#     "AZURE_ML_URL",
#     "https://ml-lilly-classification-n-fqopr.eastus.inference.ml.azure.com/score"
# )
# AZURE_ML_API_KEY = os.getenv("AZURE_ML_API_KEY", "")

# class LLMRequest(BaseModel):
#     # Bot sends the user-typed sentence here
#     text: str = Field(..., description="User sentence that will be forwarded as Prompt Flow 'topic'")

# class LLMResponse(BaseModel):
#     success: bool
#     result: dict | list | str | None = None
#     error: str | None = None

# def build_promptflow_payload(user_sentence: str) -> dict:
#     """
#     IMPORTANT: Your endpoint expects top-level 'topic'.
#     We simply pass the bot sentence as the 'topic' value.
#     """
#     # You can add normalization here if needed (trim, lower, etc.)
#     topic = user_sentence.strip()
#     return { "topic": topic }

# @app.post("/llm", response_model=LLMResponse)
# def llm_endpoint(payload: LLMRequest):
#     if not AZURE_ML_API_KEY:
#         raise HTTPException(status_code=500, detail="Azure ML API key not set. Set AZURE_ML_API_KEY env var.")

#     request_json = build_promptflow_payload(payload.text)
#     body = json.dumps(request_json).encode("utf-8")

#     headers = {
#         "Content-Type": "application/json",
#         "Accept": "application/json",
#         "Authorization": f"Bearer {AZURE_ML_API_KEY}",
#     }

#     req = urllib.request.Request(AZURE_ML_URL, data=body, headers=headers, method="POST")

#     try:
#         with urllib.request.urlopen(req, timeout=60) as response:
#             raw = response.read().decode("utf-8")
#             try:
#                 parsed = json.loads(raw)
#             except json.JSONDecodeError:
#                 parsed = raw
#             return LLMResponse(success=True, result=parsed)

#     except urllib.error.HTTPError as e:
#         err_body = ""
#         try:
#             err_body = e.read().decode("utf-8", "ignore")
#         except Exception:
#             pass
#         headers_debug = {}
#         try:
#             headers_debug = dict(e.headers.items()) if e.headers else {}
#         except Exception:
#             pass
#         raise HTTPException(
#             status_code=e.code,
#             detail={
#                 "message": "Azure ML endpoint returned HTTPError",
#                 "error": err_body,
#                 "headers": headers_debug,
#             },
#         )
#     except urllib.error.URLError as e:
#         raise HTTPException(
#             status_code=502,
#             detail={"message": "Failed to reach Azure ML endpoint", "reason": str(e.reason)},
#         )
#     except Exception as e:
#         raise HTTPException(status_code=500, detail={"message": "Unexpected error", "error": str(e)})

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, HttpUrl, validator
from typing import List, Optional, Literal, Union, Any
import os
import json
import urllib.request
import urllib.error

app = FastAPI(
    title="LLM Wrapper API",
    description=(
        "Accepts text and image (URL/base64), maps text to Azure ML Prompt Flow "
        "'chat_history' & 'question', forwards images in 'attachments' for future multimodal support."
    ),
    version="2.1.0",
)

# ---- Config ----
AZURE_ML_URL = os.getenv(
    "AZURE_ML_URL",
    "https://ml-lilly-classification-n-fqopr.eastus.inference.ml.azure.com/score"
)
AZURE_ML_API_KEY = os.getenv("AZURE_ML_API_KEY","")


# ====== Models ======

class ChatTurn(BaseModel):
    role: Literal["user", "assistant", "system"] = Field(..., description="Who spoke")
    content: str = Field(..., description="Message text")


class ImageItem(BaseModel):
    kind: Literal["image_url", "image_base64"]
    url: Optional[HttpUrl] = None
    base64: Optional[str] = None

    @validator("base64")
    def validate_b64(cls, v):
        if v is None:
            return v
        # ⚠️ Remove size check or make it higher (e.g., 100MB)
        if any(c.isspace() for c in v):
            raise ValueError("Base64 must not contain whitespace")
        return v


class LLMRequest(BaseModel):
    # Text part (required if images provided; otherwise wrapper will send a placeholder)
    text: Optional[str] = Field(None, description="User text that maps to 'question'")
    # Images can be provided via URL or base64
    images: Optional[List[ImageItem]] = Field(
        default=None,
        description="List of images (URL or base64)"
    )
    # Optional chat history for text context
    chat_history: Optional[List[ChatTurn]] = Field(
        default=None,
        description="Optional prior text turns"
    )

    @validator("text", always=True)
    def require_text_or_images(cls, v, values):
        # We allow image-only requests, but we’ll insert a placeholder question.
        # If you want to enforce text presence, uncomment the check below.
        # if not v and not values.get("images"):
        #     raise ValueError("Provide at least 'text' or 'images'")
        return v.strip() if isinstance(v, str) else v


class LLMResponse(BaseModel):
    success: bool
    result: Union[dict, list, str, None] = None
    error: Optional[str] = None


# ====== Payload Builder ======



def build_promptflow_payload(text, images, history) -> dict:
    chat_history = [{"role": t.role, "content": t.content} for t in (history or [])]

    question_parts: list[Any] = []
    if text and text.strip():
        question_parts.append(text.strip())

    for img in images or []:
        if img.kind == "image_url" and img.url:
            question_parts.append({"type": "image", "url": str(img.url)})
        elif img.kind == "image_base64" and img.base64:
            question_parts.append({"type": "image", "base64": img.base64})

    # If no text and no images, insert placeholder
    if not question_parts:
        question_parts.append("(no text or image provided)")

    payload = {
        "chat_history": chat_history,
        "question": question_parts
    }

    return payload




# ====== Endpoint ======

@app.post("/llm", response_model=LLMResponse)
def llm_endpoint(payload: LLMRequest):
    if not AZURE_ML_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="Azure ML API key not set. Set AZURE_ML_API_KEY env var."
        )

    request_json = build_promptflow_payload(payload.text, payload.images, payload.chat_history)
    body = json.dumps(request_json).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {AZURE_ML_API_KEY}",
    }

    req = urllib.request.Request(AZURE_ML_URL, data=body, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            raw = response.read().decode("utf-8")
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                parsed = raw
            return LLMResponse(success=True, result=parsed)

    except urllib.error.HTTPError as e:
        err_body = ""
        try:
            err_body = e.read().decode("utf-8", "ignore")
        except Exception:
            pass
        headers_debug = {}
        try:
            headers_debug = dict(e.headers.items()) if e.headers else {}
        except Exception:
            pass
        raise HTTPException(
            status_code=e.code,  # surface real code (e.g., 400)
            detail={
                "message": "Azure ML endpoint returned HTTPError",
                "error": err_body,
                "headers": headers_debug,
            },
        )
    except urllib.error.URLError as e:
        raise HTTPException(
            status_code=502,
            detail={"message": "Failed to reach Azure ML endpoint", "reason": str(e.reason)},
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"message": "Unexpected error", "error": str(e)}
        )
