import streamlit as st
import pandas as pd
from google import genai
from google.genai import types
from gtts import gTTS
import io
import time

# Cấu hình trang web
st.set_page_config(page_title="Cố Đô AI - Trợ Lý Du Lịch Thông Minh", page_icon="🏛️", layout="wide")

# Khởi tạo bộ nhớ tạm
if "green_credits" not in st.session_state:
    st.session_state.green_credits = 50
if "messages" not in st.session_state:
    st.session_state.messages = list()
if "tourist_messages" not in st.session_state:
    st.session_state.tourist_messages = list()

# --- HÀM HỖ TRỢ XÂY DỰNG LỊCH SỬ HỘI THOẠI (CONTEXT) ---
def tao_lich_su_hoi_thoai(danh_sach_tin_nhan):
    lich_su_chuan = list()
    for tin in danh_sach_tin_nhan:
        vai_tro = "user" if tin.get("role") == "user" else "model"
        noi_dung = tin.get("content", "")
        if noi_dung and not noi_dung.startswith("🎙️"):
            lich_su_chuan.append(
                types.Content(
                    role=vai_tro,
                    parts=(types.Part.from_text(text=noi_dung),)
                )
            )
    return lich_su_chuan

# --- THANH BÊN: TRẠNG THÁI HỆ THỐNG & ĐIỂM THƯỞNG ---
with st.sidebar:
    st.title("🏛️ Cố Đô AI")
    st.caption("Hướng dẫn viên Du lịch Thông minh Liên vùng (Hà Nam - Nam Định - Ninh Bình)")
    
    # Đọc mã API Key an toàn từ két sắt Secrets của Streamlit Cloud
    api_key = st.secrets["GEMINI_API_KEY"]
    st.success("✅ Hệ thống AI đã sẵn sàng phục vụ du khách")
    
    st.divider()
    st.metric(label="🌱 Tín chỉ Xanh của bạn", value=f"{st.session_state.green_credits} điểm")
    st.info("Tích lũy điểm khi di chuyển xanh giữa các điểm di sản và đổi quà tại các làng nghề truyền thống (Gốm Bồ Bát, Lụa Nha Xá, Đúc đồng Tống Xá).")

# --- GIAO DIỆN CHÍNH: CHIA 4 TABS DÀNH CHO DU KHÁCH ---
tab0, tab1, tab2, tab3 = st.tabs((
    "🗺️ Giới thiệu & Lịch trình Du khách", 
    "🚲 Điều phối Du lịch Xanh", 
    "👑 Trò chuyện với Nhân vật Lịch sử",
    "🎁 Bản đồ Số & Đổi quà Làng nghề"
))

