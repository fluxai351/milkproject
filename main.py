import streamlit as st
from supabase import create_client
import urllib.parse
import pandas as pd

# --- 1. CONFIGURATION ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 2. UNIVERSAL UI/UX FIX ---
st.set_page_config(page_title="Dairy Master Pro", page_icon="🥛", layout="wide")

st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;700&display=swap" rel="stylesheet">
    <style>
        /* 1. Hide Branding but keep functionality */
        header, footer, #MainMenu {visibility: hidden; display: none;}
        
        /* 2. Professional RTL Font */
        html, body, [data-testid="stSidebar"], .stMarkdown, p, h1, h2, h3, input, label {
            direction: rtl !important;
            text-align: right !important;
            font-family: 'Noto Nastaliq Urdu', serif !important;
        }

        /* 3. The "Anti-Khichri" Layout Fix */
        .main .block-container {
            max-width: 800px !important; /* Perfect for both Laptop and Mobile */
            padding-top: 1rem !important;
        }

        /* 4. Professional Header */
        .header-box {
            background: linear-gradient(135deg, #075E54 0%, #128C7E 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 25px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }

        /* 5. Card Styling */
        .report-card {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 12px;
            border-right: 8px solid #075E54;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            margin-bottom: 15px;
            color: #333;
        }

        /* 6. Buttons */
        .stButton>button {
            background-color: #075E54 !important;
            color: white !important;
            border-radius: 10px !important;
            width: 100% !important;
            height: 50px;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGIN ---
if "authenticated" not in st.session_state:
    st.markdown('<div class="header-box"><h1>🔐 لاگ ان</h1></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        u = st.text_input("صارف کا نام")
        p = st.text_input("پاس ورڈ", type="password")
        if st.button("داخل ہوں"):
            if u == st.secrets["APP_USERNAME"] and p == st.secrets["APP_PASSWORD"]:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("غلط پاس ورڈ")
    st.stop()

# --- 4. APP START ---
st.markdown('<div class="header-box"><h1>🥛 ڈیری ماسٹر پرو</h1></div>', unsafe_allow_html=True)

# Sidebar Menu
st.sidebar.title("مینو")
page = st.sidebar.radio("انتخاب کریں:", 
    ["ہوم اسکرین", "گاہک کی انٹری", "دودھ کی انٹری", "رقم کی وصولی", "ونڈے کی انٹری", "اخراجات", "مکمل کھاتہ رپورٹ", "منافع و نقصان"])

if st.sidebar.button("لاگ آؤٹ"):
    del st.session_state["authenticated"]
    st.rerun()

def get_customers():
    return supabase.table("customers").select("*").execute().data

# --- PAGES ---
if page == "ہوم اسکرین":
    st.write("### خوش آمدید!")
    st.write("بائیں طرف موجود مینو سے کام شروع کریں۔")

elif page == "گاہک کی انٹری":
    st.write("### 👤 نیا گاہک")
    with st.form("c", clear_on_submit=True):
        name = st.text_input("نام")
        phone = st.text_input("فون (923...)")
        rate = st.number_input("ریٹ", value=200)
        if st.form_submit_button("سیو کریں"):
            supabase.table("customers").insert({"name": name, "phone": phone, "rate": rate}).execute()
            st.success("گاہک محفوظ!")

elif page == "دودھ کی انٹری":
    st.write("### 🥛 دودھ کا حساب")
    custs = get_customers()
    if custs:
        c_names = {c['name']: c for c in custs}
        s_name = st.selectbox("گاہک", list(c_names.keys()))
        with st.form("m", clear_on_submit=True):
            qty = st.number_input("لیٹر", min_value=0.5, step=0.5)
            if st.form_submit_button("محفوظ کریں"):
                total = qty * c_names[s_name]['rate']
                supabase.table("milk_entries").insert({"customer_id": c_names[s_name]['id'], "quantity": qty, "total_price": total}).execute()
                st.success(f"بل: {total}")
                msg = urllib.parse.quote(f"آج کا دودھ: {qty}L\nبل: {total}Rs")
                st.markdown(f'[واٹس ایپ رسید بھیجیں](https://wa.me/{c_names[s_name]["phone"]}?text={msg})')

elif page == "رقم کی وصولی":
    st.write("### 💸 وصولی")
    custs = get_customers()
    if custs:
        c_ids = {c['name']: c['id'] for c in custs}
        s_name = st.selectbox("گاہک", list(c_ids.keys()))
        with st.form("p", clear_on_submit=True):
            amt = st.number_input("رقم", min_value=0)
            if st.form_submit_button("سیو کریں"):
                supabase.table("payments").insert({"customer_id": c_ids[s_name], "amount_paid": amt}).execute()
                st.success("وصولی ریکارڈ ہو گئی!")

elif page == "مکمل کھاتہ رپورٹ":
    st.write("### 📊 گاہک کھاتہ")
    custs = get_customers()
    if custs:
        c_dict = {c['name']: c['id'] for c in custs}
        s_name = st.selectbox("گاہک منتخب کریں", list(c_dict.keys()))
        cid = c_dict[s_name]
        
        # Data fetch
        m = sum(x['total_price'] for x in supabase.table("milk_entries").select("total_price").eq("customer_id", cid).execute().data)
        p = sum(x['amount_paid'] for x in supabase.table("payments").select("amount_paid").eq("customer_id", cid).execute().data)
        f = sum(x['feed_price'] for x in supabase.table("feed_entries").select("feed_price").eq("customer_id", cid).execute().data)
        
        st.markdown(f'<div class="report-card">دودھ: {m} Rs</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="report-card">ونڈہ: {f} Rs</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="report-card">وصولی: {p} Rs</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align:center; background:{"#ff4b4b" if (m+f-p)>0 else "#25D366"}; color:white; padding:15px; border-radius:10px;"><h3>باقیہ: {m+f-p} Rs</h3></div>', unsafe_allow_html=True)

# Note: Baqi pages (Expenses, Profit Loss) bhi isi pattern par add kar dein.
