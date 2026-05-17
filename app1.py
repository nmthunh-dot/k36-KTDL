import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import folium
from streamlit_folium import st_folium
import random

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN & CSS THÍCH ỨNG SÁNG/TỐI
# ==========================================
st.set_page_config(page_title="CX System Pro", page_icon="🍗", layout="wide")

st.markdown("""
    <style>
    /* Hiệu ứng chữ nổi thích ứng */
    .title-embossed {
        font-size: 40px; font-weight: 900; color: #3B82F6; 
        text-shadow: 2px 2px 4px rgba(0,0,0,0.15);
        margin-bottom: 5px;
    }
    .subtitle { font-size: 18px; color: var(--text-color); opacity: 0.8; margin-bottom: 30px; font-weight: 500; }
    
    /* Thẻ KPI tự động đổi màu nền và màu chữ */
    .kpi-card {
        background-color: var(--secondary-background-color);
        color: var(--text-color);
        padding: 22px; border-radius: 15px; 
        box-shadow: 3px 3px 12px rgba(0,0,0,0.08);
        border-left: 6px solid #3B82F6; 
        border: 1px solid rgba(128, 128, 128, 0.2);
    }
    .kpi-value { font-size: 32px; font-weight: bold; color: #E74C3C; margin-top: 5px; }
    .kpi-label { font-size: 13px; font-weight: bold; text-transform: uppercase; opacity: 0.9; }
    
    /* Thẻ bình luận ảo trực quan */
    .review-card {
        background-color: var(--background-color);
        color: var(--text-color);
        padding: 15px; border-radius: 10px; margin-bottom: 12px;
        border-left: 4px solid #E74C3C; 
        border: 1px solid rgba(128, 128, 128, 0.15);
        box-shadow: 1px 1px 6px rgba(0,0,0,0.05);
    }
    
    /* Khung kết luận quản trị */
    .conclusion-box {
        background-color: var(--secondary-background-color);
        color: var(--text-color);
        padding: 25px; border-radius: 12px;
        border: 1px dashed #3B82F6;
        margin-top: 15px;
    }
    </style>
""", unsafe_allow_html=True)

BRANCHES_INFO = {
    'Quận 1': {'lat': 10.7769, 'lon': 106.7009},
    'Quận 10': {'lat': 10.7725, 'lon': 106.6681},
    'Gò Vấp': {'lat': 10.8271, 'lon': 106.6769}
}

# Từ điển lưu trữ kết luận chi tiết độc lập của từng chi nhánh
BRANCH_CONCLUSIONS = {
    'Quận 1': {
        'title': '📍 ĐÁNH GIÁ CHI NHÁNH QUẬN 1',
        'color': '#2563EB',
        'content': """<b>Vấn đề nghiêm trọng nhất:</b> <i>Chỗ để xe & Thái độ của đội ngũ bảo vệ (Chiếm 60% phản hồi tiêu cực).</i><br><br>
                      <b>Chi tiết phân tích hành vi:</b> Khách hàng than phiền bãi xe luôn rơi vào tình trạng quá tải nghiêm trọng trong khung giờ cao điểm tối (18h-21h). Nhân sự bảo vệ có hành vi nạt nộ lớn tiếng, không dắt xe hộ khách.<br><br>
                      🎯 <b>Kế hoạch hành động sửa đổi:</b> Đàm phán thuê lại bãi phụ kế bên ngay trong tuần tới cho phân khúc khách ăn tại quán; đồng thời chấn chỉnh ngay thái độ nhân sự bảo vệ ca tối hoặc luân chuyển vị trí."""
    },
    'Quận 10': {
        'title': '📍 ĐÁNH GIÁ CHI NHÁNH QUẬN 10',
        'color': '#10B981',
        'content': """<b>Vấn đề nghiêm trọng nhất:</b> <i>Lỗi kỹ thuật đồng bộ công thức sản phẩm - Hương vị Sốt Phô Mai.</i><br><br>
                      <b>Chi tiết phân tích hành vi:</b> Thuật toán NLP bóc tách tỷ lệ từ khóa phản hồi khách hàng phàn nàn sốt có vị mặn gắt đột biến, kết cấu lỏng như nước, không đạt độ sệt béo tiêu chuẩn của thương hiệu.<br><br>
                      🎯 <b>Kế hoạch hành động sửa đổi:</b> Trưởng bộ phận giám sát bếp cần kiểm tra lô nguyên liệu bột phô mai nhập kho đầu tháng. Đo lường lại quy trình đong đếm tỷ lệ nước/bột chuẩn quy trình tại bếp Quận 10."""
    },
    'Gò Vấp': {
        'title': '📍 ĐÁNH GIÁ CHI NHÁNH GÒ VẤP',
        'color': '#F59E0B',
        'content': """<b>Vấn đề nghiêm trọng nhất:</b> <i>Đóng gói lỗi hỏng nghiêm trọng ở kênh Online (ShopeeFood/GrabFood).</i><br><br>
                      <b>Chi tiết phân tích hành vi:</b> Tập trung nhiều phàn nàn về việc 'Trà đào bị tràn nước' làm ướt bọc đựng, khiến hơi nước bốc lên làm da gà rán bị hấp hơi dẫn đến ỉu rộp, mất độ giòn.<br><br>
                      🎯 <b>Kế hoạch hành động sửa đổi:</b> Thay thế toàn bộ nắp vòm nhựa đóng tay bằng <b>máy ép màng nhiệt ly nước</b> chuyên dụng khi ship đi xa. Yêu cầu bọc riêng đá và hộp gà rán độc lập."""
    }
}

