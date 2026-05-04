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
st.set_page_config(page_title="The Golden Cross - Master Edition", page_icon="👑", layout="wide")

# --- 🔒 SECURITY (PASSWORD GATE) ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #00E5FF; letter-spacing: 2px;'>👑 THE GOLDEN CROSS</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #FFD700;'>PURE MATH MASTER EDITION (10-PAIRS STRATEGY)</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='background-color: #1A1C23; padding: 30px; border-radius: 10px; border: 1px solid #FFD700; box-shadow: 0 4px 15px rgba(255, 215, 0, 0.1);'>", unsafe_allow_html=True)
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

# --- 🎨 Main App CSS ---
st.markdown("""
    <style>
    .main { background-color: #0B0E14; }
    .neon-text { color: #FFD700; font-weight: 800; text-align: center; margin-bottom: 0px;}
    .sub-text { color: #A0AEC0; text-align: center; font-size: 14px; margin-bottom: 20px;}
    .premium-box { background-color: #000000; border: 1px solid #FFD700; border-radius: 8px; padding: 20px 10px; text-align: center; margin-bottom: 15px; box-shadow: 0 2px 10px rgba(255, 215, 0, 0.15);}
    .premium-num { font-size: 32px; color: #FFFFFF; font-weight: 900; letter-spacing: 2px; }
    .cold-box { background-color: #000000; border: 1px solid #00E5FF; border-radius: 8px; padding: 20px 10px; text-align: center; margin-bottom: 15px; box-shadow: 0 2px 10px rgba(0, 229, 255, 0.15);}
    .cold-num { font-size: 32px; color: #FFFFFF; font-weight: 900; letter-spacing: 2px; }
    .core-num { font-size: 40px; font-weight: 900; padding: 10px 20px; border-radius: 10px; display: inline-block; margin: 10px;}
    </style>
""", unsafe_allow_html=True)

# --- ⚙️ Core Engines (Pure Math Logic) ---

def get_best_partners(target, hist_tuples, num_partners=4):
    """သမိုင်းကြောင်းအရ အတူတူတွဲထွက်လေ့ရှိဆုံး ဂဏန်းများကို ရှာဖွေခြင်း"""
    target_int = int(target)
    partners = []
    for draw in hist_tuples:
        if draw[0] == target_int: partners.append(draw[1])
        if draw[1] == target_int: partners.append(draw[0])
    c = Counter(partners)
    # အပူးဂဏန်းကို ပယ်ထားမည် (သီးသန့် ထည့်သွင်းမည်ဖြစ်သောကြောင့်)
    sorted_p = [str(k) for k, v in c.most_common() if str(k) != str(target_int)]
    
    # ၄ လုံးမပြည့်ပါက ကျန်သောဂဏန်းများဖြင့် ဖြည့်မည်
    for i in range(10):
        if str(i) not in sorted_p and str(i) != str(target_int):
            sorted_p.append(str(i))
            
    return sorted_p[:num_partners]

