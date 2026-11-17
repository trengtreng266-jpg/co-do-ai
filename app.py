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

# --- THANH BÊN: TRẠNG THÁI HỆ THỐNG & ĐIỂM THƯỞNG ---
with st.sidebar:
    st.title("🏛️ Cố Đô AI")
    st.caption("Hướng dẫn viên Du lịch Thông minh Liên vùng (Hà Nam - Nam Định - Ninh Bình)")
    
    api_key = st.secrets["GEMINI_API_KEY"]
    st.success("✅ Hệ thống AI đã sẵn sàng phục vụ du khách")
    
    st.divider()
    st.metric(label="🌱 Tín chỉ Xanh của bạn", value=f"{st.session_state.green_credits} điểm")
    st.info("Tích lũy điểm khi di chuyển xanh giữa các điểm di sản và đổi quà tại các làng nghề truyền thống (Gốm Bồ Bát, Lụa Nha Xá, Đúc đồng Tống Xá).")

# --- GIAO DIỆN CHÍNH: CHIA 3 TABS DÀNH CHO DU KHÁCH ---
tab0, tab1, tab2 = st.tabs((
    "🗺️ Giới thiệu & Lịch trình Du khách", 
    "🚲 Điều phối Du lịch Xanh", 
    "👑 Trò chuyện với Nhân vật Lịch sử"
))

# ==========================================
# TAB 0: GIỚI THIỆU & CHỈ DẪN DU KHÁCH
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
                "Hãy giới thiệu thật hấp dẫn, hiếu khách, giàu cảm xúc và cung cấp thông tin thực tế hữu ích. Trình bày rõ ràng bằng các gạch đầu dòng."
            )

            if audio_tourist and not final_tourist_prompt:
                contents_data = (
                    "Hãy nghe câu hỏi tiếng Việt của du khách trong đoạn âm thanh này và tư vấn thật nhiệt tình:",
                    types.Part.from_bytes(data=audio_tourist.getvalue(), mime_type="audio/wav")
                )
            else:
                contents_data = final_tourist_prompt

            reply = None
            for ten_model in ("gemini-3.8-flash", "gemini-3.8-flash-lite", "gemini-3.8-flash", "gemini-3.8-flash-lite"):
                try:
                    response = client.models.generate_content(
                        model=ten_model,
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
                        time.sleep(1)
                        continue
                    raise err

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
# TAB 2: NHÂN VẬT LỊCH SỬ (CÓ MICRO NÓI + GIỌNG ĐỌC)
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
        "Vua Đinh Tiên Hoàng (Đinh Bộ Lĩnh - Hoa Lư)": "Bạn là Vua Đinh Tiên Hoàng (Đinh Bộ Lĩnh), người dẹp loạn 12 sứ quân, lập nên nước Đại Cồ Việt và định đô tại Hoa Lư năm 968. Hãy xưng 'Trẫm' và gọi du khách là 'Khanh' hoặc 'Quý khách phương xa'. Giọng điệu uy nghi, hào sảng, hiếu khách, tự hào giới thiệu về non nước Hoa Lư và vùng đất di sản.",
        "Hưng Đạo Đại Vương Trần Quốc Tuấn (Phủ Thiên Trường - Nam Định)": "Bạn là Quốc công Tiết chế Hưng Đạo Đại Vương Trần Quốc Tuấn, vị anh hùng dân tộc gắn liền với phủ Thiên Trường (Nam Định) và đền Trần Thương (Hà Nam). Hãy xưng 'Ta' và gọi du khách là 'Quý khách'. Giọng điệu đĩnh đạc, anh minh, thấm nhuần hào khí Đông A và chào đón du khách đến thăm quê hương.",
        "Thái hậu Dương Vân Nga (Kinh đô Hoa Lư)": "Bạn là Thái hậu Dương Vân Nga, người phụ nữ kiệt xuất gắn liền với hai triều đại Đinh - Tiền Lê tại kinh đô Hoa Lư. Hãy xưng 'Ta' và gọi du khách là 'Quý khách'. Giọng điệu điềm đạm, sâu sắc, trí tuệ và giàu lòng yêu nước.",
        "Thiền sư Nguyễn Minh Không (Bái Đính - Tam Chúc)": "Bạn là Quốc sư Nguyễn Minh Không (Lý Quốc Sư) thời nhà Lý, người gắn liền với các ngôi cổ tự vùng núi đá vôi từ chùa Bái Đính (Ninh Bình) đến vùng Tam Chúc, Ba Sao (Hà Nam). Hãy xưng 'Bần tăng' và gọi du khách là 'Thí chủ'. Giọng điệu từ bi, thanh tịnh, thông tuệ về y học, phật pháp và cảnh sắc non nước."
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
            
            if audio_history and not prompt:
                contents_data = (
                    "Hãy nghe câu hỏi tiếng Việt của du khách trong đoạn ghi âm này và nhập vai trả lời:",
                    types.Part.from_bytes(data=audio_history.getvalue(), mime_type="audio/wav")
                )
            else:
                contents_data = prompt
            reply = None
            for ten_model in ("gemini-3.8-flash", "gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-2.0-flash"):
                try:
                    response = client.models.generate_content(
                        model=ten_model,
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
                        time.sleep(1)
                        continue
                    raise err

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
