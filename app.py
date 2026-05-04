import streamlit as st
import pandas as pd
import itertools
from collections import Counter
import warnings
import requests
from datetime import datetime
import io
import json
import os

# --- 🤖 Machine Learning Integration ---
try:
    from sklearn.ensemble import RandomForestClassifier
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

warnings.filterwarnings('ignore')

# --- 🎨 UI Configuration ---
st.set_page_config(page_title="The Golden Cross AI V16", page_icon="👑", layout="wide")

# --- 🔒 SECURITY (PASSWORD GATE) ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #00FF88; letter-spacing: 2px;'>🤖 THE GOLDEN CROSS (V16)</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #FFD700;'>NEXT-GEN ADAPTIVE EDITION</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='background-color: #1A1C23; padding: 30px; border-radius: 10px; border: 1px solid #00FF88; box-shadow: 0 4px 15px rgba(0, 255, 136, 0.1);'>", unsafe_allow_html=True)
        pwd = st.text_input("🔒 Admin Password ရိုက်ထည့်ပါ", type="password")
        if st.button("🔓 Login (ဝင်မည်)", use_container_width=True):
            if pwd == "GoldenCrossAdmin":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Password မှားယွင်းနေပါသည်။")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop() 

# --- 🎨 Main App CSS ---
st.markdown("""
    <style>
    .main { background-color: #0B0E14; }
    .neon-text { color: #00FF88; font-weight: 800; text-align: center; margin-bottom: 0px;}
    .yellow-status { color: #FFD700; font-family: 'Courier New', Courier, monospace; line-height: 1.6; background-color: #1A1C23; padding: 15px; border-radius: 8px; border-left: 4px solid #FFD700; margin-bottom: 20px; font-size: 14px;}
    .log-card { background-color: #16181D; padding: 10px 15px; border-radius: 5px; margin-bottom: 5px; font-family: 'Courier New', Courier, monospace; font-size: 13px; border: 1px solid #2D3748;}
    .sub-text { color: #A0AEC0; text-align: center; font-size: 14px; margin-bottom: 20px;}
    .premium-box { background-color: #000000; border: 1px solid #FFD700; border-radius: 8px; padding: 20px 10px; text-align: center; margin-bottom: 15px; box-shadow: 0 2px 10px rgba(255, 215, 0, 0.15);}
    .premium-num { font-size: 26px; color: #FFFFFF; font-weight: 900; letter-spacing: 2px; }
    .main-num-box { font-size: 40px; color: #FFD700; font-weight: 900; background: #1A1C23; padding: 15px 30px; border-radius: 10px; border: 2px solid #FFD700; display: inline-block; margin: 10px; box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);}
    .super-box { background: linear-gradient(145deg, #1A1C23, #0B0E14); border: 2px solid #00FF88; border-radius: 12px; padding: 25px 10px; text-align: center; margin-bottom: 20px; box-shadow: 0 0 20px rgba(0, 255, 136, 0.2);}
    .super-num { font-size: 34px; color: #00FF88; font-weight: 900; letter-spacing: 3px; background-color: #000; padding: 10px 20px; border-radius: 8px; margin: 0 10px; display: inline-block; border: 1px solid rgba(0,255,136,0.5);}
    .ai-box { background-color: #1A1C23; border-left: 5px solid #00E5FF; padding: 15px; border-radius: 8px; margin-bottom: 20px; font-family: 'Courier New', Courier, monospace;}
    .ai-highlight { color: #00E5FF; font-weight: bold; font-size: 18px;}
    </style>
""", unsafe_allow_html=True)

# --- ⚙️ Core Engines ---
def get_d_p_n(num):
    num = int(num) % 10
    n_map = {1:8, 8:1, 3:5, 5:3, 7:0, 0:7, 2:4, 4:2, 6:9, 9:6}
    return [num, (num + 5) % 10, n_map.get(num, num)]