def get_hot_cold_cores(timeline):
    """Hot (Top 1) နှင့် Cold (Bottom 1) ကို ရှာဖွေခြင်း"""
    if len(timeline) == 0: return "0", "1"
    
    # Hot Core (နောက်ဆုံး ၁၅ ပွဲအတွင်း အထွက်ဆုံး)
    hot_timeline = timeline[-15:] if len(timeline) > 15 else timeline
    hot_flat = [str(d) for pair in hot_timeline for d in pair]
    hot_counter = Counter(hot_flat)
    
    if hot_counter:
        hot_core = hot_counter.most_common(1)[0][0]
    else:
        hot_core = "0"
        
    # Cold Core (နောက်ဆုံး ၃၀ ပွဲအတွင်း အအေးဆုံး)
    cold_timeline = timeline[-30:] if len(timeline) > 30 else timeline
    cold_flat = [str(d) for pair in cold_timeline for d in pair]
    cold_counter = Counter(cold_flat)
    
    # မထွက်ဖူးသော ဂဏန်းများရှိလျှင် ၎င်းတို့ကို ဦးစားပေးမည်
    all_digits = [str(i) for i in range(10)]
    coldest_sorted = sorted(all_digits, key=lambda x: cold_counter.get(x, 0))
    
    # Hot Core နှင့် မတူသော အအေးဆုံးဂဏန်းကို ရွေးမည်
    cold_core = None
    for digit in coldest_sorted:
        if digit != hot_core:
            cold_core = digit
            break
            
    return hot_core, cold_core

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
            
            # Logic အတိုင်း Hot 1, Cold 1 ရှာမည်
            hot_core, cold_core = get_hot_cold_cores(hist)
            
            # တွဲဖက်များ ရှာမည် (တစ်လုံးလျှင် ၄ ကပ်)
            hot_partners = get_best_partners(hot_core, hist, num_partners=4)
            cold_partners = get_best_partners(cold_core, hist, num_partners=4)
            
            # အကွက်များ တည်ဆောက်မည် (စုစုပေါင်း ၁၀ ကွက်)
            hot_pairs = [f"{hot_core}{hot_core}"] + [f"{hot_core}{p}" for p in hot_partners]
            cold_pairs = [f"{cold_core}{cold_core}"] + [f"{cold_core}{p}" for p in cold_partners]
            all_pairs = list(dict.fromkeys(hot_pairs + cold_pairs)) # Duplicates ပယ်မည် (အကယ်၍ တူနေခဲ့လျှင်)
            
            # Result စစ်ဆေးမည်
            # Order မတူလည်း ရစေရန် (ဥပမာ ထွက်တာ '38', ကိုယ်ပေးတာ '83' ဆိုရင်လည်း Win)
            # 2D သဘာဝအရ R (ပြန်) ထိုးလေ့ရှိသဖြင့်
            actual_rev = f"{actual_draw[1]}{actual_draw[0]}"
            is_win = (actual_str in all_pairs) or (actual_rev in all_pairs)
            
            hit_status = "Win 🟢" if is_win else "Loss 🔴"
            
            simulation_records.append({
                "Match": f"ပွဲ {i+1}",
                "Actual Result": actual_str,
                "Hot Core": hot_core,
                "Cold Core": cold_core,
                "Cost (Pairs)": len(all_pairs),
                "Result": hit_status
            })
            
    if not simulation_records:
        return pd.DataFrame(columns=["Match", "Actual Result", "Hot Core", "Cold Core", "Cost (Pairs)", "Result"])
        
    return pd.DataFrame(simulation_records)

# --- 🌐 API & Telegram Helpers ---
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

def send_telegram_message(token, chat_id, message):
    if not token or not chat_id: return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    try:
        r = requests.post(url, json=payload, timeout=5)
        return r.status_code == 200
    except: return False

# --- 📱 Sidebar (Data Center) ---
st.sidebar.title("Data Center 📥")
uploaded_file = st.sidebar.file_uploader("Excel ဖိုင် တင်ရန်", type=["xlsx"])

if 'history' not in st.session_state: st.session_state.history = []
if 'last_uploaded' not in st.session_state: st.session_state.last_uploaded = None

if uploaded_file is not None:
    file_id = f"{uploaded_file.name}_{uploaded_file.size}"
    if st.session_state.last_uploaded != file_id:
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
                st.session_state.last_uploaded = file_id 
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

if st.sidebar.button("🌐 လတ်တလော 2D Data ဆွဲယူမည်", use_container_width=True):
    fetched_draw = fetch_live_2d()
    if fetched_draw:
        new_sess = "AM" if default_idx == 0 else "PM"
        st.session_state.history.append({'session': new_sess, 'draw': fetched_draw})
        st.sidebar.success(f"✅ အလိုအလျောက် ဆွဲယူပြီးပါပြီ: {fetched_draw[0]}{fetched_draw[1]}")
        st.rerun()
    else:
        st.sidebar.error("❌ Live Data ဆွဲယူ၍ မရပါ။")

with st.sidebar.form("live_entry_form", clear_on_submit=True):
    c1, c2 = st.columns(2)
    new_top = c1.number_input("ထိပ်စီး", min_value=0, max_value=9, step=1, value=0)
    new_bot = c2.number_input("နောက်ပိတ်", min_value=0, max_value=9, step=1, value=0)
    new_session = st.radio("Session", ["AM", "PM"], index=default_idx, horizontal=True)
    submitted = st.form_submit_button("➕ လက်ဖြင့် အသစ်ထည့်မည်", use_container_width=True)
    if submitted:
        st.session_state.history.append({'session': new_session, 'draw': (new_top, new_bot)})
        st.rerun()

if st.sidebar.button("↩️ Undo (ပြန်ဖျက်မည်)"):
    if len(st.session_state.history) > 0:
        st.session_state.history.pop()
        if hasattr(st, "rerun"): st.rerun()
        else: st.experimental_rerun()

# --- ⚙️ Telegram Bot Settings ---
CONFIG_FILE = "telegram_config.json"
if 'tg_token' not in st.session_state or 'tg_chat_id' not in st.session_state:
    st.session_state.tg_token = ""
    st.session_state.tg_chat_id = ""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config_data = json.load(f)
                st.session_state.tg_token = config_data.get("token", "")
                st.session_state.tg_chat_id = config_data.get("chat_id", "")
        except: pass

