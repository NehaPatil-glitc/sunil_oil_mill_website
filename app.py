import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
from urllib.parse import quote
from dotenv import load_dotenv

st.set_page_config(page_title="Sunil Industries", layout="wide")

# ---------- LOAD ADMIN PASSWORD ----------
load_dotenv()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")  # fallback

# ---------- DATABASE ----------
conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS machines(
name TEXT,
power TEXT,
production TEXT,
weight TEXT,
uses TEXT,
image TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders(
name TEXT,
mobile TEXT,
city TEXT,
product TEXT,
date TEXT
)
""")
conn.commit()

# ---------- INSERT DEFAULT MACHINES ----------
cursor.execute("SELECT COUNT(*) FROM machines")
count = cursor.fetchone()[0]
if count == 0:
    default_machines = [
        ("Mini Rotary Oil Mill Machine","2HP","8-12kg/hr","225kg",
         "Groundnut, Coconut, Sunflower, Sesame, Mustard, Almond","images/2hp.jpeg"),
        ("Wooden Oil Ghani Machine","3HP","8-12kg/hr","150kg",
         "Groundnut, Coconut, Sunflower, Sesame, Mustard, Almond","images/wooden.jpeg"),
        ("3HP Rotary Oil Machine","3HP","8-12kg/hr","230kg",
         "Groundnut, Coconut, Sunflower, Sesame, Mustard, Almond","images/3hp.jpeg"),
        ("7.5HP Rotary Oil Machine","7.5HP","30-50kg/hr","400kg",
         "Groundnut, Coconut, Sunflower, Sesame, Mustard, Almond","images/7.5hp.jpeg")
    ]
    cursor.executemany("INSERT INTO machines VALUES (?,?,?,?,?,?)", default_machines)
    conn.commit()

# ---------- STYLES ----------
st.markdown("""
<style>
.stApp{background:#f4f6fb;}
h1,h2,h3{color:#0e4c92;}
img{border-radius:10px;}
[data-testid="metric-container"]{background:white;padding:15px;border-radius:10px;box-shadow:0 3px 10px rgba(0,0,0,0.1);}
.whatsapp{position:fixed;bottom:30px;right:30px;background:#25D366;color:white;border-radius:50%;width:60px;height:60px;display:flex;justify-content:center;align-items:center;font-size:28px;box-shadow:0 4px 10px rgba(0,0,0,0.3);text-decoration:none;}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown("""
<div style="background:linear-gradient(90deg,#0e4c92,#1a73e8);
padding:30px;border-radius:10px;text-align:center;color:white;">
<h1>Sunil Industries</h1>
<p>Pure Oil Extraction Machines for Small & Medium Businesses</p>
</div>
""", unsafe_allow_html=True)

menu = st.sidebar.selectbox("Navigation",["Home","Machines","Enquiry Form","Contact","Admin"])

# ---------- HOME ----------
if menu == "Home":
    st.header("Welcome to Sunil Industries")
    st.write("""
**Sunil Industries – Oil Mill Machine Manufacturer**  
*Pure Oil Extraction Machines for Small & Medium Businesses*

We specialize in high-quality oil extraction machines suitable for small & medium businesses.  
Our machines are known for:
- High efficiency
- Durable build quality
- Low maintenance
- Cold press oil extraction
""")
    st.subheader("Why Choose Our Machines?")
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Machine Types","4+")
    with col2: st.metric("Warranty","1 Year")
    with col3: st.metric("Production Capacity","8–50 kg/hr")
    st.success("📍 Location: Kolhapur, Maharashtra, India")

# ---------- MACHINES ----------
elif menu == "Machines":
    st.header("Our Machines")
    df = pd.read_sql("SELECT * FROM machines", conn)
    for _, row in df.iterrows():
        col1, col2 = st.columns([1,1])
        with col1:
            st.image(row["image"], use_container_width=True)
        with col2:
            st.subheader(row["name"])
            st.write("Motor:", row["power"])
            st.write("Production:", row["production"])
            st.write("Weight:", row["weight"])
            st.write("Uses:", row["uses"])
            
            # WhatsApp button with logo
            message = f"Hello I want details about {row['name']}"
            encoded_message = quote(message)
            whatsapp_url = f"https://wa.me/919371126464?text={encoded_message}"
            
            st.markdown(f"""
            <a href="{whatsapp_url}" target="_blank" style="
                display:inline-flex;
                align-items:center;
                padding:10px 15px;
                background-color:#25D366;
                color:white;
                border-radius:8px;
                text-decoration:none;
                font-weight:bold;
            ">
                <img src="https://upload.wikimedia.org/wikipedia/commons/6/6b/WhatsApp.svg" 
                     width="20" style="margin-right:8px;">
                Order on WhatsApp
            </a>
            """, unsafe_allow_html=True)
        st.divider()

# ---------- ENQUIRY FORM ----------
elif menu == "Enquiry Form":
    st.header("Customer Enquiry")
    machines = pd.read_sql("SELECT name FROM machines", conn)
    product_list = machines["name"].tolist()
    with st.form("form"):
        name = st.text_input("Name")
        mobile = st.text_input("Mobile Number")
        city = st.text_input("City")
        product = st.selectbox("Machine Type", product_list)
        submit = st.form_submit_button("Submit")
    if submit:
        cursor.execute(
            "INSERT INTO orders VALUES (?,?,?,?,?)",
            (name, mobile, city, product, datetime.now().strftime("%d-%m-%Y"))
        )
        conn.commit()
        st.success("Enquiry Submitted")

# ---------- CONTACT ----------
elif menu == "Contact":
    st.header("Contact Us")
    st.write("**Business Name:** Sunil Industries")
    st.write("**Owner:** Prashant Sutar")
    st.write("**Mobile Numbers:** 9371126464, 9373082376")
    st.write("""
**Address:**  
1325/69 E Ward, Shivaji Udyamnagar  
Near Bharat Bakery  
Kolhapur – 416008  
Maharashtra, India
""")

# ---------- ADMIN ----------
elif menu == "Admin":
    password = st.text_input("Enter Admin Password", type="password")
    if password == ADMIN_PASSWORD:
        st.success("Admin Login Successful")

        st.subheader("➕ Add New Machine")
        name = st.text_input("Machine Name")
        power = st.text_input("Motor Power")
        production = st.text_input("Production Capacity")
        weight = st.text_input("Weight")
        uses = st.text_input("Uses (comma-separated)")
        uploaded_image = st.file_uploader("Upload Machine Image", type=["jpg","jpeg","png"])
        if st.button("Add Machine"):
            if uploaded_image:
                image_path = os.path.join("images", uploaded_image.name)
                with open(image_path, "wb") as f: f.write(uploaded_image.getbuffer())
                cursor.execute(
                    "INSERT INTO machines VALUES (?,?,?,?,?,?)",
                    (name, power, production, weight, uses, image_path)
                )
                conn.commit()
                st.success("Machine Added")

        st.divider()
        st.subheader("Manage Existing Machines")
        machines_df = pd.read_sql("SELECT rowid AS ID, * FROM machines", conn)
        for _, row in machines_df.iterrows():
            with st.expander(f"{row['name']}"):
                st.write("Motor:", row["power"])
                st.write("Production:", row["production"])
                st.write("Weight:", row["weight"])
                st.write("Uses:", row["uses"])
                
                # Pre-fill form for editing
                edit_name = st.text_input("Name", value=row["name"], key=f"name_{row['ID']}")
                edit_power = st.text_input("Motor Power", value=row["power"], key=f"power_{row['ID']}")
                edit_production = st.text_input("Production", value=row["production"], key=f"prod_{row['ID']}")
                edit_weight = st.text_input("Weight", value=row["weight"], key=f"weight_{row['ID']}")
                edit_uses = st.text_input("Uses", value=row["uses"], key=f"uses_{row['ID']}")
                new_image = st.file_uploader("Upload new Image", type=["jpg","jpeg","png"], key=f"img_{row['ID']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Update", key=f"update_{row['ID']}"):
                        img_path = row["image"]
                        if new_image:
                            img_path = os.path.join("images", new_image.name)
                            with open(img_path, "wb") as f: f.write(new_image.getbuffer())
                        cursor.execute("""
                            UPDATE machines
                            SET name=?, power=?, production=?, weight=?, uses=?, image=?
                            WHERE rowid=?
                        """, (edit_name, edit_power, edit_production, edit_weight, edit_uses, img_path, row["ID"]))
                        conn.commit()
                        st.success("Machine updated successfully!")
                with col2:
                    if st.button("Delete", key=f"delete_{row['ID']}"):
                        cursor.execute("DELETE FROM machines WHERE rowid=?", (row["ID"],))
                        conn.commit()
                        st.success("Machine deleted successfully!")

        st.divider()
        st.subheader("Customer Enquiries")
        orders = pd.read_sql("SELECT rowid AS ID, * FROM orders", conn)
        st.dataframe(orders)
        if not orders.empty:
            st.subheader("📊 Analytics")
            col1, col2, col3 = st.columns(3)
            with col1: st.metric("Total Enquiries", len(orders))
            with col2: st.metric("Most Demanded Machine", orders["product"].value_counts().idxmax())
            with col3: st.metric("Cities", orders["city"].nunique())
            st.subheader("📊 Enquiries Per City")
            st.bar_chart(orders["city"].value_counts())

        st.subheader("🔒 Change Admin Password")
        new_pass = st.text_input("Enter new password", type="password", key="newpass")
        if st.button("Update Password"):
            if new_pass:
                with open(".env", "w") as f:
                    f.write(f"ADMIN_PASSWORD={new_pass}\n")
                st.success("Password updated successfully!")

    elif password != "":
        st.error("Wrong Password")

# ---------- FIXED WHATSAPP BUTTON ----------
st.markdown("""
<a href="https://wa.me/919371126464" target="_blank" class="whatsapp">💬</a>
""", unsafe_allow_html=True)