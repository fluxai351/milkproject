import streamlit as st

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Dairy Master Pro",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------------- GLOBAL CSS ----------------
st.markdown(
    """
    <style>
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    body {
        background-color: #f5f7fa;
    }

    .center-box {
        max-width: 420px;
        margin: auto;
        margin-top: 12vh;
    }

    .card {
        background: #ffffff;
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.08);
    }

    .app-header {
        background: linear-gradient(135deg, #075E54, #128C7E);
        color: white;
        padding: 24px;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 28px;
    }

    .app-header h2 {
        margin: 0;
        font-size: 26px;
        font-weight: 700;
    }

    .app-header p {
        margin-top: 6px;
        font-size: 14px;
        opacity: 0.9;
    }

    .stTextInput input {
        height: 48px;
        border-radius: 12px;
        font-size: 15px;
    }

    .stButton button {
        width: 100%;
        height: 48px;
        border-radius: 14px;
        background-color: #075E54;
        color: white;
        font-size: 16px;
        font-weight: 700;
        border: none;
    }

    .stButton button:hover {
        background-color: #064c45;
    }

    .error-msg {
        color: #c0392b;
        text-align: center;
        margin-top: 10px;
        font-size: 14px;
    }

    .dashboard {
        max-width: 1000px;
        margin: auto;
        margin-top: 40px;
    }

    .dashboard h1 {
        color: #075E54;
        font-size: 32px;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- SESSION STATE ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- AUTH ----------------
VALID_USER = "admin"
VALID_PASS = "1234"

# ---------------- LOGIN SCREEN ----------------
if not st.session_state.logged_in:

    st.markdown('<div class="center-box">', unsafe_allow_html=True)
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="app-header">
            <h2>🥛 Dairy Master Pro</h2>
            <p>محفوظ لاگ ان</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    username = st.text_input("صارف کا نام", placeholder="مثلاً: admin")
    password = st.text_input("پاس ورڈ", type="password", placeholder="••••••")

    login_clicked = st.button("لاگ ان کریں")

    if login_clicked:
        if username == VALID_USER and password == VALID_PASS:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.markdown(
                '<div class="error-msg">غلط صارف کا نام یا پاس ورڈ</div>',
                unsafe_allow_html=True
            )

    st.markdown('</div></div>', unsafe_allow_html=True)

# ---------------- DASHBOARD ----------------
else:
    st.markdown('<div class="dashboard">', unsafe_allow_html=True)

    st.markdown("<h1>خوش آمدید 👋</h1>", unsafe_allow_html=True)
    st.write("یہ آپ کا **Dairy Master Pro** ڈیش بورڈ ہے۔")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("آج کی دودھ خرید", "1,250 لیٹر")

    with col2:
        st.metric("کل فروخت", "₨ 312,500")

    with col3:
        st.metric("بقایا رقم", "₨ 58,000")

    st.divider()

    st.subheader("سسٹم ایکشنز")

    if st.button("لاگ آؤٹ"):
        st.session_state.logged_in = False
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