with st.sidebar.expander("⚙️ Telegram Bot Settings"):
    tg_token_input = st.text_input("Bot Token", value=st.session_state.tg_token, type="password")
    tg_chat_input = st.text_input("Chat ID / Group ID", value=st.session_state.tg_chat_id)
    if st.button("💾 အမြဲတမ်း သိမ်းမည်"):
        st.session_state.tg_token = tg_token_input
        st.session_state.tg_chat_id = tg_chat_input
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump({"token": tg_token_input, "chat_id": tg_chat_input}, f)
            st.success("✅ အမြဲတမ်း သိမ်းဆည်းပြီးပါပြီ။")
        except Exception as e: st.error(f"❌ သိမ်းဆည်းရာတွင် အမှားအယွင်းဖြစ်နေပါသည်: {e}")

# --- 📱 Main App UI ---
st.markdown("<h1 class='neon-text'>THE GOLDEN CROSS</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-text'>PURE MATH MASTER EDITION (10-PAIRS STRATEGY)</p>", unsafe_allow_html=True)

custom_lb = st.number_input("Backtest စမ်းသပ်မည့် ပွဲစဉ်အရေအတွက် (ဥပမာ- 20, 50):", value=50)

if st.button("🚀 Pure Math Engine ကို Run မည်", use_container_width=True):
    if len(st.session_state.history) < 15: 
        st.warning("⚠️ Data အနည်းဆုံး ပွဲ ၁၅ ခန့် လိုအပ်ပါသည်။ Data ထပ်ဖြည့်ပေးပါ။")
    else:
        st.session_state.run_master = True
        st.session_state.custom_lb = custom_lb

