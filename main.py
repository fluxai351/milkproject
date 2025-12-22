import streamlit as st
from supabase import create_client
import urllib.parse
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURATION ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 2. PROFESSIONAL URDU UI/UX SETTINGS ---
st.set_page_config(page_title="ڈیری ماسٹر پرو", page_icon="🥛", layout="wide")

st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;700&display=swap" rel="stylesheet">
    <style>
        html, body, [data-testid="stSidebar"], .stMarkdown, .stTextInput, .stNumberInput, .stSelectbox {
            direction: rtl; text-align: right; font-family: 'Noto Nastaliq Urdu', serif !important;
        }
        .main { background-color: #f0f2f6; }
        .header-box {
            background: linear-gradient(135deg, #075E54 0%, #128C7E 100%);
            color: white; padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 25px;
        }
        .stButton>button {
            background-color: #075E54; color: white; border-radius: 10px; width: 100%; font-weight: bold; border: none; padding: 10px;
        }
        .stButton>button:hover { background-color: #25D366; color: white; border: none; }
        .report-card {
            background-color: white; padding: 20px; border-radius: 15px; border-right: 5px solid #075E54;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 15px;
        }
    </style>
""", unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS ---
def get_customers():
    return supabase.table("customers").select("*").execute().data

# --- 4. HEADER ---
st.markdown('<div class="header-box"><h1>🥛 ڈیری ماسٹر (پرو ورژن)</h1><p>آپ کے فارم کا مکمل حساب کتاب</p></div>', unsafe_allow_html=True)

# --- 5. SIDEBAR NAVIGATION ---
st.sidebar.markdown("### مین مینو")

# Sub-menus as Expander
menu_choice = "Dashboard"

with st.sidebar.expander("🛠️ ابتدائی کام", expanded=True):
    choice1 = st.radio("", ["گاہک کی انٹری", "دودھ کی انٹری"], key="m1", label_visibility="collapsed")
    if choice1: menu_choice = choice1

with st.sidebar.expander("💸 حساب کتاب"):
    choice2 = st.radio("", ["رقم کی وصولی", "ونڈے کی انٹری", "اخراجات (Expenses)"], key="m2", label_visibility="collapsed")
    if choice2: menu_choice = choice2

with st.sidebar.expander("📊 رپورٹ اور کھاتہ"):
    choice3 = st.radio("", ["مکمل کھاتہ رپورٹ", "منافع و نقصان", "اسٹاک رپورٹ"], key="m3", label_visibility="collapsed")
    if choice3: menu_choice = choice3

# --- 6. APP LOGIC ---

# A. GAHAK ENTRY
if menu_choice == "گاہک کی انٹری":
    st.markdown("### 👤 نئے گاہک کا اندراج")
    with st.form("cust_form", clear_on_submit=True):
        name = st.text_input("گاہک کا نام")
        phone = st.text_input("واٹس ایپ نمبر (923...)")
        rate = st.number_input("دودھ کا ریٹ (فی لیٹر)", value=200)
        if st.form_submit_button("محفوظ کریں"):
            if name and phone:
                supabase.table("customers").insert({"name": name, "phone": phone, "rate": rate}).execute()
                st.success("گاہک کا ڈیٹا محفوظ ہو گیا!")

# B. MILK ENTRY
elif menu_choice == "دودھ کی انٹری":
    st.markdown("### 🥛 روزانہ دودھ کی انٹری")
    custs = get_customers()
    if custs:
        c_dict = {c['name']: c for c in custs}
        s_name = st.selectbox("گاہک منتخب کریں", list(c_dict.keys()))
        selected = c_dict[s_name]
        with st.form("milk_form", clear_on_submit=True):
            qty = st.number_input("مقدار (لیٹر)", min_value=0.5, step=0.5)
            if st.form_submit_button("انٹری محفوظ کریں"):
                total = qty * selected['rate']
                supabase.table("milk_entries").insert({"customer_id": selected['id'], "quantity": qty, "total_price": total}).execute()
                st.success(f"{s_name} کی {qty} لیٹر انٹری ہو گئی۔")
                # WhatsApp
                msg = f"السلام علیکم {s_name}!\nآج کا دودھ: {qty}L\nریٹ: {selected['rate']}\nٹوٹل: {total}Rs."
                url = f"https://wa.me/{selected['phone']}?text={urllib.parse.quote(msg)}"
                st.markdown(f'<a href="{url}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366; color:white; padding:10px; border-radius:10px; text-align:center;">واٹس ایپ رسید بھیجیں ✅</div></a>', unsafe_allow_html=True)

# C. PAYMENTS
elif menu_choice == "رقم کی وصولی":
    st.markdown("### 💸 رقم کی وصولی (Cash Received)")
    custs = get_customers()
    if custs:
        c_names = {c['name']: c['id'] for c in custs}
        s_name = st.selectbox("گاہک", list(c_names.keys()))
        with st.form("pay_form", clear_on_submit=True):
            amt = st.number_input("وصول شدہ رقم", min_value=0)
            if st.form_submit_button("رقم محفوظ کریں"):
                supabase.table("payments").insert({"customer_id": c_names[s_name], "amount_paid": amt}).execute()
                st.success("ادائیگی ریکارڈ کر لی گئی۔")

# D. WANDA/FEED
elif menu_choice == "ونڈے کی انٹری":
    st.markdown("### 🌾 ونڈے / چوکر کا حساب")
    custs = get_customers()
    if custs:
        c_names = {c['name']: c['id'] for c in custs}
        s_name = st.selectbox("گاہک", list(c_names.keys()))
        with st.form("f_form", clear_on_submit=True):
            item = st.text_input("آئٹم (ونڈا، چوکر وغیرہ)")
            f_qty = st.number_input("مقدار (بوری/کلو)", min_value=1.0)
            f_price = st.number_input("کل قیمت", min_value=0)
            if st.form_submit_button("ونڈہ محفوظ کریں"):
                supabase.table("feed_entries").insert({"customer_id": c_names[s_name], "feed_name": item, "feed_qty": f_qty, "feed_price": f_price}).execute()
                st.success("فیڈ کی انٹری ہو گئی۔")

# E. EXPENSES
elif menu_choice == "اخراجات (Expenses)":
    st.markdown("### 📉 فارم کے اخراجات")
    with st.form("exp_form", clear_on_submit=True):
        title = st.text_input("خرچے کی تفصیل (بجلی بل، پٹرول، مزدوری وغیرہ)")
        amt = st.number_input("رقم", min_value=0)
        if st.form_submit_button("خرچہ محفوظ کریں"):
            supabase.table("expenses").insert({"title": title, "amount": amt}).execute()
            st.success("خرچہ ریکارڈ ہو گیا!")

# F. KHAATA REPORT
elif menu_choice == "مکمل کھاتہ رپورٹ":
    st.markdown("### 📊 گاہک کا تفصیلی کھاتہ")
    custs = get_customers()
    if custs:
        c_dict = {c['name']: c for c in custs}
        s_name = st.selectbox("گاہک منتخب کریں", list(c_dict.keys()))
        cid = c_dict[s_name]['id']
        
        m_data = supabase.table("milk_entries").select("*").eq("customer_id", cid).execute().data
        p_data = supabase.table("payments").select("*").eq("customer_id", cid).execute().data
        f_data = supabase.table("feed_entries").select("*").eq("customer_id", cid).execute().data
        
        t_milk = sum(x['total_price'] for x in m_data)
        t_feed = sum(x['feed_price'] for x in f_data)
        t_paid = sum(x['amount_paid'] for x in p_data)
        balance = (t_milk + t_feed) - t_paid
        
        col1, col2, col3 = st.columns(3)
        col1.markdown(f'<div class="report-card"><h4>ٹوٹل دودھ</h4><h2>{t_milk}</h2></div>', unsafe_allow_html=True)
        col2.markdown(f'<div class="report-card"><h4>ٹوٹل ونڈہ</h4><h2>{t_feed}</h2></div>', unsafe_allow_html=True)
        col3.markdown(f'<div class="report-card"><h4>ٹوٹل وصولی</h4><h2>{t_paid}</h2></div>', unsafe_allow_html=True)
        
        color = "#ff4b4b" if balance > 0 else "#25D366"
        st.markdown(f'<div style="background:{color}; color:white; padding:20px; border-radius:15px; text-align:center;"><h3>باقیہ رقم (Balance): {balance} Rs</h3></div>', unsafe_allow_html=True)

# G. PROFIT/LOSS
elif menu_choice == "منافع و نقصان":
    st.markdown("### 📈 کاروبار کا خلاصہ")
    all_milk = sum(x['total_price'] for x in supabase.table("milk_entries").select("total_price").execute().data)
    all_feed = sum(x['feed_price'] for x in supabase.table("feed_entries").select("feed_price").execute().data)
    all_exp = sum(x['amount'] for x in supabase.table("expenses").select("amount").execute().data)
    
    total_income = all_milk + all_feed
    profit = total_income - all_exp
    
    col1, col2 = st.columns(2)
    col1.metric("ٹوٹل آمدن (Milk+Feed)", f"{total_income} Rs")
    col2.metric("ٹوٹل اخراجات", f"{all_exp} Rs")
    
    st.markdown(f'<div class="report-card" style="text-align:center;"><h3>خالص منافع (Net Profit): {profit} Rs</h3></div>', unsafe_allow_html=True)

# H. STOCK REPORT
elif menu_choice == "اسٹاک رپورٹ":
    st.markdown("### 📦 اسٹاک کی تفصیلات")
    feed_data = supabase.table("feed_entries").select("*").execute().data
    if feed_data:
        df = pd.DataFrame(feed_data)
        st.table(df[['feed_name', 'feed_qty', 'feed_price']])
