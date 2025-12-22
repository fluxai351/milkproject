import streamlit as st
from supabase import create_client
import urllib.parse
import pandas as pd

# --- 1. CONFIGURATION (Secrets) ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 2. SECURE LOGIN SYSTEM ---
def check_password():
    if "password_correct" not in st.session_state:
        st.markdown("""
            <style>
                .login-box {
                    background-color: white; padding: 2rem; border-radius: 15px;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.1); text-align: center;
                }
            </style>
            <div class="login-box"><h2>🔐 لاگ ان کریں</h2></div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            u = st.text_input("صارف کا نام")
            p = st.text_input("پاس ورڈ", type="password")
            if st.button("داخل ہوں"):
                if u == st.secrets["APP_USERNAME"] and p == st.secrets["APP_PASSWORD"]:
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("❌ غلط صارف یا پاس ورڈ")
        return False
    return True

# --- 3. UI SETTINGS & CSS ---
st.set_page_config(page_title="Dairy Master Pro", page_icon="🥛", layout="centered")

st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;700&display=swap" rel="stylesheet">
    <style>
        #MainMenu, footer, header {visibility: hidden;}
        html, body, [data-testid="stSidebar"], .stMarkdown {
            direction: rtl; text-align: right; font-family: 'Noto Nastaliq Urdu', serif !important;
        }
        .header-box {
            background: linear-gradient(135deg, #075E54 0%, #128C7E 100%);
            color: white; padding: 1.2rem; border-radius: 15px; text-align: center; margin-bottom: 20px;
        }
        .report-card {
            background-color: white; padding: 15px; border-radius: 10px; border-right: 5px solid #075E54;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 10px; color: black;
        }
        [data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; }
    </style>
""", unsafe_allow_html=True)

# --- APP EXECUTION ---
if check_password():
    st.markdown('<div class="header-box"><h1>🥛 ڈیری ماسٹر پرو</h1></div>', unsafe_allow_html=True)
    
    if st.sidebar.button("لاگ آؤٹ"):
        del st.session_state["password_correct"]
        st.rerun()

    page = st.sidebar.selectbox("مینو منتخب کریں", [
        "--- انتخاب کریں ---", "گاہک کی انٹری", "دودھ کی انٹری", 
        "رقم کی وصولی", "ونڈے کی انٹری", "اخراجات", 
        "مکمل کھاتہ رپورٹ", "منافع و نقصان"
    ])

    def get_customers():
        return supabase.table("customers").select("*").execute().data

    # --- PAGES LOGIC ---
    if page == "گاہک کی انٹری":
        st.subheader("👤 نئے گاہک کا اندراج")
        with st.form("c_form", clear_on_submit=True):
            name = st.text_input("نام")
            phone = st.text_input("واٹس ایپ (923...)")
            rate = st.number_input("ریٹ", value=200)
            if st.form_submit_button("سیو کریں"):
                supabase.table("customers").insert({"name": name, "phone": phone, "rate": rate}).execute()
                st.success("گاہک محفوظ ہو گیا!")

    elif page == "دودھ کی انٹری":
        st.subheader("🥛 روزانہ دودھ کی انٹری")
        custs = get_customers()
        if custs:
            c_dict = {c['name']: c for c in custs}
            s_name = st.selectbox("گاہک منتخب کریں", list(c_dict.keys()))
            with st.form("m_form", clear_on_submit=True):
                qty = st.number_input("مقدار (L)", min_value=0.5, step=0.5)
                if st.form_submit_button("محفوظ کریں"):
                    total = qty * c_dict[s_name]['rate']
                    supabase.table("milk_entries").insert({"customer_id": c_dict[s_name]['id'], "quantity": qty, "total_price": total}).execute()
                    st.success(f"انٹری مکمل! کل: {total}")
                    msg = urllib.parse.quote(f"آج کا دودھ: {qty}L\nٹوٹل: {total}Rs")
                    st.markdown(f'<a href="https://wa.me/{c_dict[s_name]["phone"]}?text={msg}" target="_blank" style="text-decoration:none;"><div style="background-color:#25D366;color:white;padding:10px;border-radius:10px;text-align:center;">رسید بھیجیں ✅</div></a>', unsafe_allow_html=True)

    elif page == "رقم کی وصولی":
        st.subheader("💸 رقم کی وصولی")
        custs = get_customers()
        if custs:
            c_names = {c['name']: c['id'] for c in custs}
            s_name = st.selectbox("گاہک", list(c_names.keys()))
            with st.form("p_form", clear_on_submit=True):
                amt = st.number_input("رقم", min_value=0)
                if st.form_submit_button("محفوظ کریں"):
                    supabase.table("payments").insert({"customer_id": c_names[s_name], "amount_paid": amt}).execute()
                    st.success("ادائیگی ریکارڈ ہو گئی!")

    elif page == "ونڈے کی انٹری":
        st.subheader("🌾 ونڈے کی انٹری")
        custs = get_customers()
        if custs:
            c_names = {c['name']: c['id'] for c in custs}
            s_name = st.selectbox("گاہک", list(c_names.keys()))
            with st.form("f_form", clear_on_submit=True):
                item = st.text_input("آئٹم")
                qty = st.number_input("مقدار", min_value=1.0)
                price = st.number_input("قیمت", min_value=0)
                if st.form_submit_button("سیو کریں"):
                    supabase.table("feed_entries").insert({"customer_id": c_names[s_name], "feed_name": item, "feed_qty": qty, "feed_price": price}).execute()
                    st.success("انٹری مکمل!")

    elif page == "اخراجات":
        st.subheader("📉 اخراجات")
        with st.form("e_form", clear_on_submit=True):
            t = st.text_input("تفصیل")
            a = st.number_input("رقم", min_value=0)
            if st.form_submit_button("سیو کریں"):
                supabase.table("expenses").insert({"title": t, "amount": a}).execute()
                st.success("خرچہ محفوظ!")

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
            st.markdown(f'<div class="report-card">دودھ بل: {m}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="report-card">ونڈہ بل: {f}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="report-card">ٹوٹل وصولی: {p}</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="background:{"#ff4b4b" if bal > 0 else "#25D366"}; color:white; padding:15px; border-radius:10px; text-align:center;"><h3>باقیہ: {bal} Rs</h3></div>', unsafe_allow_html=True)

    elif page == "منافع و نقصان":
        st.subheader("📈 نفع و نقصان")
        all_m = sum(x['total_price'] for x in supabase.table("milk_entries").select("total_price").execute().data)
        all_f = sum(x['feed_price'] for x in supabase.table("feed_entries").select("feed_price").execute().data)
        all_e = sum(x['amount'] for x in supabase.table("expenses").select("amount").execute().data)
        st.metric("ٹوٹل آمدن", f"{all_m + all_f} Rs")
        st.metric("ٹوٹل اخراجات", f"{all_e} Rs")
        st.success(f"خالص منافع: {(all_m + all_f) - all_e} Rs")

    else:
        st.info("بائیں مینو سے آپشن منتخب کریں۔")
