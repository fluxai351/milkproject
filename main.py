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
        header, footer, #MainMenu {visibility: hidden; display: none;}
        html, body, [data-testid="stSidebar"], .stMarkdown, p, h1, h2, h3, input, label {
            direction: rtl !important; text-align: right !important;
            font-family: 'Noto Nastaliq Urdu', serif !important;
        }
        .main .block-container { max-width: 800px !important; padding-top: 1rem !important; }
        .header-box {
            background: linear-gradient(135deg, #075E54 0%, #128C7E 100%);
            color: white; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 25px;
        }
        .report-card {
            background-color: #ffffff; padding: 20px; border-radius: 12px;
            border-right: 8px solid #075E54; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
            margin-bottom: 15px; color: #333;
        }
        .stButton>button {
            background-color: #075E54 !important; color: white !important;
            border-radius: 10px !important; width: 100% !important; height: 50px; font-weight: bold;
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
    st.info("بائیں طرف موجود مینو سے کسی بھی آپشن کا انتخاب کریں۔")

elif page == "گاہک کی انٹری":
    st.write("### 👤 نیا گاہک")
    with st.form("c_form", clear_on_submit=True):
        name = st.text_input("نام")
        phone = st.text_input("واٹس ایپ نمبر (923...)")
        rate = st.number_input("دودھ کا ریٹ", value=200)
        if st.form_submit_button("محفوظ کریں"):
            if name and phone:
                supabase.table("customers").insert({"name": name, "phone": phone, "rate": rate}).execute()
                st.success(f"گاہک {name} محفوظ ہو گیا!")

elif page == "دودھ کی انٹری":
    st.write("### 🥛 روزانہ دودھ کی انٹری")
    custs = get_customers()
    if custs:
        c_dict = {c['name']: c for c in custs}
        s_name = st.selectbox("گاہک منتخب کریں", list(c_dict.keys()))
        with st.form("m_form", clear_on_submit=True):
            qty = st.number_input("مقدار (لیٹر)", min_value=0.1, step=0.1)
            if st.form_submit_button("سیو کریں"):
                total = qty * c_dict[s_name]['rate']
                supabase.table("milk_entries").insert({"customer_id": c_dict[s_name]['id'], "quantity": qty, "total_price": total}).execute()
                st.success("انٹری مکمل!")
                msg = urllib.parse.quote(f"آج کا دودھ: {qty}L\nبل: {total}Rs")
                st.markdown(f'[واٹس ایپ رسید بھیجیں](https://wa.me/{c_dict[s_name]["phone"]}?text={msg})')

elif page == "رقم کی وصولی":
    st.write("### 💸 رقم کی وصولی")
    custs = get_customers()
    if custs:
        c_ids = {c['name']: c['id'] for c in custs}
        s_name = st.selectbox("گاہک منتخب کریں", list(c_ids.keys()))
        with st.form("p_form", clear_on_submit=True):
            amt = st.number_input("وصول شدہ رقم", min_value=0)
            if st.form_submit_button("محفوظ کریں"):
                supabase.table("payments").insert({"customer_id": c_ids[s_name], "amount_paid": amt}).execute()
                st.success("ادائیگی ریکارڈ ہو گئی!")

# --- 1. ونڈے کی انٹری (Functional) ---
elif page == "ونڈے کی انٹری":
    st.write("### 🌾 ونڈہ / چوکر کی انٹری")
    custs = get_customers()
    if custs:
        c_ids = {c['name']: c['id'] for c in custs}
        s_name = st.selectbox("گاہک منتخب کریں", list(c_ids.keys()))
        with st.form("f_form", clear_on_submit=True):
            f_item = st.text_input("آئٹم کا نام (مثلاً: ونڈہ، بنولہ)")
            f_qty = st.number_input("مقدار (بوری/کلو)", min_value=1.0)
            f_price = st.number_input("کل قیمت", min_value=0)
            if st.form_submit_button("ریکارڈ محفوظ کریں"):
                if f_item and f_price > 0:
                    supabase.table("feed_entries").insert({
                        "customer_id": c_ids[s_name], 
                        "feed_name": f_item, 
                        "feed_qty": f_qty, 
                        "feed_price": f_price
                    }).execute()
                    st.success(f"{f_item} کی انٹری محفوظ ہو گئی!")

# --- 2. اخراجات (Functional) ---
elif page == "اخراجات":
    st.write("### 📉 فارم کے اخراجات")
    with st.form("e_form", clear_on_submit=True):
        e_title = st.text_input("خرچے کی تفصیل (مثلاً: بجلی بل، مزدوری)")
        e_amt = st.number_input("رقم", min_value=0)
        if st.form_submit_button("خرچہ سیو کریں"):
            if e_title and e_amt > 0:
                supabase.table("expenses").insert({"title": e_title, "amount": e_amt}).execute()
                st.success("خرچہ ریکارڈ کر لیا گیا!")

elif page == "مکمل کھاتہ رپورٹ":
    st.write("### 📊 تفصیلی کھاتہ")
    custs = get_customers()
    if custs:
        c_dict = {c['name']: c['id'] for c in custs}
        s_name = st.selectbox("گاہک منتخب کریں", list(c_dict.keys()))
        cid = c_dict[s_name]
        
        m_data = supabase.table("milk_entries").select("total_price").eq("customer_id", cid).execute().data
        p_data = supabase.table("payments").select("amount_paid").eq("customer_id", cid).execute().data
        f_data = supabase.table("feed_entries").select("feed_price").eq("customer_id", cid).execute().data
        
        m_total = sum(x['total_price'] for x in m_data)
        p_total = sum(x['amount_paid'] for x in p_data)
        f_total = sum(x['feed_price'] for x in f_data)
        balance = (m_total + f_total) - p_total
        
        st.markdown(f'<div class="report-card">دودھ بل: {m_total} Rs</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="report-card">ونڈہ بل: {f_total} Rs</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="report-card">ٹوٹل وصولی: {p_total} Rs</div>', unsafe_allow_html=True)
        color = "#ff4b4b" if balance > 0 else "#25D366"
        st.markdown(f'<div style="text-align:center; background:{color}; color:white; padding:15px; border-radius:10px;"><h3>باقیہ رقم: {balance} Rs</h3></div>', unsafe_allow_html=True)

# --- 3. منافع و نقصان (Functional) ---
elif page == "منافع و نقصان":
    st.write("### 📈 نفع و نقصان کی رپورٹ")
    
    # Calculation
    milk_rev = sum(x['total_price'] for x in supabase.table("milk_entries").select("total_price").execute().data)
    feed_rev = sum(x['feed_price'] for x in supabase.table("feed_entries").select("feed_price").execute().data)
    total_expenses = sum(x['amount'] for x in supabase.table("expenses").select("amount").execute().data)
    
    total_income = milk_rev + feed_rev
    net_profit = total_income - total_expenses
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("ٹوٹل آمدن (دودھ + ونڈہ)", f"{total_income} Rs")
    with col2:
        st.metric("ٹوٹل اخراجات", f"{total_expenses} Rs")
        
    if net_profit >= 0:
        st.success(f"خالص منافع: {net_profit} Rs")
    else:
        st.error(f"خالص نقصان: {abs(net_profit)} Rs")
    
    st.write("---")
    st.write("#### اخراجات کی تفصیل")
    exp_list = supabase.table("expenses").select("*").execute().data
    if exp_list:
        st.table(pd.DataFrame(exp_list)[['title', 'amount', 'created_at']])
