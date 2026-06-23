from pydantic import BaseModel
from typing import List, Optional

# 1. 고객의 기본 계정 및 세션 상태 정보
class UserAccountContext(BaseModel):
    customer_id: int
    name: str
    tier: str = "basic"  # basic, premium, enterprise
    email: str
    
    # [Tip] 대화 중에 예약 진행 시 채워질 임시 세션 필드들
    current_reservation_date: Optional[str] = None
    current_reservation_people: Optional[int] = None

# 2. 입력값 검증용 가드레일 (기존 코드 유지)
class InputGuardRailOutput(BaseModel):
    is_off_topic: bool
    reason: str

# 3. 개별 메뉴(요리) 상세 정보
class Dish(BaseModel):  # 파이썬 클래스 네이밍 컨벤션에 따라 대문자 Dish 추천
    name: str
    price: int
    ingredients: List[str]  # ['유기농 밀가루', '토마토 소스', '모짜렐라 치즈']
    allergies: List[str]    # ['밀', '우유']
    description : str

# 4. 레스토랑의 전체 데이터베이스 상태
class Restaurant(BaseModel):
    menu: List[Dish]

TODAYS_RESTAURANT_DATA = Restaurant(
    menu=[
        Dish(
            name="트러플 크림 뇨끼 (Truffle Cream Gnocchi)",
            price=28000,
            ingredients=["감자 뇨끼", "블랙 트러플 페이스트", "생크림", "파마산 치즈", "양송이버섯"],
            allergies=["밀", "우유", "버섯"],
            description="강원도 감자로 빚은 쫀득한 뇨끼에 진한 이탈리아산 블랙 트러플 크림 소스를 곁들인 시그니처 요리 (채식 주의자 섭취 가능, 비건은 불가)"
        ),
        Dish(
            name="한우 안심 스테이크 (Hanwoo Tenderloin Steak)",
            price=65000,
            ingredients=["1++ 등급 한우 안심", "로즈마리", "무염 버터", "아스파라거스", "레드와인 소스"],
            allergies=["우유", "아황산류(와인소스)"],
            description="최상급 1++ 한우 안심을 참나무 숯에 구워 부드러운 식감과 육즙을 극대화한 스테이크"
        ),
        Dish(
            name="지중해식 문어 샐러드 (Mediterranean Octopus Salad)",
            price=22000,
            ingredients=["자숙 문어", "방울토마토", "올리브 오일", "레몬 드레싱", "루콜라", "나쵸칩"],
            allergies=["연체류(문어)", "밀"],
            description="허브와 함께 부드럽게 데친 문어에 신선한 야채와 상큼한 레몬 드레싱을 곁들인 전채 요리"
        ),
        Dish(
            name="비건 아보카도 타르타르 (Vegan Avocado Tartare)",
            price=19000,
            ingredients=["아보카도", "망고", "오이", "라임 즙", "딜(허브)", "올리브 오일"],
            allergies=[],  # 알레르기 유발 물질 없음
            description="신선한 아보카도와 달콤한 망고를 큐브 모양으로 다져 상큼하게 버무린 100% 식물성 비건 요리"
        )
    ]
)