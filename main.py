import streamlit as st
from supabase import create_client
import pandas as pd
import urllib.parse

# ======================================================
# APP CONFIG
# ======================================================
st.set_page_config(
    page_title="Dairy Master Pro",
    page_icon="🥛",
    layout="wide"
)

# ======================================================
# GLOBAL STYLES (PRO UI)
# ======================================================
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;700&display=swap" rel="stylesheet">
<style>
#MainMenu, footer, header {visibility:hidden;}

html, body, [data-testid="stSidebar"], .stMarkdown, p, h1, h2, h3, input, label {
    direction: rtl;
    text-align: right;
    font-family: 'Noto Nastaliq Urdu', serif;
}

/* Centered container */
.center-box {
    max-width: 420px;
    margin: auto;
    margin-top: 10vh;
}

/* Card */
.card {
    background: white;
    padding: 28px;
    border-radius: 18px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
}

/* Header */
.app-header {
    background: linear-gradient(135deg,#075E54,#128C7E);
    color: white;
    padding: 22px;
    border-radius: 18px;
    text-align: center;
    margin-bottom: 25px;
}

/* Buttons */
.stButton button {
    background: #075E54;
    color: white;
    border-radius: 12px;
    height: 48px;
    font-size: 16px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ======================================================
# SUPABASE
# ======================================================
@st.cache_resource
def supabase_client():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

supabase = supabase_client()

# ======================================================
# LOGIN SCREEN (COMPLETELY REDESIGNED)
# ======================================================
def login_screen():
    st.markdown('<div class="center-box">', unsafe_allow_html=True)
    st.markdown("""
        <div class="card">
            <div class="app-header">
                <h2>🥛 Dairy Master Pro</h2>
                <p>محفوظ لاگ ان</p>
            </div>
    """, unsafe_allow_html=True)

    username = st.text_input("صارف کا نام", placeholder="مثلاً: admin")
    password = st.text_input("پاس ورڈ", type="password", placeholder="••••••")

    if st.button("لاگ ان کریں"):
        if (
            username == st.secrets["APP_USERNAME"] and
            password == st.secrets["APP_PASSWORD"]
        ):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("❌ غلط لاگ ان معلومات")

    st.markdown("</div></div>", unsafe_allow_html=True)

if not st.session_state.get("authenticated"):
    login_screen()
    st.stop()

# ======================================================
# MAIN APP HEADER
# ======================================================
st.markdown("""
<div class="app-header">
    <h1>🥛 ڈیری ماسٹر پرو</h1>
    <p>دودھ، ونڈہ، رقم اور منافع کا مکمل نظام</p>
</div>
""", unsafe_allow_html=True)

# ======================================================
# SIDEBAR
# ======================================================
st.sidebar.title("📋 مینو")
page = st.sidebar.radio(
    "انتخاب کریں",
    ["ہوم", "گاہک", "دودھ", "رقم", "ونڈہ", "اخراجات", "کھاتہ", "منافع"]
)

st.sidebar.markdown("---")
if st.sidebar.button("🚪 لاگ آؤٹ"):
    st.session_state.clear()
    st.rerun()

# ======================================================
# DATA
# ======================================================
@st.cache_data(ttl=300)
def customers():
    return supabase.table("customers").select("*").execute().data

cust = customers()
cust_map = {c["name"]: c for c in cust} if cust else {}

# ======================================================
# PAGES
# ======================================================
if page == "ہوم":
    st.success("خوش آمدید! بائیں جانب مینو سے کام منتخب کریں۔")

elif page == "گاہک":
    with st.container():
        st.subheader("👤 نیا گاہک")
        with st.form("cust"):
            name = st.text_input("نام")
            phone = st.text_input("واٹس ایپ نمبر")
            rate = st.number_input("دودھ ریٹ", value=200)
            if st.form_submit_button("محفوظ کریں"):
                supabase.table("customers").insert({
                    "name": name, "phone": phone, "rate": rate
                }).execute()
                st.success("✅ گاہک محفوظ ہو گیا")

elif page == "دودھ" and cust_map:
    cname = st.selectbox("گاہک منتخب کریں", cust_map.keys())
    with st.form("milk"):
        qty = st.number_input("لیٹر", min_value=0.1)
        if st.form_submit_button("سیو کریں"):
            total = qty * cust_map[cname]["rate"]
            supabase.table("milk_entries").insert({
                "customer_id": cust_map[cname]["id"],
                "quantity": qty,
                "total_price": total
            }).execute()
            st.success("🥛 دودھ محفوظ")

elif page == "منافع":
    milk = supabase.table("milk_entries").select("total_price").execute().data
    feed = supabase.table("feed_entries").select("feed_price").execute().data
    exp = supabase.table("expenses").select("amount").execute().data

    income = sum(x["total_price"] for x in milk) + sum(x["feed_price"] for x in feed)
    expenses = sum(x["amount"] for x in exp)

    st.metric("کل آمدن", f"{income} Rs")
    st.metric("کل اخراجات", f"{expenses} Rs")
    st.metric("خالص نتیجہ", f"{income-expenses} Rs")

