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
    # 預設 5 個房間，狀態改為記錄 { "room_id": {"team": "隊伍名稱", "join_time": "ISO時間字串或None"} }
    default_status = {
        "202": {"team": "", "join_time": None},
        "306": {"team": "", "join_time": None},
        "106": {"team": "", "join_time": None},
        "107": {"team": "", "join_time": None},
        "105": {"team": "", "join_time": None}
    }
    if not os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_status, f, ensure_ascii=False, indent=4)
    else:
        # 確保格式相容，若舊檔沒有的房間可以自動補上
        data = load_data(STATUS_FILE)
        updated = False
        for r in ["202", "306", "106", "107", "105"]:
            if r not in data:
                data[r] = {"team": "", "join_time": None}
                updated = True
        if updated:
            save_data(STATUS_FILE, data)

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

# --- 計算時間差的輔助函式 ---
def get_elapsed_time(join_time_str):
    if not join_time_str:
        return "00:00:00"
    join_dt = datetime.fromisoformat(join_time_str)
    now = datetime.now()
    diff = now - join_dt
    total_seconds = int(diff.total_seconds())
    if total_seconds < 0:
        return "00:00:00"
    
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

# --- 介面開始 ---
st.set_page_config(page_title="宿舍導賞指揮中心", layout="wide")
st.title("🏢 宿舍導賞即時指揮中心")

# 左邊：房間狀態 / 右邊：留言板
col_status, col_chat = st.columns([1, 1])

with col_status:
    st.header("📍 房間參觀狀態與隊伍計時")
    current_status = load_data(STATUS_FILE)
    rooms = ["202", "306", "106", "107", "105"]
    
    for room in rooms:
        room_info = current_status.get(room, {"team": "", "join_time": None})
        current_team = room_info["team"]
        is_occupied = bool(current_team)
        
        status_icon = "🔴" if is_occupied else "🟢"
        
        with st.container(border=True):
            c1, c2 = st.columns([2, 1])
            
            with c1:
                st.write(f"### {status_icon} 房間 {room}")
                if is_occupied:
                    elapsed = get_elapsed_time(room_info["join_time"])
                    st.markdown(f"**當前隊伍：** `{current_team}`")
                    st.markdown(f"⏱️ **已逗留時間：** `{elapsed}`")
                else:
                    st.write("狀態：目前空閒")
            
            with c2:
                st.write("### 隊伍操作")
                team_input = st.text_input("輸入隊伍名稱", key=f"input_{room}", label_visibility="collapsed", placeholder="隊伍名稱...")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("加入", key=f"join_{room}Y"):
                        if team_input.strip():
                            current_status[room] = {
                                "team": team_input.strip(),
                                "join_time": datetime.now().isoformat()
                            }
                            save_data(STATUS_FILE, current_status)
                            st.rerun()
                        else:
                            st.warning("請輸入隊伍名稱！")
                with col_btn2:
                    if st.button("離開", key=f"leave_{room}"):
                        current_status[room] = {
                            "team": "",
                            "join_time": None
                        }
                        save_data(STATUS_FILE, current_status)
                        st.rerun()

    st.divider()
    st.write("💡 提示：輸入隊伍名稱後點擊「加入」即會開始計時，點擊「離開」則會清除紀錄。畫面會每 3 秒自動更新。")

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
