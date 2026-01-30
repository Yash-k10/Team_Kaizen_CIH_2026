import streamlit as st
from database import init_db, get_db, hash_password
from matching_engine import match
from datetime import datetime

init_db()

# ---------------- SESSION ----------------
if "role" not in st.session_state:
    st.session_state.role = None

# ---------------- LOGIN ----------------
def login(role):
    st.subheader(f"{role.capitalize()} Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        db = get_db()
        c = db.cursor()
        c.execute("SELECT * FROM users WHERE email=? AND role=?", (email, role))
        user = c.fetchone()
        if user and user[5] == hash_password(password):
            st.session_state.role = role
            st.session_state.user = email
            st.success("Login successful")
        else:
            st.error("Invalid credentials")

# ---------------- LANDING ----------------
if not st.session_state.role:
    st.title("❤️ JeevSetu – Organ Donation Platform")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("User Login"):
            login("user")
    with col2:
        if st.button("Hospital Login"):
            login("hospital")
    with col3:
        if st.button("Admin Login"):
            login("admin")

# ---------------- USER / HOSPITAL ----------------
elif st.session_state.role in ["user", "hospital"]:
    st.sidebar.title("Menu")
    choice = st.sidebar.radio("Navigate", ["SOS Alert", "Find Organ"])

    if choice == "SOS Alert":
        with st.form("sos"):
            age = st.number_input("Patient Age", 1, 100)
            blood = st.selectbox("Blood Group", ["A+","A-","B+","B-","AB+","AB-","O+","O-"])
            organ = st.selectbox("Organ", ["Kidney","Liver","Heart","Lung"])
            urgency = st.slider("Urgency", 0, 100)
            loc = st.text_input("Location")

            if st.form_submit_button("Send SOS"):
                db = get_db()
                db.execute("""
                INSERT INTO sos_cases VALUES (NULL,?,?,?,?,?,?)
                """, (st.session_state.role, age, blood, organ, urgency, loc, datetime.now().isoformat()))
                db.commit()
                st.success("SOS Alert Created")

    if choice == "Find Organ":
        patient = {"blood": "A+", "lat": 19.0, "lon": 72.0, "urgency": 80}
        donors = [{"name": "Donor1", "blood": "A+", "lat": 19.1, "lon": 72.1}]
        results = match(patient, donors)
        st.dataframe(results)

# ---------------- ADMIN ----------------
elif st.session_state.role == "admin":
    st.title("Admin Dashboard")
    db = get_db()
    st.subheader("Pending Hospitals")
    rows = db.execute("SELECT name,email FROM hospitals WHERE verified=0").fetchall()
    st.table(rows)
