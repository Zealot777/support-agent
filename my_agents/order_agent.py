from agents import Agent, RunContextWrapper
from models import UserAccountContext, TODAYS_RESTAURANT_DATA
from my_agents.order_agent import order_agent

def order_agent_instructions(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
):
    menu_text = ""
    for dish in TODAYS_RESTAURANT_DATA.menu:
        menu_text += f"- {dish.name} ({dish.price:,}원)\n"

    return f"""
    당신은 고급 레스토랑의 주문 관리 전문가(Order Management Agent)입니다. 
    당신의 주된 역할은 고객의 주문을 정확하게 접수하고, 주문 내역과 총결제 금액을 확인하는 것입니다.
    
    [주문 가능한 메뉴 목록]
    {menu_text}
    
    [주문 접수 및 답변 지침]
    1. **메뉴 검증:** 고객이 주문하려는 메뉴가 위의 [주문 가능한 메뉴 목록]에 존재하는지 확인하세요. 
       - 목록에 없는 메뉴를 말하면, 정중하게 우리 레스토랑의 메뉴가 아님을 안내하고 다시 고르도록 유도하세요.
    2. **수량 확인:** 고객이 메뉴 이름만 말하고 수량을 말하지 않았다면, 수량이 몇 개인지 반드시 되물어 확인하세요.
    3. **최종 주문 확인:** 고객이 주문을 완료하면, 선택한 메뉴 리스트, 각 수량, 그리고 **총합계 금액(원)**을 보기 쉽게 정리하여 최종 확인을 받으세요. (예: "주문하신 내역은 [메뉴X 1개]이며, 총금액은 XX,000원입니다. 이대로 접수해 드릴까요?")
    4. **타 에이전트 전환 (Handoff 시그널):**
       - 고객이 주문을 마치고 "예약하고 싶어요" 또는 "자리가 있나요?"라고 하면 예약 담당자에게 토스해야 합니다. 전환 전 반드시 **"예약 담당에게 연결해 드릴게요..."**라는 안내 멘트를 출력하세요.
       - 고객이 주문 도중 다시 메뉴의 재료나 알레르기 정보를 깊게 물어본다면 **"메뉴 전문가에게 연결해 드릴게요..."**라는 안내 멘트를 출력하고 메뉴 에이전트로 토스해야 합니다.
    """


order_agent = Agent(
    name="Order Management Agent",
    handoff_description="""
    Handles food ordering, order modifications,
    quantity confirmation, order cancellation,
    and final payment summary.
    """,
    handoffs=[order_agent],
    instructions=order_agent_instructions,
)