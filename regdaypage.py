import streamlit as st
import json
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- 檔案設定 ---
STATUS_FILE = "room_status.json"
MSG_FILE = "messages.json"

# 自動重新整理 (每 3 秒一次)，確保大家看到的都是最新的
st_autorefresh(interval=3000, key="datarefresh")

# --- 初始化功能 ---
def init_files():
    if not os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'w') as f:
            json.dump({"405": False, "406": False, "505": False, "506": False}, f)
    if not os.path.exists(MSG_FILE):
        with open(MSG_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)

def load_data(file):
    with open(file, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(file, data):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

init_files()

# --- 介面開始 ---
st.set_page_config(page_title="宿舍導賞指揮中心", layout="wide")
st.title("🏢 宿舍導賞即時指揮中心")

# 左邊：房間狀態 / 右邊：留言板
col_status, col_chat = st.columns([1, 1])

with col_status:
    st.header("📍 房間參觀狀態")
    current_status = load_data(STATUS_FILE)
    rooms = ["405", "406", "505", "506"]
    
    for room in rooms:
        c1, c2 = st.columns([2, 1])
        is_occupied = current_status[room]
        status_icon = "🔴" if is_occupied else "🟢"
        c1.write(f"### {status_icon} 房間 {room}")
        if c2.button(f"切換", key=f"btn_{room}"):
            current_status[room] = not is_occupied
            save_data(STATUS_FILE, current_status)
            st.rerun()
    st.divider()
    st.write("💡 提示：按一下「切換」即可更新房況")

with col_chat:
    st.header("💬 即時通訊板")
    
    # 留言輸入區
    with st.container():
        user_name = st.text_input("你是誰？ (例如: 101室, 405帶隊員)", placeholder="輸入稱呼...")
        msg_text = st.text_input("想說什麼？", placeholder="輸入訊息...")
        if st.button("發送訊息", use_container_width=True):
            if user_name and msg_text:
                all_msgs = load_data(MSG_FILE)
                new_msg = {
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "user": user_name,
                    "text": msg_text
                }
                all_msgs.insert(0, new_msg)  # 新訊息排在最前面
                save_data(MSG_FILE, all_msgs[:20]) # 只保留最近 20 條訊息
                st.rerun()
            else:
                st.warning("請填寫名字和訊息！")

    # 顯示留言區
    st.write("---")
    messages = load_data(MSG_FILE)
    for m in messages:
        st.markdown(f"**[{m['time']}] {m['user']}**: {m['text']}")