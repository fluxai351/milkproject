import streamlit as st
from supabase import create_client
import urllib.parse
import pandas as pd

# --- 1. CONFIGURATION ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 2. THE ULTIMATE UI/UX FIX ---
st.set_page_config(page_title="Dairy Master Pro", page_icon="🥛", layout="centered")

st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;700&display=swap" rel="stylesheet">
    <style>
        /* Hide Streamlit elements */
        header, footer, #MainMenu {visibility: hidden; display: none;}
        
        /* RTL & Font Fix */
        html, body, [data-testid="stSidebar"], .stMarkdown, p, h1, h2, h3, label {
            direction: rtl !important;
            text-align: right !important;
            font-family: 'Noto Nastaliq Urdu', serif !important;
        }

        /* INPUT FIELDS PROFESSIONAL LOOK */
        /* Is se typing masla hal hoga mobile par */
        .stTextInput input, .stNumberInput input {
            direction: ltr !important; /* Numbers/Passwords usually LTR */
            text-align: right !important;
            border-radius: 12px !important;
            height: 50px !important;
            border: 2px solid #eee !important;
            font-size: 18px !important;
            padding: 10px !important;
            -webkit-appearance: none; /* Mobile Safari fix */
        }
        
        .stTextInput input:focus {
            border-color: #128C7E !important;
            box-shadow: 0 0 8px rgba(18, 140, 126, 0.2) !important;
        }

        /* HEADER BOX */
        .header-box {
            background: linear-gradient(135deg, #075E54 0%, #128C7E 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 25px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }

        /* MOBILE OPTIMIZATION */
        .block-container {
            padding-top: 2rem !important;
            max-width: 500px !important;
        }
        
        /* BUTTONS */
        .stButton>button {
            background: #075E54 !important;
            color: white !important;
            border-radius: 12px !important;
            height: 55px !important;
            width: 100% !important;
            border: none !important;
            font-size: 18px !important;
            font-weight: bold !important;
            margin-top: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGIN (Fixed for Mobile) ---
if "authenticated" not in st.session_state:
    st.markdown('<div class="header-box"><h1>🥛 لاگ ان</h1></div>', unsafe_allow_html=True)
    
    # Using a clean container for inputs
    with st.container():
        u = st.text_input("یوزر نیم (Username)", placeholder="admin")
        p = st.text_input("پاس ورڈ (Password)", type="password", placeholder="••••••••")
        
        if st.button("داخل ہوں"):
            if u == st.secrets["APP_USERNAME"] and p == st.secrets["APP_PASSWORD"]:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("❌ یوزر نیم یا پاس ورڈ غلط ہے۔")
    st.stop()

# --- 4. MAIN APP CONTENT ---
st.markdown('<div class="header-box"><h1>🥛 ڈیری ماسٹر پرو</h1></div>', unsafe_allow_html=True)

# Sidebar with better spacing
st.sidebar.markdown("### 📋 مین مینو")
page = st.sidebar.radio("منتخب کریں:", [
    "ہوم اسکرین", "گاہک کی انٹری", "دودھ کی انٹری", "رقم کی وصولی", 
    "ونڈے کی انٹری", "اخراجات", "مکمل کھاتہ رپورٹ", "منافع و نقصان"
])

if st.sidebar.button("لاگ آؤٹ"):
    del st.session_state["authenticated"]
    st.rerun()

# --- HELPERS ---
def get_customers():
    return supabase.table("customers").select("*").execute().data

# --- PAGES ---
if page == "ہوم اسکرین":
    st.info("خوش آمدید! مینو سے کام شروع کریں۔")

elif page == "گاہک کی انٹری":
    st.subheader("👤 نیا گاہک")
    with st.form("c_form", clear_on_submit=True):
        name = st.text_input("نام")
        phone = st.text_input("واٹس ایپ (923...)")
        rate = st.number_input("دودھ کا ریٹ", value=200)
        if st.form_submit_button("محفوظ کریں"):
            supabase.table("customers").insert({"name": name, "phone": phone, "rate": rate}).execute()
            st.success("گاہک محفوظ!")

elif page == "دودھ کی انٹری":
    st.subheader("🥛 روزانہ دودھ")
    custs = get_customers()
    if custs:
        c_dict = {c['name']: c for c in custs}
        s_name = st.selectbox("گاہک منتخب کریں", list(c_dict.keys()))
        with st.form("m_form", clear_on_submit=True):
            qty = st.number_input("مقدار (L)", min_value=0.1, step=0.1)
            if st.form_submit_button("انٹری کریں"):
                total = qty * c_dict[s_name]['rate']
                supabase.table("milk_entries").insert({"customer_id": c_dict[s_name]['id'], "quantity": qty, "total_price": total}).execute()
                st.success(f"بل: {total} Rs")
                msg = urllib.parse.quote(f"دودھ: {qty}L\nبل: {total}Rs")
                st.markdown(f'<a href="https://wa.me/{c_dict[s_name]["phone"]}?text={msg}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:12px;border-radius:10px;text-align:center;">WhatsApp رسید بھیجیں ✅</div></a>', unsafe_allow_html=True)

elif page == "ونڈے کی انٹری":
    st.subheader("🌾 ونڈہ انٹری")
    custs = get_customers()
    if custs:
        c_ids = {c['name']: c['id'] for c in custs}
        s_name = st.selectbox("گاہک", list(c_ids.keys()))
        with st.form("f_form", clear_on_submit=True):
            item = st.text_input("آئٹم")
            qty = st.number_input("مقدار", min_value=1.0)
            price = st.number_input("قیمت", min_value=0)
            if st.form_submit_button("سیو کریں"):
                supabase.table("feed_entries").insert({"customer_id": c_ids[s_name], "feed_name": item, "feed_qty": qty, "feed_price": price}).execute()
                st.success("محفوظ ہو گیا!")

elif page == "اخراجات":
    st.subheader("📉 اخراجات")
    with st.form("e_form", clear_on_submit=True):
        t = st.text_input("تفصیل")
        a = st.number_input("رقم", min_value=0)
        if st.form_submit_button("سیو کریں"):
            supabase.table("expenses").insert({"title": t, "amount": a}).execute()
            st.success("ریکارڈ محفوظ!")

elif page == "مکمل کھاتہ رپورٹ":
    st.subheader("📊 گاہک کا کھاتہ")
    custs = get_customers()
    if custs:
        c_dict = {c['name']: c['id'] for c in custs}
        s_name = st.selectbox("گاہک", list(c_dict.keys()))
        cid = c_dict[s_name]
        
        m = sum(x['total_price'] for x in supabase.table("milk_entries").select("total_price").eq("customer_id", cid).execute().data)
        p = sum(x['amount_paid'] for x in supabase.table("payments").select("amount_paid").eq("customer_id", cid).execute().data)
        f = sum(x['feed_price'] for x in supabase.table("feed_entries").select("feed_price").eq("customer_id", cid).execute().data)
        bal = (m + f) - p
        
        st.markdown(f'<div style="background:white; padding:15px; border-radius:10px; border-right:8px solid #075E54; margin-bottom:10px; box-shadow:0 2px 5px rgba(0,0,0,0.05);">دودھ: {m} | فیڈ: {f} | وصولی: {p}</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="text-align:center; background:{"#ff4b4b" if bal>0 else "#25D366"}; color:white; padding:15px; border-radius:10px;"><h3>باقیہ رقم: {bal} Rs</h3></div>', unsafe_allow_html=True)

elif page == "منافع و نقصان":
    st.subheader("📈 کاروبار کا نفع نقصان")
    all_m = sum(x['total_price'] for x in supabase.table("milk_entries").select("total_price").execute().data)
    all_f = sum(x['feed_price'] for x in supabase.table("feed_entries").select("feed_price").execute().data)
    all_e = sum(x['amount'] for x in supabase.table("expenses").select("amount").execute().data)
    
    st.metric("ٹوٹل آمدن", f"{all_m + all_f} Rs")
    st.metric("ٹوٹل اخراجات", f"{all_e} Rs")
    st.info(f"خالص منافع: {(all_m + all_f) - all_e} Rs")
