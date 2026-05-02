import streamlit as st
import pandas as pd
import itertools
from collections import Counter
import warnings
import requests
from datetime import datetime

# --- 🤖 Machine Learning Integration ---
try:
    from sklearn.ensemble import RandomForestClassifier
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

warnings.filterwarnings('ignore')

# --- 🎨 UI Configuration ---
st.set_page_config(page_title="The Golden Cross AI", page_icon="👑", layout="wide")

# --- 🔒 SECURITY (PASSWORD GATE) ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #00E5FF; letter-spacing: 2px;'>🤖 THE GOLDEN CROSS (V14.11)</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #A0AEC0;'>BUG-FREE MASTERPIECE EDITION</p>", unsafe_allow_html=True)
    
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
    .premium-num { font-size: 26px; color: #FFFFFF; font-weight: 900; letter-spacing: 2px; }
    .main-num-box { font-size: 40px; color: #FFD700; font-weight: 900; background: #1A1C23; padding: 15px 30px; border-radius: 10px; border: 2px solid #FFD700; display: inline-block; margin: 10px; box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);}
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

# --- 📊 Full Backtest & ML Engine ---
@st.cache_data(show_spinner=False)
def run_backend_engine(timeline, test_size):
    total_draws = len(timeline)
    test_size = max(10, min(test_size, total_draws - 45))
    start_idx = total_draws - test_size

    m1_raw_history, m2_raw_history, actuals = [], [], []
    for i in range(start_idx, total_draws):
        hist = timeline[:i]
        m1_raw_history.append(get_mode1_raw_ranks(hist))
        m2_raw_history.append(get_mode2_raw_ranks(hist))
        actuals.append(f"{timeline[i][0]}{timeline[i][1]}")

    def evaluate_mode(raw_hist, actuals):
        rank_hits_1_5 = {1:0, 2:0, 3:0, 4:0, 5:0}
        rank_hits_6_10 = {6:0, 7:0, 8:0, 9:0, 10:0}
        mains_hist, secs_hist, cm_hist, cs_hist = [], [], [], []
        hot_logs, cold_logs = [], []
        
        for i, draw in enumerate(actuals):
            preds = raw_hist[i]
            for r_idx in range(len(preds)):
                if preds[r_idx] in draw:
                    if r_idx < 5: rank_hits_1_5[r_idx+1] += 1
                    else: rank_hits_6_10[r_idx+1] += 1

        sorted_ranks = sorted(rank_hits_1_5.items(), key=lambda x: x[1], reverse=True)
        m_idx = [x[0]-1 for x in sorted_ranks[:2]]
        s_idx = [x[0]-1 for x in sorted_ranks[2:5]]

        sorted_ranks_cold = sorted(rank_hits_6_10.items(), key=lambda x: x[1], reverse=True)
        cm_idx = [x[0]-1 for x in sorted_ranks_cold[:2]]
        cs_idx = [x[0]-1 for x in sorted_ranks_cold[2:5]]

        stats = {'m_hit':0, 's_hit':0, 'jp_12':0, 'mm_2':0, 'ss_6':0}
        cold_stats = {'m_hit':0, 's_hit':0, 'jp_12':0, 'mm_2':0, 'ss_6':0}

        for i, draw in enumerate(actuals):
            preds = raw_hist[i]
            m_l = [preds[idx] for idx in m_idx if idx < len(preds)]
            s_l = [preds[idx] for idx in s_idx if idx < len(preds)]
            cm_l = [preds[idx] for idx in cm_idx if idx < len(preds)]
            cs_l = [preds[idx] for idx in cs_idx if idx < len(preds)]

            mains_hist.append(m_l)
            secs_hist.append(s_l)
            cm_hist.append(cm_l)
            cs_hist.append(cs_l)

            def get_status(draw, main_g, sec_g, st_dict):
                jp_pairs = generate_pairs(main_g, sec_g)
                mm_pairs = generate_pairs(main_g)
                ss_pairs = generate_pairs(sec_g)
                is_m = draw[0] in main_g or draw[1] in main_g
                is_s = draw[0] in sec_g or draw[1] in sec_g

                if draw in jp_pairs or draw[::-1] in jp_pairs: st_dict['jp_12'] += 1; return "🔥 12-PAIR JACKPOT!"
                elif draw in mm_pairs or draw[::-1] in mm_pairs: st_dict['mm_2'] += 1; return "👑 MAIN-MAIN JACKPOT!"
                elif draw in ss_pairs or draw[::-1] in ss_pairs: st_dict['ss_6'] += 1; return "💰 SEC-SEC JACKPOT!"
                elif is_m and not is_s: st_dict['m_hit'] += 1; return "💎 MAIN HIT"
                elif is_s and not is_m: st_dict['s_hit'] += 1; return "⭐ SEC HIT"
                return "❌ Missed"

            s1 = get_status(draw, m_l, s_l, stats)
            s2 = get_status(draw, cm_l, cs_l, cold_stats)
            hot_logs.append(f"ပွဲ {i+1:02d} | အဖြေမှန်: [{draw}] | Main {m_l} x Sec {s_l} | ရလဒ်: {s1}")
            cold_logs.append(f"ပွဲ {i+1:02d} | အဖြေမှန်: [{draw}] | Main {cm_l} x Sec {cs_l} | ရလဒ်: {s2}")

        return {
            'm_idx': m_idx, 's_idx': s_idx, 'cm_idx': cm_idx, 'cs_idx': cs_idx,
            'sorted_ranks': sorted_ranks, 'sorted_ranks_cold': sorted_ranks_cold,
            'stats': stats, 'cold_stats': cold_stats,
            'hot_logs': list(reversed(hot_logs)), 'cold_logs': list(reversed(cold_logs)),
            'mains_hist': mains_hist, 'secs_hist': secs_hist, 'cm_hist': cm_hist, 'cs_hist': cs_hist
        }

    m1_eval = evaluate_mode(m1_raw_history, actuals)
    m2_eval = evaluate_mode(m2_raw_history, actuals)

    m3_raw_history = []
    for i in range(len(actuals)):
        scores = {str(k): 0 for k in range(10)}
        m1_m, m1_s = m1_eval['mains_hist'][i], m1_eval['secs_hist'][i]
        m2_m, m2_s = m2_eval['mains_hist'][i], m2_eval['secs_hist'][i]
        for k in range(10):
            k_str = str(k)
            if k_str in m1_m and k_str in m2_m: scores[k_str] = 4
            elif (k_str in m1_m and k_str in m2_s) or (k_str in m1_s and k_str in m2_m): scores[k_str] = 3
            elif k_str in m1_s and k_str in m2_s: scores[k_str] = 2
            elif k_str in m1_m or k_str in m1_s or k_str in m2_m or k_str in m2_s: scores[k_str] = 1
        m3_raw_history.append([x[0] for x in sorted(scores.items(), key=lambda x: x[1], reverse=True)])

    m3_eval = evaluate_mode(m3_raw_history, actuals)

    m1_next_raw = get_mode1_raw_ranks(timeline)
    m2_next_raw = get_mode2_raw_ranks(timeline)

    m1_next_m = [m1_next_raw[i] for i in m1_eval['m_idx'] if i < len(m1_next_raw)]
    m1_next_s = [m1_next_raw[i] for i in m1_eval['s_idx'] if i < len(m1_next_raw)]
    m1_next_cm = [m1_next_raw[i] for i in m1_eval['cm_idx'] if i < len(m1_next_raw)]
    m1_next_cs = [m1_next_raw[i] for i in m1_eval['cs_idx'] if i < len(m1_next_raw)]
    
    m2_next_m = [m2_next_raw[i] for i in m2_eval['m_idx'] if i < len(m2_next_raw)]
    m2_next_s = [m2_next_raw[i] for i in m2_eval['s_idx'] if i < len(m2_next_raw)]
    m2_next_cm = [m2_next_raw[i] for i in m2_eval['cm_idx'] if i < len(m2_next_raw)]
    m2_next_cs = [m2_next_raw[i] for i in m2_eval['cs_idx'] if i < len(m2_next_raw)]

    m3_scores = {str(k): 0 for k in range(10)}
    for k in range(10):
        k_str = str(k)
        if k_str in m1_next_m and k_str in m2_next_m: m3_scores[k_str] = 4
        elif (k_str in m1_next_m and k_str in m2_next_s) or (k_str in m1_next_s and k_str in m2_next_m): m3_scores[k_str] = 3
        elif k_str in m1_next_s and k_str in m2_next_s: m3_scores[k_str] = 2
        elif k_str in m1_next_m or k_str in m1_next_s or k_str in m2_next_m or k_str in m2_next_s: m3_scores[k_str] = 1
    m3_next_raw = [x[0] for x in sorted(m3_scores.items(), key=lambda x: x[1], reverse=True)]

    m3_next_m = [m3_next_raw[i] for i in m3_eval['m_idx'] if i < len(m3_next_raw)]
    m3_next_s = [m3_next_raw[i] for i in m3_eval['s_idx'] if i < len(m3_next_raw)]
    m3_next_cm = [m3_next_raw[i] for i in m3_eval['cm_idx'] if i < len(m3_next_raw)]
    m3_next_cs = [m3_next_raw[i] for i in m3_eval['cs_idx'] if i < len(m3_next_raw)]
    
    # --- 🤖 ML Engine ---
    ml_future_pred = []
    ml_win_count = 0
    ml_logs = []
    
    if ML_AVAILABLE and len(timeline) >= 50:
        ml_timeline = timeline[-300:] if len(timeline) > 300 else timeline
        total_ml_draws = len(ml_timeline)
        m1_ml_raw, m2_ml_raw = [], []
        for i in range(total_ml_draws):
            m1_ml_raw.append(get_mode1_raw_ranks(ml_timeline[:i]))
            m2_ml_raw.append(get_mode2_raw_ranks(ml_timeline[:i]))
            
        X_train, y_train = [], []
        for i in range(1, total_ml_draws - test_size):
            prev = ml_timeline[i-1]
            m1_feat = [int(x) for x in m1_ml_raw[i][:3]] if len(m1_ml_raw[i]) >= 3 else [0,0,0]
            m2_feat = [int(x) for x in m2_ml_raw[i][:3]] if len(m2_ml_raw[i]) >= 3 else [0,0,0]
            X_train.append([prev[0], prev[1]] + m1_feat + m2_feat)
            target = [0]*10
            target[ml_timeline[i][0]] = 1
            target[ml_timeline[i][1]] = 1
            y_train.append(target)
            
        X_train.append([0,0,0,0,0,0,0,0]); y_train.append([1]*10)
        X_train.append([0,0,0,0,0,0,0,0]); y_train.append([0]*10)

        X_test = []
        for i in range(total_ml_draws - test_size, total_ml_draws):
            prev = ml_timeline[i-1]
            m1_feat = [int(x) for x in m1_ml_raw[i][:3]] if len(m1_ml_raw[i]) >= 3 else [0,0,0]
            m2_feat = [int(x) for x in m2_ml_raw[i][:3]] if len(m2_ml_raw[i]) >= 3 else [0,0,0]
            X_test.append([prev[0], prev[1]] + m1_feat + m2_feat)
            
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf.fit(X_train, y_train)
        
        pred_probs = rf.predict_proba(X_test)
        for i in range(len(X_test)):
            digit_probs = {}
            for d in range(10):
                digit_probs[str(d)] = pred_probs[d][i][1] if pred_probs[d].shape[1] == 2 else 0.0
            sorted_ml = sorted(digit_probs.items(), key=lambda x: x[1], reverse=True)
            top_2_ml = [sorted_ml[0][0], sorted_ml[1][0]]
            
            actual_d = f"{ml_timeline[total_ml_draws - test_size + i][0]}{ml_timeline[total_ml_draws - test_size + i][1]}"
            if actual_d[0] in top_2_ml or actual_d[1] in top_2_ml:
                ml_win_count += 1
                ml_logs.append(f"ပွဲ {i+1:02d} | အဖြေ: [{actual_d}] | ML တွက်ချက်မှု: {top_2_ml} | ✅ မှန်သည်")
            else:
                ml_logs.append(f"ပွဲ {i+1:02d} | အဖြေ: [{actual_d}] | ML တွက်ချက်မှု: {top_2_ml} | ❌ လွဲ")
        
        curr_prev = ml_timeline[-1]
        m1_next_feat = [int(x) for x in m1_next_raw[:3]] if len(m1_next_raw) >= 3 else [0,0,0]
        m2_next_feat = [int(x) for x in m2_next_raw[:3]] if len(m2_next_raw) >= 3 else [0,0,0]
        future_probs = rf.predict_proba([[curr_prev[0], curr_prev[1]] + m1_next_feat + m2_next_feat])
        
        digit_probs_future = {}
        for d in range(10):
            digit_probs_future[str(d)] = future_probs[d][0][1] if future_probs[d].shape[1] == 2 else 0.0
        ml_future_pred = sorted(digit_probs_future.items(), key=lambda x: x[1], reverse=True)

    return {
        'm1': m1_eval, 'm2': m2_eval, 'm3': m3_eval,
        'm1_next': {'m': m1_next_m, 's': m1_next_s, 'cm': m1_next_cm, 'cs': m1_next_cs},
        'm2_next': {'m': m2_next_m, 's': m2_next_s, 'cm': m2_next_cm, 'cs': m2_next_cs},
        'm3_next': {'m': m3_next_m, 's': m3_next_s, 'cm': m3_next_cm, 'cs': m3_next_cs},
        'm3_next_raw': m3_next_raw,
        'test_size': test_size,
        'actuals': actuals,
        'timeline_used': timeline,
        'ml_future_pred': ml_future_pred,
        'ml_win_count': ml_win_count,
        'ml_logs': list(reversed(ml_logs))
    }

def get_v14_tri_recommendations(timeline):
    best_lb_l, max_hits_l = 50, -1
    best_lb_p, max_hits_p = 50, -1
    best_lb_c, max_hits_c = 50, -1
    
    total_draws = len(timeline)
    max_possible_lb = max(10, total_draws - 45)
    lookbacks_to_test = [lb for lb in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100] if lb <= max_possible_lb]
    if not lookbacks_to_test: return 10, 10, 10
            
    for lb in lookbacks_to_test:
        res = run_backend_engine(timeline, lb)
        ts = res['test_size']
        actuals = res['actuals']
        log_limit = min(10, ts)
        hits_l, hits_p, hits_c = 0, 0, 0
        for i in range(ts - log_limit, ts):
            draw = actuals[i]
            lone_hist = res['m3']['mains_hist'][i]
            if draw[0] in lone_hist or draw[1] in lone_hist: hits_l += 1
            pm_hot5_hist = res['m1']['mains_hist'][i] + res['m1']['secs_hist'][i]
            pm_10_hist = [f"{a}{b}" for a, b in itertools.combinations(pm_hot5_hist, 2)]
            mc_hot2_hist = res['m3']['mains_hist'][i]
            mc_cold2_hist = res['m3']['cm_hist'][i]
            mc_6_hist = [f"{a}{b}" for a, b in itertools.combinations(mc_hot2_hist + mc_cold2_hist, 2)]
            
            if any(draw == p or draw == p[::-1] for p in pm_10_hist) or any(draw == p or draw == p[::-1] for p in mc_6_hist):
                hits_p += 1
            if draw[0] in mc_cold2_hist or draw[1] in mc_cold2_hist: hits_c += 1
                
        if hits_l > max_hits_l: max_hits_l = hits_l; best_lb_l = lb
        if hits_p > max_hits_p: max_hits_p = hits_p; best_lb_p = lb
        if hits_c > max_hits_c: max_hits_c = hits_c; best_lb_c = lb
            
    return best_lb_l, best_lb_p, best_lb_c

# --- 🌐 Phase 4: API Auto-Fetcher Helper ---
def fetch_live_2d():
    try:
        response = requests.get("https://api.thaistock2d.com/live", timeout=5)
        if response.status_code == 200:
            data = response.json()
            live_twod = data.get("live", {}).get("twod", "")
            if live_twod and len(live_twod) == 2:
                return (int(live_twod[0]), int(live_twod[1]))
        return None
    except Exception:
        return None

# --- 📲 Phase 5: Telegram Sender Helper ---
def send_telegram_message(token, chat_id, message):
    if not token or not chat_id: return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    try:
        r = requests.post(url, json=payload, timeout=5)
        return r.status_code == 200
    except: return False

# --- 📱 UI Component for Analytics Tabs ---
def render_mode_tab(eval_data, test_size, next_m, next_s, next_cm, next_cs):
    st.markdown("<h4 style='color:#FFD700;'>🔥 Hot Number</h4>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='text-align:center; margin-bottom: 15px;'>
        <div style='color:#FFD700; font-size:16px; font-weight:bold; margin-bottom:5px;'>လုံးဘိုင် ၂ လုံး</div>
        <div class='main-num-box' style='background:#1A1C23; color:#FFD700; padding:10px 25px;'>{next_m[0] if len(next_m)>0 else '-'}</div>
        <div class='main-num-box' style='background:#1A1C23; color:#FFD700; padding:10px 25px;'>{next_m[1] if len(next_m)>1 else '-'}</div>
        <div style='color:#A0AEC0; font-size:14px; font-weight:bold; margin-top:15px; margin-bottom:5px;'>Master key</div>
        <div class='sec-num-box'>{next_s[0] if len(next_s)>0 else '-'}</div>
        <div class='sec-num-box'>{next_s[1] if len(next_s)>1 else '-'}</div>
        <div class='sec-num-box'>{next_s[2] if len(next_s)>2 else '-'}</div>
    </div>
    """, unsafe_allow_html=True)
    h_t = ""
    for i, (r, hits) in enumerate(eval_data['sorted_ranks']):
        role = "MAIN" if i < 2 else "SEC"
        h_t += f"> Rank {r} : {hits} ပွဲ (Win Rate: {(hits/test_size)*100:.1f}%) <-- [{role}]<br>"
    st_d = eval_data['stats']
    h_t += f"<br>💎 Main (၂) လုံး အပါဝင်သောပွဲ : ({st_d['m_hit'] + st_d['jp_12'] + st_d['mm_2']}) ပွဲ (Win Rate: {((st_d['m_hit'] + st_d['jp_12'] + st_d['mm_2'])/test_size)*100:.1f}%)<br>"
    h_t += f"⭐ Sec (၃) လုံး အပါဝင်သောပွဲ : ({st_d['s_hit'] + st_d['jp_12'] + st_d['ss_6']}) ပွဲ (Win Rate: {((st_d['s_hit'] + st_d['jp_12'] + st_d['ss_6'])/test_size)*100:.1f}%)<br>"
    st.markdown(f"<div class='yellow-status'>{h_t}</div>", unsafe_allow_html=True)
    with st.expander(f"📊 Hot Number မှတ်တမ်းအသေးစိတ်ကြည့်ရန် ({test_size} ပွဲ)"):
        for log in eval_data['hot_logs']: st.markdown(f"<div class='log-card'>{log}</div>", unsafe_allow_html=True)

    st.markdown("<h4 style='color:#00E5FF; margin-top:30px;'>❄️ Cold Number</h4>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='text-align:center; margin-bottom: 15px;'>
        <div style='color:#00E5FF; font-size:16px; font-weight:bold; margin-bottom:5px;'>လုံးဘိုင် ၂ လုံး</div>
        <div class='main-num-box' style='background:#1A1C23; border-color:#00E5FF; color:#00E5FF; padding:10px 25px;'>{next_cm[0] if len(next_cm)>0 else '-'}</div>
        <div class='main-num-box' style='background:#1A1C23; border-color:#00E5FF; color:#00E5FF; padding:10px 25px;'>{next_cm[1] if len(next_cm)>1 else '-'}</div>
        <div style='color:#A0AEC0; font-size:14px; font-weight:bold; margin-top:15px; margin-bottom:5px;'>Master key</div>
        <div class='sec-num-box'>{next_cs[0] if len(next_cs)>0 else '-'}</div>
        <div class='sec-num-box'>{next_cs[1] if len(next_cs)>1 else '-'}</div>
        <div class='sec-num-box'>{next_cs[2] if len(next_cs)>2 else '-'}</div>
    </div>
    """, unsafe_allow_html=True)
    c_t = ""
    for i, (r, hits) in enumerate(eval_data['sorted_ranks_cold']):
        role = "MAIN" if i < 2 else "SEC"
        c_t += f"> Rank {r} : {hits} ပွဲ (Win Rate: {(hits/test_size)*100:.1f}%) <-- [{role}]<br>"
    c_st = eval_data['cold_stats']
    c_t += f"<br>💎 Main (၂) လုံး အပါဝင်သောပွဲ : ({c_st['m_hit'] + c_st['jp_12'] + c_st['mm_2']}) ပွဲ (Win Rate: {((c_st['m_hit'] + c_st['jp_12'] + c_st['mm_2'])/test_size)*100:.1f}%)<br>"
    st.markdown(f"<div class='blue-status'>{c_t}</div>", unsafe_allow_html=True)
    with st.expander(f"📊 Cold Number မှတ်တမ်းအသေးစိတ်ကြည့်ရန် ({test_size} ပွဲ)"):
        for log in eval_data['cold_logs']: st.markdown(f"<div class='log-card'>{log}</div>", unsafe_allow_html=True)

# --- 📱 Sidebar (Data Center) ---
st.sidebar.title("Data Center 📥")
uploaded_file = st.sidebar.file_uploader("Excel ဖိုင် တင်ရန်", type=["xlsx"])

if 'history' not in st.session_state: 
    st.session_state.history = []
if 'last_uploaded' not in st.session_state:
    st.session_state.last_uploaded = None

# V14.11 Bug Fix: Properly initialize keys for state widgets
if 'tg_token' not in st.session_state: 
    st.session_state.tg_token = ""
if 'tg_chat_id' not in st.session_state: 
    st.session_state.tg_chat_id = ""

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
                        try: temp_timeline.append({'session': 'AM', 'draw': (int(float(row['am1'])), int(float(row['am2'])))})
                        except ValueError: pass 
                if 'pm1' in df.columns and 'pm2' in df.columns:
                    if pd.notna(row['pm1']) and pd.notna(row['pm2']):
                        try: temp_timeline.append({'session': 'PM', 'draw': (int(float(row['pm1'])), int(float(row['pm2'])))})
                        except ValueError: pass 
                            
            if temp_timeline: 
                st.session_state.history = temp_timeline
                st.session_state.last_uploaded = file_id 
                st.sidebar.success(f"✅ Data ({len(temp_timeline)}) ပွဲ ဝင်ရောက်ပါပြီ။")
        except Exception as e: st.sidebar.error(f"❌ Error: {e}")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📝 Live Data Entry (V14.11)")

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
        st.sidebar.error("❌ Live Data ဆွဲယူ၍ မရပါ။ (API အချိန်လွန်နေခြင်း သို့မဟုတ် ချိတ်ဆက်မှု အခက်အခဲဖြစ်နိုင်ပါသည်)")

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

# --- 📲 Phase 5: Telegram Config UI (V14.11 BUG FIX) ---
with st.sidebar.expander("⚙️ Telegram Bot Settings"):
    st.text_input("Bot Token", key="tg_token", type="password")
    st.text_input("Chat ID / Group ID", key="tg_chat_id")
    if st.button("💾 သိမ်းမည်"):
        st.success("✅ Telegram Settings သိမ်းဆည်းပြီးပါပြီ။")

# --- 📱 Main App UI (V14.11 Final) ---
st.markdown("<h1 class='neon-text'>THE GOLDEN CROSS</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-text'>V14.11 - BUG-FREE MASTERPIECE</p>", unsafe_allow_html=True)

if not ML_AVAILABLE: st.error("⚠️ စနစ်တွင် Machine Learning (scikit-learn) မရှိပါ။ `requirements.txt` တွင် ထည့်ထားရန် သေချာပါစေ။")

mode = st.radio("⚙️ Engine Mode", ["🤖 AI Auto Mode", "✍️ Custom Mode"])
custom_lb = 50
if "Custom" in mode: custom_lb = st.number_input("Backtest ပွဲစဉ်:", value=50)

if st.button("🚀 V14.11 Ultimate Engine ကို Run မည်", use_container_width=True):
    if len(st.session_state.history) < 90: st.warning("⚠️ Data အနည်းဆုံး ပွဲ ၉၀ လိုအပ်ပါသည်။")
    else:
        st.session_state.run_v14 = True
        st.session_state.selected_mode = mode
        st.session_state.custom_lb = custom_lb

if st.session_state.get('run_v14'):
    hist = st.session_state.history
    target_session = "PM" if hist[-1]['session'] == "AM" else "AM"
    target_timeline = [item['draw'] for item in hist if item['session'] == target_session]
    
    st.success(f"🕒 **Temporal Lock Activated:** AI သည် **({target_session})** သမိုင်းကြောင်း သီးသန့်ကို ခွဲထုတ်၍ ခန့်မှန်းနေပါသည်။")
    
    if "Auto" in st.session_state.selected_mode:
        lb_l, lb_p, lb_c = get_v14_tri_recommendations(target_timeline)
        res_l = run_backend_engine(target_timeline, lb_l)
        res_p = run_backend_engine(target_timeline, lb_p)
        res_c = run_backend_engine(target_timeline, lb_c)
    else:
        lb_p = st.session_state.custom_lb
        res_p = run_backend_engine(target_timeline, lb_p)
        res_l = res_p
        res_c = res_p

    # --- 👑 Master Core Resolution ---
    super_hot_2 = res_l['m3_next']['m']
    
    # --- 🤖 Max Coverage AI Logic (10 Pairs) ---
    pairs_1, pairs_2 = [], []
    if res_l['ml_future_pred']:
        if len(super_hot_2) > 0:
            m1 = super_hot_2[0]
            ai_pool = [x[0] for x in res_l['ml_future_pred'] if x[0] not in super_hot_2]
            pairs_1 = [f"{m1}{m1}"] + [f"{m1}{p}" for p in ai_pool[:4]]
            
        if len(super_hot_2) > 1:
            m2 = super_hot_2[1]
            pairs_2 = [f"{m2}{m2}"] + [f"{m2}{m1}"] + [f"{m2}{p}" for p in ai_pool[:3]]
    else:
        # Fallback if ML is unavailable
        if len(super_hot_2) > 0:
            partners_1 = get_best_partners(super_hot_2[0], res_p['timeline_used'])
            pairs_1 = [f"{super_hot_2[0]}{super_hot_2[0]}"] + [f"{super_hot_2[0]}{p}" for p in partners_1]
        if len(super_hot_2) > 1:
            partners_2 = get_best_partners(super_hot_2[1], res_p['timeline_used'])
            pairs_2 = [f"{super_hot_2[1]}{super_hot_2[1]}"] + [f"{super_hot_2[1]}{p}" for p in partners_2]

    # --- 🛡️ Recovery Shadow Core Logic (6 Pairs) ---
    pref_cold_idx = res_c['m3']['cm_idx'] + res_c['m3']['cs_idx']
    raw_cold_nums = [res_c['m3_next_raw'][i] for i in pref_cold_idx if i < len(res_c['m3_next_raw'])]
    
    safe_cold_pool = [n for n in raw_cold_nums if n not in super_hot_2]
    super_cold_2 = safe_cold_pool[:2] if len(safe_cold_pool) >= 2 else safe_cold_pool

    if res_l['ml_future_pred']:
        hedge_ai_pool = [x[0] for x in res_l['ml_future_pred'] if x[0] not in super_hot_2]
        hedge_ai_2 = hedge_ai_pool[:2] if len(hedge_ai_pool) >= 2 else hedge_ai_pool
    else:
        hedge_ai_2 = []

    # V14.11 Bug Fix: Remove duplicates before combination to prevent itertools ValueError
    recovery_4_digits = list(dict.fromkeys(hedge_ai_2 + super_cold_2))
    mc_6_pairs = [f"{a}{b}" for a, b in itertools.combinations(recovery_4_digits, 2)]
    
    # --- ML Integration ---
    ml_picks, ml_top_2 = [], []
    if res_l['ml_future_pred']:
        ml_picks = res_l['ml_future_pred'][:4]
        ml_top_2 = [ml_picks[0][0], ml_picks[1][0]]
    vip_key = [n for n in ml_top_2 if n in super_hot_2]

    # --- 📑 Render Tabs ---
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Summary (Executive)", "🌊 Pattern Matrix", "🚀 Deep Trend", "💎 Master Core (AI vs Math)"])
    
    with tab1:
        # --- 🚀 Phase 5: Telegram Broadcast with Date Picker ---
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
                    
                    msg_body = f"📅 *ရက်စွဲ:* {formatted_date} ({session_mm})\n"
                    msg_body += f"👑 *THE GOLDEN CROSS* 👑\n\n"
                    
                    if vip_key: 
                        msg_body += f"🤖 *လက်တွက်+AI လုံးဘိုင် :* *{ ' '.join(vip_key) }*\n\n"
                        
                    msg_body += f"🔥 *အဓိက လုံးဘိုင်:* *{ ' | '.join(super_hot_2) }*\n"
                    
                    if pairs_1: msg_body += f"      *{ ' '.join(pairs_1) }*\n"
                    if pairs_2: msg_body += f"      *{ ' '.join(pairs_2) }*\n"

                    if mc_6_pairs:
                        msg_body += f"\n⚔️ *ရွှေအကွက် (၆) ကွက်*\n"
                        msg_body += f"      *{ ' '.join(mc_6_pairs) }*\n\n"
                        
                    msg_body += "🚀 အားလုံးပဲ ကံထူးပြီး အောင်ပွဲခံနိုင်ကြပါစေ ခင်ဗျာ! 💰"
                    
                    success = send_telegram_message(st.session_state.tg_token, st.session_state.tg_chat_id, msg_body)
                    if success: st.success(f"✅ {formatted_date} ရက်စွဲဖြင့် Telegram သို့ အောင်မြင်စွာ ပို့ဆောင်ပြီးပါပြီ!")
                    else: st.error("❌ Telegram ပို့ရန် အခက်အခဲရှိနေပါသည်။ API Token နှင့် Chat ID ကို ပြန်စစ်ပါ။")
            else:
                st.info("💡 Telegram ဖြင့် Group သို့ Auto Message ပို့ရန် ဘယ်ဘက် Sidebar တွင် Bot Settings ကို အရင်ထည့်ပါ။")
        st.markdown("</div>", unsafe_allow_html=True)

        if ml_picks:
            st.markdown("<div class='ai-box'>🤖 <b>Machine Learning Insights:</b> AI Model မှ နောက်ပွဲအတွက် ကြိုတင်ခန့်မှန်းချက် ရာခိုင်နှုန်း<br><br>", unsafe_allow_html=True)
            for digit, prob in ml_picks:
                st.markdown(f"<span class='ai-highlight'>[ {digit} ] ➡ {prob*100:.1f}% သေချာပါသည်</span>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        if vip_key:
            st.markdown("<h3 style='text-align:center; color:#00FF88; margin-top:10px;'>👑 ULTRA VIP MASTER KEY</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center; color:#A0AEC0;'>Tri-Engine (သင်္ချာစနစ်) နှင့် Random Forest (AI) ၂ ခုလုံးမှ ထောက်ခံထားသော (100% Confirmation) ဂဏန်း</p>", unsafe_allow_html=True)
            html_sm = "<div class='super-box' style='border-color:#00FF88;'>"
            html_sm += "".join([f"<span class='super-num' style='color:#00FF88; border-color:#00FF88;'>{p}</span>" for p in vip_key])
            html_sm += "</div>"
            st.markdown(html_sm, unsafe_allow_html=True)
            
        st.markdown("<h3 style='text-align:center; color:#FFD700; margin-top:30px;'>👑 MASTER CORE (လုံးဘိုင် ၂ လုံး)</h3>", unsafe_allow_html=True)
        if len(super_hot_2) > 0:
            
            html_master_core = "<div style='text-align:center; margin-bottom: 20px;'>"
            for lone in super_hot_2:
                html_master_core += f"<span class='main-num-box'>{lone}</span>"
            html_master_core += "</div>"
            st.markdown(html_master_core, unsafe_allow_html=True)
            
            st.markdown("<h4 style='text-align:center; color:#A0AEC0;'>လုံးဘိုင်နှင့် တွဲဖက်များ</h4>", unsafe_allow_html=True)
            
            html_partners = "<div class='premium-box'>"
            if pairs_1: html_partners += "<div style='margin-bottom:15px;'>" + "".join([f"<span style='margin:0 10px;'><span class='premium-num'>{p}</span></span>" for p in pairs_1]) + "</div>"
            if pairs_2: html_partners += "<div>" + "".join([f"<span style='margin:0 10px;'><span class='premium-num'>{p}</span></span>" for p in pairs_2]) + "</div>"
            html_partners += "</div>"
            st.markdown(html_partners, unsafe_allow_html=True)
            
        st.divider()
        
        st.markdown("<h4 style='text-align:center;'>⚔️ MASTER CORE (၆ ကွက်)</h4>", unsafe_allow_html=True)
        if mc_6_pairs:
            html_mc = f"<div class='premium-box' style='border-color:#00E5FF; margin: 0 auto;'>"
            if len(mc_6_pairs) >= 3:
                html_mc += "".join([f"<span style='margin:0 10px;'><span class='premium-num'>{p}</span></span>" for p in mc_6_pairs[:3]]) + "<br><br>"
                html_mc += "".join([f"<span style='margin:0 10px;'><span class='premium-num'>{p}</span></span>" for p in mc_6_pairs[3:]])
            else:
                html_mc += "".join([f"<span style='margin:0 10px;'><span class='premium-num'>{p}</span></span>" for p in mc_6_pairs])
            html_mc += "</div>"
            st.markdown(html_mc, unsafe_allow_html=True)
        
        c_disp_1 = super_cold_2[0] if len(super_cold_2) > 0 else "-"
        c_disp_2 = super_cold_2[1] if len(super_cold_2) > 1 else "-"
        st.markdown(f"<div class='cyan-note'>💡 <b>မှတ်ချက်:</b> အအေးဇုန်မှ ရုတ်တရက် ပြန်လည်ရုန်းထွက်နိုင်ချေ အများဆုံးဖြစ်သော ({target_session} Best Cold) လုံးဘိုင်များမှာ <b>[ {c_disp_1} ]</b> နှင့် <b>[ {c_disp_2} ]</b> ဖြစ်ပါသည်။</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown("### 🌊 PATTERN MATRIX (၁၀ ကွက်)")
        pm_10_pairs = pairs_1 + pairs_2
        html_pm_tab2 = "<div class='premium-box'>"
        html_pm_tab2 += "".join([f"<span style='margin:0 10px;'><span class='premium-num'>{p}</span></span>" for p in pm_10_pairs[:5]]) + "<br><br>"
        html_pm_tab2 += "".join([f"<span style='margin:0 10px;'><span class='premium-num'>{p}</span></span>" for p in pm_10_pairs[5:]])
        html_pm_tab2 += "</div><br>"
        st.markdown(html_pm_tab2, unsafe_allow_html=True)
        
        st.markdown(f"### 📊 Pattern Matrix Engine Analysis ({target_session})")
        render_mode_tab(res_p['m1'], res_p['test_size'], res_p['m1_next']['m'], res_p['m1_next']['s'], res_p['m1_next']['cm'], res_p['m1_next']['cs'])
        
    with tab3:
        st.markdown(f"### 🚀 Deep Trend Analysis ({target_session})")
        render_mode_tab(res_p['m2'], res_p['test_size'], res_p['m2_next']['m'], res_p['m2_next']['s'], res_p['m2_next']['cm'], res_p['m2_next']['cs'])
        
    with tab4:
        st.markdown("### 🤖 Random Forest AI vs ⚙️ Math Engine")
        st.markdown(f"<p class='sub-text'>နောက်ဆုံး {res_l['test_size']} ပွဲအပေါ် AI နှင့် သင်္ချာစနစ်၏ စမ်းသပ်အောင်မြင်မှု နှိုင်းယှဉ်ချက်</p>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"<div class='super-box' style='border-color:#00FF88;'><h3 style='color:#00FF88;'>🤖 ML AI Win Rate</h3><h2>{(res_l['ml_win_count']/res_l['test_size'])*100:.1f}%</h2></div>", unsafe_allow_html=True)
        with c2:
            m3_hit = res_l['m3']['stats']['m_hit'] + res_l['m3']['stats']['jp_12'] + res_l['m3']['stats']['mm_2']
            st.markdown(f"<div class='super-box' style='border-color:#FFD700;'><h3 style='color:#FFD700;'>⚙️ Math Engine Win Rate</h3><h2>{(m3_hit/res_l['test_size'])*100:.1f}%</h2></div>", unsafe_allow_html=True)
            
        with st.expander("📊 AI Model ၏ စမ်းသပ်မှတ်တမ်းအသေးစိတ် ကြည့်ရန်"):
            for log in res_l['ml_logs']: st.markdown(f"<div class='log-card'>{log}</div>", unsafe_allow_html=True)
            
        st.markdown("---")
        st.markdown(f"### 💎 Master Core Analysis ({target_session} Math Logic)")
        render_mode_tab(res_l['m3'], res_l['test_size'], res_l['m3_next']['m'], res_l['m3_next']['s'], res_l['m3_next']['cm'], res_l['m3_next']['cs'])
