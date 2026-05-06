import streamlit as st
import pandas as pd
import itertools
from collections import Counter

# --- 🎨 UI Configuration ---
st.set_page_config(page_title="The Golden Cross AI", page_icon="👑", layout="wide")

# --- 🔒 SECURITY (PASSWORD GATE) ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #FFD700; letter-spacing: 2px;'>👑 THE GOLDEN CROSS</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #A0AEC0;'>AUTHORIZED ADMIN ONLY</p>", unsafe_allow_html=True)
    
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
    .gold-text { color: #FFD700; font-weight: 800; text-align: center; margin-bottom: 0px;}
    .yellow-status { color: #FFD700; font-family: 'Courier New', Courier, monospace; line-height: 1.6; background-color: #1A1C23; padding: 15px; border-radius: 8px; border-left: 4px solid #FFD700; margin-bottom: 20px; font-size: 14px;}
    .blue-status { color: #00E5FF; font-family: 'Courier New', Courier, monospace; line-height: 1.6; background-color: #1A1C23; padding: 15px; border-radius: 8px; border-left: 4px solid #00E5FF; margin-bottom: 20px; font-size: 14px;}
    .cyan-note { color: #00E5FF; font-family: 'Courier New', Courier, monospace; background-color: #1A1C23; padding: 12px; border-radius: 8px; border-left: 4px solid #00E5FF; margin-top: 15px; margin-bottom: 20px; font-size: 14px;}
    .log-card { background-color: #16181D; padding: 10px 15px; border-radius: 5px; margin-bottom: 5px; font-family: 'Courier New', Courier, monospace; font-size: 13px; border: 1px solid #2D3748;}
    .sub-text { color: #A0AEC0; text-align: center; font-size: 14px; margin-bottom: 20px;}
    
    .premium-box { background-color: #000000; border: 1px solid #FFD700; border-radius: 8px; padding: 20px 10px; text-align: center; margin-bottom: 15px; box-shadow: 0 2px 10px rgba(255, 215, 0, 0.15);}
    .premium-num { font-size: 26px; color: #FFFFFF; font-weight: 900; letter-spacing: 2px; }
    .main-num-box { font-size: 40px; color: #FFD700; font-weight: 900; background: #1A1C23; padding: 15px 30px; border-radius: 10px; border: 2px solid #FFD700; display: inline-block; margin: 10px;}
    .sec-num-box { font-size: 22px; color: #A0AEC0; font-weight: bold; background: #1A1C23; padding: 8px 18px; border-radius: 8px; border: 1px solid #555; display: inline-block; margin: 5px;}
    
    .super-box { background: linear-gradient(145deg, #1A1C23, #0B0E14); border: 2px solid #FFD700; border-radius: 12px; padding: 25px 10px; text-align: center; margin-bottom: 20px; box-shadow: 0 0 20px rgba(255, 215, 0, 0.2);}
    .super-num { font-size: 34px; color: #FFD700; font-weight: 900; letter-spacing: 3px; background-color: #000; padding: 10px 20px; border-radius: 8px; margin: 0 10px; display: inline-block; border: 1px solid rgba(255,215,0,0.5);}
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

# --- 🎯 HISTORY MATCH ENGINE (Simple Frequency) ---
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

# --- 📊 Full Backtest Engine (V12 Logic Restored) ---
def run_backend_engine(timeline, test_size):
    total_draws = len(timeline)
    test_size = min(test_size, total_draws - 45)
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
        mains_hist, secs_hist, cm_hist, cs_hist = [], [], [], []
        hot_logs, cold_logs = [], []

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

    # 🔮 THE PREDICTION ENGINE
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

    return {
        'm1': m1_eval, 'm2': m2_eval, 'm3': m3_eval,
        'm1_next': {'m': m1_next_m, 's': m1_next_s, 'cm': m1_next_cm, 'cs': m1_next_cs},
        'm2_next': {'m': m2_next_m, 's': m2_next_s, 'cm': m2_next_cm, 'cs': m2_next_cs},
        'm3_next': {'m': m3_next_m, 's': m3_next_s, 'cm': m3_next_cm, 'cs': m3_next_cs},
        'm3_next_raw': m3_next_raw,
        'test_size': test_size,
        'actuals': actuals
    }

# --- 🧠 V13.1 TRI-ENGINE AI OPTIMIZATION ---
def get_tri_recommendations(timeline):
    best_lb_l, max_hits_l = 50, -1
    best_lb_p, max_hits_p = 50, -1
    best_lb_c, max_hits_c = 50, -1
    
    total_draws = len(timeline)
    max_possible_lb = max(10, total_draws - 45)
    
    lookbacks_to_test = [lb for lb in [10, 20, 30, 40, 50, 60, 70, 80, 90, 100] if lb <= max_possible_lb]
    if not lookbacks_to_test:
        if max_possible_lb >= 10: lookbacks_to_test = [max_possible_lb]
        else: return 10, 10, 10
            
    for lb in lookbacks_to_test:
        res = run_backend_engine(timeline, lb)
        ts = res['test_size']
        actuals = res['actuals']
        
        log_limit = min(10, ts)
        hits_l, hits_p, hits_c = 0, 0, 0
        for i in range(ts - log_limit, ts):
            draw = actuals[i]
            
            # Lone Hit
            lone_hist = res['m3']['mains_hist'][i]
            if draw[0] in lone_hist or draw[1] in lone_hist: hits_l += 1
            
            # Pairs Hit
            pm_hot5_hist = res['m1']['mains_hist'][i] + res['m1']['secs_hist'][i]
            pm_10_hist = [f"{a}{b}" for a, b in itertools.combinations(pm_hot5_hist, 2)]
            mc_hot2_hist = res['m3']['mains_hist'][i]
            mc_cold2_hist = res['m3']['cm_hist'][i]
            mc_6_hist = [f"{a}{b}" for a, b in itertools.combinations(mc_hot2_hist + mc_cold2_hist, 2)]
            
            if any(draw == p or draw == p[::-1] for p in pm_10_hist) or any(draw == p or draw == p[::-1] for p in mc_6_hist):
                hits_p += 1
                
            # Cold Hit
            if draw[0] in mc_cold2_hist or draw[1] in mc_cold2_hist: hits_c += 1
                
        if hits_l > max_hits_l: max_hits_l = hits_l; best_lb_l = lb
        if hits_p > max_hits_p: max_hits_p = hits_p; best_lb_p = lb
        if hits_c > max_hits_c: max_hits_c = hits_c; best_lb_c = lb
            
    return best_lb_l, best_lb_p, best_lb_c

# --- 📱 V12 UI COMPONENT FOR ANALYTICS TABS ---
def render_mode_tab(eval_data, test_size, next_m, next_s, next_cm, next_cs):
    st.markdown("<h4 style='color:#FFD700;'>🔥 Hot Number</h4>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style='text-align:center; margin-bottom: 15px;'>
        <div style='color:#FFD700; font-size:16px; font-weight:bold; margin-bottom:5px;'>လုံးဘိုင် ၂ လုံး</div>
        <div class='main-num-box' style='padding:10px 25px;'>{next_m[0] if len(next_m)>0 else '-'}</div>
        <div class='main-num-box' style='padding:10px 25px;'>{next_m[1] if len(next_m)>1 else '-'}</div>
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
    h_t += f"🔥 အကွက် (၁၂) ကွက်တည်းဖြင့် JACKPOT ဝင်သောပွဲ : ({st_d['jp_12']}) ပွဲ (Win Rate: {(st_d['jp_12']/test_size)*100:.1f}%)<br>"
    h_t += f"👑 Main အချင်းချင်း (၂ ကွက်) ဝင်ပွဲ : ({st_d['mm_2']}) ပွဲ (Win Rate: {(st_d['mm_2']/test_size)*100:.1f}%)<br>"
    h_t += f"💰 Sec အချင်းချင်း (၆ ကွက်) ဝင်ပွဲ : ({st_d['ss_6']}) ပွဲ (Win Rate: {(st_d['ss_6']/test_size)*100:.1f}%)"
    st.markdown(f"<div class='yellow-status'>{h_t}</div>", unsafe_allow_html=True)
    
    with st.expander(f"📊 Hot Number မှတ်တမ်းအသေးစိတ်ကြည့်ရန် ({test_size} ပွဲ)"):
        for log in eval_data['hot_logs']: st.markdown(f"<div class='log-card'>{log}</div>", unsafe_allow_html=True)

    st.markdown("<h4 style='color:#00E5FF; margin-top:30px;'>❄️ Cold Number</h4>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style='text-align:center; margin-bottom: 15px;'>
        <div style='color:#00E5FF; font-size:16px; font-weight:bold; margin-bottom:5px;'>လုံးဘိုင် ၂ လုံး</div>
        <div class='main-num-box' style='border-color:#00E5FF; color:#00E5FF; padding:10px 25px;'>{next_cm[0] if len(next_cm)>0 else '-'}</div>
        <div class='main-num-box' style='border-color:#00E5FF; color:#00E5FF; padding:10px 25px;'>{next_cm[1] if len(next_cm)>1 else '-'}</div>
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
    c_t += f"⭐ Sec (၃) လုံး အပါဝင်သောပွဲ : ({c_st['s_hit'] + c_st['jp_12'] + c_st['ss_6']}) ပွဲ (Win Rate: {((c_st['s_hit'] + c_st['jp_12'] + c_st['ss_6'])/test_size)*100:.1f}%)<br>"
    c_t += f"🔥 အကွက် (၁၂) ကွက်တည်းဖြင့် JACKPOT ဝင်သောပွဲ : ({c_st['jp_12']}) ပွဲ (Win Rate: {(c_st['jp_12']/test_size)*100:.1f}%)<br>"
    c_t += f"👑 Main အချင်းချင်း (၂ ကွက်) ဝင်ပွဲ : ({c_st['mm_2']}) ပွဲ (Win Rate: {(c_st['mm_2']/test_size)*100:.1f}%)<br>"
    c_t += f"💰 Sec အချင်းချင်း (၆ ကွက်) ဝင်ပွဲ : ({c_st['ss_6']}) ပွဲ (Win Rate: {(c_st['ss_6']/test_size)*100:.1f}%)"
    st.markdown(f"<div class='blue-status'>{c_t}</div>", unsafe_allow_html=True)
    
    with st.expander(f"📊 Cold Number မှတ်တမ်းအသေးစိတ်ကြည့်ရန် ({test_size} ပွဲ)"):
        for log in eval_data['cold_logs']: st.markdown(f"<div class='log-card'>{log}</div>", unsafe_allow_html=True)


# --- 📱 Sidebar (Data Center) ---
st.sidebar.title("Data Center 📥")
uploaded_file = st.sidebar.file_uploader("Excel ဖိုင် တင်ရန်", type=["xlsx"])

if 'history' not in st.session_state:
    st.session_state.history = [(1,2), (3,4), (5,6), (7,8), (9,0), (1,1), (2,2), (3,3), (4,4), (5,5), (6,6), (7,7), (5,3), (8,7), (1,6), (4,2)] * 4

if 'last_uploaded' not in st.session_state:
    st.session_state.last_uploaded = None

if uploaded_file is not None:
    file_details = f"{uploaded_file.name}_{uploaded_file.size}"
    if st.session_state.last_uploaded != file_details:
        try:
            df = pd.read_excel(uploaded_file, engine='openpyxl')
            df.columns = df.columns.str.strip().str.lower()
            temp = []
            for _, row in df.iterrows():
                if 'am1' in df.columns and 'am2' in df.columns:
                    try: temp.append((int(float(row['am1'])), int(float(row['am2']))))
                    except: pass
                if 'pm1' in df.columns and 'pm2' in df.columns:
                    try: temp.append((int(float(row['pm1'])), int(float(row['pm2']))))
                    except: pass
            if temp: 
                st.session_state.history = temp
                st.session_state.last_uploaded = file_details 
                st.sidebar.success(f"✅ Data ({len(temp)}) ပွဲ ဝင်ရောက်ပါပြီ။")
        except Exception as e: st.sidebar.error(f"❌ Error: {e}")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📝 Live Data Entry")
if st.session_state.history:
    last_draw = st.session_state.history[-1]
    st.sidebar.info(f"**နောက်ဆုံးထွက်: [ {last_draw[0]}{last_draw[1]} ]** (စုစုပေါင်း {len(st.session_state.history)} ပွဲ)")

c1, c2 = st.sidebar.columns(2)
new_top = c1.number_input("ထိပ်စီး", min_value=0, max_value=9, step=1, value=0)
new_bot = c2.number_input("နောက်ပိတ်", min_value=0, max_value=9, step=1, value=0)

if st.sidebar.button("➕ အသစ်ထည့်မည်", use_container_width=True):
    st.session_state.history.append((new_top, new_bot))
    if hasattr(st, "rerun"): st.rerun()
    else: st.experimental_rerun()

if st.sidebar.button("↩️ Undo (ပြန်ဖျက်မည်)"):
    if len(st.session_state.history) > 0:
        st.session_state.history.pop()
        if hasattr(st, "rerun"): st.rerun()
        else: st.experimental_rerun()

# --- 📱 Main App (Mode Selection & Execution) ---
st.markdown("<h1 class='gold-text'>THE GOLDEN CROSS</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-text'>V13.1 - THE ULTIMATE LEGENDARY EDITION</p>", unsafe_allow_html=True)

st.markdown("### ⚙️ Engine Mode ရွေးချယ်ရန်")
mode = st.radio("", ["🤖 AI Auto Mode (အကြံပြုချက် - Super Main နှင့် Super Cold ကို ရှာဖွေပေးမည်)", "✍️ Custom Mode (မိမိစိတ်ကြိုက် ပွဲစဉ်အရေအတွက် ရိုက်ထည့်မည်)"])

custom_lb = 50
if "Custom" in mode:
    custom_lb = st.number_input("ပွဲစဉ် အရေအတွက် ရိုက်ထည့်ပါ:", min_value=10, max_value=500, value=50)

if st.button("🚀 စနစ်ကို တွက်ချက်မည် (RUN ENGINE)"):
    st.session_state.run_v13 = True
    st.session_state.selected_mode = mode
    st.session_state.custom_lb = custom_lb

if st.session_state.get('run_v13'):
    hist = st.session_state.history
    mode_ran = st.session_state.selected_mode
    
    if "Auto" in mode_ran:
        lb_l, lb_p, lb_c = 50, 50, 50
        if len(hist) > 45:
            lb_l, lb_p, lb_c = get_tri_recommendations(hist)
        res_l = run_backend_engine(hist, lb_l)
        res_p = run_backend_engine(hist, lb_p)
        res_c = run_backend_engine(hist, lb_c)
        st.info(f"🤖 **AI Auto Mode:** [လုံးဘိုင် ({lb_l}) ပွဲ] ၊ [အကွက် ({lb_p}) ပွဲ] နှင့် [အအေး ({lb_c}) ပွဲ] တို့ကို ပေါင်းစပ် တွက်ချက်ထားပါသည်။")
    else:
        lb_p = st.session_state.custom_lb
        res_p = run_backend_engine(hist, lb_p)
        res_l = res_p
        res_c = res_p
        st.info(f"✍️ **Custom Mode:** Admin ရိုက်ထည့်ထားသော ({lb_p}) ပွဲစာ ရေစီးကြောင်းဖြင့် တွက်ချက်ထားပါသည်။")

    # --- 💎 Collision Resolution (The Ultimate Hybrid) ---
    super_hot_2 = res_l['m3_next']['m']
    
    pref_cold_idx = res_c['m3']['cm_idx'] + res_c['m3']['cs_idx']
    raw_cold_nums = [res_c['m3_next_raw'][i] for i in pref_cold_idx if i < len(res_c['m3_next_raw'])]
    
    safe_cold_pool = [n for n in raw_cold_nums if n not in super_hot_2]
    super_cold_2 = safe_cold_pool[:2] if len(safe_cold_pool) >= 2 else safe_cold_pool
    
    master_4_digits = super_hot_2 + super_cold_2
    mc_6_pairs = [f"{a}{b}" for a, b in itertools.combinations(master_4_digits, 2)]
    
    pm_hot5 = res_p['m1_next']['m'] + res_p['m1_next']['s']
    pm_10_pairs = [f"{a}{b}" for a, b in itertools.combinations(pm_hot5, 2)]
    
    all_pairs = list(set(pm_10_pairs + mc_6_pairs))
    super_main_pairs = [p for p in all_pairs if p[0] in super_hot_2 or p[1] in super_hot_2]
    
    # --- Generate V13 Logs for Summary Tab (History Match Support) ---
    summary_logs = []
    ts_p = res_p['test_size']
    actuals = res_p['actuals']
    log_limit = min(10, ts_p)
    
    for k in range(1, log_limit + 1):
        idx = ts_p - log_limit - 1 + k
        draw = actuals[idx]
        
        hist_super_hot_2 = res_l['m3']['mains_hist'][res_l['test_size'] - log_limit - 1 + k]
        
        # Calculate historical partners for lone baing hit check
        hist_timeline = hist[:len(hist) - log_limit - 1 + k]
        hist_partner_pairs = []
        for lone in hist_super_hot_2:
            partners = get_best_partners(lone, hist_timeline)
            for p in partners:
                hist_partner_pairs.extend([f"{lone}{p}", f"{p}{lone}"])
        
        is_lone_hit = draw[0] in hist_super_hot_2 or draw[1] in hist_super_hot_2
        is_history_hit = any(draw == p or draw == p[::-1] for p in set(hist_partner_pairs))
        
        hist_p_hot5 = res_p['m1']['mains_hist'][idx] + res_p['m1']['secs_hist'][idx]
        hist_p_10 = [f"{a}{b}" for a, b in itertools.combinations(hist_p_hot5, 2)]
        hist_c_hot2 = res_c['m3']['mains_hist'][res_c['test_size'] - log_limit - 1 + k]
        hist_c_cold2 = res_c['m3']['cm_hist'][res_c['test_size'] - log_limit - 1 + k]
        hist_mc_6 = [f"{a}{b}" for a, b in itertools.combinations(hist_c_hot2 + hist_c_cold2, 2)]
        
        p_hit = any(draw == p or draw == p[::-1] for p in hist_p_10) or any(draw == p or draw == p[::-1] for p in hist_mc_6)
        
        # New 3-State Logic for Master Core
        if is_history_hit: lone_str = f"✅ ({draw} ဝင်သည်)"
        elif is_lone_hit: lone_str = "✅ (တွဲဖက် ❌)"
        else: lone_str = "❌ လွဲ"
            
        p_str = "✅" if p_hit else "❌"
        
        if "Auto" in mode_ran:
            hist_super_mains = [p for p in set(hist_p_10 + hist_mc_6) if p[0] in hist_super_hot_2 or p[1] in hist_super_hot_2]
            sm_hit = any(draw == p or draw == p[::-1] for p in hist_super_mains)
            sm_str = "✅ Hit" if sm_hit else "❌ Miss"
            summary_logs.append(f"ပွဲ {(ts_p - log_limit + k):02d} | အဖြေ: [{draw}] | 👑 Super Main: {sm_str} | 🛡️ လုံးဘိုင်+တွဲဖက်: {lone_str} | 🌊 အရံအကွက်: {p_str}")
        else:
            summary_logs.append(f"ပွဲ {(ts_p - log_limit + k):02d} | အဖြေ: [{draw}] | 🛡️ လုံးဘိုင်+တွဲဖက်: {lone_str} | 🌊 အကွက်: {p_str}")
            
    summary_logs.reverse()

    # --- 📑 Render Tabs ---
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Summary", "🌊 Pattern Matrix", "🚀 Deep Trend", "💎 Master Core"])
    
    with tab1:
        if "Auto" in mode_ran:
            st.markdown("<h3 style='text-align:center; color:#FFD700; margin-top:10px;'>👑 THE GOLDEN CROSS (SUPER MAIN)</h3>", unsafe_allow_html=True)
            st.markdown("<p style='text-align:center; color:#A0AEC0;'>လုံးဘိုင်အင်ဂျင် နှင့် အကွက်အင်ဂျင် (၂) ခုလုံးမှ ထောက်ခံထားသော အမြင့်ဆုံး VIP အကွက်များ</p>", unsafe_allow_html=True)
            
            if super_main_pairs:
                html_sm = "<div class='super-box'>"
                html_sm += "".join([f"<span class='super-num'>{p}</span>" for p in super_main_pairs])
                html_sm += "</div>"
                st.markdown(html_sm, unsafe_allow_html=True)
            else:
                st.warning("⚠️ ယခုပွဲစဉ်တွင် အင်ဂျင် (၂) ခု ဆုံမှတ်မရှိပါ။ အောက်ပါ အရန်အကွက်များကိုသာ အသုံးပြုပါ။")
            st.divider()

        st.markdown("### 🛡️ MASTER CORE (လုံးဘိုင် နှင့် အကောင်းဆုံး တွဲဖက်များ)")
        st.markdown("<p style='color:gray; font-size:14px;'>သမိုင်းကြောင်းအရ အကြိမ်အရေအတွက် အများဆုံး တွဲထွက်ထားသော ဂဏန်းများ</p>", unsafe_allow_html=True)
        
        if len(super_hot_2) > 0:
            html_history = "<div class='premium-box' style='text-align:left; padding: 20px 30px;'>"
            for lone in super_hot_2:
                partners = get_best_partners(lone, hist)
                p_str = " ".join([f"<span class='sec-num-box' style='font-size: 18px; padding: 5px 12px;'>{p}</span>" for p in partners])
                html_history += f"<div style='margin-bottom: 12px;'><span class='main-num-box' style='font-size: 24px; padding: 5px 15px;'>{lone}</span> <span style='color:#FFD700; font-size: 18px; font-weight: bold;'>➡ တွဲရန် :</span> {p_str}</div>"
            html_history += "</div>"
            st.markdown(html_history, unsafe_allow_html=True)
        
        st.divider()
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 🌊 PATTERN MATRIX (၁၀ ကွက်)")
            html_pm = f"<div class='premium-box'>"
            html_pm += "".join([f"<span style='margin:0 10px;'><span class='premium-num'>{p}</span></span>" for p in pm_10_pairs[:5]]) + "<br><br>"
            html_pm += "".join([f"<span style='margin:0 10px;'><span class='premium-num'>{p}</span></span>" for p in pm_10_pairs[5:]])
            html_pm += "</div>"
            st.markdown(html_pm, unsafe_allow_html=True)
            
        with c2:
            st.markdown("#### ⚔️ MASTER CORE (၆ ကွက်)")
            html_mc = f"<div class='premium-box' style='border-color:#00E5FF;'>"
            if len(mc_6_pairs) >= 3:
                html_mc += "".join([f"<span style='margin:0 10px;'><span class='premium-num'>{p}</span></span>" for p in mc_6_pairs[:3]]) + "<br><br>"
                html_mc += "".join([f"<span style='margin:0 10px;'><span class='premium-num'>{p}</span></span>" for p in mc_6_pairs[3:]])
            else:
                html_mc += "".join([f"<span style='margin:0 10px;'><span class='premium-num'>{p}</span></span>" for p in mc_6_pairs])
            html_mc += "</div>"
            st.markdown(html_mc, unsafe_allow_html=True)
            
        c_disp_1 = super_cold_2[0] if len(super_cold_2) > 0 else "-"
        c_disp_2 = super_cold_2[1] if len(super_cold_2) > 1 else "-"
        st.markdown(f"<div class='cyan-note'>💡 <b>မှတ်ချက်:</b> အအေးဇုန်မှ ရုတ်တရက် ပြန်လည်ရုန်းထွက်နိုင်ချေ အများဆုံးဖြစ်သော (The Best Cold) လုံးဘိုင်များမှာ <b>[ {c_disp_1} ]</b> နှင့် <b>[ {c_disp_2} ]</b> ဖြစ်ပါသည်။</div>", unsafe_allow_html=True)
        
        with st.expander("📊 နောက်ဆုံး 10 ပွဲ မှတ်တမ်းအသေးစိတ်ကြည့်ရန်"):
            for log in summary_logs:
                st.markdown(f"<div class='log-card'>{log}</div>", unsafe_allow_html=True)

    with tab2:
        st.markdown("### 🌊 Pattern Matrix Analysis")
        render_mode_tab(res_p['m1'], res_p['test_size'], res_p['m1_next']['m'], res_p['m1_next']['s'], res_p['m1_next']['cm'], res_p['m1_next']['cs'])
        
    with tab3:
        st.markdown("### 🚀 Deep Trend Analysis")
        render_mode_tab(res_p['m2'], res_p['test_size'], res_p['m2_next']['m'], res_p['m2_next']['s'], res_p['m2_next']['cm'], res_p['m2_next']['cs'])
        
    with tab4:
        st.markdown("### 💎 Master Core Analysis")
        render_mode_tab(res_l['m3'], res_l['test_size'], res_l['m3_next']['m'], res_l['m3_next']['s'], res_l['m3_next']['cm'], res_l['m3_next']['cs'])
