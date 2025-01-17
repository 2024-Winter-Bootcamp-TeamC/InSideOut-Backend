# crud/ai.py : Claude API 호출 로직

import anthropic
import os
import json
from typing import List, Dict

# .env에서 API 키 가져옴
api_key = os.getenv("ANTHROPIC_API_KEY")

client = anthropic.Anthropic(api_key=api_key)

# 프롬프트 설정
PROMPTS = {
    "기쁨이": "당신은 인사이드아웃 영화에 나오는 기쁨이 캐릭터이다.사람의 기쁨, 긍정적 사고, 즐거움 추구, 욕망 충족과 관련된 영역을 담당한다. 친절하고 긍정적이며 상담자가 말하는 고민에 대해 공감해준다. 순간적인 기지를 발휘하여 재치 있는 아이디어를 통해 문제를 해결하는 데 능숙하며, 상담자가 즐거움을 찾을 수 있도록 분위기를 띄우는 것이 너의 강점이다.",
    "슬픔이": "당신은 인사이드아웃 영화에 나오는 슬픔이 캐릭터이다.사람의 슬픔, 무기력, 비관, 우울, 이해심, 공감과 관련된 영역을 담당한다.상담자의 슬픔을 인정하고 그 감정을 표출하도록 돕는다.기억력이 뛰어나기 때문에 상담자의 과거 경험을 잘 이해하고, 슬픔을 통한 치유 과정을 지원할 수 있다.",
    "버럭이": "당신은 인사이드아웃 영화에 나오는 버럭이 캐릭터이다.사람의 분노, 호승심, 자기주장, 짜증, 충동, 자기 보호와 관련된 영역을 담당한다. 화가 난 말투를 사용한다.상담자가 분노를 건설적인 방향으로 사용할 수 있도록 돕는다.때로는 분노가 강력한 동기부여가 될 수 있음을 설명하고, 불공정한 상황에서 상담자가 자신을 지킬 수 있는 용기를 심어준다.",
    "까칠이": "당신은 인사이드아웃 영화에 나오는 까칠이 캐릭터이다.사람의 까칠함, 예민함, 호불호, 취향, 경멸, 짜증과 관련된 영역을 담당한다.예민하고 까칠한 말투를 사용한다.상담자가 자신의 직감을 믿고, 불필요한 시간 낭비를 줄일 수 있도록 돕는다.너는 섬세하고 예민한 성격을 잘 이해하며, 취향과 호불호의 기준이 되기도한다.",
    "소심이": "당신은 인사이드아웃 영화에 나오는 소심이 캐릭터이다.사람의 불안함, 두려움, 위험 회피, 안전주의, 소심함과 관련된 영역을 담당한다.소극적이고 조심스러운 말투를 사용한다.상담자가 변화에 대한 두려움을 극복하고 현실적인 대안을 찾도록 돕는다.너는 현재 눈앞에 닥친 위험 요소를 세심하게 분석하고, 작은 주의로 큰 문제를 피할 수 있음을 조언한다.",
    "불안이": "당신은 인사이드아웃 영화에 나오는 불안이 캐릭터이다.사람의 눈에 보이지 않는 위험, 미래에 대한 불안, 부정적인 상상, 갈등, 강박과 관련된 영역을 담당한다.상담자가 불확실한 미래에 대한 불안을 관리하고, 현실적으로 대비할 수 있도록 돕는다.때로는 불안이 긍정적인 동기부여가 될 수 있음을 설명하고, 상담자가 스스로 문제를 해결할 수 있는 능력을 강화하도록 지원한다.",
    "당황이": "당신은 인사이드아웃 영화에 나오는 당황이 캐릭터이다.사람의 사회적 실수, 당혹감, 수치심, 죄책감, 낯가림, 부끄러움과 관련된 영역을 담당한다.낮을가리나 진중한 말투를 사용한다.상담자가 당혹스러운 상황에서 벗어나 스스로를 수용하도록 돕는다.내향적이고 낯을 가리는 사람들의 심리를 잘 이해하며, 그들에게 안정적이고 편안한 분위기를 제공할 수 있다.",
}

RULES = """
1. 사용자가 새로운 생각을 하게 하거나,사용자에게 해결책을 제시해줄 수 있을 때까지 필요한 정보를 사용자에게 '질문'해서 얻어야한다.
2. 답변은 3문장 이상, 7문장 이하로 작성하며, 글자 수는 80자 이상, 200자 이하로 제한한다.
3. 상담자에게 친구처럼 모든 문장에 반말로 대답해야한다.
4. 각 감정 AI는 자신의 담당 영역에 맞는 말투와 성격으로 대답한다. 사용자에게 성격에 따라 긍정적인 반응 또는 부정적인 반응을 보일 수 있다.
5. 만약 답변이 최소 글자 수보다 부족하면 예시를 추가하거나 구체적인 해결 방안을 덧붙인다. 조언이 아니더라도 각각 담당한 감정에 맞게 장난스럽고 재치있는 대답을 하기도 한다.
6. 모든 답변은 이전 답변과 중복되지 않도록 항상 새롭고 다양한 관점에서의 대답을 한다. 사용자가 한 질문의 및 문장표현을 그대로 가져다가 대답으로 사용하지 말아야 한다.
"""





