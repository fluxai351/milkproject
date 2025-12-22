import streamlit as st
from supabase import create_client
import urllib.parse
import pandas as pd

# --- 1. CONFIGURATION ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 2. PAGE CONFIG & STYLING ---
st.set_page_config(page_title="ڈیری ماسٹر پرو", page_icon="🥛", layout="wide")

st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;700&display=swap" rel="stylesheet">
    <style>
        html, body, [data-testid="stSidebar"], .stMarkdown, .stTextInput, .stNumberInput, .stSelectbox {
            direction: rtl; text-align: right; font-family: 'Noto Nastaliq Urdu', serif !important;
        }
        .header-box {
            background: linear-gradient(135deg, #075E54 0%, #128C7E 100%);
            color: white; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 25px;
        }
        .report-card {
            background-color: white; padding: 15px; border-radius: 10px; border-right: 5px solid #075E54;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 10px;
        }
        .stButton>button { background-color: #075E54; color: white; border-radius: 8px; width: 100%; }
    </style>
""", unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS ---
def get_customers():
    return supabase.table("customers").select("*").execute().data

# --- 4. HEADER ---
st.markdown('<div class="header-box"><h1>🥛 ڈیری ماسٹر پرو</h1></div>', unsafe_allow_html=True)

# --- 5. SIDEBAR (Fixed Navigation) ---
st.sidebar.markdown("### 📋 مین مینو")

# Main Category Selection
main_menu = st.sidebar.selectbox("کیٹیگری منتخب کریں:", 
    ["🛠️ ابتدائی کام", "💸 حساب کتاب", "📊 رپورٹ اور کھاتہ"])

# Sub-Menu Logic based on Category
if main_menu == "🛠️ ابتدائی کام":
    page = st.sidebar.radio("آپشن منتخب کریں:", ["گاہک کی انٹری", "دودھ کی انٹری"])
elif main_menu == "💸 حساب کتاب":
    page = st.sidebar.radio("آپشن منتخب کریں:", ["رقم کی وصولی", "ونڈے کی انٹری", "اخراجات (Expenses)"])
else:
    page = st.sidebar.radio("آپشن منتخب کریں:", ["مکمل کھاتہ رپورٹ", "منافع و نقصان", "اسٹاک رپورٹ"])

# --- 6. APP PAGES LOGIC ---

if page == "گاہک کی انٹری":
    st.subheader("👤 نئے گاہک کا اندراج")
    with st.form("c_form", clear_on_submit=True):
        name = st.text_input("گاہک کا نام")
        phone = st.text_input("واٹس ایپ نمبر (923...)")
        rate = st.number_input("دودھ کا ریٹ", value=200)
        if st.form_submit_button("محفوظ کریں"):
            supabase.table("customers").insert({"name": name, "phone": phone, "rate": rate}).execute()
            st.success("گاہک محفوظ ہو گیا!")

elif page == "دودھ کی انٹری":
    st.subheader("🥛 روزانہ دودھ کی انٹری")
    custs = get_customers()
    if custs:
        c_dict = {c['name']: c for c in custs}
        s_name = st.selectbox("گاہک منتخب کریں", list(c_dict.keys()))
        with st.form("m_form", clear_on_submit=True):
            qty = st.number_input("مقدار (لیٹر)", min_value=0.5, step=0.5)
            if st.form_submit_button("انٹری محفوظ کریں"):
                total = qty * c_dict[s_name]['rate']
                supabase.table("milk_entries").insert({"customer_id": c_dict[s_name]['id'], "quantity": qty, "total_price": total}).execute()
                st.success(f"{s_name} کی انٹری مکمل!")
                # WhatsApp link logic yahan add ho sakti hai

elif page == "رقم کی وصولی":
    st.subheader("💸 رقم کی وصولی")
    custs = get_customers()
    if custs:
        c_names = {c['name']: c['id'] for c in custs}
        s_name = st.selectbox("گاہک", list(c_names.keys()))
        with st.form("p_form", clear_on_submit=True):
            amt = st.number_input("وصول شدہ رقم", min_value=0)
            if st.form_submit_button("رقم محفوظ کریں"):
                supabase.table("payments").insert({"customer_id": c_names[s_name], "amount_paid": amt}).execute()
                st.success("ادائیگی ریکارڈ ہو گئی!")

elif page == "ونڈے کی انٹری":
    st.subheader("🌾 ونڈے / فیڈ کی انٹری")
    custs = get_customers()
    if custs:
        c_names = {c['name']: c['id'] for c in custs}
        s_name = st.selectbox("گاہک", list(c_names.keys()))
        with st.form("f_form", clear_on_submit=True):
            item = st.text_input("آئٹم کا نام")
            qty = st.number_input("مقدار", min_value=1.0)
            price = st.number_input("کل قیمت", min_value=0)
            if st.form_submit_button("سیو کریں"):
                supabase.table("feed_entries").insert({"customer_id": c_names[s_name], "feed_name": item, "feed_qty": qty, "feed_price": price}).execute()
                st.success("فیڈ انٹری مکمل!")

elif page == "اخراجات (Expenses)":
    st.subheader("📉 فارم کے اخراجات")
    with st.form("e_form", clear_on_submit=True):
        title = st.text_input("تفصیل (بجلی، پٹرول وغیرہ)")
        amt = st.number_input("رقم", min_value=0)
        if st.form_submit_button("خرچہ محفوظ کریں"):
            supabase.table("expenses").insert({"title": title, "amount": amt}).execute()
            st.success("خرچہ ریکارڈ ہو گیا!")

elif page == "مکمل کھاتہ رپورٹ":
    st.subheader("📊 گاہک کا کھاتہ")
    custs = get_customers()
    if custs:
        c_dict = {c['name']: c for c in custs}
        s_name = st.selectbox("گاہک منتخب کریں", list(c_dict.keys()))
        cid = c_dict[s_name]['id']
        
        m_data = supabase.table("milk_entries").select("total_price").eq("customer_id", cid).execute().data
        p_data = supabase.table("payments").select("amount_paid").eq("customer_id", cid).execute().data
        f_data = supabase.table("feed_entries").select("feed_price").eq("customer_id", cid).execute().data
        
        t_milk = sum(x['total_price'] for x in m_data)
        t_feed = sum(x['feed_price'] for x in f_data)
        t_paid = sum(x['amount_paid'] for x in p_data)
        bal = (t_milk + t_feed) - t_paid
        
        col1, col2, col3 = st.columns(3)
        col1.markdown(f'<div class="report-card"><h6>کل دودھ بل</h6><h4>{t_milk}</h4></div>', unsafe_allow_html=True)
        col2.markdown(f'<div class="report-card"><h6>کل ونڈہ بل</h6><h4>{t_feed}</h4></div>', unsafe_allow_html=True)
        col3.markdown(f'<div class="report-card"><h6>ٹوٹل وصولی</h6><h4>{t_paid}</h4></div>', unsafe_allow_html=True)
        
        st.markdown(f'<div style="background:{"#ff4b4b" if bal > 0 else "#25D366"}; color:white; padding:15px; border-radius:10px; text-align:center;"><h3>باقیہ رقم: {bal} Rs</h3></div>', unsafe_allow_html=True)

elif page == "منافع و نقصان":
    st.subheader("📈 نفع و نقصان کا خلاصہ")
    all_m = sum(x['total_price'] for x in supabase.table("milk_entries").select("total_price").execute().data)
    all_f = sum(x['feed_price'] for x in supabase.table("feed_entries").select("feed_price").execute().data)
    all_e = sum(x['amount'] for x in supabase.table("expenses").select("amount").execute().data)
    
    st.metric("ٹوٹل سیل (دودھ + ونڈہ)", f"{all_m + all_f} Rs")
    st.metric("ٹوٹل اخراجات", f"{all_e} Rs")
    st.success(f"خالص منافع: {(all_m + all_f) - all_e} Rs")

elif page == "اسٹاک رپورٹ":
    st.subheader("📦 ونڈے کا ریکارڈ")
    f_data = supabase.table("feed_entries").select("*").execute().data
    if f_data:
        st.table(pd.DataFrame(f_data)[['feed_name', 'feed_qty', 'feed_price']])
