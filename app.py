import streamlit as st
import pandas as pd
import numpy as np
import time
import hashlib
import sqlite3
import random
import pyotp
import qrcode
from io import BytesIO
from datetime import datetime, timedelta
from math import radians, sin, cos, asin, sqrt, log
from sklearn.ensemble import RandomForestClassifier

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Jeensetu | Bridging Lives",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ================= CSS STYLING =================
st.markdown("""
<style>
    /* 1. GLOBAL FONTS & BACKGROUND */
    @import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@300;700&family=Poppins:wght@300;400;600&display=swap');
    
    .stApp {
        background: linear-gradient(180deg, #FFF5F5 0%, #FFFFFF 100%);
        font-family: 'Poppins', sans-serif;
        padding-bottom: 80px; /* Space for footer */
    }
    
    /* 2. CUSTOM HEADINGS */
    h1, h2, h3 {
        font-family: 'Merriweather', serif;
        color: #2D3436;
    }
    
    .jeensetu-title {
        background: linear-gradient(90deg, #ff6b6b, #ff4757);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0;
    }
    
    .jeensetu-subtitle {
        color: #636e72;
        text-align: center;
        font-size: 1.2rem;
        margin-top: 5px;
        margin-bottom: 30px;
    }

    /* 3. CARD DESIGN */
    .css-1r6slb0, .stForm {
        background-color: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.05);
        border: 1px solid #f1f2f6;
    }
    
    /* 4. NAVBAR STYLES */
    .logo {
        font-size: 24px;
        font-weight: bold;
        color: #ff4757;
        font-family: 'Merriweather', serif;
        padding-top: 10px;
    }
    
    /* 5. FOOTER STYLE */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: white;
        color: #888;
        text-align: center;
        padding: 15px;
        border-top: 1px solid #eee;
        z-index: 999;
        font-size: 14px;
        font-weight: 500;
        box-shadow: 0 -5px 10px rgba(0,0,0,0.02);
    }
    
    /* 6. BUTTON OVERRIDES */
    div.stButton > button {
        border-radius: 8px;
        height: 45px;
        font-weight: 600;
        transition: all 0.2s;
        border: 1px solid #eee;
    }
    div.stButton > button:hover {
        border-color: #ff4757;
        color: #ff4757;
    }
    
    /* Counter Box */
    .counter-box {
        background: linear-gradient(135deg, #ff6b6b 0%, #ff4757 100%);
        color: white;
        width: 50px;
        height: 60px;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        font-weight: bold;
        box-shadow: 0 5px 15px rgba(255, 71, 87, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# ================= ML ENGINE =================
@st.cache_resource
def train_match_model():
    data = []
    for _ in range(1000):
        age_diff = random.randint(0, 40)
        dist = random.randint(5, 2000)
        hla = random.randint(0, 6)
        blood_score = random.choice([1, 2])
        score = (hla * 15) + (blood_score * 20) - (dist / 100) - (age_diff / 2)
        success = 1 if score > 50 else 0
        data.append([age_diff, dist, hla, blood_score, success])
    
    df = pd.DataFrame(data, columns=['age_diff', 'dist', 'hla', 'blood', 'target'])
    X = df.drop('target', axis=1)
    y = df['target']
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model

def predict_compatibility_ml(donor, patient, model):
    p_age = patient.get('age', 35)
    d_age = 30 
    age_diff = abs(p_age - d_age)
    dist = haversine(patient['lat'], patient['lon'], donor['lat'], donor['lon'])
    donor_hla = set([int(x) for x in donor['hla_a'].split(',')])
    patient_hla = set(patient['hla_a'])
    hla_match = len(donor_hla.intersection(patient_hla))
    b_score = 2 if donor['blood_type'] == patient['blood_type'] else 1
    
    input_vector = np.array([[age_diff, dist, hla_match, b_score]])
    success_prob = model.predict_proba(input_vector)[0][1]
    return round(success_prob * 100, 1), dist

# ================= SETUP & UTILS =================
ORGAN_LIMITS = {"Heart": 4, "Lungs": 6, "Liver": 12, "Kidney": 36, "Cornea": 240}
CITIES = {
    "New Delhi, India": (28.6139, 77.2090), "Mumbai, India": (19.0760, 72.8777),
    "Pune, India": (18.5204, 73.8567), "Nagpur, India": (21.1458, 79.0882), "New York, USA": (40.7128, -74.0060)
}

if "lang" not in st.session_state: st.session_state.lang = "en"
if "page" not in st.session_state: st.session_state.page = "home"
if "auth_role" not in st.session_state: st.session_state.auth_role = None
if "user" not in st.session_state: st.session_state.user = None
if "is_2fa_verified" not in st.session_state: st.session_state.is_2fa_verified = False
if "temp_secret" not in st.session_state: st.session_state.temp_secret = None

TEXT = {
    "en": {
        "nav_home": "Home", "nav_donor": "Become a Donor", "nav_match": "Find a Match", "nav_sos": "Emergency SOS", "nav_login": "Login",
        "hero_title": "Jeensetu", "hero_sub": "Bridging Lives Through Organ Donation",
        "hero_desc": "Join thousands of heroes who have pledged to give the gift of life. Your decision today can save up to 8 lives tomorrow.",
        "btn_donor": "♡ Become a Donor", "btn_match": "🔍 Find a Match", "btn_sos": "⚠️ Emergency SOS",
        "lives_saved": "❤️ LIVES SAVED SO FAR ❤️",
        "role_select": "Select Your Role", "welcome_back": "Welcome Back",
        "login_btn": "Login", "reg_btn": "Create Account",
        "totp_title": "🔐 2FA Setup", "totp_instr": "Scan with Google Authenticator", "totp_verify": "Verify Code"
    },
    "mr": {
        "nav_home": "मुख्य पृष्ठ", "nav_donor": "अवयव दाता बना", "nav_match": "जुळवणी शोधा", "nav_sos": "तात्काळ मदत (SOS)", "nav_login": "लॉगिन",
        "hero_title": "जीनसेतू", "hero_sub": "अवयव दानातून जीवन जोडणारा पूल",
        "hero_desc": "हजारो नायकांमध्ये सामील व्हा ज्यांनी जीवनाचे दान देण्याचे वचन दिले आहे. तुमचा आजचा निर्णय उद्या 8 जीव वाचवू शकतो.",
        "btn_donor": "♡ दाता बना", "btn_match": "🔍 जुळवणी शोधा", "btn_sos": "⚠️ SOS",
        "lives_saved": "❤️ आतापर्यंत वाचवलेले प्राण ❤️",
        "role_select": "तुमची भूमिका निवडा", "welcome_back": "परत स्वागत आहे",
        "login_btn": "प्रवेश करा", "reg_btn": "खाते तयार करा",
        "totp_title": "🔐 2FA सेट करा", "totp_instr": "गुगल ऑथेंटिकेटरने स्कॅन करा", "totp_verify": "कोड तपासा"
    }
}

def get_txt(key): return TEXT[st.session_state.lang].get(key, key)
def navigate(page): st.session_state.page = page; st.rerun()
def hash_pass(p): return hashlib.sha256(str(p).encode()).hexdigest()

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2 - lat1); dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return R * 2 * asin(sqrt(a))

def calculate_meld(b, i, c):
    if any(v <= 0 for v in [b, i, c]): return 0
    return round((3.78 * log(b)) + (11.2 * log(i)) + (9.57 * log(c)) + 6.43, 1)

def init_db():
    conn = sqlite3.connect('jeensetu_final_v2.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (email TEXT PRIMARY KEY, password TEXT, name TEXT, role TEXT, age INTEGER, blood TEXT, totp_secret TEXT, reg_no TEXT, area TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS donors (id TEXT PRIMARY KEY, hospital TEXT, organ TEXT, blood_type TEXT, lat REAL, lon REAL, hla_a TEXT, contact TEXT, harvest_time TEXT)''')
    
    c.execute("SELECT * FROM users WHERE email='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?,?,?)", ('admin', hash_pass('admin123'), 'Super Admin', 'admin', 0, 'NA', None, None, None))
        
    c.execute("SELECT count(*) FROM donors")
    if c.fetchone()[0] == 0:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO donors VALUES ('D-101', 'KEM Hospital Mumbai', 'Heart', 'B', 19.00, 72.82, '24,33', 'kem@mumbai.org', ?)", (now_str,))
        c.execute("INSERT INTO donors VALUES ('D-102', 'Ruby Hall Pune', 'Kidney', 'A', 18.52, 73.85, '2,24', 'transplant@rubyhall.com', ?)", (now_str,))
        conn.commit()
    conn.close()

init_db()

def run_query(q, p=(), one=False, all=False):
    conn = sqlite3.connect('jeensetu_final_v2.db')
    c = conn.cursor()
    c.execute(q, p)
    res = c.fetchone() if one else c.fetchall() if all else None
    conn.commit(); conn.close()
    return res

# ================= COMPONENTS =================
def render_navbar():
    """Renders a functional top navigation bar"""
    # Grid Layout: Logo | Links (Buttons) | Settings
    c1, c2, c3 = st.columns([1.5, 3.5, 1.5])
    
    with c1:
        st.markdown(f'<div class="logo">❤️ {get_txt("hero_title")}</div>', unsafe_allow_html=True)
    
    with c2:
        # These are now REAL BUTTONS inside columns to act like a navbar
        b1, b2, b3, b4 = st.columns(4)
        with b1:
            if st.button(get_txt("nav_home"), key="nav_b1"): navigate("home")
        with b2:
            if st.button(get_txt("nav_donor"), key="nav_b2"): 
                if st.session_state.user: navigate("dashboard")
                else: st.session_state.auth_role = "User"; navigate("auth")
        with b3:
            if st.button(get_txt("nav_match"), key="nav_b3"): navigate("intake")
        with b4:
            if st.button("SOS", key="nav_b4", type="primary"): navigate("sos")

    with c3:
        sc1, sc2 = st.columns(2)
        with sc1:
            if st.button("🌐 " + ("EN" if st.session_state.lang == "mr" else "MR"), key="lang_switch"):
                st.session_state.lang = "mr" if st.session_state.lang == "en" else "en"
                st.rerun()
        with sc2:
            if st.session_state.user:
                if st.button(get_txt("logout")): st.session_state.user = None; navigate("auth")
            else:
                if st.button(get_txt("nav_login")): navigate("auth")

def render_footer():
    """Renders the fixed footer"""
    st.markdown("""
    <div class="footer">
        Team Kaizen 2026 | CIH 2026
    </div>
    """, unsafe_allow_html=True)

def render_donor_card(name, blood):
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #2ecc71, #27ae60); padding:20px; border-radius:15px; color:white; position:relative; box-shadow:0 10px 20px rgba(46,204,113,0.3);">
        <div style="position:absolute; top:15px; right:20px; font-size:30px;">🫀</div>
        <small style="text-transform:uppercase; letter-spacing:1px; opacity:0.8;">Jeensetu Registry</small>
        <h2 style="margin:5px 0; color:white;">Official Donor</h2>
        <p style="margin:0; opacity:0.9;">{name}</p>
        <div style="margin-top:10px; font-weight:bold; font-size:20px;">{blood}</div>
        <div style="text-align:right; font-size:12px; margin-top:10px;">Verified via 2FA ✅</div>
    </div>
    """, unsafe_allow_html=True)

