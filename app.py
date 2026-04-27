import streamlit as st
import yfinance as yf
import google.generativeai as genai
from gtts import gTTS
import io
import pandas as pd
import os
import time

# ==========================================
# 1. PAGE CONFIGURATION & BRANDED THEME
# ==========================================
st.set_page_config(
    page_title="SunTierra & Mar y Mar Farms", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Green (#2D5A27) and Gold (#D4AF37) Coordination
st.markdown(f"""
    <style>
    /* Main Background */
    .stApp {{ background-color: #FFFFFF; }}
    
    /* Headers - Forest Green */
    h1, h2, h3 {{ 
        color: #2D5A27 !important; 
        font-family: 'Helvetica Neue', Arial, sans-serif; 
    }}
    
    /* Branding Subheader - Gold */
    .subheader-gold {{ 
        color: #D4AF37; 
        font-weight: bold; 
        font-size: 1.8rem; 
        margin-bottom: 0px; 
        line-height: 1.2;
    }}
    
    /* Branded Buttons */
    .stButton>button {{ 
        background-color: #2D5A27; 
        color: white; 
        border-radius: 8px; 
        border: 2px solid #2D5A27;
        width: 100%; 
        font-weight: bold;
    }}
    .stButton>button:hover {{ 
        border: 2px solid #D4AF37; 
        color: #D4AF37; 
    }}
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] {{ gap: 10px; }}
    .stTabs [aria-selected="true"] {{ 
        background-color: #2D5A27 !important; 
        color: white !important; 
        border-radius: 4px;
    }}
    
    /* Mobile Scaling for Metric Labels */
    [data-testid="stMetricValue"] {{ font-size: 1.8rem !important; }}
    </style>
    """, unsafe_allow_html=True)

# MOBILE-RESPONSIVE HEADER
# Columns will automatically stack on most mobile devices
col_logo, col_text = st.columns([1, 2]) 

with col_logo:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True) 
    else:
        st.title("🚜")

with col_text:
    st.markdown('<p class="subheader-gold">SunTierra & Mar y Mar Farms</p>', unsafe_allow_html=True)
    st.markdown("### Operations & Dynamic Agronomy Hub")
    st.caption("Created by Mano")

# Secure API Configuration
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ API Key missing in Streamlit Cloud Secrets. Please check your dashboard.")
    st.stop()

# --- CACHED STOCK DATA ENGINE (Protects against "Too Many Requests") ---
@st.cache_data(ttl=3600)
def get_stock_data(ticker_symbol):
    ticker_obj = yf.Ticker(ticker_symbol)
    for _ in range(3): # Retry logic
        try:
            data_info = ticker_obj.info
            if 'shortName' in data_info:
                return ticker_obj, data_info
        except:
            time.sleep(1)
    return None, None

tab1, tab2 = st.tabs(["📈 Market Intelligence", "🧠 Dynamic Field Tutor"])

# ==========================================
# 2. MARKET INTELLIGENCE MODULE
# ==========================================
with tab1:
    st.header("Market Intelligence")
    ticker_input = st.text_input("Enter a ticker symbol (e.g., NVDA, DE, AAPL):").strip().upper()
    
    if ticker_input:
        with st.spinner(f"Fetching data for {ticker_input}..."):
            ticker, info = get_stock_data(ticker_input)
            
            if info:
                st.subheader(f"{info.get('longName')} ({ticker_input})")
                
                # Dynamic Competitor Analysis (AI Powered)
                try:
                    comp_model = genai.GenerativeModel('gemini-2.5-flash')
                    comp_res = comp_model.generate_content(f"Top 3 direct competitors for {ticker_input}. 1 sentence each.")
                    st.info(comp_res.text)
                except: pass

                # Metrics Row
                c1, c2, c3 = st.columns(3)
                c1.metric("Price", f"${info.get('currentPrice', 'N/A')}")
                c2.metric("Target", f"${info.get('targetMeanPrice', 'N/A')}")
                c3.metric("Analyst", str(info.get('recommendationKey', 'N/A')).title())
                
                st.divider()
                
                # Interactive Charting
                st.markdown("### Historical Performance")
                timeframe = st.selectbox("Select Timeline:", ["1y", "3y", "5y", "max"], index=1)
                hist = ticker.history(period=timeframe)
                
                if not hist.empty:
                    st.line_chart(hist['Close'], color="#2D5A27")
                    
                    # Monthly Returns Logic
                    st.markdown(f"**Monthly Returns ({timeframe.upper()})**")
                    try:
                        m_close = hist['Close'].resample('ME').last()
                    except:
                        m_close = hist['Close'].resample('M').last()
                    
                    m_ret = (m_close.pct_change() * 100).dropna()
                    ret_df = pd.DataFrame({
                        "Month": m_ret.index.strftime('%B %Y'),
                        "Return (%)": m_ret.round(2)
                    }).iloc[::-1] # Reverse to show newest first
                    st.dataframe(ret_df, use_container_width=True)
            else:
                st.error("⚠️ Ticker not found or Yahoo Finance is rate-limiting. Try again in 1 minute.")

# ==========================================
# 3. DYNAMIC AGRONOMY & INFINITE QUIZ
# ==========================================
with tab2:
    st.header("Dynamic Viticulture Expert")
    st.write("San Joaquin Valley (Tulare & Fresno Counties) Specific Analysis")
    
    variety_input = st.text_input("Enter a table grape variety (e.g., Autumn King, Allison):")
    
    if st.button("Generate Commercial & Agronomy Report"):
        if variety_input:
            with st.spinner(f"Compiling intelligence for {variety_input}..."):
                model = genai.GenerativeModel('gemini-2.5-flash') 
                prompt = f"""
                You are a master viticulturist for Tulare and Fresno Counties, CA.
                Variety: '{variety_input}'
                
                1. Provide a Chronological Agronomy plan (Winter Pruning -> Fall Harvest).
                2. Provide a Commercial Analysis:
                   - Harvest Competitors (who else is in the market then?)
                   - Yield vs others
                   - Ease of growing (technical difficulty)
                   - Pricing power & Market Saturation.
                
                Finish with '### Technical Data Summary' and a few bullet points.
                """
                response = model.generate_content(prompt)
                st.session_state.agronomy_report = response.text
                st.session_state.variety_quizzed = variety_input
                st.session_state.current_question = None

    if "agronomy_report" in st.session_state:
        st.markdown(st.session_state.agronomy_report)
        st.divider()
        
        st.subheader("🎤 Dynamic Field Quiz")
        
        # Infinite Question Logic
        if st.session_state.get("current_question") is None:
            with st.spinner("Generating new challenge..."):
                q_model = genai.GenerativeModel('gemini-2.5-flash')
                q_prompt = f"Ask one technical question based on this report: {st.session_state.agronomy_report}. No answer."
                st.session_state.current_question = q_model.generate_content(q_prompt).text

        st.info(st.session_state.current_question)
        
        # Audio Interaction
        col_read, col_next = st.columns([1, 1])
        with col_read:
            if st.button("🔊 Read Question"):
                tts = gTTS(text=st.session_state.current_question, lang='en')
                audio_fp = io.BytesIO()
                tts.write_to_fp(audio_fp)
                st.audio(audio_fp, format='audio/mp3', autoplay=True)
        
        with col_next:
            if st.button("🔄 Get Next Question"):
                st.session_state.current_question = None
                st.rerun()
                
        audio_value = st.audio_input("Record Your Answer")
        
        if audio_value:
            with st.spinner("Grading..."):
                grader_model = genai.GenerativeModel('gemini-2.5-flash')
                audio_part = {"mime_type": "audio/wav", "data": audio_value.getvalue()}
                
                grading_prompt = f"""
                Report Context: {st.session_state.agronomy_report}
                Question: {st.session_state.current_question}
                Listen to the audio answer. Grade it for technical accuracy. 
                Explain why they are right or wrong based on the report.
                """
                grade = grader_model.generate_content([grading_prompt, audio_part])
                st.success(grade.text)
