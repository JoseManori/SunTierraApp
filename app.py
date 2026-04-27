import streamlit as st
import yfinance as yf
import google.generativeai as genai
from gtts import gTTS
import io
import pandas as pd
from PIL import Image
import os

# ==========================================
# 1. PAGE CONFIGURATION & BRANDING
# ==========================================
st.set_page_config(page_title="SunTierra & Mar y Mar Farms", layout="wide")

# Header Branding - Adjusted for a larger logo
col_logo, col_text = st.columns([2, 3]) 

with col_logo:
    if os.path.exists("logo.png"):
        # Increased width to 350 for better readability
        st.image("logo.png", width=350) 
    else:
        st.title("🚜")

with col_text:
    st.title("SunTierra & Mar y Mar Farms")
    st.subheader("Operations & Dynamic Agronomy Hub")
    st.caption("Created by Mano")

# API Configuration
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception:
    st.error("⚠️ API Key missing in Cloud Secrets.")
    st.stop()

tab1, tab2 = st.tabs(["📈 Market Intelligence", "🧠 Dynamic Field Tutor"])

# ==========================================
# 2. MARKET INTELLIGENCE MODULE
# ==========================================
with tab1:
    st.header("Market Intelligence")
    ticker_input = st.text_input("Enter a ticker symbol:").strip().upper()
    
    if ticker_input:
        with st.spinner("Analyzing Market..."):
            try:
                ticker = yf.Ticker(ticker_input)
                info = ticker.info
                if 'shortName' in info:
                    st.subheader(f"{info.get('longName')} ({ticker_input})")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Price", f"${info.get('currentPrice')}")
                    c2.metric("Target", f"${info.get('targetMeanPrice')}")
                    c3.metric("Status", str(info.get('recommendationKey')).title())
                    
                    st.divider()
                    st.markdown("### Interactive History")
                    timeframe = st.selectbox("Timeline:", ["1y", "3y", "5y", "max"], index=1)
                    hist = ticker.history(period=timeframe)
                    st.line_chart(hist['Close'])
                else:
                    st.error("Ticker not found.")
            except Exception as e:
                st.error(f"Error fetching data: {e}")

# ==========================================
# 3. DYNAMIC AGRONOMY & INFINITE QUIZ
# ==========================================
with tab2:
    st.header("Dynamic Viticulture Expert")
    variety_input = st.text_input("Enter a grape variety (e.g., Autumn King):")
    
    if st.button("Generate Commercial Report"):
        if variety_input:
            with st.spinner(f"Analyzing {variety_input}..."):
                model = genai.GenerativeModel('gemini-2.5-flash') 
                prompt = f"""
                You are a master viticulturist for Tulare and Fresno Counties.
                Provide a report for '{variety_input}' with:
                1. Chronological Agronomy (Pruning to Harvest).
                2. Commercial Analysis (Competitors at harvest, yield comparison, ease of growing, pricing power, and saturation).
                
                Finish with a section: "### Technical Data Summary" containing key specs.
                """
                response = model.generate_content(prompt)
                st.session_state.agronomy_report = response.text
                st.session_state.variety_quizzed = variety_input
                st.session_state.current_question = None

    if "agronomy_report" in st.session_state:
        st.markdown(st.session_state.agronomy_report)
        st.divider()
        
        st.subheader("🎤 Dynamic Field Quiz")
        
        # --- DYNAMIC QUESTION GENERATION ---
        if st.session_state.get("current_question") is None:
            with st.spinner("Generating new technical challenge..."):
                q_model = genai.GenerativeModel('gemini-2.5-flash')
                q_prompt = f"Based on this report: {st.session_state.agronomy_report}, ask one highly specific, challenging technical question for a grower. Do not provide the answer."
                st.session_state.current_question = q_model.generate_content(q_prompt).text

        st.info(st.session_state.current_question)
        
        if st.button("🔊 Read Question"):
            tts = gTTS(text=st.session_state.current_question, lang='en')
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            st.audio(audio_fp, format='audio/mp3', autoplay=True)
                
        audio_value = st.audio_input("Record Answer")
        
        if audio_value:
            with st.spinner("Grading..."):
                grader_model = genai.GenerativeModel('gemini-2.5-flash')
                audio_part = {"mime_type": "audio/wav", "data": audio_value.getvalue()}
                
                grading_prompt = f"""
                Report: {st.session_state.agronomy_report}
                Question: {st.session_state.current_question}
                Listen to the student's audio. Grade it strictly. 
                If they are correct, congratulate them and tell them to 'Click the button below for your next challenge'.
                If incorrect, explain why.
                """
                grade = grader_model.generate_content([grading_prompt, audio_part])
                st.success(grade.text)
        
        # This button is now outside the "if audio_value" block so it stays visible
        if st.button("🔄 Get Next Question"):
            st.session_state.current_question = None
            st.rerun()
