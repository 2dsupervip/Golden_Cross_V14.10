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
    st.markdown("<h1 style='text-align: center; color: #00E5FF; letter-spacing: 2px;'>🤖 THE GOLDEN CROSS (V16)</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #FFD700;'>NEXT-GEN EDITION</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div style='background-color: #1A1C23; padding: 30px; border-radius: 10px; border: 1px solid #00E5FF; box-shadow: 0 4px 15px rgba(0, 229, 255, 0.1);'>", unsafe_allow_html=True)
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
    .neon-text { color: #00E5FF; font-weight: 800; text-align: center; margin-bottom: 0px;}
    .yellow-status { color: #FFD700; font-family: 'Courier New', Courier, monospace; line-height: 1.6; background-color: #1A1C23; padding: 15px; border-radius: 8px; border-left: 4px solid #FFD700; margin-bottom: 20px; font-size: 14px;}
    .blue-status { color: #00E5FF; font-family: 'Courier New', Courier, monospace; line-height: 1.6; background-color: #1A1C23; padding: 15px; border-radius: 8px; border-left: 4px solid #00E5FF; margin-bottom: 20px; font-size: 14px;}
    .cyan-note { color: #00E5FF; font-family: 'Courier New', Courier, monospace; background-color: #1A1C23; padding: 12px; border-radius: 8px; border-left: 4px solid #00E5FF; margin-top: 15px; margin-bottom: 20px; font-size: 14px;}
    .log-card { background-color: #16181D; padding: 10px 15px; border-radius: 5px; margin-bottom: 5px; font-family: 'Courier New', Courier, monospace; font-size: 13px; border: 1px solid #2D3748;}
    .sub-text { color: #A0AEC0; text-align: center; font-size: 14px; margin-bottom: 20px;}
    .premium-box { background-color: #000000; border: 1px solid #FFD700; border-radius: 8px; padding: 20px 10px; text-align: center; margin-bottom: 15px; box-shadow: 0 2px 10px rgba(255, 215, 0, 0.15);}
    .premium-num { font-size: 28px; color: #FFFFFF; font-weight: 900; letter-spacing: 2px; }
    .sec-num-box { font-size: 22px; color: #A0AEC0; font-weight: bold; background: #1A1C23; padding: 8px 18px; border-radius: 8px; border: 1px solid #555; display: inline-block; margin: 5px;}
    .super-box { background: linear-gradient(145deg, #1A1C23, #0B0E14); border: 2px solid #00E5FF; border-radius: 12px; padding: 25px 10px; text-align: center; margin-bottom: 20px; box-shadow: 0 0 20px rgba(0, 229, 255, 0.2);}
    .super-num { font-size: 34px; color: #00E5FF; font-weight: 900; letter-spacing: 3px; background-color: #000; padding: 10px 20px; border-radius: 8px; margin: 0 10px; display: inline-block; border: 1px solid rgba(0,229,255,0.5);}
    .ai-box { background-color: #1A1C23; border-left: 5px solid #00FF88; padding: 15px; border-radius: 8px; margin-bottom: 20px; font-family: 'Courier New', Courier, monospace;}
    .ai-highlight { color: #00FF88; font-weight: bold; font-size: 18px;}
    </style>
""", unsafe_allow_html=True)

# --- ⚙️ Core Engines (Data Logic) ---
def get_d_p_n(num):
    num = int(num) % 10
    n_map = {1:8, 8:1, 3:5, 5:3, 7:0, 0:7, 2:4, 4:2, 6:9, 9:6}
    return [num, (num + 5) % 10, n_map.get(num, num)]

def generate_pairs(group1, group2=None):
    pairs = []
    if group2:
        for a in group1:
            for b in group2: pairs.extend([f"{a}{b}", f"{b}{a}"])
    else:
        for a, b in itertools.permutations(group1, 2): pairs.append(f"{a}{b}")
        for a in group1: pairs.append(f"{a}{a}")
    return list(set(pairs))

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

# --- 🧪 A/B Testing Engine ---
def run_v15_simulation(timeline, test_size=50):
    total_draws = len(timeline)
    test_size = min(test_size, total_draws - 45)
    start_idx = total_draws - test_size
    simulation_records = []
    
    for i in range(start_idx, total_draws):
        hist = timeline[:i]
        actual_draw = timeline[i]
        actual_str = f"{actual_draw[0]}{actual_draw[1]}"
        
        m1_raw = get_mode1_raw_ranks(hist)
        m2_raw = get_mode2_raw_ranks(hist)
        recent_5 = [str(d) for pair in hist[-5:] for d in pair]
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
        
        flat_30 = [str(d) for pair in hist[-30:] for d in pair]
        c_30 = Counter(flat_30)
        coldest_raw = sorted([str(x) for x in range(10)], key=lambda x: c_30.get(x, 0))
        m_cold = [x for x in coldest_raw if x not in super_hot_2][:2]
        
        X_train, y_train = [], []
        
        if ML_AVAILABLE:
            ml_timeline = hist[-300:] if len(hist) > 300 else hist
            for j in range(1, len(ml_timeline)):
                prev = ml_timeline[j-1]
                m1_feat = [int(x) for x in get_mode1_raw_ranks(ml_timeline[:j])[:3]]
                m2_feat = [int(x) for x in get_mode2_raw_ranks(ml_timeline[:j])[:3]]
                X_train.append([prev[0], prev[1]] + m1_feat + m2_feat)
                target = [0]*10
                target[ml_timeline[j][0]] = 1
                target[ml_timeline[j][1]] = 1
                y_train.append(target)
                
            X_train.append([0,0,0,0,0,0,0,0]); y_train.append([1]*10)
            X_train.append([0,0,0,0,0,0,0,0]); y_train.append([0]*10)
            
            rf = RandomForestClassifier(n_estimators=100, max_depth=7, min_samples_split=4, random_state=42)
            rf.fit(X_train, y_train)
            
            curr_prev = hist[-1]
            m1_next_feat = [int(x) for x in m1_raw[:3]]
            m2_next_feat = [int(x) for x in m2_raw[:3]]
            future_probs = rf.predict_proba([[curr_prev[0], curr_prev[1]] + m1_next_feat + m2_next_feat])
            
            digit_probs_future = {}
            for d in range(10):
                digit_probs_future[str(d)] = future_probs[d][0][1] if future_probs[d].shape[1] == 2 else 0.0
            ml_picks = sorted(digit_probs_future.items(), key=lambda x: x[1], reverse=True)[:4]
            ml_top_2 = [ml_picks[0][0], ml_picks[1][0]]
            shadow_ai = [ml_picks[2][0], ml_picks[3][0]] if len(ml_picks) >= 4 else []
        else:
            ml_top_2, shadow_ai, ml_picks = [], [], []

        vip_key = [n for n in ml_top_2 if n in super_hot_2]
        
        if len(vip_key) == 2:
            tier, confidence, adaptive_cost = "Tier 1", 95, 6 + len(shadow_ai) * 2
            hit_status = "Win" if actual_str[0] in super_hot_2 or actual_str[1] in super_hot_2 or actual_str[0] in m_cold or actual_str[1] in m_cold or actual_str[0] in shadow_ai or actual_str[1] in shadow_ai else "Loss"
        elif len(vip_key) == 1:
            tier, confidence, adaptive_cost = "Tier 2", 75, 16
            hit_status = "Win" if (actual_str[0] in super_hot_2 or actual_str[1] in super_hot_2) or (actual_str[0] in m_cold or actual_str[1] in m_cold) else "Loss"
        elif not ml_picks:
            tier, confidence, adaptive_cost = "Tier 3", 30, 12
            hit_status = "Win" if actual_str[0] in m_cold or actual_str[1] in m_cold else "Loss"
        else:
            tier, confidence, adaptive_cost = "Tier 2", 50, 16
            hit_status = "Win" if (actual_str[0] in super_hot_2 or actual_str[1] in super_hot_2) or (actual_str[0] in m_cold or actual_str[1] in m_cold) else "Loss"
            
        simulation_records.append({
            "Match": f"ပွဲ {i+1-start_idx}",
            "Actual Result": actual_str,
            "Confidence Score": f"{confidence}%",
            "Adaptive Tier": tier,
            "Cost (Pairs)": adaptive_cost,
            "Result": hit_status
        })
        
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
                # Requirement 1: Error Handling for "x" using try...except ValueError: pass
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

# --- ⚙️ Telegram Bot Settings (Permanent Storage) ---
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

# --- 📱 Main App UI (V16 Engine) ---
st.markdown("<h1 class='neon-text'>THE GOLDEN CROSS</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-text'>V16 - NEXT-GEN EDITION (AI AUTO LOCK & ADVANCED UI)</p>", unsafe_allow_html=True)

if not ML_AVAILABLE: st.error("⚠️ စနစ်တွင် Machine Learning (scikit-learn) မရှိပါ။")

mode = st.radio("⚙️ Engine Mode", ["🤖 AI Auto Mode", "✍️ Custom Mode"])
custom_lb = 50
if "Custom" in mode: custom_lb = st.number_input("Backtest ပွဲစဉ်:", value=50)

if st.button("🚀 V16 Engine ကို Run မည်", use_container_width=True):
    if len(st.session_state.history) < 50: st.warning("⚠️ Data အနည်းဆုံး ပွဲ ၅၀ လိုအပ်ပါသည်။")
    else:
        st.session_state.run_v16 = True
        st.session_state.selected_mode = mode
        st.session_state.custom_lb = custom_lb

if st.session_state.get('run_v16'):
    hist = st.session_state.history
    target_session = "PM" if hist[-1]['session'] == "AM" else "AM"
    target_timeline = [item['draw'] for item in hist if item['session'] == target_session]
    
    # Requirement 2: AI Auto Mode Customization (TF 10 for AM, TF 40 for PM)
    if "Auto" in st.session_state.selected_mode:
        tf_limit = 10 if target_session == "AM" else 40
        if len(target_timeline) > tf_limit:
            target_timeline = target_timeline[-tf_limit:]
        st.success(f"🕒 **AI Auto Mode Activated:** {target_session} အတွက် Fixed Timeframe ({tf_limit} ပွဲ) ဖြင့် တွက်ချက်နေပါသည်။")
    else:
        st.success(f"🕒 **Custom Mode Activated:** ({target_session}) သမိုင်းကြောင်းအပြည့်ကို အသုံးပြုနေပါသည်။")
    
    # --- 🧠 V16 Engine Prediction Logic ---
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

    ml_picks, ml_top_2, shadow_ai = [], [], []
    if ML_AVAILABLE and len(target_timeline) >= 30:
        ml_timeline = target_timeline[-300:] if len(target_timeline) > 300 else target_timeline
        X_train, y_train = [], []
        for j in range(1, len(ml_timeline)):
            prev = ml_timeline[j-1]
            m1_feat = [int(x) for x in get_mode1_raw_ranks(ml_timeline[:j])[:3]]
            m2_feat = [int(x) for x in get_mode2_raw_ranks(ml_timeline[:j])[:3]]
            X_train.append([prev[0], prev[1]] + m1_feat + m2_feat)
            target = [0]*10
            target[ml_timeline[j][0]] = 1
            target[ml_timeline[j][1]] = 1
            y_train.append(target)
            
        X_train.append([0,0,0,0,0,0,0,0]); y_train.append([1]*10)
        X_train.append([0,0,0,0,0,0,0,0]); y_train.append([0]*10)
        
        rf = RandomForestClassifier(n_estimators=100, max_depth=7, min_samples_split=4, random_state=42)
        rf.fit(X_train, y_train)
        
        curr_prev = target_timeline[-1]
        m1_next_feat = [int(x) for x in m1_raw[:3]]
        m2_next_feat = [int(x) for x in m2_raw[:3]]
        future_probs = rf.predict_proba([[curr_prev[0], curr_prev[1]] + m1_next_feat + m2_next_feat])
        
        digit_probs_future = {}
        for d in range(10):
            digit_probs_future[str(d)] = future_probs[d][0][1] if future_probs[d].shape[1] == 2 else 0.0
        ml_picks = sorted(digit_probs_future.items(), key=lambda x: x[1], reverse=True)[:4]
        ml_top_2 = [ml_picks[0][0], ml_picks[1][0]]
        shadow_ai = [ml_picks[2][0], ml_picks[3][0]] if len(ml_picks) >= 4 else []

    vip_key = [n for n in ml_top_2 if n in super_hot_2]

    base_pairs_1, base_pairs_2 = [], []
    if ml_picks:
        if len(super_hot_2) > 0:
            m1 = super_hot_2[0]
            ai_pool = [x[0] for x in ml_picks if x[0] not in super_hot_2]
            base_pairs_1 = [f"{m1}{m1}"] + [f"{m1}{p}" for p in ai_pool[:4]]
        if len(super_hot_2) > 1:
            m2 = super_hot_2[1]
            base_pairs_2 = [f"{m2}{m2}"] + [f"{m2}{m1}"] + [f"{m2}{p}" for p in ai_pool[:3]]
    else:
        if len(super_hot_2) > 0:
            partners_1 = get_best_partners(super_hot_2[0], target_timeline)
            base_pairs_1 = [f"{super_hot_2[0]}{super_hot_2[0]}"] + [f"{super_hot_2[0]}{p}" for p in partners_1]
        if len(super_hot_2) > 1:
            partners_2 = get_best_partners(super_hot_2[1], target_timeline)
            base_pairs_2 = [f"{super_hot_2[1]}{super_hot_2[1]}"] + [f"{super_hot_2[1]}{p}" for p in partners_2]

    hedge_ai_pool = [x[0] for x in ml_picks if x[0] not in super_hot_2] if ml_picks else []
    hedge_ai_2 = hedge_ai_pool[:2] if len(hedge_ai_pool) >= 2 else hedge_ai_pool
    recovery_4_digits = list(dict.fromkeys(hedge_ai_2 + super_cold_2))
    base_mc_6_pairs = [f"{a}{b}" for a, b in itertools.combinations(recovery_4_digits, 2)]

    final_main_pairs_1, final_main_pairs_2, final_cold_pairs = [], [], []
    tier_title = ""

    if len(vip_key) == 2:
        tier_title = "🔥 Tier 1: Anti-Trap Shield Mode"
        live_confidence = 95
        final_main_pairs_1 = base_pairs_1[:2]
        final_main_pairs_2 = base_pairs_2[:2] if base_pairs_2 else base_pairs_1[2:4]
        trap_pool = list(dict.fromkeys(shadow_ai + super_cold_2))
        final_cold_pairs = list(dict.fromkeys([f"{a}{b}" for a, b in itertools.combinations(trap_pool, 2)] + [f"{c}{c}" for c in trap_pool]))[:6]
    elif len(vip_key) == 1 or len(vip_key) == 0:
        if not ml_picks:
            tier_title = "❄️ Tier 3: Defensive Mode"
            live_confidence = 30
            final_main_pairs_1 = base_pairs_1[:2]
            final_main_pairs_2 = base_pairs_2[:2] if base_pairs_2 else base_pairs_1[2:4]
            deep_cold_focus = list(dict.fromkeys(coldest_raw[:5] + super_cold_2))
            final_cold_pairs = list(dict.fromkeys([f"{a}{b}" for a, b in itertools.combinations(deep_cold_focus, 2)] + [f"{c}{c}" for c in super_cold_2]))[:8]
        else:
            tier_title = "⚖️ Tier 2: Normal Confidence Mode"
            live_confidence = 75 if len(vip_key) == 1 else 50
            final_main_pairs_1 = base_pairs_1
            final_main_pairs_2 = base_pairs_2
            final_cold_pairs = base_mc_6_pairs

    # --- 📑 Render Tabs (Added Performance Dashboard Tab) ---
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Live Prediction", "🔬 V16 Backtest", "📊 System Info", "📈 Performance Dashboard"])
    
    with tab1:
        st.markdown(f"<div style='background-color:#1A1C23; padding:10px; border-radius:8px; border-left:4px solid #FF00FF; margin-bottom:20px; font-family:monospace;'>📊 <b>Engine Status:</b> {tier_title} (Score: {live_confidence}%)</div>", unsafe_allow_html=True)

        st.markdown("<div style='background-color:#16181D; padding:15px; border-radius:10px; margin-bottom:20px; border:1px solid #2D3748;'>", unsafe_allow_html=True)
        col_dt, col_btn = st.columns([1, 2])
        with col_dt:
            selected_date = st.date_input("📅 ရက်စွဲရွေးချယ်ရန်", datetime.now().date())
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True) 
            if st.session_state.tg_token and st.session_state.tg_chat_id:
                if st.button("🚀 Telegram သို့ VIP ဂဏန်းများ ပို့မည်", type="primary", use_container_width=True):
                    formatted_date = selected_date.strftime("%d-%m-%Y")
                    session_mm = "မနက်ပိုင်း" if target_session == "AM" else "ညနေပိုင်း"
                    
                    # Requirement 4: Bold format formatting for Telegram
                    msg_body = f"📅 *ရက်စွဲ:* *{formatted_date}* ({session_mm})\n"
                    msg_body += f"👑 *THE GOLDEN CROSS V16* 👑\n\n"
                    msg_body += f"📊 *Engine Status:* {tier_title}\n\n"
                    
                    if vip_key: 
                        msg_body += f"🤖 *လက်တွက်+AI လုံးဘိုင် :* **{ ' '.join(vip_key) }**\n\n"
                        
                    msg_body += f"🔥 *အဓိက လုံးဘိုင် (Main):* **{ ' | '.join(super_hot_2) }**\n"
                    
                    if final_main_pairs_1: msg_body += f"      **{ ' '.join(final_main_pairs_1) }**\n"
                    if final_main_pairs_2: msg_body += f"      **{ ' '.join(final_main_pairs_2) }**\n"

                    if final_cold_pairs:
                        msg_body += f"\n⚔️ *ရွှေအကွက် (Cold / Recovery):*\n"
                        msg_body += f"      **{ ' '.join(final_cold_pairs) }**\n\n"
                        
                    msg_body += "🚀 အားလုံးပဲ ကံထူးပြီး အောင်ပွဲခံနိုင်ကြပါစေ ခင်ဗျာ! 💰"
                    
                    success = send_telegram_message(st.session_state.tg_token, st.session_state.tg_chat_id, msg_body)
                    if success: st.success(f"✅ Telegram သို့ အောင်မြင်စွာ ပို့ဆောင်ပြီးပါပြီ!")
                    else: st.error("❌ Telegram ပို့ရန် အခက်အခဲရှိနေပါသည်။")
            else:
                st.info("💡 Telegram ဖြင့် Group သို့ Auto Message ပို့ရန် ဘယ်ဘက် Sidebar တွင် Bot Settings ကို အရင်ထည့်ပါ။")
        st.markdown("</div>", unsafe_allow_html=True)

        if ml_picks:
            st.markdown("<div class='ai-box'>🤖 <b>Machine Learning Insights:</b> AI Model မှ နောက်ပွဲအတွက် ကြိုတင်ခန့်မှန်းချက်<br><br>", unsafe_allow_html=True)
            for digit, prob in ml_picks:
                st.markdown(f"<span class='ai-highlight'>[ {digit} ] ➡ {prob*100:.1f}% သေချာပါသည်</span>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        if vip_key:
            st.markdown("<h3 style='text-align:center; color:#00FF88; margin-top:10px;'>👑 ULTRA VIP MASTER KEY</h3>", unsafe_allow_html=True)
            html_sm = "<div class='super-box' style='border-color:#00FF88;'>"
            html_sm += "".join([f"<span class='super-num' style='color:#00FF88; border-color:#00FF88;'>{p}</span>" for p in vip_key])
            html_sm += "</div>"
            st.markdown(html_sm, unsafe_allow_html=True)
            
        st.markdown("<h3 style='text-align:center; color:#FFD700; margin-top:30px;'>👑 ADAPTIVE MASTER CORE (MAIN)</h3>", unsafe_allow_html=True)
        if len(super_hot_2) > 0:
            # Requirement 3: UI Uniformity (Using premium-box and premium-num style like Pattern Matrix)
            html_master_core = "<div class='premium-box' style='border-color:#FFD700; margin-bottom: 20px;'>"
            for lone in super_hot_2:
                html_master_core += f"<span style='margin:0 15px;'><span class='premium-num' style='color:#FFD700; font-size: 32px;'>{lone}</span></span>"
            html_master_core += "</div>"
            st.markdown(html_master_core, unsafe_allow_html=True)
            
            html_partners = "<div class='premium-box'>"
            if final_main_pairs_1: html_partners += "<div style='margin-bottom:15px;'>" + "".join([f"<span style='margin:0 10px;'><span class='premium-num'>{p}</span></span>" for p in final_main_pairs_1]) + "</div>"
            if final_main_pairs_2: html_partners += "<div>" + "".join([f"<span style='margin:0 10px;'><span class='premium-num'>{p}</span></span>" for p in final_main_pairs_2]) + "</div>"
            html_partners += "</div>"
            st.markdown(html_partners, unsafe_allow_html=True)
            
        st.divider()
        
        st.markdown("<h4 style='text-align:center;'>⚔️ ADAPTIVE SHADOW CORE (COLD)</h4>", unsafe_allow_html=True)
        if final_cold_pairs:
            html_mc = f"<div class='premium-box' style='border-color:#00E5FF; margin: 0 auto;'>"
            if len(final_cold_pairs) > 4:
                html_mc += "".join([f"<span style='margin:0 10px;'><span class='premium-num'>{p}</span></span>" for p in final_cold_pairs[:4]]) + "<br><br>"
                html_mc += "".join([f"<span style='margin:0 10px;'><span class='premium-num'>{p}</span></span>" for p in final_cold_pairs[4:]])
            else:
                html_mc += "".join([f"<span style='margin:0 10px;'><span class='premium-num'>{p}</span></span>" for p in final_cold_pairs])
            html_mc += "</div>"
            st.markdown(html_mc, unsafe_allow_html=True)
        
        c_disp_1 = super_cold_2[0] if len(super_cold_2) > 0 else "-"
        c_disp_2 = super_cold_2[1] if len(super_cold_2) > 1 else "-"
        st.markdown(f"<div class='cyan-note'>💡 <b>မှတ်ချက်:</b> အအေးဇုန်မှ ရုတ်တရက် ပြန်လည်ရုန်းထွက်နိုင်ချေ အများဆုံးဖြစ်သော ({target_session} True Deep Cold) လုံးဘိုင်များမှာ <b>[ {c_disp_1} ]</b> နှင့် <b>[ {c_disp_2} ]</b> ဖြစ်ပါသည်။</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown("### 🔬 V16 A/B Testing Simulator")
        if st.button("🚀 Run V16 Diagnostic Simulation", use_container_width=True):
            with st.spinner("Holy Grail Engine ၏ နောက်ကြောင်းပြန် အချက်အလက်များကို ခွဲခြမ်းစိတ်ဖြာနေပါသည်..."):
                test_size_val = st.session_state.custom_lb if "Custom" in st.session_state.selected_mode else len(target_timeline)
                sim_df = run_v15_simulation(target_timeline, test_size_val)
                st.dataframe(sim_df, use_container_width=True)
                wins = len(sim_df[sim_df['Result'] == 'Win'])
                total_played = len(sim_df)
                total_cost = sim_df['Cost (Pairs)'].sum()
                
                col1, col2 = st.columns(2)
                col1.info(f"**V16 Hit Rate**\n\n🎯 Matches Won: {wins} / {total_played} ပွဲ\n📈 Accuracy: {(wins/total_played)*100:.1f}%")
                col2.success(f"**Cost Analysis**\n\n💰 စုစုပေါင်း ရင်းနှီးရသည့်အကွက်: {total_cost} ကွက်\n(Average: {total_cost/total_played:.1f} pairs/draw)")

    with tab3:
        st.markdown("### ⚙️ V16 System Architecture Info")
        st.info("""
        **1. 🚀 Next-Gen Error Handling:** Data Center တွင် Error မတက်အောင် ကာကွယ်မှုအပြည့်။\n
        **2. 🤖 AI Auto Mode Config:** AM တွင် 10 ပွဲစဉ်၊ PM တွင် 40 ပွဲစဉ် Fixed Timeline ဖြင့် ပိုမိုတိကျစွာ ခန့်မှန်းခြင်း။\n
        **3. 💎 Pattern Matrix UI:** မျက်နှာပြင်ပြသမှုကို Premium Layout Style သို့ ပြောင်းလဲထားခြင်း။\n
        **4. 📲 Telegram Enhanced Formatting:** Auto message ပို့ရာတွင် Bold Text Format ဖြင့် VIP ဂဏန်းများကို ပိုမိုထင်ရှားစေခြင်း။\n
        **5. 📈 Performance Tracking:** နောက်ဆုံးအောင်မြင်မှုများအား Dashboard ဖြင့် လွယ်ကူစွာ စောင့်ကြည့်နိုင်ခြင်း။
        """)

    # Requirement 5: Analytics Dashboard (Performance Dashboard with Line Chart)
    with tab4:
        st.markdown("### 📈 Recent Performance (Hit Rates Dashboard)")
        st.markdown("<p style='color:#A0AEC0;'>နောက်ဆုံးပွဲစဉ် ၂၀ ရဲ့ အောင်မြင်မှုရာခိုင်နှုန်း (Hit Rates) အတက်အကျ</p>", unsafe_allow_html=True)
        
        full_timeline = [item['draw'] for item in st.session_state.history if item['session'] == target_session]
        if len(full_timeline) >= 45:
            with st.spinner("Performance Data ဆွဲထုတ်နေပါသည်..."):
                perf_sim = run_v15_simulation(full_timeline, test_size=20)
                if not perf_sim.empty:
                    perf_sim['Is_Win'] = perf_sim['Result'].apply(lambda x: 1 if x == 'Win' else 0)
                    perf_sim['Win_Rate_%'] = perf_sim['Is_Win'].expanding().mean() * 100
                    
                    chart_data = perf_sim[['Match', 'Win_Rate_%']].set_index('Match')
                    st.line_chart(chart_data)
                    st.success(f"📊 လက်ရှိ နောက်ဆုံးတွက်ချက်ထားသည့် Win Rate မှာ **{chart_data.iloc[-1]['Win_Rate_%']:.1f}%** ဖြစ်ပါသည်။")
        else:
            st.info("⚠️ Dashboard ပြသရန် Data အလုံအလောက်မရှိသေးပါ။ (အနည်းဆုံး ပွဲ ၄၅ လိုအပ်ပါသည်)")
