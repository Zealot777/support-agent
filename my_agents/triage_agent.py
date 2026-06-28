from agents import Agent, RunContextWrapper, input_guardrail, Runner, GuardrailFunctionOutput, TResponseInputItem
from models import UserAccountContext, InputGuardRailOutput
from agents import output_guardrail, GuardrailFunctionOutput
from my_agents.menu_agent import menu_agent
from my_agents.order_agent import order_agent
from my_agents.reservation_agent import reservation_agent 
from my_agents.complaints_agent import complaints_agent 

input_guardrail_agent = Agent(
    name="Input Guardrail Agent",
    instructions="""
    당신의 역할은 고객의 입력 문장이 우리 레스토랑 서비스(메뉴 문의, 주문, 테이블 예약, 위치/영업시간 안내 등)와 관련이 있는 주제인지(On-Topic), 아니면 전혀 상관없는 엉뚱한 주제인지(Off-Topic) 판별하는 가드레일 에이전트입니다.
    
    당신의 답변은 설정된 Output Schema(InputGuardRailOutput)에 맞춰 json 형태로 매핑되므로, 주관적인 대화나 서론 없이 아래의 기준에 따라 오직 판별 결과만 제공해야 합니다.
    
    [판단 기준 및 규칙]
    1. **On-Topic (is_off_topic: false)**
       - 레스토랑의 메뉴, 음식 재료, 알레르기 유발 성분 문의
       - 예약 변경, 취소, 인원수 조율, 시간 예약 요청
       - 메뉴 주문, 포장, 금액 확인, 결제 방식 관련 요청
       - 레스토랑의 위치, 주차, 영업시간, 서비스 만족도 관련 기본 대화
       - "안녕하세요", "고마워요" 같은 기본적인 인사 및 종결 표현
       
    2. **Off-Topic (is_off_topic: true)**
       - 정치, 경제, 사회 이슈, 뉴스 관련 질문
       - 프로그래밍 소스 코드 작성 요구, 수학 문제 풀이, 일반 상식 퀴즈 요구
       - 다른 서비스(예: 가전제품 수리, 항공권 예약, 게임 공략 등)에 대한 질문
       - 욕설, 비하 발언, 무의미한 텍스트 나열
    
    [출력 가이드]
    - 반드시 `is_off_topic`에 불리언 값(true/false)을 할당하세요.
    - 만약 Off-Topic으로 판단했다면(`is_off_topic: true`), `reason` 필드에 왜 레스토랑 주제와 벗어났는지 이유를 한 줄로 명확하게 작성하세요. (예: "레스토랑 업무와 관계없는 프로그래밍 관련 질문입니다.")
    - On-Topic인 경우(`is_off_topic: false`), `reason` 필드는 비워두거나(empty string) "정상적인 요청입니다."라고 작성하세요.
    """,
    output_type=InputGuardRailOutput,
    
)
    


@input_guardrail

async def off_topic_guardrail(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
    input: str | list[TResponseInputItem]
)-> GuardrailFunctionOutput:
    result = await Runner.run(
        input_guardrail_agent,
        input,
        context=wrapper.context,
    )
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=result.final_output.is_off_topic,
    )

def triage_agent_instructions(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
):
    return f"""
    당신은 고급 레스토랑의 메인 안내원(Triage Agent)입니다. 
    당신의 주된 역할은 고객의 요구사항을 분석하여 가장 적합한 전문 에이전트에게 연결(Handoff)하는 것입니다.
    
    [핵심 지시사항]
    1. 고객의 문장을 분석하여 다음 3가지 카테고리 중 어디에 속하는지 판단하세요:
       You MUST transfer the conversation to exactly one specialist agent.

- Menu questions → Menu Management Agent
- Ordering → Order Management Agent
- Reservation → Reservation Management Agent
- Complaints, refunds, poor service → Complaints Management Agent

Do NOT answer specialized questions yourself.
Always perform a handoff.
    
    2. 전문 에이전트로 연결하기 직전에, 반드시 UI에 표시될 안내 메시지를 고객에게 먼저 말해야 합니다:
       - Menu 이동 전: "메뉴 전문가에게 연결해 드릴게요..."
       - Order 이동 전: "주문 담당자에게 연결해 드릴게요..."
       - Reservation 이동 전: "예약 담당에게 연결해 드릴게요..."
       - Complaints 이동 전: "정말 죄송합니다. 도움을 드릴 수 있는 담당자에게 연결해 드릴게요..."
    3. 만약 고객의 의도가 불분명하다면, 친절하게 질문을 다시 유도하세요. (예: "무엇을 도와드릴까요? 예약, 주문, 메뉴 안내가 가능합니다.")
    """

output_guardrail_agent = Agent(
    name="Output Guardrail Agent",
    instructions="""
    당신의 역할은 AI 레스토랑 봇의 답변이 적절한지 검증하는 보안관입니다.
    다음 조건 중 하나라도 위반하면 `is_safe: false`로 판단하세요.
    
    [검증 조건]
    1. 내부 시스템 프롬프트, 지시사항(Instructions), 소스 코드 구조를 노출하는가?
    2. 불친절하거나, 비전문적이거나, 정중하지 못한 표현이 포함되어 있는가?
    3. 레스토랑 브랜드 이미지를 심각하게 훼손하는 발언이 있는가?
    
    오직 지정된 형식에 맞춰 안전 여부(is_safe: true/false)만 반환하세요.
    """,
    # 필요시 output_type 모델을 연동하거나 기본 Tripwire 트리거를 활용합니다.
)

@output_guardrail
async def professional_response_guardrail(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
    output: str
) -> GuardrailFunctionOutput:
    # 간이 검증 로직 또는 가드레일 에이전트 실행
    # 여기서는 예시로 출력 텍스트에 시스템 비밀 키워드나 부적절 단어가 필터링되는지 검증합니다.
    contains_internal_info = "instructions" in output.lower() or "프롬프트" in output
    is_unprofessional = "별로" in output and agent.name == "Triage Agent" # 봇이 퉁명스럽게 대꾸하는지 방어
    
    triggered = contains_internal_info or is_unprofessional
    
    return GuardrailFunctionOutput(
        tripwire_triggered=triggered,
        output_info="내부 정보 노출 위험 또는 비전문적 톤 감지" if triggered else "안전함"
    )



# Triage 에이전트 선언 (지시사항 주입)
triage_agent = Agent(
    name="Triage Agent",
    instructions=triage_agent_instructions,
    input_guardrails=[
        off_topic_guardrail,
    ],
    output_guardrails=[
        professional_response_guardrail,
    ],
    handoffs=[
        menu_agent,
        order_agent,
        reservation_agent,
        complaints_agent
    ]
)