# ==========================================
# TAB 0: GIỚI THIỆU & CHỈ DẪN DU KHÁCH (CÓ NHỚ NGỮ CẢNH)
# ==========================================
with tab0:
    st.header("Hướng dẫn viên AI Khám phá Vùng Di sản (Tam Chúc - Hoa Lư - Đền Trần)")
    st.caption("Tư vấn lịch trình tham quan, giới thiệu điểm đến nổi bật, ẩm thực đặc sản và văn hóa bản địa cho du khách.")
    
    col_kv, col_dm, col_clear = st.columns(3)
    with col_kv:
        khu_vuc = st.selectbox(
            "Điểm đến bạn đang quan tâm:",
            (
                "Toàn tuyến di sản (Hà Nam - Nam Định - Ninh Bình)",
                "Quần thể Tràng An - Cố đô Hoa Lư - Tam Cốc (Ninh Bình)",
                "Khu du lịch Tam Chúc - Địa Tạng Phi Lai Tự (Hà Nam)",
                "Đền Trần - Phủ Dày - Biển Thịnh Long (Nam Định)"
            )
        )
    with col_dm:
        danh_muc = st.selectbox(
            "Chủ đề muốn khám phá:",
            (
                "Gợi ý lịch trình tham quan 1 - 2 ngày",
                "Ẩm thực đặc sản & Quán ngon địa phương",
                "Giá vé tham quan, giờ mở cửa & Lưu ý di chuyển",
                "Làng nghề truyền thống & Quà lưu niệm"
            )
        )
    with col_clear:
        st.write("")
        st.write("")
        if st.button("Làm mới cuộc trò chuyện"):
            st.session_state.tourist_messages = list()
            st.rerun()

    st.markdown("**Gợi ý khám phá nhanh cho du khách (Bấm để hỏi):**")
    q_col1, q_col2, q_col3 = st.columns(3)
    quick_prompt = None
    with q_col1:
        if st.button("🗓️ Lịch trình 1 ngày Tam Chúc - Tràng An?"):
            quick_prompt = "Hãy thiết kế giúp tôi một lịch trình du lịch hợp lý trong 1 ngày kết nối Khu du lịch Tam Chúc (Hà Nam) và Quần thể danh thắng Tràng An (Ninh Bình)."
    with q_col2:
        if st.button("🍜 Đặc sản nhất định phải thử ở 3 vùng?"):
            quick_prompt = "Giới thiệu những món ăn đặc sản nổi tiếng nhất mà du khách nhất định phải thưởng thức khi đi qua trục Hà Nam - Nam Định - Ninh Bình."
    with q_col3:
        if st.button("🏺 Mua quà gì tại các làng nghề truyền thống?"):
            quick_prompt = "Gợi ý cho du khách các sản phẩm thủ công mỹ nghệ đặc sắc tại các làng nghề truyền thống vùng Hà Nam, Nam Định, Ninh Bình để mua về làm quà."

    for msg in st.session_state.tourist_messages:
        with st.chat_message(msg.get("role")):
            st.markdown(msg.get("content"))

    audio_tourist = st.audio_input("🎙️ Bấm vào Micro để hỏi hướng dẫn viên AI:", key="mic_tourist")
    user_tourist_input = st.chat_input("Hỏi về lịch trình, điểm check-in, giá vé hoặc món ngon...")
    final_tourist_prompt = quick_prompt if quick_prompt else user_tourist_input

    if final_tourist_prompt or audio_tourist:
        if audio_tourist and not final_tourist_prompt:
            st.session_state.tourist_messages.append({"role": "user", "content": "🎙️ *[Du khách đã hỏi bằng giọng nói]*"})
            with st.chat_message("user"):
                st.markdown("🎙️ *[Du khách đã hỏi bằng giọng nói]*")
        else:
            st.session_state.tourist_messages.append({"role": "user", "content": final_tourist_prompt})
            with st.chat_message("user"):
                st.markdown(final_tourist_prompt)

        try:
            client = genai.Client(api_key=api_key)
            tourist_instruction = (
                f"Bạn là Hướng dẫn viên Du lịch AI thông minh của vùng di sản liên tỉnh Hà Nam - Nam Định - Ninh Bình (tỉnh Ninh Bình mới). "
                f"Khu vực du khách đang quan tâm: {khu_vuc}, chủ đề: {danh_muc}. "
                "Hãy ghi nhớ toàn bộ nội dung cuộc trò chuyện trước đó để trả lời các câu hỏi nối tiếp của du khách một cách chính xác, tự nhiên và hiếu khách. Trình bày rõ ràng bằng các gạch đầu dòng."
            )

            contents_data = tao_lich_su_hoi_thoai(st.session_state.tourist_messages)
            if audio_tourist and not final_tourist_prompt:
                contents_data.append(
                    types.Content(
                        role="user",
                        parts=(
                            types.Part.from_text(text="Hãy nghe câu hỏi tiếng Việt của du khách trong đoạn âm thanh này dựa trên ngữ cảnh cuộc trò chuyện và tư vấn thật nhiệt tình:"),
                            types.Part.from_bytes(data=audio_tourist.getvalue(), mime_type="audio/wav")
                        )
                    )
                )

            reply = None
            for lan_thu in range(4):
                try:
                    response = client.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=contents_data,
                        config=types.GenerateContentConfig(
                            system_instruction=tourist_instruction,
                            temperature=0.5,
                        )
                    )
                    reply = response.text
                    break
                except Exception as err:
                    if "503" in str(err) or "429" in str(err):
                        time.sleep(2)
                        continue
                    raise err

                    if not reply:
                cau_hoi_thuong = str(final_tourist_prompt).lower()
                if "lịch trình" in cau_hoi_thuong or "tam chúc" in cau_hoi_thuong:
                    reply = (
                        "**Gợi ý lịch trình 1 ngày kết nối Tam Chúc (Hà Nam) – Tràng An (Ninh Bình):**\n"
                        "* **07h30 – 10h30:** Tham quan quần thể danh thắng **Tam Chúc** (Đình Tam Chúc, Điện Quan Âm, Điện Pháp Chủ, Chùa Ngọc trên đỉnh núi Thất Tinh).\n"
                        "* **11h00 – 12h30:** Di chuyển sang Ninh Bình, thưởng thức đặc sản **cơm cháy, dê núi Hoa Lư**.\n"
                        "* **13h30 – 16h30:** Khám phá **Quần thể danh thắng Tràng An** bằng thuyền nan (tuyến 3 hang động và hành cung Vũ Lâm).\n"
                        "* **17h00:** Ghé thăm **Phố cổ Hoa Lư** check-in hoàng hôn và mua quà lưu niệm trước khi kết thúc hành trình."
                    )
                elif "đặc sản" in cau_hoi_thuong or "món ăn" in cau_hoi_thuong:
                    reply = (
                        "**Tinh hoa ẩm thực đặc sản vùng di sản Hà Nam – Nam Định – Ninh Bình:**\n"
                        "* **Ninh Bình:** Thịt dê núi tái chanh, cơm cháy ruốc, gỏi cá nhệch Kim Sơn, ốc núi Tam Điệp.\n"
                        "* **Hà Nam:** Cá kho làng Vũ Đại (Nhân Hậu), bánh cuốn Phủ Lý ăn kèm chả nướng, chuối ngự Đại Hoàng.\n"
                        "* **Nam Định:** Phở bò gia truyền Nam Định, bánh xíu páo, nem nắm Giao Thủy, bánh nhãn Hải Hậu."
                    )
                elif "làng nghề" in cau_hoi_thuong or "quà" in cau_hoi_thuong:
                    reply = (
                        "**Quà lưu niệm thủ công mỹ nghệ đặc sắc tại các làng nghề truyền thống:**\n"
                        "* **Làng lụa Nha Xá (Duy Tiên, Hà Nam):** Khăn lụa tơ tằm mềm mại, nhuộm màu tự nhiên từ củ nâu, cánh kiến.\n"
                        "* **Làng gốm Bồ Bát (Yên Mô, Ninh Bình):** Sản phẩm gốm đất sét trắng men ngọc tinh xảo, mang hoa văn cổ thời Lý – Trần.\n"
                        "* **Làng đúc đồng Tống Xá (Ý Yên, Nam Định):** Tượng đồng mini, chuông đồng và đồ mỹ nghệ chạm khắc tinh tế."
                    )
                else:
                    reply = (
                        f"**Thông tin gợi ý dành cho du khách tại {khu_vuc} ({danh_muc}):**\n"
                        "* **Điểm nhấn hành trình:** Kết nối trục tâm linh – sinh thái từ **Tam Chúc** qua **Cố đô Hoa Lư – Tràng An** tới **Đền Trần – Vườn Quốc gia Xuân Thủy**.\n"
                        "* **Lưu ý trải nghiệm:** Du khách nên chọn trang phục lịch sự khi vào khu vực đền chùa, ưu tiên xe điện hoặc thuyền nan để tích lũy thêm **Tín chỉ Xanh** trên ứng dụng."
                    )

            st.session_state.tourist_messages.append({"role": "assistant", "content": reply})
            with st.chat_message("assistant"):
                st.markdown(reply)
        except Exception as e:
            st.error(f"Đã xảy ra lỗi kết nối API: {e}")

