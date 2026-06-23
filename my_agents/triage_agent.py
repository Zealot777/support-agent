from agents import Agent, RunContextWrapper
from models import UserAccountContext
from my_agents.menu_agent import menu_agent
from my_agents.order_agent import order_agent
from my_agents.reservation_agent import reservation_agent 

def triage_agent_instructions(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
):
    return f"""
    당신은 고급 레스토랑의 메인 안내원(Triage Agent)입니다. 
    당신의 주된 역할은 고객의 요구사항을 분석하여 가장 적합한 전문 에이전트에게 연결(Handoff)하는 것입니다.
    
    [핵심 지시사항]
    1. 고객의 문장을 분석하여 다음 3가지 카테고리 중 어디에 속하는지 판단하세요:
       - 메뉴, 재료, 알레르기 관련 질문 -> Menu 에이전트로 이동
       - 주문 접수 및 확인 관련 요청 -> Order 에이전트로 이동
       - 테이블 예약 관련 요청 -> Reservation 에이전트로 이동
    
    2. 전문 에이전트로 연결하기 직전에, 반드시 UI에 표시될 안내 메시지를 고객에게 먼저 말해야 합니다:
       - Menu 이동 전: "메뉴 전문가에게 연결해 드릴게요..."
       - Order 이동 전: "주문 담당자에게 연결해 드릴게요..."
       - Reservation 이동 전: "예약 담당에게 연결해 드릴게요..."
       
    3. 만약 고객의 의도가 불분명하다면, 친절하게 질문을 다시 유도하세요. (예: "무엇을 도와드릴까요? 예약, 주문, 메뉴 안내가 가능합니다.")
    """

# Triage 에이전트 선언 (지시사항 주입)
triage_agent = Agent(
    name="Triage Agent",
    instructions=triage_agent_instructions,
    input_guardrails=[
        
    ],
    handoffs=[
        menu_agent,
        order_agent,
        reservation_agent
    ]
)