# ==========================================
# 2. HỆ THỐNG ĐĂNG NHẬP
# ==========================================
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

def login():
    st.markdown('<p class="title-embossed" style="text-align:center;">HỆ THỐNG QUẢN TRỊ CX v2.5</p>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Tên đăng nhập")
            password = st.text_input("Mật khẩu", type="password")
            submit_button = st.form_submit_button("Đăng Nhập", use_container_width=True)
            if submit_button:
                if username == "admin" and password == "123456":
                    st.session_state['logged_in'] = True
                    st.rerun()
                else:
                    st.error("Sai tài khoản! (Gợi ý: admin / 123456)")

if not st.session_state['logged_in']:
    login()
    st.stop()

with st.sidebar:
    if st.button("🚪 Đăng xuất", use_container_width=True):
        st.session_state['logged_in'] = False
        st.rerun()
    st.markdown("---")

# ==========================================
# 3. KHO DỮ LIỆU BÌNH LUẬN SÁNG TẠO (REALISTIC F&B)
# ==========================================
@st.cache_data
def generate_advanced_mock_data():
    np.random.seed(101)
    dates = pd.date_range(start='2026-05-01', periods=14, freq='D')
    aspects = ['Sốt phô mai', 'Sốt cay HQ', 'Trà đào cam sả', 'Chỗ để xe', 'Thái độ NV', 'Giao hàng']
    sources = ['ShopeeFood', 'GrabFood', 'Google Maps', 'Fanpage']
    
    reviews_lib = {
        'Sốt phô mai': [
            "Ncl sốt phô mai hnay mặn chát lun á, ăn xong uống hết cả lít nước, mong quán check lại gùmg.",
            "Vị phô mai bị lỏng bét như nước lèo ý chê nha, không bám dính vào miếng gà tí nào cả.",
            "Thất vọng ghê, vị phô mai nay cứ chua chua kì cục sao á, không béo ngậy như mọi khi dở tệ.",
            "Gà ngon nhưng đổ sốt phô mai quá ít, mà vị đợt này bị đổi đúng k shop?"
        ],
        'Chỗ để xe': [
            "Quán ngay trung tâm Quận 1 mà bãi xe bé tí, bảo vệ thì thái độ lồi lõm nạt khách bực cả mình!",
            "Ghé quán tối t7 đông khách mà hết chỗ giữ xe, bảo vệ bắt chạy đi chỗ khác tự trả tiền??? Quá tệ.",
            "View đẹp gà ngon nhưng bãi xe quá tải, dắt cái xe ra mún ná thở lun á.",
            "Ức chế nhất là khâu gửi xe, đứng đợi 15p ko ai dắt hộ còn bị cằn nhằn."
        ],
        'Giao hàng': [
            "Giao tới ly trà đào đổ sạch bách ra túi nilon, ướt hết cả hộp gà rán rầu ghê á shop ơi.",
            "Đặt hàng qua ShopeeFood đợi gần tiếng đồng hồ gà nguội ngắt, sốt phô mai thì giao thiếu.",
            "Gói hàng lỏng lẻo quá, shipper chạy nhanh tí là nước đổ hết. Trà đào cam sả ngon uổng công đổ mất nửa ly.",
            "App báo giao xong rồi mà 10p sau shipper mới tới, gà rán bị ỉu rộp hết da."
        ],
        'Thái độ NV': [
            "Mấy bạn order mặt cứ cau có kiểu j ấy, mình hỏi xin thêm tương thôi làm gì mà căng thẳng thế.",
            "Tính tiền chậm chạp, khách xếp hàng dài mà nhân viên vẫn đứng buôn chuyện vô tư.",
            "Quản lý ca tối nói chuyện trống không với khách, cần đào tạo lại nghiệp vụ."
        ]
    }
    
    data = []
    for _ in range(400):
        branch = np.random.choice(list(BRANCHES_INFO.keys()), p=[0.4, 0.3, 0.3])
        aspect = np.random.choice(aspects)
        source = np.random.choice(sources)
        date = np.random.choice(dates)
        
        if branch == 'Quận 10':
            aspect = np.random.choice(['Sốt phô mai', 'Thái độ NV', 'Sốt cay HQ'], p=[0.6, 0.2, 0.2])
        elif branch == 'Quận 1':
            aspect = np.random.choice(['Chỗ để xe', 'Thái độ NV', 'Trà đào cam sả'], p=[0.6, 0.2, 0.2])
        elif branch == 'Gò Vấp':
            aspect = np.random.choice(['Giao hàng', 'Sốt phô mai', 'Trà đào cam sả'], p=[0.6, 0.2, 0.2])

        review_text = random.choice(reviews_lib[aspect]) if aspect in reviews_lib else f"Gà ăn tạm ổn nhưng khía cạnh {aspect} chưa đạt kỳ vọng lắm."
        data.append([date, branch, BRANCHES_INFO[branch]['lat'], BRANCHES_INFO[branch]['lon'], aspect, 'Tiêu cực', source, review_text])
        
    return pd.DataFrame(data, columns=['Ngay', 'Chi_nhanh', 'Lat', 'Lon', 'Khia_canh', 'Cam_xuc', 'Nguon', 'Chi_tiet_Review'])

df = generate_advanced_mock_data()

# ==========================================
# 4. ĐẦU TRANG & PHẦN LỌC KHÍ CỤ
# ==========================================
st.sidebar.header("🔍 Bộ Lọc Phân Tích")
selected_branches = st.sidebar.multiselect("📍 Chi nhánh:", df['Chi_nhanh'].unique(), default=df['Chi_nhanh'].unique())
selected_aspects = st.sidebar.multiselect("🎯 Khía cạnh cần soi:", df['Khia_canh'].unique(), default=df['Khia_canh'].unique())

df_filtered = df[(df['Chi_nhanh'].isin(selected_branches)) & (df['Khia_canh'].isin(selected_aspects))]

# Hiển thị tiêu đề nổi bật thích ứng
st.markdown('<div class="title-embossed">🍗 Dashboard Phản Hồi Đa Điểm Chạm</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Hệ thống phân tích không gian - thời gian thích ứng giao diện thông minh</div>', unsafe_allow_html=True)

# KPI Cards
col1, col2, col3, col4 = st.columns(4)
total_issues = len(df_filtered)
top_aspect = df_filtered['Khia_canh'].value_counts().idxmax() if not df_filtered.empty else "N/A"
top_branch = df_filtered['Chi_nhanh'].value_counts().idxmax() if not df_filtered.empty else "N/A"

col1.markdown(f'<div class="kpi-card"><div class="kpi-label">Tổng Phàn Nàn Tuần Này</div><div class="kpi-value">{total_issues}</div></div>', unsafe_allow_html=True)
col2.markdown(f'<div class="kpi-card"><div class="kpi-label">Vấn Đề Cần Giải Quyết</div><div class="kpi-value">{top_aspect}</div></div>', unsafe_allow_html=True)
col3.markdown(f'<div class="kpi-card"><div class="kpi-label">Chi Nhánh Báo Động</div><div class="kpi-value">{top_branch}</div></div>', unsafe_allow_html=True)
col4.markdown(f'<div class="kpi-card"><div class="kpi-label">Chỉ Số CSAT Toàn Chuỗi</div><div class="kpi-value" style="color:#F59E0B">64%</div></div>', unsafe_allow_html=True)

st.write("---")

# ==========================================
# 5. BẢN ĐỒ VÀ KHUNG KÉO BÌNH LUẬN TƯƠNG TÁC LỌC ĐỒNG BỘ
# ==========================================
col_map, col_reviews = st.columns([1.6, 1.4])

with col_map:
    st.subheader("🗺️ Bản Đồ Điểm Nóng Vận Hành")
    st.caption("Mẹo điều hành: Bấm vào chấm đỏ chi nhánh để lọc đồng thời cả Bình luận và Kết luận đánh giá.")
    
    clicked_branch = None
    if not df_filtered.empty:
        map_data = df_filtered.groupby(['Chi_nhanh', 'Lat', 'Lon']).size().reset_index(name='Count')
        m = folium.Map(location=[10.79, 106.68], zoom_start=12, tiles='CartoDB positron')
        
        for _, row in map_data.iterrows():
            folium.CircleMarker(
                location=[row['Lat'], row['Lon']],
                radius=float(row['Count']) / 2.5,
                popup=f"{row['Chi_nhanh']}: {row['Count']} lỗi",
                color='#E74C3C', fill=True, fill_color='#E74C3C', fill_opacity=0.6
            ).add_to(m)
            
        map_result = st_folium(m, width=650, height=430)
        
        # Bắt sự kiện click chuột trên bản đồ để lấy tên Chi nhánh
        if map_result and map_result.get("last_object_clicked"):
            lat_clicked = map_result["last_object_clicked"]["lat"]
            lon_clicked = map_result["last_object_clicked"]["lng"]
            for branch, coords in BRANCHES_INFO.items():
                if abs(coords['lat'] - lat_clicked) < 0.001 and abs(coords['lon'] - lon_clicked) < 0.001:
                    clicked_branch = branch
                    break

with col_reviews:
    st.subheader("💬 Luồng Đánh Giá Khách Hàng")
    
    if clicked_branch:
        st.success(f"📌 Chỉ hiển thị bình luận của: **{clicked_branch}**")
        df_reviews_to_show = df_filtered[df_filtered['Chi_nhanh'] == clicked_branch]
    else:
        st.markdown("*Đang xem dữ liệu tổng hợp toàn chuỗi. Hãy click một điểm đỏ trên bản đồ để lọc sâu.*")
        df_reviews_to_show = df_filtered
        
    # Khung container cuộn (Scrollable container) giữ nguyên
    with st.container(height=390):
        if not df_reviews_to_show.empty:
            shuffled_df = df_reviews_to_show.sample(frac=1)
            for _, row in shuffled_df.iterrows():
                st.markdown(f"""
                <div class="review-card">
                    <strong>{row['Chi_nhanh']} | Kênh: {row['Nguon']} - <span style="color:#E74C3C">{row['Khia_canh']}</span></strong><br>
                    "{row['Chi_tiet_Review']}"
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Không có bình luận nào.")

st.write("---")

# ==========================================
# 6. KẾT LUẬN ĐÁNH GIÁ ĐỒNG BỘ THEO SỰ KIỆN CLICK BẢN ĐỒ
# ==========================================
st.subheader("📋 Kết Luận & Đánh Giá Chi Nhánh")

# Xử lý logic hiển thị kết luận theo đúng yêu cầu: bấm vào đâu hiện đánh giá độc lập ở đó
if clicked_branch:
    st.markdown(f"Đang hiển thị báo cáo đánh giá sau cùng cho: **{clicked_branch}**")
    branch_data = BRANCH_CONCLUSIONS[clicked_branch]
    st.markdown(f"""
    <div class="conclusion-box" style="border-left: 6px solid {branch_data['color']};">
        <h3 style="margin:0; color:{branch_data['color']}; font-weight: bold;">{branch_data['title']}</h3>
        <p style="font-size:16px; margin-top:15px; line-height:1.6;">
            {branch_data['content']}
        </p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("*Đang hiển thị toàn bộ ma trận đánh giá tổng hợp của cả 3 chi nhánh (Hãy bấm vào bản đồ để lọc riêng từng vùng):*")
    col_q1, col_q10, col_gv = st.columns(3)
    
    with col_q1:
        st.markdown(f"""<div class="conclusion-box" style="border-left: 5px solid {BRANCH_CONCLUSIONS['Quận 1']['color']}; min-height:300px;">
            <h4 style="margin:0; color:{BRANCH_CONCLUSIONS['Quận 1']['color']};">{BRANCH_CONCLUSIONS['Quận 1']['title']}</h4>
            <p style="font-size:14px; margin-top:10px;">{BRANCH_CONCLUSIONS['Quận 1']['content']}</p>
        </div>""", unsafe_allow_html=True)
        
    with col_q10:
        st.markdown(f"""<div class="conclusion-box" style="border-left: 5px solid {BRANCH_CONCLUSIONS['Quận 10']['color']}; min-height:300px;">
            <h4 style="margin:0; color:{BRANCH_CONCLUSIONS['Quận 10']['color']};">{BRANCH_CONCLUSIONS['Quận 10']['title']}</h4>
            <p style="font-size:14px; margin-top:10px;">{BRANCH_CONCLUSIONS['Quận 10']['content']}</p>
        </div>""", unsafe_allow_html=True)
        
    with col_gv:
        st.markdown(f"""<div class="conclusion-box" style="border-left: 5px solid {BRANCH_CONCLUSIONS['Gò Vấp']['color']}; min-height:300px;">
            <h4 style="margin:0; color:{BRANCH_CONCLUSIONS['Gò Vấp']['color']};">{BRANCH_CONCLUSIONS['Gò Vấp']['title']}</h4>
            <p style="font-size:14px; margin-top:10px;">{BRANCH_CONCLUSIONS['Gò Vấp']['content']}</p>
        </div>""", unsafe_allow_html=True)

st.write("---")

# ==========================================
# 7. GIỮ NGUYÊN CÁC BIỂU ĐỒ TRỰC QUAN XU HƯỚNG BÊN DƯỚI
# ==========================================
st.subheader("📈 Biểu Đồ Thống Kê Xu Hướng")
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    if not df_filtered.empty:
        source_df = df_filtered['Nguon'].value_counts().reset_index()
        source_df.columns = ['Nguon', 'Count']
        fig_pie = px.pie(source_df, values='Count', names='Nguon', hole=0.5, 
                         color_discrete_sequence=['#3498DB', '#9B59B6', '#F1C40F'])
        fig_pie.update_layout(title_text="Tỷ lệ Nguồn Phản Hồi", title_font=dict(size=18, color='#3B82F6'))
        st.plotly_chart(fig_pie, use_container_width=True)

with col_chart2:
    if not df_filtered.empty:
        aspect_df = df_filtered['Khia_canh'].value_counts().reset_index()
        aspect_df.columns = ['Khia_canh', 'Count']
        fig_bar = px.bar(aspect_df, x='Count', y='Khia_canh', orientation='h', 
                         color='Count', color_continuous_scale='Reds')
        fig_bar.update_layout(title_text="Xếp Hạng Các Vấn Đề", title_font=dict(size=18, color='#3B82F6'), yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)