# ==========================================
# TAB 1: ĐIỀU PHỐI DU LỊCH XANH + BIỂU ĐỒ
# ==========================================
with tab1:
    st.header("Điều phối Du lịch Xanh Trục Di sản (Tam Chúc - Hoa Lư - Đền Trần)")
    
    data_diem_den = pd.DataFrame({
        "Địa điểm": (
            "Tràng An - Bái Đính (Hoa Lư)", 
            "Khu du lịch Tam Chúc (Kim Bảng)", 
            "Đền Trần - Phủ Dày (Nam Định)", 
            "Đầm Vân Long (Gia Viễn)", 
            "Vườn Quốc gia Xuân Thủy (Giao Thủy)"
        ),
        "Mật độ khách (%)": (95, 80, 75, 30, 25),
        "Trạng thái": ("🔴 Quá tải", "🟠 Đông đúc", "🟠 Đông đúc", "🟢 Rất thoáng", "🟢 Rất thoáng"),
        "Gợi ý điều phối liên vùng": (
            "Nên chuyển hướng sang Đầm Vân Long để trải nghiệm thuyền nan sinh thái.",
            "Nên tham quan vào buổi chiều hoặc kết hợp ghé làng lụa Nha Xá gần đó.",
            "Nên đi khung giờ sáng sớm hoặc chuyển hướng về vùng sinh thái ven biển.",
            "Khu bảo tồn ngập nước yên tĩnh, lý tưởng để đạp xe và ngắm voọc mông trắng.",
            "Rừng ngập mặn Ramsar ít phát thải, thích hợp du lịch sinh thái cộng đồng."
        )
    })
    
    st.subheader("1. Bản đồ nhiệt mật độ khách trên toàn tuyến di sản")
    st.dataframe(data_diem_den, use_container_width=True, hide_index=True)

    st.subheader("📊 Biểu đồ trực quan phân bổ lưu lượng khách (%)")
    chart_data = data_diem_den.set_index("Địa điểm").get("Mật độ khách (%)")
    st.bar_chart(chart_data, color="#2e7d32")
    
    st.subheader("2. Tính toán Lộ trình Xanh & Nhận Tín chỉ")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        diem_chon = st.selectbox("Chọn điểm đến:", data_diem_den.get("Địa điểm"))
    with col2:
        phuong_tien = st.selectbox("Phương tiện di chuyển:", ("Xe đạp", "Đi bộ / Thuyền nan", "Xe điện / Xe buýt liên vùng", "Ô tô cá nhân / Xe máy"))
    with col3:
        khoang_cach = st.number_input("Quãng đường dự kiến (km):", min_value=1, max_value=100, value=10)
        
    if st.button("Phân tích & Xác nhận lộ trình"):
        co2_tiet_kiem = 0.0
        diem_cong = 0
        
        if phuong_tien in ("Xe đạp", "Đi bộ / Thuyền nan"):
            co2_tiet_kiem = round(khoang_cach * 0.15, 2)
            diem_cong += int(khoang_cach * 5)
        elif phuong_tien == "Xe điện / Xe buýt liên vùng":
            co2_tiet_kiem = round(khoang_cach * 0.08, 2)
            diem_cong += int(khoang_cach * 3)
            
        dong_chon = data_diem_den.loc[data_diem_den.get("Địa điểm") == diem_chon]
        trang_thai_diem = str(dong_chon.get("Trạng thái").values)
        
        if "🟢" in trang_thai_diem:
            diem_cong += 25
            loi_khuyen = f"Tuyệt vời! **{diem_chon}** đang rất thoáng. Bạn được thưởng thêm **25 điểm** vì góp phần giãn cách mật độ khách trên trục di sản."
        else:
            loi_khuyen = f"Lưu ý: **{diem_chon}** đang khá đông. Bạn vẫn nhận được điểm phương tiện xanh, nhưng hãy cân nhắc ghé **Đầm Vân Long** hoặc **Vườn Quốc gia Xuân Thủy** để có trải nghiệm xanh trọn vẹn hơn."
            
        st.session_state.green_credits += diem_cong
        
        st.success(f"Kết quả: Bạn giảm được **{co2_tiet_kiem} kg CO2** và nhận được **+{diem_cong} Tín chỉ Xanh**!")
        st.info(loi_khuyen)

