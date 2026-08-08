# API for TiMESS, a memory-augmented LLM chatbot. 
## This is the backend service that handles requests from the frontend and interacts with the LLM and DynamoDB.
import uuid

from fastapi import FastAPI
from pydantic import BaseModel

from src.chains import ask
from src.dynamo import log_turn

app = FastAPI(title="TiMESS API")


class ChatRequest(BaseModel):
    user_id: str
    query: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    answer: str
    session_id: str


@app.get("/health")
def health():
    """Used by Docker/deployment to confirm the container actually
    started, not just that `docker compose up` exited with code 0."""
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())
    answer = ask(question=req.query, user_id=req.user_id)
    log_turn(session_id=session_id, user_id=req.user_id, question=req.query, answer=answer)
    return ChatResponse(answer=answer, session_id=session_id)