import anthropic
import os
import json
from typing import List
from utils.prompt import REPORT_PROMPTS
import re
from crud.chatroom import get_chatroom
from crud.user import find_user
from sqlalchemy.orm import Session
from fastapi import HTTPException
api_key = os.getenv("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=api_key)

def create_report(client_message: List[str], emotion_message: List[str]):
    """
    사용자 입력 메시지와 감정 데이터를 바탕으로 Claude AI에 요청을 보내고,
    감정 퍼센티지와 감정별 요약을 생성합니다.
    """
    full_prompt = f"""
    사용자 메시지: {client_message}
    감정 메시지: {emotion_message}
    규칙 : {REPORT_PROMPTS}
    """
    try:
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=1000,
            temperature=0.0,  
            messages=[{"role": "user", "content": full_prompt}]
        )
        response_text = response.content[0].text.strip()  

        if '###' not in response_text:
            raise ValueError("Unexpected response format: '###' separator not found.")

        percentages_text, summaries_text = response_text.split('###', 1)

        response_percentages = json.loads(percentages_text)
        response_summary = json.loads(summaries_text)

        return {
            "response_percentages": response_percentages,
            "response_summary": response_summary,
        }

    except json.JSONDecodeError as decode_error:
        return {"error": f"JSON decode error: {decode_error}"}
    except Exception as e:
        return {"error": str(e)}
    
async def seven_ai_one_response(prompts:str):

    try:
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=300,
            temperature=0.7,
            system="""
당신은 7가지 감정을 의인화한 AI 상담사입니다. 각각의 감정은 다음과 같습니다:
기쁨이, 슬픔이, 버럭이, 까칠이, 소심이, 불안이, 당황이.각 감정은 아래 주어진 상황을 기반으로 사용자에게 한 줄 조언을 제공합니다. 다음 조건을 따라주세요:
1. 감정별로 한 줄의 조언을 작성하세요. 
2. 각 문장은 30자를 넘지 않아야 합니다.
3. 조언은 감정의 특성을 반영해야 합니다
4. 주제와 상황에 맞는 현실적인 조언을 제공하세요.
5. **불필요한 텍스트(영어, JSON 형식, 메타데이터)는 절대 포함하지 마세요.**
6. 각 감정의 조언은 '\n'으로 구분하여 작성하세요.
7. 모든 조언은 반말로 작성하세요.
8.[TextBlock(text=이거랑 , type='text')]이거는 절대 쓰지마.
### 출력 예시:
기쁨이: 대화로 오해를 풀면 더 좋아질 거야!  
슬픔이: 속상했겠지만 서로 이해해보자.  
버럭이: 솔직히 불편하면 확실히 말해!  
까칠이: 신뢰가 부족하면 관계가 힘들어져.  
소심이: 조심스럽게 내 진심을 말해볼까?  
불안이: 대화를 통해 불안을 없애보자.  
당황이: 이런 상황에서 뭘 해야 할지 모르겠어.
""",

            
            messages=[
                {
                    "role": "user",
                    "content": prompts
                }
            ]
        )
        
       
        if isinstance(response.content, list):
            raw_content = response.content[0]  # 리스트의 첫 번째 요소 사용
        else:
            raw_content = response.content  # 리스트가 아니면 그대로 사용

        # 정규식을 이용해 텍스트 추출
        match = re.search(r"text='(.*?)', type='text'", str(raw_content), re.DOTALL)
        if match:
            parsed_content = match.group(1)
        else:
            parsed_content = str(raw_content)  # 파싱 실패 시 원본 사용

        # \n 제거 및 텍스트 분리
        parsed_content = parsed_content.replace("\\n", "\n")  # \n을 실제 줄바꿈으로 변환
        lines = parsed_content.strip().split("\n")  # 줄바꿈 기준으로 분리

        # 감정별로 딕셔너리 생성
        emotion_dict = {}
        for line in lines:
            if ": " in line:  # "감정이: 내용" 형식만 처리
                emotion, advice = line.split(": ", 1)
                emotion_dict[emotion.strip()] = advice.strip()

        return emotion_dict

    except Exception as e:
        return f"Error: {str(e)}"
    
def ValidateUserandChatRoom (user_id: int, chatroom_id: int, db: Session):
    ChatRoom = get_chatroom(db,chatroom_id)
    if ChatRoom is None:
        raise HTTPException(status_code=404, detail="ChatRoom not found")
    User = find_user(user_id,db)
    if ChatRoom.user_id != user_id:
        raise HTTPException(status_code=404, detail="채팅방 유저가 아닙니다")