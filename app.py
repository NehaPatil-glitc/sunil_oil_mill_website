import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime
from urllib.parse import quote
from dotenv import load_dotenv

st.set_page_config(page_title="Sunil Industries", layout="wide")

# ---------- GLOBAL CSS ----------

st.markdown("""
<style>

/* Remove extra spacing */
.block-container {
    padding-top: 2.5rem;
    padding-bottom: 1rem;
}

/* Card Design */
.card {
    padding: 15px;
    border-radius: 12px;
    background-color: #f9f9f9;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    margin-bottom: 15px;
}

/* Buttons */
.stButton>button {
    background-color: #111827;
    color: white;
    border-radius: 8px;
    border: none;
}
.stButton>button:hover {
    background-color: #374151;
}

/* Mobile Responsive */
@media (max-width: 768px) {

    .block-container {
        padding: 1rem !important;
    }

    img {
        width: 100% !important;
        height: auto !important;
    }

    h1 { font-size: 24px !important; }
    h2 { font-size: 20px !important; }
    h3 { font-size: 18px !important; }
}
            
.machine-img img {
    height: 220px;
    width: 100%;
    object-fit: cover;
    border-radius: 10px;
}

/* FORCE FULL BACKGROUND */
[data-testid="stAppViewContainer"] {
    background-color: #f5f7fa !important;
}

/* MAIN CONTENT AREA */
section.main > div {
    background-color: #f5f7fa !important;
}

/* TEXT COLORS */
[data-testid="stAppViewContainer"],
section.main,
.block-container {
    color: #000000 !important;
}

/* HEADINGS */
h1, h2, h3, h4, h5, h6 {
    color: #000000 !important;
}

/* LABELS + TEXT */
label, p, span {
    color: #000000 !important;
}
            
/* Navbar fix for mobile */
@media (max-width: 768px) {
    .stColumns {
        flex-wrap: nowrap !important;
    }
    .stColumn {
        flex: 1 !important;
        min-width: 0 !important;
    }
}

/* Hide Streamlit Branding */
#MainMenu {visibility: hidden;}   /* Top-right menu */
footer {visibility: hidden;}      /* Footer with Streamlit logo */
header {visibility: hidden;}      /* Any header, optional */

</style>
""", unsafe_allow_html=True)

# ---------- LOAD PASSWORD ----------
load_dotenv()
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

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

# ---------- CREATE IMAGE FOLDER ----------
if not os.path.exists("images"):
    os.makedirs("images")

# ---------- DEFAULT DATA ----------
cursor.execute("SELECT COUNT(*) FROM machines")
if cursor.fetchone()[0] == 0:
    data = [
        ("Mini Rotary Oil Mill Machine","2HP","8-12kg/hr","225kg","All Seeds","images/2hp.jpeg"),
        ("Wooden Oil Ghani Machine","3HP","8-12kg/hr","150kg","All Seeds","images/wooden.jpeg"),
        ("3HP Rotary Oil Machine","3HP","8-12kg/hr","230kg","All Seeds","images/3hp.jpeg"),
        ("7.5HP Rotary Oil Machine","7.5HP","30-50kg/hr","400kg","All Seeds","images/7.5hp.jpeg")
    ]
    cursor.executemany("INSERT INTO machines VALUES (?,?,?,?,?,?)", data)
    conn.commit()

# ---------- SESSION ----------
if "page" not in st.session_state:
    st.session_state.page = "Home"



# ---------- NAVBAR ----------
nav1, nav2, nav3 = st.columns([2, 6, 2])

with nav1:
    st.image("images/logo.png", width=60)

with nav2:
    st.markdown("""
    <h2 style='margin-bottom:0;'>Sunil Industries</h2>
    """, unsafe_allow_html=True)

with nav3:
    st.session_state.page = st.radio(
        "",
        options=["Home", "Admin"],
        index=0 if st.session_state.page == "Home" else 1,
        horizontal=True
    )

