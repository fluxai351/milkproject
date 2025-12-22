import streamlit as st
from supabase import create_client
import urllib.parse
import pandas as pd

# --- 1. CONFIGURATION ---
SUPABASE_URL = "https://glohhdwhcbgaahmxqhkb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdsb2hoZHdoY2JnYWFobXhxaGtiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjYzOTY1NzEsImV4cCI6MjA4MTk3MjU3MX0.WyGE8ctBT8tbz-Lt02yflJSDtsApq2kDY0j5_wQMMWg"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Page Setup
st.set_page_config(page_title="Doodh Wala App", page_icon="🥛")

# --- 2. CSS STYLING (For Professional Buttons) ---
st.markdown("""
    <style>
        .wa-button {
            background-color: #25D366;
            color: white !important;
            padding: 14px 20px;
            text-decoration: none;
            font-size: 18px;
            font-weight: bold;
            border-radius: 12px;
            display: block;
            text-align: center;
            margin: 15px 0px;
            border: none;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.15);
            transition: 0.3s ease;
        }
        .wa-button:hover {
            background-color: #128C7E;
            box-shadow: 0px 6px 15px rgba(0,0,0,0.25);
            transform: translateY(-2px);
        }
        .bill-button {
            background-color: #075E54 !important; /* Dark Green for Bill */
        }
    </style>
""", unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS ---
def get_all_customers():
    return supabase.table("customers").select("*").execute().data

def get_billing_data(customer_id):
    return supabase.table("milk_entries").select("*").eq("customer_id", customer_id).execute().data

# --- 4. UI SIDEBAR ---
menu = st.sidebar.selectbox("Kahan Jana Hai?", ["Daily Entry", "Monthly Bill", "View Customers", "Add New Customer"])

# --- PAGE 1: DAILY ENTRY ---
if menu == "Daily Entry":
    st.header("📝 Rozana ka Hisaab")
    customers = get_all_customers()
    if customers:
        customer_dict = {c['name']: c for c in customers}
        selected_name = st.selectbox("Customer Chunain:", list(customer_dict.keys()))
        selected_customer = customer_dict[selected_name]
        
        with st.form("entry_form", clear_on_submit=True):
            qty = st.number_input("Kitna Doodh (Litres)?", min_value=0.5, value=1.0, step=0.5)
            total_price = qty * selected_customer['rate']
            submitted = st.form_submit_button("Entry Save Karein")
            
            if submitted:
                data = {"customer_id": selected_customer['id'], "quantity": qty, "total_price": total_price}
                supabase.table("milk_entries").insert(data).execute()
                st.success(f"Mubarak! {selected_name} ki entry save ho gayi.")
                
                # WhatsApp Receipt Logic
                msg = f"Assalam-o-Alaikum {selected_name}! 🥛\n\n*Milk Entry Update:*\nAaj ap ne {qty} litre doodh liya hai.\nTotal: {total_price} Rs.\n\nShukriya!"
                whatsapp_url = f"https://wa.me/{selected_customer['phone']}?text={urllib.parse.quote(msg)}"
                
                st.markdown(f'<a href="{whatsapp_url}" target="_blank" class="wa-button">💬 Send WhatsApp Receipt</a>', unsafe_allow_html=True)

# --- PAGE 2: MONTHLY BILL ---
elif menu == "Monthly Bill":
    st.header("📊 Customer Bill Summary")
    customers = get_all_customers()
    if customers:
        customer_dict = {c['name']: c for c in customers}
        selected_name = st.selectbox("Customer Chunain:", list(customer_dict.keys()))
        selected_customer = customer_dict[selected_name]
        
        billing_data = get_billing_data(selected_customer['id'])
        
        if billing_data:
            df = pd.DataFrame(billing_data)
            df['Date'] = pd.to_datetime(df['created_at']).dt.date
            display_df = df[['Date', 'quantity', 'total_price']]
            display_df.columns = ['Tareekh', 'Litre', 'Raqam (Rs)']
            
            st.table(display_df)
            
            total_qty = display_df['Litre'].sum()
            total_bill = display_df['Raqam (Rs)'].sum()
            
            col1, col2 = st.columns(2)
            col1.metric("Total Litres", f"{total_qty} L")
            col2.metric("Total Bill", f"{total_bill} Rs")
            
            # WhatsApp Monthly Bill Logic
            bill_msg = f"Assalam-o-Alaikum {selected_name}! 🥛\n\n*Monthly Bill Update:*\nTotal Doodh: {total_qty} L\nKul Raqam: {total_bill} Rs\n\nShukriya!"
            bill_wa_url = f"https://wa.me/{selected_customer['phone']}?text={urllib.parse.quote(bill_msg)}"
            
            st.markdown(f'<a href="{bill_wa_url}" target="_blank" class="wa-button bill-button">📊 Send Full Monthly Bill</a>', unsafe_allow_html=True)
        else:
            st.info("Is customer ki abhi koi entry nahi hai.")

# --- PAGE 3: VIEW CUSTOMERS ---
elif menu == "View Customers":
    st.header("👥 Hamare Customers")
    data = get_all_customers()
    if data:
        st.dataframe(data, use_container_width=True)
    else:
        st.info("Koi customer nahi mila.")

# --- PAGE 4: ADD NEW CUSTOMER ---
elif menu == "Add New Customer":
    st.header("➕ Naya Customer Register Karein")
    with st.form("add_cust", clear_on_submit=True):
        name = st.text_input("Naam")
        phone = st.text_input("WhatsApp Number (e.g. 923001234567)")
        rate = st.number_input("Rate per Litre", min_value=100, value=200)
        if st.form_submit_button("Save Customer"):
            if name and phone:
                supabase.table("customers").insert({"name": name, "phone": phone, "rate": rate}).execute()
                st.success("Customer Add ho gaya!")
            else:
                st.error("Naam aur Phone lazmi hai!")