import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ---------------------------------------------------------
# 1. 페이지 설정 및 디자인 스타일 지정 (CSS)
# ---------------------------------------------------------
st.set_page_config(
    page_title="고객 구매 및 재고 분석 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Custom CSS
st.markdown("""
<style>
    /* Google Font 임포트 */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', 'Noto Sans KR', sans-serif;
    }
    
    /* 메인 배경색 및 폰트 크기 조정 */
    .main {
        background-color: #f8f9fa;
    }
    
    /* 타이틀 스타일 */
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4f46e5, #06b6d4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
        text-align: left;
    }
    
    /* KPI 카드 스타일 */
    .kpi-card {
        background-color: #ffffff;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border-left: 5px solid #4f46e5;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        margin-bottom: 1rem;
    }
    
    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    
    .kpi-title {
        font-size: 0.9rem;
        color: #6b7280;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1f2937;
        margin-top: 0.25rem;
    }
    
    /* 고객 상세 프로필 카드 */
    .profile-card {
        background: linear-gradient(135deg, #1e1b4b, #312e81);
        color: #ffffff;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
    }
    
    .profile-header {
        font-size: 1.4rem;
        font-weight: 700;
        border-bottom: 1px solid #4338ca;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    
    .profile-item {
        display: flex;
        justify-content: space-between;
        margin-bottom: 0.5rem;
        font-size: 0.95rem;
    }
    
    .profile-label {
        color: #c7d2fe;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. 데이터 로드 및 전처리
# ---------------------------------------------------------
@st.cache_data
def load_data():
    excel_path = "sample_data.xlsx"
    df_cust = pd.read_excel(excel_path, sheet_name="고객정보")
    df_purch = pd.read_excel(excel_path, sheet_name="구매정보")
    df_inv = pd.read_excel(excel_path, sheet_name="재고정보")
    
    # 날짜 데이터 처리
    df_cust["가입일자"] = pd.to_datetime(df_cust["가입일자"])
    df_purch["구매일자"] = pd.to_datetime(df_purch["구매일자"])
    df_inv["최근입고일자"] = pd.to_datetime(df_inv["최근입고일자"])
    
    return df_cust, df_purch, df_inv

try:
    df_cust, df_purch, df_inv = load_data()
except Exception as e:
    st.error(f"데이터를 불러오지 못했습니다. `sample_data.xlsx`가 올바르게 생성되었는지 확인해주세요. 오류: {e}")
    st.stop()

# 분석용 병합 데이터 생성
df_merged = df_purch.merge(df_cust, on="고객ID", how="left")
df_merged = df_merged.merge(df_inv[["상품코드", "상품명", "카테고리", "단가"]], on="상품코드", how="left")

# ---------------------------------------------------------
# 3. 사이드바 구성 (글로벌 필터 및 설명)
# ---------------------------------------------------------
st.sidebar.image("https://images.unsplash.com/photo-1551434678-e076c223a692?w=150&auto=format&fit=crop&q=60", use_container_width=True)
st.sidebar.title("📊 분석 제어판")
st.sidebar.markdown("이 대시보드는 샘플 유통 데이터를 바탕으로 고객 구매 패턴과 재고 상태를 시각화합니다.")

# 연령대/지역 필터 (멀티셀렉트)
selected_regions = st.sidebar.multiselect("지역 선택 (전체 대시보드용)", options=df_cust["지역"].unique().tolist(), default=df_cust["지역"].unique().tolist())
selected_categories = st.sidebar.multiselect("카테고리 선택 (전체 대시보드용)", options=df_inv["카테고리"].unique().tolist(), default=df_inv["카테고리"].unique().tolist())

# 대시보드 상단 타이틀
st.markdown("<div class='main-title'>고객 구매 및 재고 분석 대시보드</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. 탭 구성
# ---------------------------------------------------------
tabs = st.tabs(["👤 고객별 구매 내역", "📈 전체 매출 & 재고 현황", "📂 데이터 탐색기"])

# ---------------------------------------------------------
# 4-1. 첫 번째 탭: 고객별 구매 내역
# ---------------------------------------------------------
with tabs[0]:
    st.subheader("👤 고객 상세 구매 내역 조회")
    st.markdown("특정 고객을 선택하여 해당 고객의 프로필, 총 구매 지표, 그리고 시간별 구매 트렌드를 상세히 분석합니다.")
    
    # 고객 선택 박스 (고객ID와 이름을 같이 보여줌)
    df_cust["선택문구"] = df_cust["고객ID"] + " - " + df_cust["이름"]
    customer_list = df_cust["선택문구"].sort_values().tolist()
    selected_customer_str = st.selectbox("조회할 고객을 선택하세요:", options=customer_list)
    
    # 선택된 고객 정보 추출
    selected_cust_id = selected_customer_str.split(" - ")[0]
    cust_info = df_cust[df_cust["고객ID"] == selected_cust_id].iloc[0]
    
    # 선택된 고객의 구매 내역 필터링
    cust_purchases = df_merged[df_merged["고객ID"] == selected_cust_id].sort_values(by="구매일자", ascending=False)
    
    # 화면 레이아웃 분할 (좌측: 프로필/요약, 우측: 분석 차트/상세)
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # 고객 프로필 카드
        st.markdown(f"""
        <div class="profile-card">
            <div class="profile-header">고객 프로필</div>
            <div class="profile-item">
                <span class="profile-label">고객 ID</span>
                <strong>{cust_info['고객ID']}</strong>
            </div>
            <div class="profile-item">
                <span class="profile-label">이름</span>
                <strong>{cust_info['이름']}</strong>
            </div>
            <div class="profile-item">
                <span class="profile-label">성별</span>
                <strong>{cust_info['성별']}</strong>
            </div>
            <div class="profile-item">
                <span class="profile-label">연령대</span>
                <strong>{cust_info['연령대']}</strong>
            </div>
            <div class="profile-item">
                <span class="profile-label">지역</span>
                <strong>{cust_info['지역']}</strong>
            </div>
            <div class="profile-item">
                <span class="profile-label">가입일자</span>
                <strong>{cust_info['가입일자'].strftime('%Y-%m-%d')}</strong>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 고객 구매 요약지표
        if not cust_purchases.empty:
            total_spent = cust_purchases["구매금액"].sum()
            total_qty = cust_purchases["구매수량"].sum()
            avg_spent = cust_purchases["구매금액"].mean()
            pref_category = cust_purchases["카테고리"].value_counts().index[0]
            
            st.markdown(f"""
            <div class="kpi-card" style="border-left-color: #10b981;">
                <div class="kpi-title">누적 구매 금액</div>
                <div class="kpi-value">₩{total_spent:,.0f}</div>
            </div>
            <div class="kpi-card" style="border-left-color: #f59e0b;">
                <div class="kpi-title">총 구매 건수 (상품 수량)</div>
                <div class="kpi-value">{len(cust_purchases)}건 ({total_qty}개)</div>
            </div>
            <div class="kpi-card" style="border-left-color: #3b82f6;">
                <div class="kpi-title">회당 평균 구매액</div>
                <div class="kpi-value">₩{avg_spent:,.0f}</div>
            </div>
            <div class="kpi-card" style="border-left-color: #8b5cf6;">
                <div class="kpi-title">가장 선호하는 카테고리</div>
                <div class="kpi-value">{pref_category}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("이 고객은 구매 내역이 없습니다.")
            
    with col2:
        if not cust_purchases.empty:
            # 1. 시간 추이에 따른 구매 트렌드 차트
            cust_trend = cust_purchases.groupby(cust_purchases["구매일자"].dt.date)["구매금액"].sum().reset_index()
            cust_trend.columns = ["날짜", "구매금액"]
            
            fig_trend = px.area(
                cust_trend, 
                x="날짜", 
                y="구매금액", 
                title="시간별 구매 금액 추이",
                color_discrete_sequence=["#4f46e5"],
                labels={"구매금액": "구매 금액 (원)"}
            )
            fig_trend.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=20, r=20, t=40, b=20),
                height=300
            )
            fig_trend.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f3f4f6')
            fig_trend.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f3f4f6')
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # 2. 카테고리별 구매 금액 분포
            cust_cat = cust_purchases.groupby("카테고리")["구매금액"].sum().reset_index()
            fig_cat = px.bar(
                cust_cat,
                x="카테고리",
                y="구매금액",
                title="카테고리별 누적 구매액",
                color="카테고리",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_cat.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=20, r=20, t=40, b=20),
                height=250,
                showlegend=False
            )
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.info("시각화할 구매 데이터가 없습니다.")

    # 상세 구매 내역 표
    st.markdown("#### 📋 상세 구매 내역 목록")
    if not cust_purchases.empty:
        # 데이터프레임 가독성 있게 정리
        display_df = cust_purchases[[
            "주문번호", "상품명", "카테고리", "단가", "구매수량", "구매금액", "구매일자"
        ]].copy()
        display_df["단가"] = display_df["단가"].map("₩{:,}".format)
        display_df["구매금액"] = display_df["구매금액"].map("₩{:,}".format)
        display_df["구매일자"] = display_df["구매일자"].dt.strftime("%Y-%m-%d %H:%M:%S")
        
        st.dataframe(display_df, use_container_width=True)
    else:
        st.write("상세 정보가 없습니다.")

# ---------------------------------------------------------
# 4-2. 두 번째 탭: 전체 매출 & 재고 현황
# ---------------------------------------------------------
with tabs[1]:
    st.subheader("📈 전체 매출 및 재고 상태 실시간 모니터링")
    
    # 글로벌 필터 반영
    df_filtered = df_merged[
        df_merged["지역"].isin(selected_regions) & 
        df_merged["카테고리"].isin(selected_categories)
    ]
    
    # 전체 비즈니스 요약 KPI 카드
    total_sales_all = df_filtered["구매금액"].sum()
    total_orders_all = df_filtered["주문번호"].nunique()
    total_custs_all = df_filtered["고객ID"].nunique()
    avg_order_value = total_sales_all / total_orders_all if total_orders_all > 0 else 0
    
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1:
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #4f46e5;">
            <div class="kpi-title">필터링 기준 총 매출액</div>
            <div class="kpi-value">₩{total_sales_all:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi_col2:
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #06b6d4;">
            <div class="kpi-title">총 구매 건수</div>
            <div class="kpi-value">{total_orders_all:,}건</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi_col3:
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #10b981;">
            <div class="kpi-title">구매 고객 수</div>
            <div class="kpi-value">{total_custs_all:,}명</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi_col4:
        st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #f59e0b;">
            <div class="kpi-title">건당 평균 주문액</div>
            <div class="kpi-value">₩{avg_order_value:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.write("---")
    
    # 매출 차트 레이아웃
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # 월별 매출 트렌드
        df_filtered["년월"] = df_filtered["구매일자"].dt.to_period("M").astype(str)
        monthly_sales = df_filtered.groupby("년월")["구매금액"].sum().reset_index()
        
        fig_monthly = px.line(
            monthly_sales, 
            x="년월", 
            y="구매금액", 
            title="📅 월별 매출액 추이",
            markers=True,
            color_discrete_sequence=["#4f46e5"],
            labels={"구매금액": "매출액 (원)"}
        )
        fig_monthly.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_monthly, use_container_width=True)
        
    with chart_col2:
        # 카테고리별 매출 비중
        cat_sales = df_filtered.groupby("카테고리")["구매금액"].sum().reset_index()
        fig_pie = px.pie(
            cat_sales, 
            values="구매금액", 
            names="카테고리", 
            title="🍕 카테고리별 매출 비중",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_pie, use_container_width=True)
        
    # 재고 현황 섹션
    st.write("---")
    st.subheader("📦 상품 재고 현황 & 위험 알림")
    
    # 재고 수준 시각화 및 경보 설정 (예: 30개 미만 재고 부족)
    low_stock_limit = 30
    df_inv["재고상태"] = df_inv["재고수량"].apply(lambda x: "🚨 재고 부족" if x < low_stock_limit else "✅ 안정")
    
    inv_col1, inv_col2 = st.columns([2, 1])
    
    with inv_col1:
        # 전체 상품 재고수량 차트
        fig_stock = px.bar(
            df_inv,
            x="상품명",
            y="재고수량",
            color="재고상태",
            color_discrete_map={"🚨 재고 부족": "#ef4444", "✅ 안정": "#10b981"},
            title="상품별 현재 재고 수량",
            category_orders={"재고상태": ["🚨 재고 부족", "✅ 안정"]}
        )
        # 30개 기준선(임계치) 그리기
        fig_stock.add_hline(y=low_stock_limit, line_dash="dash", line_color="#ef4444", annotation_text="재고 부족 기준선 (30개)")
        fig_stock.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_stock, use_container_width=True)
        
    with inv_col2:
        # 재고 부족 상품 목록 표출
        st.markdown(f"#### ⚠️ 재고 부족 상품 리스트 ({low_stock_limit}개 미만)")
        df_low_stock = df_inv[df_inv["재고수량"] < low_stock_limit].sort_values(by="재고수량")
        if not df_low_stock.empty:
            display_low = df_low_stock[["상품코드", "상품명", "재고수량", "최근입고일자"]].copy()
            display_low["최근입고일자"] = display_low["최근입고일자"].dt.strftime("%Y-%m-%d")
            st.dataframe(display_low, use_container_width=True, hide_index=True)
        else:
            st.success("모든 상품의 재고가 충분합니다!")

# ---------------------------------------------------------
# 4-3. 세 번째 탭: 데이터 원본 보기
# ---------------------------------------------------------
with tabs[2]:
    st.subheader("📂 raw 데이터 테이블 보기")
    st.markdown("엑셀 파일에 저장된 시트별 원본 데이터를 탐색할 수 있습니다.")
    
    sheet_choice = st.radio(
        "확인할 데이터 시트를 선택하세요:",
        options=["고객정보", "구매정보", "재고정보"],
        horizontal=True
    )
    
    if sheet_choice == "고객정보":
        st.markdown(f"**총 고객 수**: {len(df_cust)}명")
        st.dataframe(df_cust, use_container_width=True)
    elif sheet_choice == "구매정보":
        st.markdown(f"**총 구매 건수**: {len(df_purch)}건")
        st.dataframe(df_purch, use_container_width=True)
    elif sheet_choice == "재고정보":
        st.markdown(f"**총 상품 종류**: {len(df_inv)}종")
        st.dataframe(df_inv, use_container_width=True)