if st.session_state.get('run_master'):
    hist = st.session_state.history
    target_session = "PM" if hist[-1]['session'] == "AM" else "AM"
    target_timeline = [item['draw'] for item in hist if item['session'] == target_session]
    
    st.success(f"🕒 **System Activated:** ({target_session}) သမိုင်းကြောင်းအပြည့်ကို အသုံးပြု၍ Pure Math Engine ဖြင့် တွက်ချက်နေပါသည်။")
    
    # --- 🧠 Master Engine Logic ---
    hot_core, cold_core = get_hot_cold_cores(target_timeline)
    
    hot_partners = get_best_partners(hot_core, target_timeline, num_partners=4)
    cold_partners = get_best_partners(cold_core, target_timeline, num_partners=4)
    
    hot_pairs = [f"{hot_core}{hot_core}"] + [f"{hot_core}{p}" for p in hot_partners]
    cold_pairs = [f"{cold_core}{cold_core}"] + [f"{cold_core}{p}" for p in cold_partners]
    
    # --- 📑 Render Tabs ---
    tab1, tab2, tab3 = st.tabs(["🎯 Live Prediction", "🔬 Master Simulator", "📊 Performance Dashboard"])
    
    with tab1:
        st.markdown("<div style='background-color:#16181D; padding:15px; border-radius:10px; margin-bottom:20px; border:1px solid #2D3748;'>", unsafe_allow_html=True)
        col_dt, col_btn = st.columns([1, 2])
        with col_dt:
            selected_date = st.date_input("📅 ရက်စွဲရွေးချယ်ရန်", datetime.now().date())
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True) 
            if st.session_state.tg_token and st.session_state.tg_chat_id:
                if st.button("🚀 Telegram သို့ VIP ၁၀ ကွက် ပို့မည်", type="primary", use_container_width=True):
                    formatted_date = selected_date.strftime("%d-%m-%Y")
                    session_mm = "မနက်ပိုင်း" if target_session == "AM" else "ညနေပိုင်း"
                    
                    msg_body = f"📅 *ရက်စွဲ:* *{formatted_date}* ({session_mm})\n"
                    msg_body += f"👑 *THE GOLDEN CROSS (MASTER EDITION)* 👑\n\n"
                    msg_body += f"🔥 *HOT CORE (အပူ):* **[ {hot_core} ]**\n"
                    msg_body += f"      **{ ' '.join(hot_pairs) }**\n\n"
                    msg_body += f"❄️ *COLD CORE (အအေး):* **[ {cold_core} ]**\n"
                    msg_body += f"      **{ ' '.join(cold_pairs) }**\n\n"
                    msg_body += "🚀 အားလုံးပဲ ကံထူးပြီး အောင်ပွဲခံနိုင်ကြပါစေ ခင်ဗျာ! 💰"
                    
                    success = send_telegram_message(st.session_state.tg_token, st.session_state.tg_chat_id, msg_body)
                    if success: st.success(f"✅ Telegram သို့ အောင်မြင်စွာ ပို့ဆောင်ပြီးပါပြီ!")
                    else: st.error("❌ Telegram ပို့ရန် အခက်အခဲရှိနေပါသည်။")
            else:
                st.info("💡 Telegram ဖြင့် Group သို့ Auto Message ပို့ရန် ဘယ်ဘက် Sidebar တွင် Bot Settings ကို အရင်ထည့်ပါ။")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<h3 style='text-align:center; color:#FFD700; margin-top:10px;'>🔥 HOT CORE (TREND)</h3>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center;'><span class='core-num' style='color:#FFD700; border: 2px solid #FFD700;'>{hot_core}</span></div>", unsafe_allow_html=True)
        html_hot = "<div class='premium-box' style='border-color:#FFD700;'>"
        html_hot += "".join([f"<span style='margin:0 15px;'><span class='premium-num' style='color:#FFD700;'>{p}</span></span>" for p in hot_pairs])
        html_hot += "</div>"
        st.markdown(html_hot, unsafe_allow_html=True)
            
        st.markdown("<h3 style='text-align:center; color:#00E5FF; margin-top:30px;'>❄️ COLD CORE (BREAKOUT)</h3>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align:center;'><span class='core-num' style='color:#00E5FF; border: 2px solid #00E5FF;'>{cold_core}</span></div>", unsafe_allow_html=True)
        html_cold = "<div class='cold-box'>"
        html_cold += "".join([f"<span style='margin:0 15px;'><span class='cold-num'>{p}</span></span>" for p in cold_pairs])
        html_cold += "</div>"
        st.markdown(html_cold, unsafe_allow_html=True)

    with tab2:
        st.markdown("### 🔬 Master Simulator (၁၀ ကွက်စနစ်၏ Backtest ရလဒ်)")
        if st.button("🚀 Run Simulator", use_container_width=True):
            with st.spinner("နောက်ကြောင်းပြန် အချက်အလက်များကို ခွဲခြမ်းစိတ်ဖြာနေပါသည်..."):
                t_val = st.session_state.get('custom_lb', 50)
                sim_df = run_master_simulation(target_timeline, t_val)
                
                if not sim_df.empty and 'Result' in sim_df.columns:
                    st.dataframe(sim_df, use_container_width=True)
                    wins = len(sim_df[sim_df['Result'] == 'Win 🟢'])
                    total_played = len(sim_df)
                    total_cost = sim_df['Cost (Pairs)'].sum()
                    
                    col1, col2 = st.columns(2)
                    col1.info(f"**Performance Metrics**\n\n🎯 Matches Won: {wins} / {total_played} ပွဲ\n📈 Accuracy (Win Rate): {(wins/total_played)*100:.1f}%")
                    col2.success(f"**Cost Analysis**\n\n💰 စုစုပေါင်း ရင်းနှီးရသည့်အကွက်: {total_cost} ကွက်\n(Average: {total_cost/total_played:.1f} pairs/draw)")
                else:
                    st.warning("⚠️ Simulation ပြုလုပ်ရန် Data အလုံအလောက်မရှိသေးပါ။")

    with tab3:
        st.markdown("### 📈 Recent Performance (Hit Rates Dashboard)")
        st.markdown("<p style='color:#A0AEC0;'>၁၀ ကွက်တိတိစနစ်ဖြင့် နောက်ဆုံးပွဲစဉ်များ၏ အောင်မြင်မှုရာခိုင်နှုန်း အတက်အကျ</p>", unsafe_allow_html=True)
        
        full_timeline = [item['draw'] for item in st.session_state.history if item['session'] == target_session]
        if len(full_timeline) >= 15:
            with st.spinner("Performance Data ဆွဲထုတ်နေပါသည်..."):
                perf_sim = run_master_simulation(full_timeline, test_size=20)
                if not perf_sim.empty and 'Result' in perf_sim.columns:
                    perf_sim['Is_Win'] = perf_sim['Result'].apply(lambda x: 1 if x == 'Win 🟢' else 0)
                    perf_sim['Win_Rate_%'] = perf_sim['Is_Win'].expanding().mean() * 100
                    
                    chart_data = perf_sim[['Match', 'Win_Rate_%']].set_index('Match')
                    st.line_chart(chart_data)
                    st.success(f"📊 လက်ရှိ နောက်ဆုံးတွက်ချက်ထားသည့် Win Rate မှာ **{chart_data.iloc[-1]['Win_Rate_%']:.1f}%** ဖြစ်ပါသည်။")
                else:
                    st.warning("⚠️ Dashboard ပြသရန် ခွဲခြမ်းစိတ်ဖြာမှု မအောင်မြင်သေးပါ။")
        else:
            st.info("⚠️ Dashboard ပြသရန် Data အလုံအလောက်မရှိသေးပါ။ (အနည်းဆုံး ပွဲ ၁၅ ပွဲခန့် လိုအပ်ပါသည်)")
