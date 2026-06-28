import dotenv
dotenv.load_dotenv()

from openai import OpenAI
import asyncio
import streamlit as st
from agents import (
    Runner,
    SQLiteSession,
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered
)
from models import UserAccountContext
# 작성하신 triage_agent를 가져옵니다.
from my_agents.triage_agent import triage_agent
from my_agents.menu_agent import menu_agent
from my_agents.order_agent import order_agent
from my_agents.reservation_agent import reservation_agent
from my_agents.complaints_agent import complaints_agent
menu_agent.handoffs = [
    order_agent,
    reservation_agent,
    complaints_agent,
]

order_agent.handoffs = [
    menu_agent,
    reservation_agent,
    complaints_agent,
]

reservation_agent.handoffs = [
    menu_agent,
    order_agent,
    complaints_agent,
]

complaints_agent.handoffs = [
    menu_agent,
    order_agent,
    reservation_agent,
]
client = OpenAI()
def extract_text_content(content):
    """
    SQLiteSession에 저장된 content가
    - str
    - list[{"type":"output_text","text":"..."}]
    - 기타 dict/list 구조
   일 수 있으므로 화면에 표시할 텍스트만 뽑아낸다.
    """
    if content is None:
        return ""

    # 이미 문자열이면 그대로 반환
    if isinstance(content, str):
        return content

    # Responses API content block 형태 처리
    if isinstance(content, list):
        texts = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "output_text":
                    texts.append(block.get("text", ""))
                elif "text" in block:
                    texts.append(str(block["text"]))
        return "\n".join(t for t in texts if t)

    # 혹시 dict 단독으로 오는 경우
    if isinstance(content, dict):
        if content.get("type") == "output_text":
            return content.get("text", "")
        if "text" in content:
            return str(content["text"])

    # 최후 fallback
    return str(content)

# 1. 유저 계정 컨텍스트 설정
user_account_ctx = UserAccountContext(
    customer_id=1,
    name="zealot",
    tier="basic",
    email="zealot@example.com"
)

# 2. 세션 데이터베이스 및 에이전트 상태 초기화
if "session" not in st.session_state:
    st.session_state["session"] = SQLiteSession(
        "chat-history",
        "customer-support-memory.db",
    )
session = st.session_state["session"]

# 현재 대화를 제어하는 에이전트 상태값 (기본값은 triage_agent)
if "agent" not in st.session_state:
    st.session_state["agent"] = triage_agent


async def main():
    st.title("🍔 데일리 레스토랑")

    # 3. 사이드바 구성 (현재 연결된 에이전트 정보 시각화)
    with st.sidebar:
        st.subheader("🤖 Agent 상태")
        st.success(f"현재 활성화: **{st.session_state['agent'].name}**")
        
        reset = st.button("대화 메모리 리셋")
        if reset:
            await session.clear_session()
            st.session_state["agent"] = triage_agent  # 에이전트도 초기 상태로 리셋
            st.rerun()
        
        items = await session.get_items()
        st.write("세션 내부 메타데이터:", items)

    # 4. 이전 대화 기록 불러와 화면에 렌더링
    messages = await session.get_items()
    for message in messages:
        role = message.get("role")
        content = message.get("content")

        if role in ["user", "assistant"] and content:
            with st.chat_message(role):
                rendered = extract_text_content(content)
                st.markdown(rendered)

    # 5. 유저 채팅 입력창 생성
    user_message = st.chat_input("레스토랑 봇에게 메시지를 보내세요 (예: 예약하고 싶어)")

    if user_message:
        # 유저가 입력한 텍스트 즉시 렌더링
        with st.chat_message("user"):
            st.write(user_message)
        
        # 에이전트 응답 영역 생성 및 스트리밍 시작
        with st.chat_message("assistant"):
            text_placeholder = st.empty()
            response = ""

            try:
                # [핵심] 현재 활성화된 에이전트(st.session_state["agent"])를 주입하여 동적 실행
                stream = Runner.run_streamed(
                    starting_agent=st.session_state["agent"],
                    input=user_message,
                    session=session,
                    context=user_account_ctx,
                )

                # 텍스트가 생성되는 대로 화면에 낱개 단위(delta)로 업데이트
                async for event in stream.stream_events():
                    if event.type == "raw_response_event":
                        if event.data.type == "response.output_text.delta":
                            response += event.data.delta
                            text_placeholder.write(response)
                
                # 6. [Handoff 핵심 부문] 스트리밍 완료 후 내부적으로 전환된 최종 에이전트 상태 확인
                if hasattr(stream, "last_agent") and stream.last_agent:
                    st.session_state["agent"] = stream.last_agent

            except InputGuardrailTripwireTriggered:
                text_placeholder.write("⚠️ 부적절한 요청이 감지되어 답변을 중단합니다.")            
            except OutputGuardrailTripwireTriggered:
                text_placeholder.write("⚠️ 부적절한 답변이 감지되어 답변을 중단합니다.")
            except Exception as e:
                text_placeholder.write(f"❌ 실행 중 오류가 발생했습니다: {str(e)}")
        
        # 에이전트 전환 상태를 사이드바 등에 즉시 반영하기 위해 화면 강제 리프레시
        st.rerun()


# Streamlit 앱 실행 진입점
if __name__ == "__main__":
    asyncio.run(main())