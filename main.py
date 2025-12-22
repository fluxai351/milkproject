import streamlit as st
from supabase import create_client
import urllib.parse
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURATION ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 2. PAGE CONFIG & MODERN CSS ---
st.set_page_config(page_title="Dairy Master Pro", page_icon="🥛", layout="wide")

st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;700&display=swap" rel="stylesheet">
    <style>
        /* Global Styles */
        html, body, [data-testid="stSidebar"], .stMarkdown {
            direction: rtl;
            text-align: right;
            font-family: 'Noto Nastaliq Urdu', serif !important;
        }
        
        /* Main Container Styling */
        .main { background-color: #f4f7f6; }
        
        /* Professional Card Styling */
        .st-emotion-cache-1r6slb0 { border-radius: 15px; border: 1px solid #e0e0e0; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        
        /* Header Banner */
        .header-box {
            background: linear-gradient(90deg, #075E54 0%, #128C7E 100%);
            color: white;
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            margin-bottom: 25px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
        }

        /* Custom Button Styling */
        .stButton>button {
            background-color: #075E54;
            color: white;
            border-radius: 12px;
            height: 3em;
            width: 100%;
            font-weight: bold;
            border: none;
            transition: 0.3s;
        }
        .stButton>button:hover { background-color: #25D366; color: white; transform: scale(1.02); }

        /* Sidebar Styling */
        [data-testid="stSidebar"] { background-color: #ffffff; border-left: 1px solid #eee; }
        .sidebar-header { font-size: 24px; color: #075E54; font-weight: bold; text-align: center; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS ---
def get_customers():
    return supabase.table("customers").select("*").execute().data

# --- 4. HEADER ---
st.markdown('<div class="header-box"><h1>🥛 ڈیری ماسٹر پرو</h1><p>آپ کے کاروبار کا ڈیجیٹل ساتھی</p></div>', unsafe_allow_html=True)

# --- 5. SIDEBAR MENU (Urdu Logic) ---
st.sidebar.markdown('<div class="sidebar-header">مین مینو</div>', unsafe_allow_html=True)

menu_choice = None

with st.sidebar.expander("🛠️ ابتدائی کام", expanded=True):
    choice1 = st.radio("Chunain:", ["گاہک کی انٹری", "دودھ کی انٹری"], label_visibility="collapsed")
    if choice1: menu_choice = choice1

with st.sidebar.expander("💸 حساب کتاب"):
    choice2 = st.radio("Chunain:", ["رقم کی وصولی", "ونڈے کی انٹری"], label_visibility="collapsed")
    if choice2: menu_choice = choice2

with st.sidebar.expander("📊 حساب کا کھاتہ"):
    choice3 = st.radio("Chunain:", ["مکمل کھاتہ رپورٹ", "منافع نقصان"], label_visibility="collapsed")
    if choice3: menu_choice = choice3

# --- 6. APP LOGIC ---

# A. GAHAK ENTRY
if menu_choice == "گاہک کی انٹری":
    st.subheader("👤 نئے گاہک کا اندراج")
    with st.container():
        with st.form("c_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            name = col1.text_input("گاہک کا نام")
            phone = col2.text_input("فون نمبر (923...)")
            rate = st.number_input("دودھ کا فکس ریٹ", value=200)
            if st.form_submit_button("سیو کریں"):
                supabase.table("customers").insert({"name": name, "phone": phone, "rate": rate}).execute()
                st.success("گاہک کا ڈیٹا محفوظ ہو گیا!")

# B. DOODH ENTRY
elif menu_choice == "دودھ کی انٹری":
    st.subheader("🥛 روزانہ دودھ کی انٹری")
    custs = get_customers()
    if custs:
        c_dict = {c['name']: c for c in custs}
        s_name = st.selectbox("گاہک منتخب کریں", list(c_dict.keys()))
        selected = c_dict[s_name]
        
        with st.form("m_form"):
            qty = st.number_input("کتنا لیٹر؟", min_value=0.5, step=0.5)
            total = qty * selected['rate']
            st.write(f"**کل رقم:** {total} روپے")
            if st.form_submit_button("محفوظ کریں اور رسید بھیجیں"):
                supabase.table("milk_entries").insert({"customer_id": selected['id'], "quantity": qty, "total_price": total}).execute()
                msg = f"السلام علیکم {s_name}!\nآج کا دودھ: {qty} لیٹر\nکل رقم: {total} روپے."
                url = f"https://wa.me/{selected['phone']}?text={urllib.parse.quote(msg)}"
                st.markdown(f'<a href="{url}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366; color:white; padding:10px; border-radius:10px; text-align:center;">WhatsApp رسید ✅</div></a>', unsafe_allow_html=True)

# C. PAYMENTS (RAQAM WASOOLI)
elif menu_choice == "رقم کی وصولی":
    st.subheader("💸 رقم کی وصولی")
    custs = get_customers()
    if custs:
        c_names = {c['name']: c['id'] for c in custs}
        s_name = st.selectbox("گاہک", list(c_names.keys()))
        with st.form("p_form"):
            amt = st.number_input("کتنی رقم وصول کی؟", min_value=0)
            if st.form_submit_button("ادائیگی محفوظ کریں"):
                supabase.table("payments").insert({"customer_id": c_names[s_name], "amount_paid": amt}).execute()
                st.success("رقم کا اندراج ہو گیا!")

# D. WANDA ENTRY
elif menu_choice == "ونڈے کی انٹری":
    st.subheader("🌾 ونڈے کی انٹری")
    custs = get_customers()
    if custs:
        c_names = {c['name']: c['id'] for c in custs}
        s_name = st.selectbox("گاہک", list(c_names.keys()))
        with st.form("f_form"):
            item = st.text_input("آئٹم کا نام (ونڈا/چوکر)")
            f_qty = st.number_input("کلو/بوری", min_value=1)
            f_price = st.number_input("کل قیمت", min_value=0)
            if st.form_submit_button("ونڈہ انٹری کریں"):
                supabase.table("feed_entries").insert({"customer_id": c_names[s_name], "feed_name": item, "feed_qty": f_qty, "feed_price": f_price}).execute()
                st.success("ونڈے کی انٹری محفوظ ہو گئی!")

# E. KHAATA REPORT (FINAL SUMMARY)
elif menu_choice == "مکمل کھاتہ رپورٹ":
    st.subheader("📊 گاہک کا فائنل کھاتہ")
    custs = get_customers()
    if custs:
        c_dict = {c['name']: c for c in custs}
        s_name = st.selectbox("گاہک منتخب کریں", list(c_dict.keys()))
        cid = c_dict[s_name]['id']
        
        # Fetching all data for calculation
        m_data = supabase.table("milk_entries").select("total_price").eq("customer_id", cid).execute().data
        p_data = supabase.table("payments").select("amount_paid").eq("customer_id", cid).execute().data
        f_data = supabase.table("feed_entries").select("feed_price").eq("customer_id", cid).execute().data
        
        total_milk = sum(item['total_price'] for item in m_data)
        total_paid = sum(item['amount_paid'] for item in p_data)
        total_feed = sum(item['feed_price'] for item in f_data)
        
        balance = (total_milk + total_feed) - total_paid
        
        col1, col2, col3 = st.columns(3)
        col1.metric("کل دودھ بل", f"{total_milk} Rs")
        col2.metric("کل ونڈہ بل", f"{total_feed} Rs")
        col3.metric("ٹوٹل وصولی", f"{total_paid} Rs")
        
        st.markdown(f"""
            <div style="background-color: {'#ffcccc' if balance > 0 else '#ccffcc'}; padding: 20px; border-radius: 15px; text-align: center;">
                <h2>باقیہ رقم (Balance): {balance} Rs</h2>
            </div>
        """, unsafe_allow_html=True)