def get_mode1_raw_ranks(history):
    curr = len(history)
    scores = {k: 0 for k in range(10)}
    for step in [1, 2, 4]:
        if curr - (3 * step) - 3 >= 0:
            def get_sum_fam(t_idx):
                s = (history[t_idx-1][0] + history[t_idx-2][0] + history[t_idx-3][0]) % 10
                return get_d_p_n(s)
            digits = get_sum_fam(curr) + get_sum_fam(curr-step) + get_sum_fam(curr-2*step) + get_sum_fam(curr-3*step)
            c = Counter(digits)
            sorted_f = sorted(c.keys(), key=lambda x: c[x], reverse=True)
            if len(sorted_f) > 0:
                for k in [k for k,v in c.items() if v == c[sorted_f[0]]]: scores[k] += 2
            if len(sorted_f) > 1:
                for k in [k for k,v in c.items() if v == c[sorted_f[1]]]: scores[k] += 1
    return [str(x[0]) for x in sorted(scores.items(), key=lambda x: x[1], reverse=True)]

def get_mode2_raw_ranks(history):
    scores = {k: 0 for k in range(10)}
    l = len(history)
    for w, weight in [(history[max(0, l-15):l], 3), (history[max(0, l-30):l], 2), (history[max(0, l-45):l], 1)]:
        flat = [str(d) for pair in w for d in pair]
        for k, v in Counter(flat).items(): scores[int(k)] += v * weight
    return [str(x[0]) for x in sorted(scores.items(), key=lambda x: x[1], reverse=True)]

def get_best_partners(target, hist_tuples):
    target_int = int(target)
    partners = []
    for draw in hist_tuples:
        if draw[0] == target_int: partners.append(draw[1])
        if draw[1] == target_int: partners.append(draw[0])
    c = Counter(partners)
    sorted_p = [str(k) for k, v in c.most_common()]
    for i in range(10):
        if str(i) not in sorted_p: sorted_p.append(str(i))
    return sorted_p[:4]

def fetch_live_2d():
    try:
        response = requests.get("https://api.thaistock2d.com/live", timeout=5)
        if response.status_code == 200:
            data = response.json()
            live_twod = data.get("live", {}).get("twod", "")
            if live_twod and len(live_twod) == 2: return (int(live_twod[0]), int(live_twod[1]))
        return None
    except Exception: return None

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
                if 'am1' in df.columns and 'am2' in df.columns and pd.notna(row['am1']):
                    temp_timeline.append({'session': 'AM', 'draw': (int(float(row['am1'])), int(float(row['am2'])))})
                if 'pm1' in df.columns and 'pm2' in df.columns and pd.notna(row['pm1']):
                    temp_timeline.append({'session': 'PM', 'draw': (int(float(row['pm1'])), int(float(row['pm2'])))})
            if temp_timeline: 
                st.session_state.history = temp_timeline
                st.session_state.last_uploaded = file_id 
                st.sidebar.success(f"✅ Data ({len(temp_timeline)}) ပွဲ ဝင်ရောက်ပါပြီ။")
        except Exception as e: st.sidebar.error(f"❌ Error: {e}")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📝 Live Data Entry (V16)")

default_idx = 0
if st.session_state.history:
    last_entry = st.session_state.history[-1]
    st.sidebar.info(f"**နောက်ဆုံးထွက်: [ {last_entry['draw'][0]}{last_entry['draw'][1]} ] ({last_entry['session']})**\nစုစုပေါင်း {len(st.session_state.history)} ပွဲ")
    default_idx = 1 if last_entry['session'] == "AM" else 0

if st.sidebar.button("🌐 လတ်တလော 2D Data ဆွဲယူမည်", use_container_width=True):
    fetched_draw = fetch_live_2d()
    if fetched_draw:
        new_sess = "AM" if default_idx == 0 else "PM"
        st.session_state.history.append({'session': new_sess, 'draw': fetched_draw})
        st.rerun()

with st.sidebar.form("live_entry_form", clear_on_submit=True):
    c1, c2 = st.columns(2)
    new_top = c1.number_input("ထိပ်စီး", min_value=0, max_value=9, step=1, value=0)
    new_bot = c2.number_input("နောက်ပိတ်", min_value=0, max_value=9, step=1, value=0)
    new_session = st.radio("Session", ["AM", "PM"], index=default_idx, horizontal=True)
    if st.form_submit_button("➕ လက်ဖြင့် အသစ်ထည့်မည်", use_container_width=True):
        st.session_state.history.append({'session': new_session, 'draw': (new_top, new_bot)})
        st.rerun()

