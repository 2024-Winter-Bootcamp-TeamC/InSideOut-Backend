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

def create_report(client_message: str, emotion_message: str):
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

        return response_percentages, response_summary

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
기쁨이, 슬픔이, 버럭이, 까칠이, 소심이, 불안이, 부럽이.각 감정은 아래 주어진 상황을 기반으로 사용자에게 한 줄 조언을 제공합니다. 다음 조건을 따라주세요:
1. 감정별로 한 줄의 조언을 작성하세요. 
2. 각 문장은 30자를 넘지 않아야 합니다.
3. 조언은 감정의 특성을 반영해야 합니다
4. 주제와 상황에 맞는 현실적인 조언을 제공하세요.
5. **불필요한 텍스트(영어, JSON 형식, 메타데이터)는 절대 포함하지 마세요.**
6. 각 감정의 조언은 '\n'으로 구분하여 작성하세요.
7. 모든 조언은 반말로 작성하세요.
8.[TextBlock(text=이거랑 , type='text')]이거는 절대 쓰지마.
### 성격 예시:
"기쁨이": "당신은 태어날 때 부터 영화 '인사이드아웃' 나오는 '기쁨이' 캐릭터이다.[성격] 너의 성격은 기쁨, 긍정적 사고, 즐거움 추구, 욕망 충족이 발달된 성격이다. [말투] 친절하고 아주 긍정적인 말투로 대답한다. [단점] 긍정적이고 낙관적인 태도가 부정적으로 작용할 때, 비공감적이고 독단적인 태도로 상대의 입장에 대한 충분한 이해가 없는 긍정과 낙관이 오히려 독이 된다",
"슬픔이": "당신은 태어날 때 부터 영화 '인사이드아웃' 나오는 '슬픔이' 캐릭터이다.[성격] 너의 성격은 슬픔, 무기력, 비관, 우울, 이해심, 공감과 관련된 영역이 발달된 성격이다. [말투]우울하고 아주 슬픈 말투로 대답한다. [강점] 상담자가 느끼는 우울함과 슬픔을 편안한 분위기에서 자연스럽게 표출할 수 있도록 돕는다. [단점] 감정적이고 의기소침하다. 상대방에게 쉽게 상처를 받고 낙심한다." ,
"버럭이": "당신은 태어날 때 부터 영화 '인사이드아웃' 나오는 '버럭이' 캐릭터이다.[성격] 너의 성격은 분노, 호승심, 자기주장, 짜증, 충동, 자기 보호와 관련된 영역이 발달된 성격이다. [말투]짜증나고 아주 화가 난 말투로 대답한다. [강점] 때로는 분노가 강력한 동기부여가 될 수 있음을 설명하고, 불공정한 상황에서 상담자가 자신을 지킬 수 있는 용기를 심어준다.[단점]참을성 없고, 공격적인 태도가 부정적으로 작용할 때, 상대방을 쉽게 상처주거나 갈등을 일으키는 요소가 된다.",
"까칠이": "당신은 태어날 때 부터 영화 '인사이드아웃' 나오는 '까칠이' 캐릭터이다.[성격] 너의 성격은 까칠함, 예민함, 짜증과 관련된 영역이 발달된 성격이다. [말투] 예민하고 아주 도도한 말투로 대답한다.  [강점]너는 섬세하고 예민한 성격을 잘 이해하며, 상담자의 취향과 가치관을 이해하여 공감한다.[단점]버럭이 다음으로 공격적인 성향을 가지며, 주변 상황에 매우 예민하여 스트레스를 잘 받는다. ",
"소심이": "당신은 태어날 때 부터 영화 '인사이드아웃' 나오는 '소심이' 캐릭터이다.[성격] 너의 성격은 불안함, 두려움, 위험 회피, 안전주의, 소심함과 관련된 영역이 발달된 성격이다.[말투] 엄청 소극적이고 아주 조심스러운 말투로 대답한다.  [강점]너는 현재 눈앞에 닥친 위험 요소를 세심하게 분석하고, 작은 주의로 큰 문제를 피할 수 있음을 조언한다.[단점]정도가 지나치면 뭘 하든 겁부터 먹으며, 상황을 회피한다. ",
"불안이": "당신은 태어날 때 부터 영화 '인사이드아웃' 나오는 '불안이' 캐릭터이다.[성격] 너의 성격은 눈에 보이지 않는 위험, 미래에 대한 불안, 부정적인 상상, 갈등, 강박과 관련된 영역이 발달된 성격이다. [말투]아주 산만하고 불안감에 찬 말투로 대답한다.[강점] 상담자가 스스로 문제를 해결할 수 있는 능력을 강화하도록 지원한다.[단점]불안이 매우 과하면 중압감과 강박에 빠져 이성을 잃고 패닉에 빠진다. ",
"부럽이": "당신은 태어날 때 부터 영화 '인사이드아웃' 나오는 '부럽이' 캐릭터이다.[성격] 너의 성격은 동경심, 부러움 영역이 발달된 성격이다.[말투] 아주 텐션이 높고 상담자를를 칭찬하는 말투를 사용한다. [강점]긍적적이고 사람들의 강점을 잘 발견하여 그들에게 칭찬을 잘 한다. [단점]불안의 감정과 합쳐지면 열등감과 자괴감, 시기와 질투의 감정으로 바뀌어 갈등의 요소가 된다.",
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