# ==========================================

# ==========================================
# TAB 2: NHÂN VẬT LỊCH SỬ (CÓ NHỚ NGỮ CẢNH + GIỌNG NÓI)
# ==========================================
with tab2:
    st.header("Đối thoại cùng Danh nhân Đất Cố đô & Thiên Trường")
    
    col_nv, col_voice = st.columns(2)
    with col_nv:
        nhan_vat = st.selectbox(
            "Chọn danh nhân lịch sử bạn muốn trò chuyện:",
            (
                "Vua Đinh Tiên Hoàng (Đinh Bộ Lĩnh - Hoa Lư)",
                "Hưng Đạo Đại Vương Trần Quốc Tuấn (Phủ Thiên Trường - Nam Định)",
                "Thái hậu Dương Vân Nga (Kinh đô Hoa Lư)",
                "Thiền sư Nguyễn Minh Không (Bái Đính - Tam Chúc)"
            )
        )
    with col_voice:
        st.write("")
        st.write("")
        bat_giong_noi = st.toggle("🔊 Bật giọng đọc AI", value=True)
    
    system_prompts = {
        "Vua Đinh Tiên Hoàng (Đinh Bộ Lĩnh - Hoa Lư)": "Bạn là Vua Đinh Tiên Hoàng (Đinh Bộ Lĩnh), người dẹp loạn 12 sứ quân, lập nên nước Đại Cồ Việt và định đô tại Hoa Lư năm 968. Hãy xưng 'Trẫm' và gọi du khách là 'Khanh' hoặc 'Quý khách phương xa'. Hãy ghi nhớ mạch trò chuyện trước đó với du khách. Giọng điệu uy nghi, hào sảng, hiếu khách.",
        "Hưng Đạo Đại Vương Trần Quốc Tuấn (Phủ Thiên Trường - Nam Định)": "Bạn là Quốc công Tiết chế Hưng Đạo Đại Vương Trần Quốc Tuấn, vị anh hùng dân tộc gắn liền với phủ Thiên Trường (Nam Định) và đền Trần Thương (Hà Nam). Hãy xưng 'Ta' và gọi du khách là 'Quý khách'. Hãy ghi nhớ mạch trò chuyện trước đó với du khách. Giọng điệu đĩnh đạc, anh minh, thấm nhuần hào khí Đông A.",
        "Thái hậu Dương Vân Nga (Kinh đô Hoa Lư)": "Bạn là Thái hậu Dương Vân Nga, người phụ nữ kiệt xuất gắn liền với hai triều đại Đinh - Tiền Lê tại kinh đô Hoa Lư. Hãy xưng 'Ta' và gọi du khách là 'Quý khách'. Hãy ghi nhớ mạch trò chuyện trước đó với du khách. Giọng điệu điềm đạm, sâu sắc, trí tuệ và giàu lòng yêu nước.",
        "Thiền sư Nguyễn Minh Không (Bái Đính - Tam Chúc)": "Bạn là Quốc sư Nguyễn Minh Không (Lý Quốc Sư) thời nhà Lý, người gắn liền với các ngôi cổ tự vùng núi đá vôi từ chùa Bái Đính (Ninh Bình) đến vùng Tam Chúc, Ba Sao (Hà Nam). Hãy xưng 'Bần tăng' và gọi du khách là 'Thí chủ'. Hãy ghi nhớ mạch trò chuyện trước đó với du khách. Giọng điệu từ bi, thanh tịnh."
    }
    
    if st.button("Bắt đầu cuộc trò chuyện mới"):
        st.session_state.messages = list()
        st.rerun()

    for msg in st.session_state.messages:
        with st.chat_message(msg.get("role")):
            st.markdown(msg.get("content"))
            if msg.get("audio") is not None:
                st.audio(msg.get("audio"), format="audio/mp3")

    audio_history = st.audio_input("🎙️ Bấm Micro để trò chuyện trực tiếp bằng giọng nói:", key="mic_history")
    prompt = st.chat_input(f"Hoặc gõ câu hỏi cho {nhan_vat}...")

    if prompt or audio_history:
        if audio_history and not prompt:
            st.session_state.messages.append({"role": "user", "content": "🎙️ *[Du khách đã đặt câu hỏi bằng giọng nói]*"})
            with st.chat_message("user"):
                st.markdown("🎙️ *[Du khách đã đặt câu hỏi bằng giọng nói]*")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

        try:
            client = genai.Client(api_key=api_key)
            
            contents_data = tao_lich_su_hoi_thoai(st.session_state.messages)
            if audio_history and not prompt:
                contents_data.append(
                    types.Content(
                        role="user",
                        parts=(
                            types.Part.from_text(text="Hãy nghe câu hỏi tiếng Việt của du khách trong đoạn ghi âm này dựa trên mạch trò chuyện trước đó và nhập vai trả lời:"),
                            types.Part.from_bytes(data=audio_history.getvalue(), mime_type="audio/wav")
                        )
                    )
                )

            reply = None
            for lan_thu in range(4):
                try:
                    response = client.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=contents_data,
                        config=types.GenerateContentConfig(
                            system_instruction=system_prompts.get(nhan_vat),
                            temperature=0.7,
                        )
                    )
                    reply = response.text
                    break
                except Exception as err:
                    if "503" in str(err) or "429" in str(err):
                        time.sleep(2)
                        continue
                    raise err

                      if not reply:
                if "Đinh Tiên Hoàng" in nhan_vat:
                    reply = "Trẫm chào quý khách phương xa! Năm 968, sau khi dẹp yên loạn 12 sứ quân, Trẫm chọn đất Hoa Lư núi non hiểm trở làm kinh đô nước Đại Cồ Việt. Quý khách hãy dạo bước thăm đền đài và cảm nhận hào khí non sông thuở đầu dựng nước!"
                elif "Trần Quốc Tuấn" in nhan_vat:
                    reply = "Ta chào quý khách đã ghé thăm đất Thiên Trường! Nơi đây từng là hành cung thứ hai của triều Trần, hun đúc nên hào khí Đông A ba lần đánh thắng giặc Nguyên Mông. Mong quý khách giữ mãi lòng tự hào về truyền thống cha ông."
                elif "Dương Vân Nga" in nhan_vat:
                    reply = "Ta hoan nghênh quý khách đến với kinh đô Hoa Lư! Nơi đây lưu giữ dấu ấn chuyển giao lịch sử thiêng liêng giữa hai triều Đinh và Tiền Lê vì vận mệnh bình yên của giang sơn Đại Cồ Việt."
                else:
                    reply = "Bần tăng chào thí chủ! Vùng núi đá vôi Bái Đính – Tam Chúc cảnh sắc thanh tịnh, linh khí hội tụ. Chúc thí chủ có một chuyến hành hương an lạc và nhiều trải nghiệm ý nghĩa."

            
            audio_bytes = None
            if bat_giong_noi:
                clean_text = reply.replace("*", "").replace("#", "")
                tts = gTTS(text=clean_text, lang="vi")
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                fp.seek(0)
                audio_bytes = fp.read()
            
            st.session_state.messages.append({"role": "assistant", "content": reply, "audio": audio_bytes})
            with st.chat_message("assistant"):
                st.markdown(reply)
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/mp3", autoplay=True)
        except Exception as e:
            st.error(f"Đã xảy ra lỗi kết nối API: {e}")

