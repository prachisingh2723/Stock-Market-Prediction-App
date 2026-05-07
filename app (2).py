import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import yfinance as yf

st.set_page_config(page_title="AI Stock Dashboard", layout="wide")

# -------------------------------
# BACKGROUND STYLE FUNCTION
# -------------------------------
def set_background(page, mode="Dark"):

    backgrounds = {
        "Login": "https://images.unsplash.com/photo-1639322537228-f710d846310a?auto=format&fit=crop&w=1920&q=80",
        "Market Overview": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=1920&q=80",
        "Stock Analysis": "https://images.unsplash.com/photo-1559526324-593bc073d938?auto=format&fit=crop&w=1920&q=80",
        "AI Prediction": "https://images.unsplash.com/photo-1677442136019-21780ecad995?auto=format&fit=crop&w=1920&q=80",
        "Company Info": "https://images.unsplash.com/photo-1604594849809-dfedbc827105?auto=format&fit=crop&w=1920&q=80"
    }

    bg_url = backgrounds.get(page, backgrounds["Login"])
    font_family = "Segoe UI, Roboto, sans-serif"

    if mode == "Dark":
        text_color = "#EAF2FF"
        overlay = "rgba(5,15,40,0.75)"
        box_bg = "rgba(255,255,255,0.08)"
        sidebar_bg = "rgba(10, 20, 40, 0.95)"
        button_bg = "#1e90ff"
        button_text = "white"
    else:
        text_color = "#0A1A2F"
        overlay = "rgba(255,255,255,0.55)"
        box_bg = "rgba(255,255,255,0.7)"
        sidebar_bg = "rgba(255,255,255,0.9)"
        button_bg = "#0A66C2"
        button_text = "white"

    st.markdown(f"""
<style>
[data-testid="stAppViewContainer"] {{
    background:
        linear-gradient({overlay}, {overlay}),
        url("{bg_url}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    font-family: {font_family};
}}

h1, h2, h3, h4, h5, h6, p, div, span {{
    color: {text_color} !important;
    font-family: {font_family};
}}

.stTextInput>div>div>input {{
    background-color: {box_bg};
    color: {text_color};
    border-radius: 10px;
    padding: 10px;
    border: none;
}}

.stButton>button {{
    background-color: {button_bg};
    color: {button_text};
    border-radius: 10px;
    border: none;
    padding: 10px 20px;
    font-weight: 600;
}}

section[data-testid="stSidebar"] {{
    background-color: {sidebar_bg};
}}

.stToggle > div {{
    color: {text_color} !important;
}}

[data-testid="stFileUploader"] {{
    background-color: {box_bg};
    border-radius: 10px;
    padding: 15px;
}}

[data-testid="stFileUploaderDropzone"] {{
    background-color: {box_bg};
    border: 2px dashed {button_bg};
    border-radius: 12px;
    padding: 20px;
}}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# FLOATING LOGOUT BUTTON (BOTTOM RIGHT)
# -------------------------------
def top_logout_button():
    st.markdown("""
    <style>
    /* Container ko shrink karo */
    div.stButton {
        position: fixed;
        bottom: 25px;
        right: 25px;
        z-index: 9999;
        width: auto !important;
    }

    /* Button styling */
    div.stButton > button {
        background: linear-gradient(135deg, #ff4b4b, #ff6b6b);
        color: white;
        border: none;
        padding: 10px 18px;
        border-radius: 30px;
        font-weight: 600;
        font-size: 14px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.35);
        cursor: pointer;
        transition: all 0.3s ease;
        width: auto !important;
    }

    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 22px rgba(0,0,0,0.45);
    }
    </style>
    """, unsafe_allow_html=True)

    if st.button("🔒 Logout", key="logout_btn"):
        st.session_state.logged_in = False
        st.rerun()

# -------------------------------
# USER DATABASE
# -------------------------------
USER_DB = "users.csv"
if not os.path.exists(USER_DB):
    pd.DataFrame(columns=["username","password"]).to_csv(USER_DB,index=False)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# -------------------------------
# LOGIN FUNCTIONS
# -------------------------------
def login(username,password):
    users = pd.read_csv(USER_DB)
    user = users[(users["username"]==username) & (users["password"]==password)]
    return not user.empty

def signup(username,password):
    users = pd.read_csv(USER_DB)
    if username in users["username"].values:
        return False
    new_user = pd.DataFrame({"username":[username],"password":[password]})
    users = pd.concat([users,new_user],ignore_index=True)
    users.to_csv(USER_DB,index=False)
    return True

def login_page(mode):
    set_background("Login", mode)
    st.title("📈 AI Stock Market Dashboard")

    option = st.radio("Select Option",["Login","Signup"])
    username = st.text_input("Username")
    password = st.text_input("Password",type="password")

    if option=="Login":
        if st.button("Login"):
            if login(username,password):
                st.session_state.logged_in=True
                st.rerun()
            else:
                st.error("Invalid Credentials")

    if option=="Signup":
        if st.button("Create Account"):
            if signup(username,password):
                st.success("Account Created")
            else:
                st.error("Username already exists")

# -------------------------------
# SIDEBAR
# -------------------------------
def sidebar():
    dark_mode = st.sidebar.toggle("Dark Mode")
    mode = "Dark" if dark_mode else "Light"
    page = st.sidebar.radio("Navigation",["Market Overview","Stock Analysis","AI Prediction","Company Info"])
    return page, mode

# -------------------------------
# COMPANY INFO
# -------------------------------
def company_page(mode):
    set_background("Company Info", mode)
    top_logout_button()
    st.title("🏢 Company Information")

    name = st.text_input("Enter Company Ticker (e.g., AAPL, RELIANCE.NS, INFY.NS)")
    if name:
        try:
            ticker = yf.Ticker(name)
            info = ticker.info
            hist = ticker.history(period="6mo")

            st.subheader(info.get("longName", name))
            st.write(f"**Sector:** {info.get('sector','Not Available')}")
            st.write(f"**Industry:** {info.get('industry','Not Available')}")
            st.write(f"**Market Cap:** {info.get('marketCap','Not Available')}")
            st.write(f"**Current Price:** {info.get('currentPrice','Not Available')}")
            st.write(f"**PE Ratio:** {info.get('forwardPE','Not Available')}")
            st.write(f"**Dividend Yield:** {info.get('dividendYield','Not Available')}")
            st.write(f"**Employees:** {info.get('fullTimeEmployees','Not Available')}")
            st.write(f"**Website:** {info.get('website','Not Available')}")

            st.line_chart(hist["Close"])
        except:
            st.error("Company details not found")

# -------------------------------
# MARKET OVERVIEW
# -------------------------------
@st.cache_data
def load_csv(uploaded_file):
    return pd.read_csv(uploaded_file)

def market_overview(mode):
    set_background("Market Overview", mode)
    top_logout_button()
    st.title("📊 Market Overview")

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file:
        df = load_csv(uploaded_file)
        st.dataframe(df.head(), use_container_width=True)

# -------------------------------
# STOCK ANALYSIS
# -------------------------------
def stock_analysis(mode):
    set_background("Stock Analysis", mode)
    top_logout_button()
    st.title("📈 Stock Analysis")

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded_file:
        df = load_csv(uploaded_file)

        df["MA10"] = df["Close"].rolling(10).mean()
        df["MA50"] = df["Close"].rolling(50).mean()
        df["Return"] = df["Close"].pct_change()

        df_vis = df.tail(500)
        template = "plotly_dark" if mode=="Dark" else "plotly_white"

        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Candlestick","Line","Moving Averages","Volume","Returns"])

        with tab1:
            fig = go.Figure(data=[go.Candlestick(
                x=df_vis.index,
                open=df_vis["Open"],
                high=df_vis["High"],
                low=df_vis["Low"],
                close=df_vis["Close"]
            )])
            fig.update_layout(template=template, height=500)
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.line_chart(df_vis["Close"])

        with tab3:
            st.area_chart(df_vis[["MA10","MA50"]])

        with tab4:
            st.bar_chart(df_vis["Volume"])

        with tab5:
            st.line_chart(df_vis["Return"])

# -------------------------------
# AI PREDICTION
# -------------------------------
def prediction(mode):
    set_background("AI Prediction", mode)
    st.title("🤖 AI Stock Prediction")

    st.write("Enter today's stock details:")
    open_price = st.number_input("Opening Price", min_value=0.0)
    high_price = st.number_input("High Price", min_value=0.0)
    low_price = st.number_input("Low Price", min_value=0.0)
    close_price = st.number_input("Closing Price", min_value=0.0)

    # 🔥 Row with Predict (left) and Logout (right)
    col1, col2 = st.columns([1,1])
    with col1:
        if st.button("Predict", key="predict_btn"):
            avg_price = (open_price + high_price + low_price + close_price) / 4
            trend = "UP 📈" if close_price > open_price else "DOWN 📉"
            st.metric("Predicted Next Price", round(avg_price * 1.01, 2))
            st.metric("Trend", trend)

    with col2:
        if st.button("🔒 Logout", key="logout_btn_predict"):
            st.session_state.logged_in = False
            st.rerun()




# -------------------------------
# APP FLOW
# -------------------------------
if st.session_state.logged_in == False:
    _, mode = sidebar()
    login_page(mode)
else:
    page, mode = sidebar()

    if page == "Market Overview":
        market_overview(mode)
    elif page == "Stock Analysis":
        stock_analysis(mode)
    elif page == "AI Prediction":
        prediction(mode)
    elif page == "Company Info":
        company_page(mode)