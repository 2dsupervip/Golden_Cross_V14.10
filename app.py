import streamlit as st
import pandas as pd
from collections import Counter
import warnings
import requests
from datetime import datetime
import io
import json
import os

warnings.filterwarnings('ignore')

# --- 🎨 UI Configuration ---
st.set_page_config(page_title="The Golden Cross - 12 Pairs Spread", page_icon="👑", layout="wide")

# --- 🔒 SECURITY ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #00E5FF; letter-spacing: 2px;'>👑 THE GOLDEN CROSS</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #FFD700;'>12-PAIRS SPREAD EDITION (HOT 2 + COLD 2)</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='background-color: #1A1C23; padding: 30px; border-radius: 10px; border: 1px solid #FFD700;'>", unsafe_allow_html=True)
        pwd = st.text_input("🔒 Admin Password ရိုက်ထည့်ပါ", type="password")
        if st.button("🔓 Login (ဝင်မည်)", use_container_width=True):
            if pwd == "GoldenCrossAdmin":
                st.session_state.authenticated = True
                if hasattr(st, "rerun"): st.rerun()
                else: st.experimental_rerun()
            else:
                st.error("❌ Password မှားယွင်းနေပါသည်။")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop() 

# --- 🎨 CSS ---
st.markdown("""
    <style>
    .main { background-color: #0B0E14; }
    .neon-text { color: #FFD700; font-weight: 800; text-align: center; margin-bottom: 0px;}
    .sub-text { color: #A0AEC0; text-align: center; font-size: 14px; margin-bottom: 20px;}
    .premium-box { background-color: #000000; border: 1px solid #FFD700; border-radius: 8px; padding: 15px; text-align: center; margin-bottom: 10px;}
    .premium-num { font-size: 28px; color: #FFFFFF; font-weight: bold; letter-spacing: 2px; }
    .cold-box { background-color: #000000; border: 1px solid #00E5FF; border-radius: 8px; padding: 15px; text-align: center; margin-bottom: 10px;}
    .cold-num { font-size: 28px; color: #FFFFFF; font-weight: bold; letter-spacing: 2px; }
    .core-num { font-size: 32px; font-weight: 900; padding: 8px 15px; border-radius: 8px; display: inline-block; margin: 5px;}
    </style>
""", unsafe_allow_html=True)

# --- ⚙️ Core Engines (12-Pairs Logic) ---

def get_best_partners(target, hist_tuples, num_partners=3):
    target_int = int(target)
    partners = []
    for draw in hist_tuples:
        if draw[0] == target_int: partners.append(draw[1])
        if draw[1] == target_int: partners.append(draw[0])
    c = Counter(partners)
    
    # တွေ့ရာမတွဲဘဲ အကောင်းဆုံး အကပ် ၃ လုံးကို ရှာမည် (အပူး မပါ)
    sorted_p = [str(k) for k, v in c.most_common() if str(k) != str(target_int)]
    
    for i in range(10):
        if str(i) not in sorted_p and str(i) != str(target_int):
            sorted_p.append(str(i))
            
    return sorted_p[:num_partners]

def get_hot_cold_cores(timeline):
    if len(timeline) == 0: return ["0", "1"], ["2", "3"]
    
    # Hot 2 (နောက်ဆုံး ၁၅ ပွဲ)
    hot_timeline = timeline[-15:] if len(timeline) > 15 else timeline
    hot_flat = [str(d) for pair in hot_timeline for d in pair]
    hot_counter = Counter(hot_flat)
    
    hot_cores = []
    for item in hot_counter.most_common(2):
        hot_cores.append(item[0])
    while len(hot_cores) < 2:
        for i in range(10):
            if str(i) not in hot_cores:
                hot_cores.append(str(i))
                break
                
    # Cold 2 (နောက်ဆုံး ၃၀ ပွဲ)
    cold_timeline = timeline[-30:] if len(timeline) > 30 else timeline
    cold_flat = [str(d) for pair in cold_timeline for d in pair]
    cold_counter = Counter(cold_flat)
    
    all_digits = [str(i) for i in range(10)]
    coldest_sorted = sorted(all_digits, key=lambda x: cold_counter.get(x, 0))
    
    cold_cores = []
    for digit in coldest_sorted:
        if digit not in hot_cores:
            cold_cores.append(digit)
        if len(cold_cores) == 2: break
            
    return hot_cores, cold_cores