if st.sidebar.button("↩️ Undo (ပြန်ဖျက်မည်)"):
    if len(st.session_state.history) > 0:
        st.session_state.history.pop()
        st.rerun()

# --- ⚙️ Telegram Settings ---
CONFIG_FILE = "telegram_config.json"
if 'tg_token' not in st.session_state:
    st.session_state.tg_token = ""
    st.session_state.tg_chat_id = ""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                st.session_state.tg_token = data.get("token", "")
                st.session_state.tg_chat_id = data.get("chat_id", "")
        except: pass

with st.sidebar.expander("⚙️ Telegram Bot Settings"):
    tg_tok = st.text_input("Bot Token", value=st.session_state.tg_token, type="password")
    tg_chat = st.text_input("Chat ID", value=st.session_state.tg_chat_id)
    if st.button("💾 သိမ်းမည်"):
        st.session_state.tg_token = tg_tok; st.session_state.tg_chat_id = tg_chat
        with open(CONFIG_FILE, "w") as f: json.dump({"token": tg_tok, "chat_id": tg_chat}, f)
        st.success("Saved!")

# --- 📱 Main App UI ---
st.markdown("<h1 class='neon-text'>THE GOLDEN CROSS</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-text'>V16 - NEXT-GEN ADAPTIVE EDITION (TF-FIXED & MASTER MATRIX UI)</p>", unsafe_allow_html=True)

mode = st.radio("⚙️ Engine Mode", ["🤖 AI Auto Mode (AM=10, PM=40 TF Fixed)", "✍️ Custom Mode"])
custom_lb = 50
if "Custom" in mode: custom_lb = st.number_input("Backtest ပွဲစဉ်:", value=50)

if st.button("🚀 V16 Engine ကို Run မည်", use_container_width=True):
    if len(st.session_state.history) < 50: st.warning("⚠️ Data အနည်းဆုံး ပွဲ ၅၀ လိုအပ်ပါသည်။")
    else:
        st.session_state.run_v16 = True
        st.session_state.selected_mode = mode

