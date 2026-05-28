import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 난수 생성 시드 설정
np.random.seed(42)

# 1. 고객정보 (Customer Info) 시트 데이터 생성
n_customers = 100
customer_ids = [f"C{str(i).zfill(3)}" for i in range(1, n_customers + 1)]
names = [
    "김철수", "이영희", "박민수", "최지원", "정경호", "한소희", "강동원", "송혜교", "조인성", "손예진",
    "임재범", "백지영", "이승기", "아이유", "수지", "공유", "김수현", "전지현", "이정재", "정우성"
]
# 이름을 100명으로 확장하기 위해 랜덤 조합
random_names = [np.random.choice(names) + str(np.random.randint(1, 10)) for _ in range(n_customers)]
genders = np.random.choice(["남", "여"], size=n_customers, p=[0.45, 0.55])
age_groups = np.random.choice(["20대", "30대", "40대", "50대", "60대 이상"], size=n_customers, p=[0.25, 0.35, 0.25, 0.12, 0.03])
regions = np.random.choice(["서울", "경기", "인천", "부산", "대구", "대전", "광주", "울산"], size=n_customers, p=[0.3, 0.25, 0.08, 0.12, 0.07, 0.06, 0.06, 0.06])

# 가입일자 (최근 2년 내)
start_date = datetime(2024, 1, 1)
join_dates = [start_date + timedelta(days=int(np.random.randint(0, 730))) for _ in range(n_customers)]
join_dates = [d.strftime("%Y-%m-%d") for d in join_dates]

df_customers = pd.DataFrame({
    "고객ID": customer_ids,
    "이름": random_names,
    "성별": genders,
    "연령대": age_groups,
    "지역": regions,
    "가입일자": join_dates
})

# 2. 재고정보 (Inventory Info) 시트 데이터 생성
products = {
    "P001": ("노트북 Pro", "전자기기", 1500000),
    "P002": ("스마트폰 S24", "전자기기", 1200000),
    "P003": ("태블릿 Air", "전자기기", 800000),
    "P004": ("무선 이어폰", "음향기기", 200000),
    "P005": ("스마트 워치", "액세서리", 350000),
    "P006": ("기계식 키보드", "액세서리", 150000),
    "P007": ("게이밍 마우스", "액세서리", 80000),
    "P008": ("고속 충전기", "액세서리", 35000),
    "P009": ("노이즈캔슬링 헤드폰", "음향기기", 400000),
    "P010": ("모니터 27인치", "전자기기", 300000)
}

product_ids = list(products.keys())
product_names = [products[pid][0] for pid in product_ids]
categories = [products[pid][1] for pid in product_ids]
prices = [products[pid][2] for pid in product_ids]
stocks = np.random.randint(10, 150, size=len(product_ids))
restock_dates = [(datetime(2026, 1, 1) + timedelta(days=int(np.random.randint(0, 120)))).strftime("%Y-%m-%d") for _ in range(len(product_ids))]

df_inventory = pd.DataFrame({
    "상품코드": product_ids,
    "상품명": product_names,
    "카테고리": categories,
    "단가": prices,
    "재고수량": stocks,
    "최근입고일자": restock_dates
})

# 3. 구매정보 (Purchase Info) 시트 데이터 생성
n_purchases = 500
purchase_ids = [f"O{str(i).zfill(4)}" for i in range(1, n_purchases + 1)]
p_cust_ids = np.random.choice(customer_ids, size=n_purchases)
p_prod_ids = np.random.choice(product_ids, size=n_purchases, p=[0.1, 0.15, 0.08, 0.15, 0.12, 0.08, 0.08, 0.12, 0.06, 0.06])
quantities = np.random.choice([1, 2, 3, 4, 5], size=n_purchases, p=[0.7, 0.18, 0.08, 0.03, 0.01])

# 단가를 가져와서 총 구매금액 계산
df_temp_prices = df_inventory.set_index("상품코드")["단가"]
total_amounts = [df_temp_prices[pid] * qty for pid, qty in zip(p_prod_ids, quantities)]

# 구매일자 (최근 1년 내)
p_start_date = datetime(2025, 5, 28) - timedelta(days=365)
purchase_dates = [p_start_date + timedelta(days=int(np.random.randint(0, 365))) for _ in range(n_purchases)]
purchase_dates = [d.strftime("%Y-%m-%d %H:%M:%S") for d in purchase_dates]

df_purchases = pd.DataFrame({
    "주문번호": purchase_ids,
    "고객ID": p_cust_ids,
    "상품코드": p_prod_ids,
    "구매수량": quantities,
    "구매금액": total_amounts,
    "구매일자": purchase_dates
})

# 엑셀 파일로 저장
file_name = "sample_data.xlsx"
with pd.ExcelWriter(file_name, engine="openpyxl") as writer:
    df_customers.to_excel(writer, sheet_name="고객정보", index=False)
    df_purchases.to_excel(writer, sheet_name="구매정보", index=False)
    df_inventory.to_excel(writer, sheet_name="재고정보", index=False)

print(f"성공적으로 엑셀 파일이 생성되었습니다: {file_name}")
