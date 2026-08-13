import streamlit as st
import json
import os
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# --- 設定 ---
STATUS_FILE = "room_status.json"
MSG_FILE = "messages.json"
st_autorefresh(interval=3000, key="datarefresh")

def load_data(file):
    if not os.path.exists(file): return {}
    with open(file, 'r', encoding='utf-8') as f: return json.load(f)

def save_data(file, data):
    with open(file, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)

# --- 初始化 (支援多隊伍結構) ---
rooms = ["105", "106", "107", "202", "306", "605"]
current_status = load_data(STATUS_FILE)
for r in rooms:
    if r not in current_status: current_status[r] = [] # 每個房間存一個隊伍列表

# --- 介面 ---
st.set_page_config(page_title="宿舍導賞系統", layout="centered")
st.title("🏢 宿舍導賞控制中心")

# 使用標籤頁提升手機易讀性
tab1, tab2, tab3 = st.tabs(["100-200系", "300-600系", "💬 留言板"])

def render_room(room_id):
    st.subheader(f"📍 房間 {room_id}")
    # 加入隊伍區
    new_team = st.text_input(f"為 {room_id} 新增隊伍", key=f"input_{room_id}")
    if st.button("加入隊伍", key=f"add_{room_id}"):
        if new_team:
            current_status[room_id].append({"team": new_team, "join_time": datetime.now().isoformat()})
            save_data(STATUS_FILE, current_status)
            st.rerun()

    # 顯示隊伍清單
    for idx, t in enumerate(current_status[room_id]):
        elapsed = int((datetime.now() - datetime.fromisoformat(t["join_time"])).total_seconds())
        m, s = divmod(elapsed, 60)
        h, m = divmod(m, 60)
        
        c1, c2 = st.columns([3, 1])
        c1.info(f"隊伍: {t['team']} | ⏱️ {h:02}:{m:02}:{s:02}")
        if c2.button("移除", key=f"del_{room_id}_{idx}"):
            current_status[room_id].pop(idx)
            save_data(STATUS_FILE, current_status)
            st.rerun()

with tab1:
    for r in ["105", "106", "107", "202"]: render_room(r)

with tab2:
    for r in ["306", "605"]: render_room(r)

with tab3:
    st.header("💬 即時通訊")
    # (留言板邏輯保持不變，略過以縮短版面)
    msgs = load_data(MSG_FILE)
    for m in msgs[:10]: st.text(f"{m['user']}: {m['text']}")
