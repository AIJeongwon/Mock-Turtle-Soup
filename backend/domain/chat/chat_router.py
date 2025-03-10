from fastapi import APIRouter, HTTPException
from starlette import status

from domain.chat import chat_crud, chat_schema

router = APIRouter(
    prefix="/api/chat",
)

@router.get("/start")
def start_gemini():
    return chat_crud.start_gemini()

@router.post("/query")
def query_gemini(_user_query: chat_schema.UserQuery):
    return chat_crud.query_gemini(user_query=_user_query)
