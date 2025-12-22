import streamlit as st
from supabase import create_client
import urllib.parse
import pandas as pd

# --- 1. CONFIGURATION ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 2. PROFESSIONAL UI/UX ARCHITECTURE ---
# Setting Favicon (Browser tab aur home screen icon ke liye)
st.set_page_config(
    page_title="Dairy Master Pro", 
    page_icon="🥛", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;700&display=swap" rel="stylesheet">
    <style>
        /* FULL BRANDING REMOVAL */
        header, footer, [data-testid="stHeader"], #MainMenu, .stDeployButton {
            visibility: hidden !important;
            display: none !important;
        }
        
        /* UNIVERSAL ADAPTABILITY & RTL */
        html, body, [data-testid="stSidebar"], .stMarkdown, p, h1, h2, h3, input, label, .stSelectbox {
            direction: rtl !important;
            text-align: right !important;
            font-family: 'Noto Nastaliq Urdu', serif !important;
        }

        /* FIXING MOBILE TEXT MIXING & LAYOUT */
        .block-container {
            padding-top: 0rem !important;
            max-width: 550px !important; 
            margin: auto;
        }

        @media (max-width: 768px) {
            [data-testid="column"] {
                width: 100% !important;
                flex: 1 1 100% !important;
                min-width: 100% !important;
                display: block !important;
            }
            .stMetric { margin-bottom: 20px !important; }
        }

        /* NATIVE APP STYLE HEADER */
        .header-box {
            background: linear-gradient(135deg, #075E54 0%, #128C7E 100%);
            color: white;
            padding: 30px 20px;
            border-radius: 0 0 30px 30px;
            text-align: center;
            margin: -1rem -1rem 25px -1rem;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }

        /* CARD-BASED UI */
        .stForm, .card {
            background: #ffffff !important;
            padding: 25px !important;
            border-radius: 20px !important;
            border: 1px solid #eee !important;
            box-shadow: 0 10px 25px rgba(0,0,0,0.05) !important;
            margin-bottom: 20px !important;
        }

        /* PREMIUM TOUCH BUTTONS */
        .stButton>button {
            background: linear-gradient(90deg, #075E54 0%, #128C7E 100%) !important;
            color: white !important;
            border-radius: 15px !important;
            height: 60px !important;
            font-weight: bold !important;
            font-size: 20px !important;
            border: none !important;
            box-shadow: 0 4px 10px rgba(7, 94, 84, 0.3) !important;
        }
        
        /* HIDE STREAMLIT ANCHORS */
        .st-emotion-cache-15z7884 { display: none !important; }
    </style>
""", unsafe_allow_html=True)

# --- 3. LOGIN SYSTEM ---
def login():
    if "authenticated" not in st.session_state:
        st.markdown('<div class="header-box"><h1>🔐 لاگ ان</h1><p style="color:#eee;">ڈیری ماسٹر پرو میں خوش آمدید</p></div>', unsafe_allow_html=True)
        with st.container():
            u = st.text_input("یوزر نیم")
            p = st.text_input("پاس ورڈ", type="password")
            if st.button("داخل ہوں"):
                if u == st.secrets["APP_USERNAME"] and p == st.secrets["APP_PASSWORD"]:
                    st.session_state["authenticated"] = True
                    st.rerun()
                else:
                    st.error("❌ یوزر نیم یا پاس ورڈ درست نہیں ہے۔")
        return False
    return True

# --- 4. DATA OPERATIONS ---
def get_customers():
    return supabase.table("customers").select("*").execute().data

# --- 5. MAIN APP INTERFACE ---
if login():
    st.markdown('<div class="header-box"><h1>🥛 ڈیری ماسٹر پرو</h1></div>', unsafe_allow_html=True)
    
    # Simple & Clean Sidebar Navigation
    st.sidebar.markdown("### 🛠️ مینو")
    page = st.sidebar.selectbox("کہاں جانا ہے؟", [
        "ہوم اسکرین", "گاہک کی انٹری", "دودھ کی انٹری", 
        "رقم کی وصولی", "ونڈے کی انٹری", "اخراجات", 
        "مکمل کھاتہ رپورٹ", "منافع و نقصان"
    ])
    
    if st.sidebar.button("لاگ آؤٹ"):
        del st.session_state["authenticated"]
        st.rerun()

    # --- PAGES ---
    if page == "ہوم اسکرین":
        st.markdown("""
            <div style="text-align:center; padding: 40px 20px;">
                <h2 style="color:#075E54;">خوش آمدید!</h2>
                <p>کام شروع کرنے کے لیے اوپر بائیں ہاتھ والے مینو (Sidebar) پر کلک کریں۔</p>
            </div>
        """, unsafe_allow_html=True)

    elif page == "گاہک کی انٹری":
        st.subheader("👤 نیا گاہک")
        with st.form("c_form", clear_on_submit=True):
            name = st.text_input("گاہک کا نام")
            phone = st.text_input("فون نمبر (923...)")
            rate = st.number_input("دودھ کا ریٹ", value=200)
            if st.form_submit_button("محفوظ کریں"):
                supabase.table("customers").insert({"name": name, "phone": phone, "rate": rate}).execute()
                st.success("گاہک ریکارڈ ہو گیا!")

    elif page == "دودھ کی انٹری":
        st.subheader("🥛 روزانہ دودھ")
        custs = get_customers()
        if custs:
            c_dict = {c['name']: c for c in custs}
            s_name = st.selectbox("گاہک منتخب کریں", list(c_dict.keys()))
            with st.form("m_form", clear_on_submit=True):
                qty = st.number_input("لیٹر کی مقدار", min_value=0.5, step=0.5)
                if st.form_submit_button("محفوظ کریں"):
                    total = qty * c_dict[s_name]['rate']
                    supabase.table("milk_entries").insert({"customer_id": c_dict[s_name]['id'], "quantity": qty, "total_price": total}).execute()
                    st.success(f"انٹری مکمل! بل: {total} Rs")
                    msg = urllib.parse.quote(f"آج کا دودھ: {qty}L\nٹوٹل: {total}Rs")
                    st.markdown(f'<a href="https://wa.me/{c_dict[s_name]["phone"]}?text={msg}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:15px;border-radius:15px;text-align:center;font-weight:bold;">WhatsApp رسید بھیجیں</div></a>', unsafe_allow_html=True)

    elif page == "رقم کی وصولی":
        st.subheader("💸 رقم کی وصولی")
        custs = get_customers()
        if custs:
            c_names = {c['name']: c['id'] for c in custs}
            s_name = st.selectbox("گاہک", list(c_names.keys()))
            with st.form("p_form", clear_on_submit=True):
                amt = st.number_input("وصول شدہ رقم", min_value=0)
                if st.form_submit_button("ریکارڈ کریں"):
                    supabase.table("payments").insert({"customer_id": c_names[s_name], "amount_paid": amt}).execute()
                    st.success("رقم وصول ہو گئی!")

    elif page == "ونڈے کی انٹری":
        st.subheader("🌾 ونڈہ انٹری")
        custs = get_customers()
        if custs:
            c_names = {c['name']: c['id'] for c in custs}
            s_name = st.selectbox("گاہک منتخب کریں", list(c_names.keys()))
            with st.form("f_form", clear_on_submit=True):
                item = st.text_input("آئٹم کا نام")
                qty = st.number_input("مقدار", min_value=1.0)
                price = st.number_input("کل قیمت", min_value=0)
                if st.form_submit_button("محفوظ کریں"):
                    supabase.table("feed_entries").insert({"customer_id": c_names[s_name], "feed_name": item, "feed_qty": qty, "feed_price": price}).execute()
                    st.success("فیڈ انٹری محفوظ!")

    elif page == "مکمل کھاتہ رپورٹ":
        st.subheader("📊 تفصیلی کھاتہ")
        custs = get_customers()
        if custs:
            c_dict = {c['name']: c for c in custs}
            s_name = st.selectbox("گاہک منتخب کریں", list(c_dict.keys()))
            cid = c_dict[s_name]['id']
            m = sum(x['total_price'] for x in supabase.table("milk_entries").select("total_price").eq("customer_id", cid).execute().data)
            p = sum(x['amount_paid'] for x in supabase.table("payments").select("amount_paid").eq("customer_id", cid).execute().data)
            f = sum(x['feed_price'] for x in supabase.table("feed_entries").select("feed_price").eq("customer_id", cid).execute().data)
            bal = (m + f) - p
            
            st.markdown(f"""
                <div style="background:#f9f9f9; padding:20px; border-radius:15px; border-right:10px solid #075E54; margin-bottom:20px;">
                    <p style="font-size:18px;">کل دودھ بل: <b>{m} Rs</b></p>
                    <p style="font-size:18px;">کل ونڈہ بل: <b>{f} Rs</b></p>
                    <p style="font-size:18px;">ٹوٹل وصولی: <b>{p} Rs</b></p>
                    <hr>
                    <h2 style="color:{'#d9534f' if bal > 0 else '#5cb85c'}; text-align:center;">باقیہ: {bal} Rs</h2>
                </div>
            """, unsafe_allow_html=True)

    elif page == "منافع و نقصان":
        st.subheader("📈 کاروبار کا خلاصہ")
        all_m = sum(x['total_price'] for x in supabase.table("milk_entries").select("total_price").execute().data)
        all_f = sum(x['feed_price'] for x in supabase.table("feed_entries").select("feed_price").execute().data)
        all_e = sum(x['amount'] for x in supabase.table("expenses").select("amount").execute().data)
        
        st.metric("ٹوٹل آمدن", f"{all_m + all_f} Rs")
        st.metric("ٹوٹل اخراجات", f"{all_e} Rs")
        profit = (all_m + all_f) - all_e
        st.markdown(f'<div style="text-align:center; padding:20px; background:#e8f5e9; border-radius:15px;"><h3>خالص منافع: {profit} Rs</h3></div>', unsafe_allow_html=True)
