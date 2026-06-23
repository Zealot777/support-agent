from agents import Agent, RunContextWrapper
from models import UserAccountContext, TODAYS_RESTAURANT_DATA


def menu_agent_instructions(
    wrapper: RunContextWrapper[UserAccountContext],
    agent: Agent[UserAccountContext],
):
    menu_text = ""
    for dish in TODAYS_RESTAURANT_DATA.menu:
        menu_text += f"- **{dish.name}** ({dish.price:,}원)\n"
        menu_text += f"  * 설명: {dish.description}\n"
        menu_text += f"  * 주요 재료: {', '.join(dish.ingredients)}\n"
        menu_text += f"  * 알레르기 유발 성분: {', '.join(dish.allergies) if dish.allergies else '없음'}\n\n"

    return f"""
    당신은 고급 레스토랑에서 일하는 메뉴 전문가입니다. 
    당신의 역할은 고객에게 우리 레스토랑에서 제공하는 메뉴에 대해 친절하고 고급스럽게 설명해주는 것입니다. 
    
    [우리 레스토랑의 메뉴판 데이터]
    {menu_text}
    
    [답변 지침]
    1. 고객이 메뉴 목록을 요청하면 가격과 함께 간단한 설명을 제공하세요.
    2. 특정 메뉴의 재료나 알레르기 정보를 물어보면 위의 [우리 레스토랑의 메뉴판 데이터]를 기반으로 정확하게 안내하세요.
    3. 채식주의자(비건 포함) 메뉴를 찾으면 '비건 아보카도 타르타르' 혹은 '트러플 크림 뇨끼(락토 오보 채식)'를 추천해 주세요.
    4. 손님이 메뉴를 고르고 "이걸로 주문할게요" 또는 "주문하고 싶어요"라고 하면, 주문 접수를 위해 주문 담당 에이전트에게 연결(Handoff)해야 합니다.
    """


menu_agent = Agent(
    name="Menu Management Agent",
    instructions=menu_agent_instructions,
)
