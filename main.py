import streamlit as st
from supabase import create_client
import urllib.parse
import pandas as pd

# --- 1. CONFIGURATION (From Secrets) ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 2. PAGE SETUP & LOGO ---
st.set_page_config(page_title="Doodh Wala App", page_icon="🥛", layout="wide")

# Urdu Styling for Right-to-Left feel
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&display=swap');
    html, body, [data-testid="stSidebar"] {
        text-align: right;
        direction: rtl;
        font-family: 'Noto Nastaliq Urdu', serif;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        background-color: #075E54;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# Logo aur Header
col1, col2 = st.columns([1, 4])
with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/372/372971.png", width=80) # Default Logo
with col2:
    st.title("🥛 دودھ مینجمنٹ سسٹم")

# --- 3. SIDEBAR NAVIGATION (Urdu Menu) ---
st.sidebar.header("مین مینو")

# Dropdown 1: ابتدائی کام
with st.sidebar.expander("🛠️ ابتدائی کام", expanded=True):
    sub_menu1 = st.radio("", ["گاہک کی انٹری", "دودھ کی انٹری"])

# Dropdown 2: حساب کتاب
with st.sidebar.expander("💸 حساب کتاب"):
    sub_menu2 = st.radio("", ["دودھ کی وصولی", "رقم کی اندراج", "ونڈے کی انٹری"])

# Dropdown 3: حساب کا کھاتہ
with st.sidebar.expander("📊 حساب کا کھاتہ"):
    sub_menu3 = st.radio("", ["منافع نقصان رپورٹ", "کھاتہ رقم کے ساتھ"])

# --- 4. LOGIC ---

if sub_menu1 == "گاہک کی انٹری":
    st.header("👤 نئے گاہک کا اندراج")
    with st.form("cust_form"):
        name = st.text_input("گاہک کا نام")
        phone = st.text_input("واٹس ایپ نمبر")
        rate = st.number_input("ریٹ", value=200)
        if st.form_submit_button("محفوظ کریں"):
            supabase.table("customers").insert({"name": name, "phone": phone, "rate": rate}).execute()
            st.success("گاہک کا ڈیٹا محفوظ ہو گیا!")

elif sub_menu1 == "دودھ کی انٹری":
    st.header("🥛 روزانہ دودھ کی انٹری")
    # Yahan hum purana wala Daily Entry ka logic dalenge (Urdu labels ke sath)
    st.info("یہاں سے روزانہ کا دودھ ڈالیں")
    # ... baki code (hum bari bari add karenge)

# ... isi tarah baki features add hote jayenge