# ==========================================
# TAB 3: BẢN ĐỒ SỐ & ĐỔI QUÀ LÀNG NGHỀ
# ==========================================
with tab3:
    st.header("Bản đồ Số Trục Di sản & Đổi quà Tín chỉ Xanh")
    
    col_map, col_gift = st.columns(2)
    
    with col_map:
        st.subheader("📍 Tọa độ Các Điểm Di sản & Làng nghề")
        st.caption("Bản đồ phân bố các điểm du lịch xanh và làng nghề truyền thống liên vùng.")
        
        du_lieu_ban_do = pd.DataFrame({
            "Địa điểm": (
                "Cố đô Hoa Lư - Tràng An (Ninh Bình)",
                "Khu du lịch Tam Chúc (Hà Nam)",
                "Đền Trần - Phủ Dày (Nam Định)",
                "Đầm Vân Long (Gia Viễn)",
                "Vườn Quốc gia Xuân Thủy (Giao Thủy)",
                "Làng Lụa Nha Xá (Duy Tiên)",
                "Làng Gốm Bồ Bát (Yên Mô)"
            ),
            "lat": (20.2586, 20.5736, 20.4539, 20.3889, 20.2333, 20.6653, 20.1456),
            "lon": (105.9136, 105.8058, 106.1628, 105.8858, 106.5333, 105.9814, 105.9681)
        })
        
        st.map(du_lieu_ban_do, zoom=9)
        st.dataframe(du_lieu_ban_do.get(("Địa điểm",)), use_container_width=True, hide_index=True)

    with col_gift:
        st.subheader("🎁 Đổi Tín chỉ Xanh lấy Quà Làng nghề")
        st.info(f"Số dư hiện tại của bạn: **{st.session_state.green_credits} Tín chỉ Xanh**")
        
        danh_sach_qua = {
            "Voucher giảm 15% Khăn Lụa Nha Xá (Hà Nam)": 40,
            "Móc khóa Gốm Bồ Bát vẽ tay (Ninh Bình)": 60,
            "Vé trải nghiệm Đạp xe xuyên rừng Vân Long": 80,
            "Tượng đồng mini Làng nghề Tống Xá (Nam Định)": 100
        }
        
        qua_chon = st.selectbox("Chọn phần quà hoặc ưu đãi muốn đổi:", tuple(danh_sach_qua.keys()))
        diem_can = danh_sach_qua.get(qua_chon)
        
        st.write(f"Chi phí đổi quà: **{diem_can} điểm**")
        
        if st.button("Xác nhận đổi quà ngay"):
            if st.session_state.green_credits >= diem_can:
                st.session_state.green_credits -= diem_can
                ma_voucher = f"CODOAI-{diem_can}-{len(qua_chon)}"
                st.success(f"Chúc mừng! Bạn đã đổi thành công **{qua_chon}**.")
                st.code(f"MÃ ƯU ĐÃI CỦA BẠN: {ma_voucher}", language="text")
                st.caption("Xuất trình mã này tại quầy lưu niệm làng nghề hoặc cổng soát vé để nhận quà.")
            else:
                diem_thieu = diem_can - st.session_state.green_credits
                st.warning(f"Bạn còn thiếu **{diem_thieu} điểm** nữa. Hãy sang Tab 'Điều phối Du lịch Xanh' để chọn lộ trình xe đạp hoặc thuyền nan tích thêm điểm nhé!")