if st.session_state.get('run_v16'):
    hist = st.session_state.history
    target_session = "PM" if hist[-1]['session'] == "AM" else "AM"
    full_target_timeline = [item['draw'] for item in hist if item['session'] == target_session]
    
    # 🎯 1. Implement Fixed TF for AI Auto Mode
    if "Auto" in st.session_state.selected_mode:
        fixed_tf = 10 if target_session == "AM" else 40
        st.success(f"🕒 **AI Auto Mode Active:** {target_session} Session အတွက် သတ်မှတ်ထားသော Timeframe ({fixed_tf}) ကို အသုံးပြု၍ တွက်ချက်နေပါသည်။")
        target_timeline = full_target_timeline[-fixed_tf:] if len(full_target_timeline) > fixed_tf else full_target_timeline
    else:
        target_timeline = full_target_timeline[-custom_lb:] if len(full_target_timeline) > custom_lb else full_target_timeline

    # Engine Math Logic
    m1_raw = get_mode1_raw_ranks(target_timeline)
    m2_raw = get_mode2_raw_ranks(target_timeline)
    
    recent_5 = [str(d) for pair in target_timeline[-5:] for d in pair]
    c_recent = Counter(recent_5)
    
    scores = {str(k): 0.0 for k in range(10)}
    m1_m, m1_s = m1_raw[:2], m1_raw[2:5]
    m2_m, m2_s = m2_raw[:2], m2_raw[2:5]
    
    for k in range(10):
        k_str = str(k)
        if k_str in m1_m and k_str in m2_m: scores[k_str] += 4
        elif (k_str in m1_m and k_str in m2_s) or (k_str in m1_s and k_str in m2_m): scores[k_str] += 3
        elif k_str in m1_s and k_str in m2_s: scores[k_str] += 2
        elif k_str in m1_m or k_str in m1_s or k_str in m2_m or k_str in m2_s: scores[k_str] += 1
        scores[k_str] += c_recent.get(k_str, 0) * 0.5
        
    m3_raw = [x[0] for x in sorted(scores.items(), key=lambda x: x[1], reverse=True)]
    super_hot_2 = m3_raw[:2]
    
    flat_30 = [str(d) for pair in target_timeline[-30:] for d in pair]
    c_30 = Counter(flat_30)
    coldest_raw = sorted([str(x) for x in range(10)], key=lambda x: c_30.get(x, 0))
    super_cold_2 = [x for x in coldest_raw if x not in super_hot_2][:2]

    # AI Integration
    ml_picks, ml_top_2, shadow_ai = [], [], []
    if ML_AVAILABLE and len(full_target_timeline) >= 50:
        ml_timeline = full_target_timeline[-300:] if len(full_target_timeline) > 300 else full_target_timeline
        X_train, y_train = [], []
        for j in range(1, len(ml_timeline)):
            prev = ml_timeline[j-1]
            X_train.append([prev[0], prev[1]] + [int(x) for x in get_mode1_raw_ranks(ml_timeline[:j])[:3]] + [int(x) for x in get_mode2_raw_ranks(ml_timeline[:j])[:3]])
            target = [0]*10; target[ml_timeline[j][0]] = 1; target[ml_timeline[j][1]] = 1
            y_train.append(target)
            
        rf = RandomForestClassifier(n_estimators=100, max_depth=7, min_samples_split=4, random_state=42)
        rf.fit(X_train, y_train)
        
        future_probs = rf.predict_proba([[target_timeline[-1][0], target_timeline[-1][1]] + [int(x) for x in m1_raw[:3]] + [int(x) for x in m2_raw[:3]]])
        digit_probs = {str(d): future_probs[d][0][1] if future_probs[d].shape[1] == 2 else 0.0 for d in range(10)}
        ml_picks = sorted(digit_probs.items(), key=lambda x: x[1], reverse=True)[:4]
        ml_top_2 = [ml_picks[0][0], ml_picks[1][0]]

    vip_key = [n for n in ml_top_2 if n in super_hot_2]

    # Pairing
    base_pairs_1, base_pairs_2 = [], []
    if len(super_hot_2) > 0:
        partners_1 = get_best_partners(super_hot_2[0], target_timeline)
        base_pairs_1 = [f"{super_hot_2[0]}{super_hot_2[0]}"] + [f"{super_hot_2[0]}{p}" for p in partners_1]
    if len(super_hot_2) > 1:
        partners_2 = get_best_partners(super_hot_2[1], target_timeline)
        base_pairs_2 = [f"{super_hot_2[1]}{super_hot_2[1]}"] + [f"{super_hot_2[1]}{p}" for p in partners_2]

    tab1, tab2, tab3 = st.tabs(["🎯 Live Prediction & Telegram", "🔬 Pattern Matrix UI", "📊 System Info & Analytics"])
    
    with tab1:
        st.markdown("<div style='background-color:#16181D; padding:15px; border-radius:10px; margin-bottom:20px; border:1px solid #2D3748;'>", unsafe_allow_html=True)
        col_dt, col_btn = st.columns([1, 2])
        with col_dt: selected_date = st.date_input("📅 ရက်စွဲရွေးချယ်ရန်", datetime.now().date())
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True) 
            if st.session_state.tg_token:
                if st.button("🚀 Telegram သို့ VIP ဂဏန်းများ ပို့မည်", type="primary", use_container_width=True):
                    # 🎯 3. Telegram Digits in Bold (**digit**)
                    session_mm = "မနက်ပိုင်း" if target_session == "AM" else "ညနေပိုင်း"
                    msg = f"📅 *ရက်စွဲ:* **{selected_date.strftime('%d-%m-%Y')}** ({session_mm})\n"
                    msg += f"👑 *THE GOLDEN CROSS V16* 👑\n\n"
                    
                    if vip_key: msg += f"🤖 *လက်တွက်+AI လုံးဘိုင်:* **{ ' '.join(vip_key) }**\n\n"
                    msg += f"🔥 *အဓိက လုံးဘိုင်:* **{ ' | '.join(super_hot_2) }**\n"
                    if base_pairs_1: msg += f"      **{ ' '.join(base_pairs_1) }**\n"
                    if base_pairs_2: msg += f"      **{ ' '.join(base_pairs_2) }**\n\n"
                    msg += "🚀 အားလုံးပဲ ကံထူးပြီး အောင်ပွဲခံနိုင်ကြပါစေ ခင်ဗျာ! 💰"
                    
                    if send_telegram_message(st.session_state.tg_token, st.session_state.tg_chat_id, msg): st.success("✅ Telegram ပို့ပြီးပါပြီ!")
                    else: st.error("❌ Telegram ပို့ရာတွင် အမှားရှိနေပါသည်။")
        st.markdown("</div>", unsafe_allow_html=True)

        # 🎯 2. Implement Master Core to match Pattern Matrix style
        st.markdown("<h3 style='text-align:center; color:#FFD700; margin-top:30px;'>👑 MASTER CORE (MAIN PAIRS)</h3>", unsafe_allow_html=True)
        html_master = "<div class='premium-box'>"
        if base_pairs_1:
            html_master += "<div style='margin-bottom:15px;'>" + "".join([f"<span style='margin:0 10px;'><span class='premium-num'>{p}</span></span>" for p in base_pairs_1]) + "</div>"
        if base_pairs_2:
            html_master += "<div>" + "".join([f"<span style='margin:0 10px;'><span class='premium-num'>{p}</span></span>" for p in base_pairs_2]) + "</div>"
        html_master += "</div>"
        st.markdown(html_master, unsafe_allow_html=True)

    with tab2:
        st.markdown("### 🌊 ALL MATRIX PATTERNS (V16 Uniform UI)")
        st.info("💡 Master Core နှင့် Pattern Matrix တို့၏ Display Style ကို တပြေးညီ (Uniform Layout) ပြောင်းလဲသတ်မှတ်ထားပါသည်။")
        
        # Displaying the exact same style for comparison or full pattern
        pm_hot5 = m1_raw[:2] + m1_raw[2:5]
        pm_10_pairs = [f"{a}{b}" for a, b in itertools.combinations(pm_hot5, 2)]
        
        st.markdown("<h4 style='text-align:center; color:#A0AEC0;'>10-PAIR PATTERN MATRIX</h4>", unsafe_allow_html=True)
        html_pm = "<div class='premium-box'>"
        if len(pm_10_pairs) >= 5:
            html_pm += "<div style='margin-bottom:15px;'>" + "".join([f"<span style='margin:0 10px;'><span class='premium-num'>{p}</span></span>" for p in pm_10_pairs[:5]]) + "</div>"
            html_pm += "<div>" + "".join([f"<span style='margin:0 10px;'><span class='premium-num'>{p}</span></span>" for p in pm_10_pairs[5:]]) + "</div>"
        html_pm += "</div>"
        st.markdown(html_pm, unsafe_allow_html=True)

    with tab3:
        st.markdown("### 📊 Performance Dashboard (Analytics)")
        st.markdown("ယခင်ပွဲစဉ်များ၏ အောင်မြင်မှုရာခိုင်နှုန်း (Hit Rates) များကို အလွယ်တကူ စောင့်ကြည့်နိုင်ပါသည်။")
        
        # 🎯 4. Chart Implementation (Mock data based on simple history mapping for visualization)
        # Using streamlit native line_chart to show simulated win patterns over the last 30 draws
        try:
            chart_data = []
            for i in range(10, min(40, len(full_target_timeline))):
                test_hist = full_target_timeline[:i]
                sim_m1 = get_mode1_raw_ranks(test_hist)[:2]
                next_draw = full_target_timeline[i]
                is_hit = 1 if (str(next_draw[0]) in sim_m1 or str(next_draw[1]) in sim_m1) else 0
                chart_data.append(is_hit)
            
            if chart_data:
                # Calculate rolling win rate
                rolling_win_rate = [sum(chart_data[max(0, k-5):k+1]) / len(chart_data[max(0, k-5):k+1]) * 100 for k in range(len(chart_data))]
                df_chart = pd.DataFrame({"Win Rate Trend (%)": rolling_win_rate})
                st.line_chart(df_chart, color="#00FF88")
            else:
                st.info("Chart ပြသရန် Data မလုံလောက်သေးပါ။")
        except:
            st.warning("Dashboard ကိုတွက်ချက်နေစဉ် အမှားအယွင်းရှိခဲ့ပါသည်။")