# ================= PAGES =================

# --- 1. HOME PAGE ---
def home_page():
    render_navbar()
    
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.markdown("<div style='text-align:center; font-size:80px;'>❤️</div>", unsafe_allow_html=True)
        st.markdown(f"<h1 class='jeensetu-title'>{get_txt('hero_title')}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p class='jeensetu-subtitle'>{get_txt('hero_sub')}</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; color:#777; margin-bottom:40px;'>{get_txt('hero_desc')}</p>", unsafe_allow_html=True)

    b1, b2, b3 = st.columns([1, 1, 1])
    with b1:
        if st.button(get_txt("btn_donor"), use_container_width=True, key="h_btn1"):
            if st.session_state.user: navigate("dashboard")
            else: st.session_state.auth_role = "User"; navigate("auth")
    with b2:
        if st.button(get_txt("btn_match"), use_container_width=True, key="h_btn2"):
            navigate("intake")
    with b3:
        if st.button(get_txt("btn_sos"), type="primary", use_container_width=True, key="h_btn3"):
            navigate("sos")

    st.markdown(f"<div style='text-align:center; color:#ff4757; margin-top:50px; font-weight:bold; letter-spacing:1px;'>{get_txt('lives_saved')}</div>", unsafe_allow_html=True)
    
    cnt_cols = st.columns([1, 0.5, 0.5, 0.5, 0.5, 0.5, 1])
    nums = ['1', '2', '8', '4', '7']
    for i, n in enumerate(nums):
        with cnt_cols[i+1]:
            st.markdown(f"<div class='counter-box'>{n}</div>", unsafe_allow_html=True)