# ---------- HOME ----------
if st.session_state.page == "Home":
    st.markdown("""
    ### Welcome to Sunil Industries

    ✔ High Quality Machines  
    ✔ Durable & Long Lasting  
    ✔ Suitable for all oil seeds  
    ✔ Trusted by customers  

    📍 Kolhapur, Maharashtra  
    📞 9371226464 / 9373082376  
    """)

    st.divider()

    # ---------- MACHINES ----------
    st.subheader("Our Machines")

    df = pd.read_sql("SELECT * FROM machines", conn)

    if df.empty:
        st.warning("No machines available")
    else:
        cols = st.columns(2)

        for i, row in df.iterrows():
            with cols[i % 2]:
                st.image(row["image"], use_container_width=True)
                st.subheader(row["name"])
                st.write("Motor:", row["power"])
                st.write("Production:", row["production"])
                st.write("Weight:", row["weight"])
                st.write("Uses:", row["uses"])

                msg = quote(f"Hello, I am interested in {row['name']}. Please share details.")
                link = f"https://wa.me/919371226464?text={msg}"

                st.markdown(f"[📲 Enquire on WhatsApp]({link})")

    st.divider()

    # ---------- ENQUIRY ----------
    st.subheader("Enquiry Form")

    machines = df["name"].tolist()

    with st.form("form"):
        name = st.text_input("Name")
        mobile = st.text_input("Mobile")
        city = st.text_input("City")
        product = st.selectbox("Machine", machines if machines else ["N/A"])
        submit = st.form_submit_button("Submit")

    if submit:
        if name == "" or mobile == "" or len(mobile) != 10:
            st.error("Enter valid details")
        else:
            cursor.execute("INSERT INTO orders VALUES (?,?,?,?,?)",
                           (name, mobile, city, product, datetime.now().strftime("%d-%m-%Y")))
            conn.commit()
            st.success("Enquiry submitted! We will contact you soon.")

    st.divider()

    # ---------- CONTACT ----------
    st.subheader("Contact Us")

    st.write("**Owner:** Prashant Sutar")
    st.write("**Mobile:** 9371226464, 9373082376")

    st.write("""
1325/69 E Ward, Shivaji Udyamnagar  
Near Bharat Bakery  
Kolhapur – 416008  
Maharashtra, India
""")

# ---------- ADMIN ----------
elif st.session_state.page == "Admin":

    password = st.text_input("Enter Admin Password", type="password")

    if password == ADMIN_PASSWORD:

        st.success("Login Successful")

        # ---------- ADD ----------
        st.subheader("Add Machine")

        name = st.text_input("Name")
        power = st.text_input("Power")
        production = st.text_input("Production")
        weight = st.text_input("Weight")
        uses = st.text_input("Uses")
        img = st.file_uploader("Upload Image")

        if st.button("Add"):
            if img:
                path = os.path.join("images", img.name)
                with open(path, "wb") as f:
                    f.write(img.getbuffer())

                cursor.execute("INSERT INTO machines VALUES (?,?,?,?,?,?)",
                               (name, power, production, weight, uses, path))
                conn.commit()
                st.success("Added")

        st.divider()

        # ---------- EDIT / DELETE ----------
        st.subheader("Manage Machines")

        machines_df = pd.read_sql("SELECT rowid AS ID, * FROM machines", conn)

        for _, row in machines_df.iterrows():
            with st.expander(row["name"]):

                new_name = st.text_input("Name", row["name"], key=f"n{row['ID']}")
                new_power = st.text_input("Power", row["power"], key=f"p{row['ID']}")
                new_prod = st.text_input("Production", row["production"], key=f"pr{row['ID']}")
                new_weight = st.text_input("Weight", row["weight"], key=f"w{row['ID']}")
                new_uses = st.text_input("Uses", row["uses"], key=f"u{row['ID']}")

                new_img = st.file_uploader("New Image", key=f"img{row['ID']}")

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("Update", key=f"up{row['ID']}"):
                        img_path = row["image"]

                        if new_img:
                            img_path = os.path.join("images", new_img.name)
                            with open(img_path, "wb") as f:
                                f.write(new_img.getbuffer())

                        cursor.execute("""
                        UPDATE machines SET name=?, power=?, production=?, weight=?, uses=?, image=?
                        WHERE rowid=?
                        """, (new_name, new_power, new_prod, new_weight, new_uses, img_path, row["ID"]))
                        conn.commit()
                        st.success("Updated")

                with col2:
                    if st.button("Delete", key=f"del{row['ID']}"):
                        cursor.execute("DELETE FROM machines WHERE rowid=?", (row["ID"],))
                        conn.commit()
                        st.warning("Deleted")

        st.divider()

        # ---------- ENQUIRIES ----------
        st.subheader("Enquiries")

        orders = pd.read_sql("SELECT * FROM orders", conn)

        if orders.empty:
            st.info("No enquiries yet")
        else:
            st.dataframe(orders)

            csv = orders.to_csv(index=False).encode('utf-8')
            st.download_button("Download CSV", csv, "enquiries.csv", "text/csv")

        st.divider()

        # ---------- PASSWORD ----------
        st.subheader("Change Password")

        new_pass = st.text_input("New Password", type="password")

        if st.button("Update Password"):
            if new_pass:
                with open(".env", "w") as f:
                    f.write(f"ADMIN_PASSWORD={new_pass}")
                st.success("Password Updated")

    elif password != "":
        st.error("Wrong Password")

# ---------- WHATSAPP FLOAT ----------
st.markdown("""
<a href="https://wa.me/919371226464?text=Hello%20I%20want%20details"
target="_blank"
style="position:fixed;bottom:25px;right:25px;background:#25D366;
border-radius:50%;width:60px;height:60px;display:flex;
align-items:center;justify-content:center;">
<img src="https://img.icons8.com/color/48/whatsapp.png" width="35">
</a>
""", unsafe_allow_html=True)