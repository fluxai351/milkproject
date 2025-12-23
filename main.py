# =========================================================
# 🥛 DAIRY MASTER PRO — PRODUCTION BUILD
# Senior-Optimized | Urdu RTL | Supabase Backend
# =========================================================

import streamlit as st
from supabase import create_client
import urllib.parse
import pandas as pd

# =========================================================
# 1. APP CONFIG (NO STREAMLIT BRANDING)
# =========================================================

st.set_page_config(
    page_title="Dairy Master Pro",
    page_icon="🥛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# 2. GLOBAL STYLING (RTL + HIDE STREAMLIT/GITHUB)
# =========================================================

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;700&display=swap" rel="stylesheet">

<style>
/* Hide Streamlit & GitHub branding */
#MainMenu, footer, header {visibility: hidden;}
a[href*="github"], a[href*="streamlit"] {display:none !important;}

/* RTL + Urdu */
html, body, [data-testid="stSidebar"], .stMarkdown, p, h1, h2, h3, h4, input, label {
    direction: rtl !important;
    text-align: right !important;
    font-family: 'Noto Nastaliq Urdu', serif !important;
}

/* Layout */
.main .block-container {
    max-width: 900px;
    padding-top: 1rem;
}

/* Header */
.header-box {
    background: linear-gradient(135deg, #075E54, #128C7E);
    color: white;
    padding: 22px;
    border-radius: 16px;
    text-align: center;
    margin-bottom: 25px;
}

/* Cards */
.report-card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    border-right: 8px solid #075E54;
    box-shadow: 0 4px 8px rgba(0,0,0,0.05);
    margin-bottom: 12px;
    color: #333;
}

/* Buttons */
.stButton > button {
    background-color: #075E54 !important;
    color: white !important;
    border-radius: 12px;
    width: 100%;
    height: 48px;
    font-weight: bold;
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# 3. SUPABASE CLIENT (CACHED)
# =========================================================

@st.cache_resource
def get_supabase():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

supabase = get_supabase()

# =========================================================
# 4. AUTHENTICATION (SECURE & CLEAN)
# =========================================================

def login_guard():
    if not st.session_state.get("authenticated"):
        st.markdown('<div class="header-box"><h1>🔐 لاگ ان</h1></div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            username = st.text_input("صارف کا نام")
            password = st.text_input("پاس ورڈ", type="password")
            if st.button("داخل ہوں"):
                if (
                    username == st.secrets["APP_USERNAME"] and
                    password == st.secrets["APP_PASSWORD"]
                ):
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("غلط معلومات")
        st.stop()

login_guard()

# =========================================================
# 5. DATA ACCESS LAYER
# =========================================================

@st.cache_data(ttl=300)
def fetch_customers():
    return supabase.table("customers").select("id,name,phone,rate").execute().data

def safe_insert(table, data):
    try:
        supabase.table(table).insert(data).execute()
        return True
    except Exception:
        st.error("ڈیٹا محفوظ نہیں ہو سکا")
        return False

@st.cache_data(ttl=120)
def customer_ledger(cid):
    milk = supabase.table("milk_entries").select("total_price").eq("customer_id", cid).execute().data
    pay = supabase.table("payments").select("amount_paid").eq("customer_id", cid).execute().data
    feed = supabase.table("feed_entries").select("feed_price").eq("customer_id", cid).execute().data

    return (
        sum(x["total_price"] for x in milk),
        sum(x["feed_price"] for x in feed),
        sum(x["amount_paid"] for x in pay)
    )

@st.cache_data(ttl=120)
def profit_loss():
    milk = supabase.table("milk_entries").select("total_price").execute().data
    feed = supabase.table("feed_entries").select("feed_price").execute().data
    exp = supabase.table("expenses").select("amount").execute().data

    income = sum(x["total_price"] for x in milk) + sum(x["feed_price"] for x in feed)
    expenses = sum(x["amount"] for x in exp)
    return income, expenses

# =========================================================
# 6. APP HEADER + SIDEBAR
# =========================================================

st.markdown('<div class="header-box"><h1>🥛 ڈیری ماسٹر پرو</h1></div>', unsafe_allow_html=True)

st.sidebar.title("📋 مینو")
page = st.sidebar.radio(
    "انتخاب کریں:",
    ["ہوم", "گاہک", "دودھ", "رقم", "ونڈہ", "اخراجات", "کھاتہ", "منافع / نقصان"]
)

if st.sidebar.button("لاگ آؤٹ"):
    st.session_state.clear()
    st.rerun()

customers = fetch_customers()
cust_map = {c["name"]: c for c in customers} if customers else {}

# =========================================================
# 7. PAGES
# =========================================================

if page == "ہوم":
    st.success("خوش آمدید! بائیں طرف مینو سے آپشن منتخب کریں۔")

elif page == "گاہک":
    with st.form("customer_form", clear_on_submit=True):
        name = st.text_input("نام")
        phone = st.text_input("واٹس ایپ نمبر (923...)")
        rate = st.number_input("دودھ ریٹ", min_value=1, value=200)
        if st.form_submit_button("محفوظ کریں") and name and phone:
            if safe_insert("customers", {"name": name, "phone": phone, "rate": rate}):
                st.success("گاہک محفوظ ہو گیا")

elif page == "دودھ" and cust_map:
    cname = st.selectbox("گاہک", cust_map.keys())
    with st.form("milk_form", clear_on_submit=True):
        qty = st.number_input("لیٹر", min_value=0.1, step=0.1)
        if st.form_submit_button("سیو کریں"):
            total = qty * cust_map[cname]["rate"]
            if safe_insert("milk_entries", {
                "customer_id": cust_map[cname]["id"],
                "quantity": qty,
                "total_price": total
            }):
                st.success("دودھ محفوظ")
                msg = urllib.parse.quote(f"دودھ: {qty}L\nبل: {total}Rs")
                st.markdown(f"[واٹس ایپ رسید](https://wa.me/{cust_map[cname]['phone']}?text={msg})")

elif page == "رقم" and cust_map:
    cname = st.selectbox("گاہک", cust_map.keys())
    with st.form("pay_form", clear_on_submit=True):
        amt = st.number_input("رقم", min_value=1)
        if st.form_submit_button("محفوظ کریں"):
            if safe_insert("payments", {"customer_id": cust_map[cname]["id"], "amount_paid": amt}):
                st.success("رقم محفوظ")

elif page == "ونڈہ" and cust_map:
    cname = st.selectbox("گاہک", cust_map.keys())
    with st.form("feed_form", clear_on_submit=True):
        item = st.text_input("آئٹم")
        qty = st.number_input("مقدار", min_value=1.0)
        price = st.number_input("قیمت", min_value=1)
        if st.form_submit_button("محفوظ کریں") and item:
            safe_insert("feed_entries", {
                "customer_id": cust_map[cname]["id"],
                "feed_name": item,
                "feed_qty": qty,
                "feed_price": price
            })
            st.success("ونڈہ محفوظ")

elif page == "اخراجات":
    with st.form("exp_form", clear_on_submit=True):
        title = st.text_input("تفصیل")
        amt = st.number_input("رقم", min_value=1)
        if st.form_submit_button("سیو کریں") and title:
            safe_insert("expenses", {"title": title, "amount": amt})
            st.success("خرچہ محفوظ")

elif page == "کھاتہ" and cust_map:
    cname = st.selectbox("گاہک", cust_map.keys())
    milk, feed, pay = customer_ledger(cust_map[cname]["id"])
    balance = (milk + feed) - pay

    st.markdown(f'<div class="report-card">دودھ بل: {milk} Rs</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="report-card">ونڈہ بل: {feed} Rs</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="report-card">وصولی: {pay} Rs</div>', unsafe_allow_html=True)

    color = "#ff4b4b" if balance > 0 else "#25D366"
    st.markdown(
        f'<div style="background:{color};color:white;padding:15px;border-radius:12px;text-align:center">'
        f'<h3>بقایا: {balance} Rs</h3></div>',
        unsafe_allow_html=True
    )

elif page == "منافع / نقصان":
    income, expenses = profit_loss()
    net = income - expenses

    st.metric("کل آمدن", f"{income} Rs")
    st.metric("کل اخراجات", f"{expenses} Rs")

    if net >= 0:
        st.success(f"خالص منافع: {net} Rs")
    else:
        st.error(f"خالص نقصان: {abs(net)} Rs")