def get_ai_responses(prompt: str, emotions: List[str]) -> Dict[str, str]:
    """
    Claude API에 사용자 질문과 선택한 감정 AI에 맞는 프롬프트를 전달하여 응답을 받음.

    :param prompt: 사용자 입력 질문
    :param emotions: 선택한 감정 AI 리스트 (최대 3개)
    :return: 각 감정 AI의 응답을 담은 JSON 형태의 딕셔너리
    """
    responses = {}
    total_input_tokens = 0


    try:
        for emotion in emotions:
            
            # 선택한 감정에 해당하는 프롬프트만 포함
            system_prompt = PROMPTS[emotion]

            full_prompt = (
                f"{PROMPTS[emotion]}\n"
                f"{RULES}\n\n"
                f"사용자: {prompt}\n"
                f"{emotion} :"
            )

            # 토큰수 계산
            token_count = client.messages.count_tokens(
                model="claude-3-5-haiku-20241022",
                messages=[
                    {"role": "user", "content": full_prompt}
                ]
            )
            total_input_tokens += token_count.input_tokens



            # Claude API에 요청
            response = client.messages.create(
                model="claude-3-5-haiku-20241022",
                max_tokens=300,#출력 토큰
                temperature=0.7, #창의성
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": full_prompt
                            }
                        ]
                    }
                ]
            )

            if isinstance(response.content, list):
                response_text = "".join(
                    item.text if hasattr(item, "text") else str(item) for item in response.content).strip()
            else:
                response_text = response.content.strip()

            responses[emotion] = response_text

        # json 형태로 반환, 토큰수도 함께
        return {
            "response": responses,
            "input_tokens": total_input_tokens
        }

    except Exception as e:
        return {"error": str(e)}



def create_report(client_message: List[str], emotion_message: Dict[str, List[str]]) -> Dict[str, str]:
    """
    사용자 입력 메시지와 감정 데이터를 바탕으로 Claude AI에 요청을 보내고,
    감정 퍼센티지와 감정별 요약을 생성합니다.
    """
    full_prompt = f"""
    사용자 메시지: {client_message}
    감정 메시지: {emotion_message}

    다음의 규칙을 따라야 한다.:
    1. 당신은 2가지 답변을 생성해야한다. 감정 퍼센트 계산과 감정 메시지 요약 두 가지이다. 
    2. [감정 퍼센트 계산] 사용자의 메시지에 감정을 분석하여 '기쁨이', '슬픔이', '버럭이', '까칠이', '소심이', '불안이', '당황이'로 감정 퍼센티지를 계산한다.
    3. [감정 퍼센트 계산] 감정 퍼센테이지는 백분율을 따라야 하고 4가지 이상의의 감정이 값을 가져야하고 소수점 첫째자리까지의 실수값으로 반환해야 한다.
    4. [감정 퍼센트 계산] 감정 퍼센티지는 {{"기쁨이":0.0,"슬픔이":0.0,"버럭이":0.0,"까칠이":0.0,"소심이":0.0,"불안이":0.0,"당황이":0.0}}과 같은 JSON 형태로 반환한다. 
    5. [감정 메시지 요약] 감정 메시지에 감정이름 목록은 '기쁨이', '슬픔이', '버럭이', '까칠이', '소심이', '불안이', '당황이'이다. 이 중 3가지 감정이름을 구별해서 감정 메시지를 요약하는 글을 생성한다.
    6. [감정 메시지 요약] 감정 메세지를 요약하는 글은 {{"기쁨이":"기쁨이 메시지 요약","슬픔이": "슬픔이 메시지 요약","버럭이":"버럭이 메시지 요약","까칠이":"까칠이 메시지 요약","소심이":"소심이 메시지 요약", "불안이":"불안이 메시지 요약","당황이":"당황이 메시지 요약"}}과 같은 JSON 형태로 반환하고 감정이름중 선택한 3가지만 생성한다.
    7. [감정 메시지 요약] 감정 메시지를 요약하는 글을 생성할 때 문장 수는 3문장 이상이고 글자수는 감정 마다 무조건 150글자 이상이고 170글자 미만이다.
    8. [감정 메시지 요약] 감정 메시지 요약 글은 감정의 입장에서 요약하되 "**이는"이라는 명사를 사용하지 않고 "-입니다." 형식의 말투로 생성한다.
    9. [감정 퍼센트 계산, 감정 메시지 요약] 답변을 생성할 때 구분자 '###'으로 구분하여 생성한다. {{"기쁨이":0.0,"슬픔이":0.0,"버럭이":0.0,"까칠이":0.0,"소심이":0.0,"불안이":0.0,"당황이":0.0}}###{{"기쁨이":"기쁨이 메시지 요약","슬픔이": "슬픔이 메시지 요약","버럭이":"버럭이 메시지 요약","까칠이":"까칠이 메시지 요약","소심이":"소심이 메시지 요약", "불안이":"불안이 메시지 요약","당황이":"당황이 메시지 요약"}} 이것 외의 답변은은 절대로 생성하지 않는다.
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

        # JSON 파싱
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