# --- 🧪 Backtesting Simulator ---
def run_master_simulation(timeline, test_size=50):
    total_draws = len(timeline)
    start_idx = max(5, total_draws - test_size) 
    simulation_records = []
    
    if total_draws > 5:
        for i in range(start_idx, total_draws):
            hist = timeline[:i]
            actual_draw = timeline[i]
            actual_str = f"{actual_draw[0]}{actual_draw[1]}"
            
            # Hot 2, Cold 2 ရှာမည်
            hot_cores, cold_cores = get_hot_cold_cores(hist)
            
            all_pairs = []
            
            # Hot ကို အကပ် ၃ လုံးစီတွဲမည်
            for hc in hot_cores:
                partners = get_best_partners(hc, hist, num_partners=3)
                all_pairs.extend([f"{hc}{p}" for p in partners])
                
            # Cold ကို အကပ် ၃ လုံးစီတွဲမည်
            for cc in cold_cores:
                partners = get_best_partners(cc, hist, num_partners=3)
                all_pairs.extend([f"{cc}{p}" for p in partners])
                
            all_pairs = list(dict.fromkeys(all_pairs)) # Duplicates ပယ်မည် (အများဆုံး ၁၂ ကွက်)
            
            actual_rev = f"{actual_draw[1]}{actual_draw[0]}"
            is_win = (actual_str in all_pairs) or (actual_rev in all_pairs)
            
            hit_status = "Win 🟢" if is_win else "Loss 🔴"
            
            simulation_records.append({
                "Match": f"ပွဲ {i+1}",
                "Actual Result": actual_str,
                "Pairs Generated": len(all_pairs),
                "Result": hit_status
            })
            
    if not simulation_records:
        return pd.DataFrame(columns=["Match", "Actual Result", "Pairs Generated", "Result"])
        
    return pd.DataFrame(simulation_records)

# --- 🌐 API Helpers ---
def fetch_live_2d():
    try:
        response = requests.get("https://api.thaistock2d.com/live", timeout=5)
        if response.status_code == 200:
            data = response.json()
            live_twod = data.get("live", {}).get("twod", "")
            if live_twod and len(live_twod) == 2:
                return (int(live_twod[0]), int(live_twod[1]))
    except: pass
    return None

# --- 📱 Sidebar (Data Center) ---
st.sidebar.title("Data Center 📥")
uploaded_file = st.sidebar.file_uploader("Excel ဖိုင် တင်ရန်", type=["xlsx"])

if 'history' not in st.session_state: st.session_state.history = []

if uploaded_file is not None:
    try:
        df = pd.read_excel(uploaded_file, engine='openpyxl')
        df.columns = df.columns.str.strip().str.lower()
        temp_timeline = []
        for _, row in df.iterrows():
            if 'am1' in df.columns and 'am2' in df.columns:
                if pd.notna(row['am1']) and pd.notna(row['am2']):
                    try: temp_timeline.append({'session': 'AM', 'draw': (int(float(str(row['am1']))), int(float(str(row['am2']))))})
                    except ValueError: pass 
            if 'pm1' in df.columns and 'pm2' in df.columns:
                if pd.notna(row['pm1']) and pd.notna(row['pm2']):
                    try: temp_timeline.append({'session': 'PM', 'draw': (int(float(str(row['pm1']))), int(float(str(row['pm2']))))})
                    except ValueError: pass 
        if temp_timeline: 
            st.session_state.history = temp_timeline
            st.sidebar.success(f"✅ Data ({len(temp_timeline)}) ပွဲ ဝင်ရောက်ပါပြီ။")
    except Exception as e: st.sidebar.error(f"❌ Error: {e}")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📝 Live Data Entry")

if st.session_state.history:
    last_entry = st.session_state.history[-1]
    last_draw = last_entry['draw']
    last_session = last_entry['session']
    st.sidebar.info(f"**နောက်ဆုံးထွက်: [ {last_draw[0]}{last_draw[1]} ] ({last_session})**\nစုစုပေါင်း {len(st.session_state.history)} ပွဲ")
    default_idx = 1 if last_session == "AM" else 0
else:
    default_idx = 0

with st.sidebar.form("live_entry_form", clear_on_submit=True):
    c1, c2 = st.columns(2)
    new_top = c1.number_input("ထိပ်စီး", min_value=0, max_value=9, step=1, value=0)
    new_bot = c2.number_input("နောက်ပိတ်", min_value=0, max_value=9, step=1, value=0)
    new_session = st.radio("Session", ["AM", "PM"], index=default_idx, horizontal=True)
    submitted = st.form_submit_button("➕ လက်ဖြင့် အသစ်ထည့်မည်", use_container_width=True)
    if submitted:
        st.session_state.history.append({'session': new_session, 'draw': (new_top, new_bot)})
        st.rerun()

# --- 📱 Main App UI ---
st.markdown("<h1 class='neon-text'>THE GOLDEN CROSS</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-text'>12-PAIRS SPREAD EDITION (HOT 2 + COLD 2)</p>", unsafe_allow_html=True)

custom_lb = st.number_input("Backtest စမ်းသပ်မည့် ပွဲစဉ်အရေအတွက် (ဥပမာ- 100):", value=100)

if st.button("🚀 Engine ကို Run မည်", use_container_width=True):
    if len(st.session_state.history) < 15: 
        st.warning("⚠️ Data အနည်းဆုံး ပွဲ ၁၅ ခန့် လိုအပ်ပါသည်။ Data ထပ်ဖြည့်ပေးပါ။")
    else:
        st.session_state.run_master = True
        st.session_state.custom_lb = custom_lb

