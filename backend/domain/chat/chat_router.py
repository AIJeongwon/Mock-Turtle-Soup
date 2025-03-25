from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from database import get_db
from domain.chat import chat_crud, chat_schema
from domain.question import question_crud

router = APIRouter(
    prefix="/api/chat",
)

@router.post("/{question_id}/start")
def start_gemini(question_id: int, _API_Key: chat_schema.API_Key, db: Session = Depends(get_db)):
    question = question_crud.get_question(db, question_id)
    chat_crud.start_gemini(question, _API_Key)
    start_str = "**어서 오세요, 바다거북스프 놀이에 참여해주셔서 감사합니다!** 🐢🍲\n\n저는 오늘 여러분을 흥미진진한 나폴리탄 괴담 속으로 안내할 주최자입니다. 준비되셨나요?\
                \n\n**시작**하겠다는 채팅을 치시면 수수께끼를 알려드리고 질문을 시작하실 수 있습니다. \n\n**주의:** 20번의 질문 안에 정답을 맞춰야 승리하며,\
                질문에 대한 답은 **예** 또는 **아니오**로만 대답 가능합니다! \n\n**자, 숨을 크게 들이쉬고, 괴담의 세계로 함께 빠져들어 보세요...**"
    return start_str

@router.post("/{question_id}/query")
def query_gemini(_user_query: chat_schema.UserQuery):
    return chat_crud.query_gemini(user_query=_user_query)
