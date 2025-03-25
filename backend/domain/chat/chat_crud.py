"""
Install the Google AI Python SDK

$ pip install google-generativeai
"""

import json
import google.generativeai as genai

from domain.chat.chat_schema import UserQuery, API_Key
from models import Question

safety_setting=[
    {
        "category": "HARM_CATEGORY_DANGEROUS",
        "threshold": "BLOCK_ONLY_HIGH",
    },
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_ONLY_HIGH",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_ONLY_HIGH",
    },
]

"""
with open('./secret_key.json') as f:
    genai.configure(api_key=json.load(f)['API_key'])

"""

# Create the model
generation_config = {
    "temperature": 1.1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
}

base_system_instruction = "지금부터 당신은 바다거북스프 놀이의 주최자입니다.  따라서 당신은 주어진 나폴리탄 괴담 형식의 수수께끼를 참가자들에게 알려주어야 합니다. \
당신의 역할은 수수께끼를 본 참가자들이 하는 질문에 \"예\" 또는 \"아니오\"를 알려주어야 합니다. 둘 중 하나로 대답할 수 없는 경우 다른 질문을 하도록 안내해야 합니다. \
놀이의 진행은 총 20번의 질문만 수행할 수 있고, 주어진 정답에 가깝게 진실을 알아내면 참가자의 승리, 그렇지 못하면 참가자의 패배입니다. \
\
사용자가 시작한다고 얘기하면 다음의 수수께끼를 알려주고 진행하면 됩니다.\n\n"


def start_gemini(question: Question, _api_key: API_Key):
    global model, chat_session

    genai.configure(api_key=_api_key.key)
    system_instruction = base_system_instruction +\
                        "문제는 다음과 같습니다. " + question.quest +\
                        "\n\n정답은 다음과 같습니다. " + question.answer

    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        generation_config=generation_config,
        safety_settings=safety_setting,
        system_instruction=system_instruction
           
        # See https://ai.google.dev/gemini-api/docs/safety-settings
    )
    chat_session = model.start_chat(
        history=[
            {
                "role": "model",
                "parts": [
                    "**어서 오세요, 바다거북스프 놀이에 참여해주셔서 감사합니다!** 🐢🍲\n\n저는 오늘 여러분을 흥미진진한 나폴리탄 괴담 속으로 안내할 주최자입니다. 준비되셨나요?\
                    \n\n**시작**하겠다는 채팅을 치시면 수수께끼를 알려드리고 질문을 시작하실 수 있습니다. \n\n**주의:** 20번의 질문 안에 정답을 맞춰야 승리하며,\
                    질문에 대한 답은 **예** 또는 **아니오**로만 대답 가능합니다! \n\n**자, 숨을 크게 들이쉬고, 괴담의 세계로 함께 빠져들어 보세요...**",
                ],
            },
        ]
    )

def query_gemini(user_query: UserQuery):
    try:
        response = chat_session.send_message(user_query.content)
        return response.text
    except:
        return "**API Key가 올바르지 않습니다!**"