if st.session_state.get('run_master'):
    hist = st.session_state.history
    target_session = "PM" if hist[-1]['session'] == "AM" else "AM"
    target_timeline = [item['draw'] for item in hist if item['session'] == target_session]
    
    # --- 🧠 Engine Logic ---
    hot_cores, cold_cores = get_hot_cold_cores(target_timeline)
    
    hot_pairs_dict = {}
    for hc in hot_cores:
        partners = get_best_partners(hc, target_timeline, num_partners=3)
        hot_pairs_dict[hc] = [f"{hc}{p}" for p in partners]
        
    cold_pairs_dict = {}
    for cc in cold_cores:
        partners = get_best_partners(cc, target_timeline, num_partners=3)
        cold_pairs_dict[cc] = [f"{cc}{p}" for p in partners]
    
    # --- 📑 Render Tabs ---
    tab1, tab2 = st.tabs(["🎯 Live Prediction", "🔬 Profit / Loss Backtest (ROI)"])
    
    with tab1:
        st.markdown("<h3 style='text-align:center; color:#FFD700; margin-top:10px;'>🔥 HOT CORES (အပူ ၂ လုံး)</h3>", unsafe_allow_html=True)
        for hc in hot_cores:
            st.markdown(f"<div style='text-align:center;'><span class='core-num' style='color:#FFD700; border: 1px solid #FFD700;'>{hc}</span></div>", unsafe_allow_html=True)
            html_hot = "<div class='premium-box' style='border-color:#FFD700;'>"
            html_hot += "".join([f"<span style='margin:0 15px;'><span class='premium-num' style='color:#FFD700;'>{p}</span></span>" for p in hot_pairs_dict[hc]])
            html_hot += "</div>"
            st.markdown(html_hot, unsafe_allow_html=True)
            
        st.markdown("<h3 style='text-align:center; color:#00E5FF; margin-top:30px;'>❄️ COLD CORES (အအေး ၂ လုံး)</h3>", unsafe_allow_html=True)
        for cc in cold_cores:
            st.markdown(f"<div style='text-align:center;'><span class='core-num' style='color:#00E5FF; border: 1px solid #00E5FF;'>{cc}</span></div>", unsafe_allow_html=True)
            html_cold = "<div class='cold-box'>"
            html_cold += "".join([f"<span style='margin:0 15px;'><span class='cold-num'>{p}</span></span>" for p in cold_pairs_dict[cc]])
            html_cold += "</div>"
            st.markdown(html_cold, unsafe_allow_html=True)

    with tab2:
        st.markdown("### 🔬 Profit & Loss Simulator (ငွေကြေးတွက်ချက်မှု)")
        if st.button("🚀 Run Simulator", use_container_width=True):
            with st.spinner("အမြတ်/အရှုံး တွက်ချက်နေပါသည်..."):
                t_val = st.session_state.get('custom_lb', 100)
                sim_df = run_master_simulation(target_timeline, t_val)
                
                if not sim_df.empty and 'Result' in sim_df.columns:
                    st.dataframe(sim_df, use_container_width=True)
                    wins = len(sim_df[sim_df['Result'] == 'Win 🟢'])
                    total_played = len(sim_df)
                    total_cost = sim_df['Pairs Generated'].sum()
                    
                    # --- ငွေကြေး တွက်ချက်မှု (၁ ကွက် ၁ ယူနစ်နှုန်းဖြင့်) ---
                    # ဥပမာ - ၁ ကွက် ၁၀၀၀ ဖိုး (၁ ယူနစ်) ၊ ပေါက်လျှင် အဆ ၈၀ (၈၀ ယူနစ်)
                    payout_multiplier = 80 
                    total_return = wins * payout_multiplier
                    net_profit = total_return - total_cost
                    
                    col1, col2 = st.columns(2)
                    col1.info(f"**Performance Metrics**\n\n🎯 Matches Won: {wins} / {total_played} ပွဲ\n📈 Win Rate: {(wins/total_played)*100:.1f}%")
                    
                    if net_profit > 0:
                        col2.success(f"**Financial ROI (၁ ကွက် ၁၀၀၀ ဖိုး ထိုးပါက)**\n\n💰 စုစုပေါင်း ရင်းနှီးငွေ: {total_cost} ထောင်ကျပ်\n💸 ပြန်ရငွေ: {total_return} ထောင်ကျပ်\n🟩 **အသားတင် အမြတ်: +{net_profit} ထောင်ကျပ်**")
                    else:
                        col2.error(f"**Financial ROI (၁ ကွက် ၁၀၀၀ ဖိုး ထိုးပါက)**\n\n💰 စုစုပေါင်း ရင်းနှီးငွေ: {total_cost} ထောင်ကျပ်\n💸 ပြန်ရငွေ: {total_return} ထောင်ကျပ်\n🟥 **အရှုံး: {net_profit} ထောင်ကျပ်**")
                else:
                    st.warning("⚠️ Simulation ပြုလုပ်ရန် Data အလုံအလောက်မရှိသေးပါ။")