# --- 2. AUTH PAGE ---
def auth_page():
    if st.session_state.auth_role is None:
        if st.button("⬅ Home"): navigate("home")
        st.markdown(f"<h2 style='text-align:center; margin-bottom:10px;'>{get_txt('welcome_back')}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; color:#777;'>{get_txt('role_select')}</p>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("<div style='text-align:center; font-size:40px;'>👤</div>", unsafe_allow_html=True)
            if st.button("User / Recipient", use_container_width=True): st.session_state.auth_role = "User"; st.rerun()
        with c2:
            st.markdown("<div style='text-align:center; font-size:40px;'>🏥</div>", unsafe_allow_html=True)
            if st.button("Hospital", use_container_width=True): st.session_state.auth_role = "Hospital"; st.rerun()
        with c3:
            st.markdown("<div style='text-align:center; font-size:40px;'>🛡️</div>", unsafe_allow_html=True)
            if st.button("Admin", use_container_width=True): st.session_state.auth_role = "Admin"; st.rerun()
            
    else:
        if st.button("⬅ Change Role"): st.session_state.auth_role = None; st.rerun()
        
        role = st.session_state.auth_role
        st.markdown(f"<h3 style='text-align:center;'>{role} Login</h3>", unsafe_allow_html=True)
        
        if role in ["User", "Admin"]:
            tab1, tab2 = st.tabs(["Login", "Register"])
            with tab1:
                email = st.text_input("Email", key="l_em")
                pwd = st.text_input("Password", type="password", key="l_pw")
                code = st.text_input("2FA Code", max_chars=6, key="l_code") if role == "User" else None
                
                if st.button(get_txt("login_btn"), use_container_width=True):
                    if role == "Admin":
                        if email == "admin" and pwd == "admin123":
                            st.session_state.user = {"name": "Super Admin", "role": "admin"}
                            navigate("admin_dashboard")
                        else: st.error("Invalid Admin Creds")
                    else:
                        u = run_query("SELECT * FROM users WHERE email=? AND password=?", (email, hash_pass(pwd)), one=True)
                        if u and u[3] == 'user':
                            if u[6]:
                                totp = pyotp.TOTP(u[6])
                                if totp.verify(code):
                                    st.session_state.user = {"name": u[2], "role": "user", "verified": 1, "email": u[0], "blood": u[5]}
                                    navigate("dashboard")
                                else: st.error("Invalid 2FA Code")
                            else:
                                st.session_state.user = {"name": u[2], "role": "user", "verified": 0, "email": u[0], "blood": u[5]}
                                navigate("dashboard")
                        else: st.error("User not found")

            with tab2:
                if role == "Admin": st.warning("Admin registration is closed."); return
                st.info("Step 1: Setup 2FA")
                r_em = st.text_input("Email", key="r_em")
                if r_em:
                    if not st.session_state.is_2fa_verified:
                        if not st.session_state.temp_secret: st.session_state.temp_secret = pyotp.random_base32()
                        try:
                            uri = pyotp.totp.TOTP(st.session_state.temp_secret).provisioning_uri(r_em, issuer_name="Jeensetu")
                            img = qrcode.make(uri)
                            buf = BytesIO(); img.save(buf, format="PNG")
                            c_img, c_txt = st.columns([1,2])
                            with c_img: st.image(buf.getvalue(), width=130)
                            with c_txt: 
                                st.caption(f"Manual Key: `{st.session_state.temp_secret}`")
                                st.info("Scan with Google Authenticator")
                        except: st.error("QR Error")
                        
                        chk = st.text_input("Verify Code", max_chars=6)
                        if st.button("Verify"):
                            if pyotp.TOTP(st.session_state.temp_secret).verify(chk):
                                st.session_state.is_2fa_verified = True; st.rerun()
                            else: st.error("Wrong Code")
                    else:
                        st.success("✅ 2FA Verified")
                        r_nm = st.text_input("Name")
                        r_pw = st.text_input("Password", type="password")
                        r_bl = st.selectbox("Blood Group", ["A", "B", "AB", "O"])
                        if st.button("Complete Registration", use_container_width=True):
                            try:
                                run_query("INSERT INTO users VALUES (?,?,?,?,?,?,?,?,?)", 
                                         (r_em, hash_pass(r_pw), r_nm, "user", 25, r_bl, st.session_state.temp_secret, None, None))
                                st.success("Created! Login now.")
                            except: st.error("Email taken")

        elif role == "Hospital":
            ht1, ht2 = st.tabs(["Login", "Register Hospital"])
            with ht1:
                he = st.text_input("Hospital Email")
                hp = st.text_input("Password", type="password")
                if st.button("Hospital Login", use_container_width=True):
                    u = run_query("SELECT * FROM users WHERE email=? AND password=?", (he, hash_pass(hp)), one=True)
                    if u and u[3] == 'hospital':
                        st.session_state.user = {"name": u[2], "role": "hospital", "reg_no": u[7], "area": u[8], "email": u[0]}
                        navigate("hospital_dashboard")
                    else: st.error("Invalid")
            
            with ht2:
                hn = st.text_input("Hospital Name")
                hr = st.text_input("Reg No")
                ha = st.selectbox("Area", list(CITIES.keys()))
                hem = st.text_input("Email", key="h_r_em")
                hpw = st.text_input("Password", type="password", key="h_r_pw")
                if st.button("Register Hospital", use_container_width=True):
                    try:
                        run_query("INSERT INTO users VALUES (?,?,?,?,?,?,?,?,?)",
                                 (hem, hash_pass(hpw), hn, "hospital", 0, "NA", None, hr, ha))
                        st.success("Hospital Registered")
                    except: st.error("Error")

# --- 3. DASHBOARD ---
def dashboard():
    render_navbar()
    u = st.session_state.user
    st.markdown(f"<h2>Welcome, {u['name']}</h2>", unsafe_allow_html=True)
    if u.get('verified'): st.success("🔐 Account Secured with 2FA")
    
    c1, c2 = st.columns([1, 2])
    with c1:
        render_donor_card(u['name'], u.get('blood', 'O+'))
    with c2:
        st.markdown("### Quick Actions")
        if st.button("🔍 Find a Match (ML Powered)", use_container_width=True): navigate("intake")
        if st.button("🚨 SOS Emergency", type="primary", use_container_width=True): navigate("sos")

# --- 4. HOSPITAL PORTAL ---
def hospital_dashboard():
    render_navbar()
    u = st.session_state.user
    st.markdown(f"## 🏥 Hospital Portal: {u['name']}")
    if st.button("⬅ Back"): navigate("dashboard")
    
    with st.form("h_form"):
        st.subheader("Add Organ to Registry")
        organ = st.selectbox("Organ", list(ORGAN_LIMITS.keys()))
        blood = st.selectbox("Blood Type", ["A", "B", "AB", "O"])
        try: idx = list(CITIES.keys()).index(u['area'])
        except: idx = 0
        loc = st.selectbox("Location", list(CITIES.keys()), index=idx)
        
        if st.form_submit_button("Publish Organ"):
            lat, lon = CITIES[loc]
            did = f"D-{random.randint(1000,9999)}"
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            run_query("INSERT INTO donors VALUES (?,?,?,?,?,?,?,?,?)", 
                     (did, u['name'], organ, blood, lat, lon, "2,24", u['email'], now))
            st.success(f"{organ} added to registry!")

# --- 5. SEARCH & RESULTS ---
def intake_page():
    render_navbar()
    if st.button("⬅ Dashboard"): navigate("dashboard")
    st.markdown("<h2 style='text-align:center'>Find a Compatible Match</h2>", unsafe_allow_html=True)
    
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            organ = st.selectbox("Organ Needed", list(ORGAN_LIMITS.keys()))
            blood = st.selectbox("Blood Group", ["A", "B", "AB", "O"])
        with c2:
            loc = st.selectbox("Patient Location", list(CITIES.keys()))
            
        meld = 0
        if organ == "Liver":
            st.info("🧬 Liver Protocol: Enter Lab Values")
            b = st.number_input("Bilirubin", 1.0); i = st.number_input("INR", 1.0); c = st.number_input("Creatinine", 1.0)
            meld = calculate_meld(b, i, c)

        if st.button("Search with AI 🤖", type="primary", use_container_width=True):
            lat, lon = CITIES[loc]
            st.session_state.criteria = {'organ': organ, 'blood_type': blood, 'lat': lat, 'lon': lon, 'meld': meld, 'hla_a': [2]}
            navigate("results")

def results_page():
    render_navbar()
    if st.button("⬅ Search"): navigate("intake")
    model = train_match_model()
    crit = st.session_state.criteria
    st.markdown(f"### Results for {crit['organ']} ({crit['blood_type']})")
    
    donors = run_query("SELECT * FROM donors WHERE organ=?", (crit['organ'],), all=True)
    matches = []
    
    for d in donors:
        d_dict = {'id': d[0], 'hospital': d[1], 'organ': d[2], 'blood_type': d[3], 'lat': d[4], 'lon': d[5], 'hla_a': d[6], 'harvest_time': d[8]}
        comp_matrix = {"O": ["O"], "A": ["A", "O"], "B": ["B", "O"], "AB": ["A", "B", "AB", "O"]}
        if d_dict['blood_type'] not in comp_matrix.get(crit['blood_type'], []): continue
        
        remaining = 0
        if d_dict['harvest_time']:
            try:
                ht = datetime.strptime(d_dict['harvest_time'], "%Y-%m-%d %H:%M:%S")
                elapsed = (datetime.now() - ht).total_seconds() / 3600
                limit = ORGAN_LIMITS.get(crit['organ'], 24)
                if elapsed > limit: continue
                remaining = limit - elapsed
            except: pass
            
        prob, dist = predict_compatibility_ml(d_dict, crit, model)
        if crit.get('meld', 0) > 20: prob += 10
        matches.append({**d_dict, 'prob': min(prob, 100), 'dist': int(dist), 'rem': remaining})
        
    matches.sort(key=lambda x: x['prob'], reverse=True)
    if not matches: st.error("No compatible organs found."); return
    
    for m in matches:
        st.markdown(f"""
        <div class="css-1r6slb0">
            <div style="display:flex; justify-content:space-between;">
                <div><h3 style="margin:0">{m['hospital']}</h3><p style="color:gray">📍 {m['dist']} km | Blood: {m['blood_type']}</p></div>
                <div style="text-align:right"><h2 style="color:#2ecc71; margin:0">{m['prob']}%</h2><small>Match Score</small></div>
            </div>
            <div style="margin-top:10px; padding:10px; background:#f1f2f6; border-radius:5px;">⏳ Expires in: {int(m['rem'])}h {int((m['rem']%1)*60)}m</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Request {m['id']}", key=m['id']): st.toast("Request Sent!")

def sos_page():
    render_navbar()
    st.error("🚨 EMERGENCY SOS ACTIVE - BROADCASTING TO ALL HOSPITALS")
    if st.button("⬅ Exit"): navigate("home")
    st.map(pd.DataFrame({'lat':[19.0760], 'lon':[72.8777]}))

def admin_dashboard():
    st.title("🛡️ Admin Database View")
    if st.button("Logout"): st.session_state.user = None; navigate("auth")
    c1, c2 = st.tabs(["Users", "Donors"])
    with c1: st.dataframe(pd.DataFrame(run_query("SELECT email, name, role, area FROM users", all=True), columns=['Email','Name','Role','Area']), use_container_width=True)
    with c2: st.dataframe(pd.DataFrame(run_query("SELECT * FROM donors", all=True)), use_container_width=True)

# ================= ROUTER =================
if st.session_state.page == "home": home_page()
elif st.session_state.page == "auth": auth_page()
elif st.session_state.page == "dashboard": dashboard()
elif st.session_state.page == "hospital_dashboard": hospital_dashboard()
elif st.session_state.page == "intake": intake_page()
elif st.session_state.page == "results": results_page()
elif st.session_state.page == "sos": sos_page()
elif st.session_state.page == "admin_dashboard": admin_dashboard()

# ================= FOOTER =================
render_footer()