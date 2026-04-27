import streamlit as st
import yfinance as yf
import google.generativeai as genai
from gtts import gTTS
import io
import pandas as pd

# ==========================================
# 1. PAGE CONFIGURATION & HEADER
# ==========================================
st.set_page_config(page_title="SunTierra Farm Systems", layout="wide")

st.title("🚜 SunTierra Farm Systems")
st.markdown("**Operations & Dynamic Agronomy Hub**")

# Automatically pull the API key from the hidden secrets vault
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("⚠️ API Key not found in secrets. Please check your .streamlit/secrets.toml file.")
    st.stop()

tab1, tab2 = st.tabs(["📈 Market Intelligence", "🧠 Dynamic Field Tutor"])

# ==========================================
# 2. MARKET INTELLIGENCE MODULE
# ==========================================
with tab1:
    st.header("Market Intelligence")
    ticker_input = st.text_input("Enter a ticker symbol (e.g., DE, NUTRI, AAPL):").strip().upper()
    
    if ticker_input:
        with st.spinner("Fetching live market data, competitors, and historical charts..."):
            try:
                ticker = yf.Ticker(ticker_input)
                info = ticker.info
                
                if 'shortName' in info:
                    st.subheader(f"{info.get('longName', ticker_input)} ({ticker_input})")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Current Price", f"${info.get('currentPrice', 'N/A')}")
                    col2.metric("Target Price (Mean)", f"${info.get('targetMeanPrice', 'N/A')}")
                    col3.metric("Analyst Consensus", str(info.get('recommendationKey', 'N/A')).replace('_', ' ').title())
                    
                    st.divider()
                    
                    # DYNAMIC COMPETITOR ANALYSIS
                    st.markdown("### Top Competitors & Market Position")
                    try:
                        comp_model = genai.GenerativeModel('gemini-2.5-flash')
                        comp_prompt = f"Name the top 3 to 5 direct business competitors for {info.get('longName', ticker_input)} ({ticker_input}). Provide a quick 1-sentence summary of how they compete in the market. Do not use formatting, just plain text."
                        comp_response = comp_model.generate_content(comp_prompt)
                        st.write(comp_response.text)
                    except Exception as e:
                        st.write(f"Company operates in the **{info.get('industry', 'unknown')}** industry. (Competitor AI unavailable).")
                    
                    st.divider()
                    
                    st.markdown("### Technical Summary")
                    st.write(info.get('longBusinessSummary', 'No technical summary available.'))
                    
                    st.divider()

                    # --- DYNAMIC INTERACTIVE CHARTING ---
                    st.markdown("### Interactive Price Chart & Monthly Returns")
                    
                    # Allow the user to select the timeline
                    timeframe = st.selectbox("Select Timeline to Analyze:", ["1y", "3y", "5y", "10y", "max"], index=1) # index 1 means "3y" is the default
                    
                    # Fetch data based on user selection
                    hist = ticker.history(period=timeframe)
                    
                    if not hist.empty:
                        # Display the Line Chart
                        st.line_chart(hist['Close'])
                        
                        st.markdown(f"### Monthly Stock Returns ({timeframe.upper()})")
                        
                        # Resample the daily data to find the closing price at the end of each month
                        try:
                            monthly_close = hist['Close'].resample('ME').last() # Modern Pandas
                        except Exception:
                            monthly_close = hist['Close'].resample('M').last()  # Older Pandas
                            
                        # Calculate the percentage change from month to month
                        monthly_returns = monthly_close.pct_change() * 100
                        monthly_returns = monthly_returns.dropna() # Remove the first blank month
                        
                        # Build a clean data table
                        returns_df = pd.DataFrame({
                            "Month": monthly_returns.index.strftime('%B %Y'),
                            "Return (%)": monthly_returns.round(2)
                        })
                        
                        # Reverse the list so the most recent month is at the very top
                        returns_df = returns_df.iloc[::-1].reset_index(drop=True)
                        
                        # Display the Table
                        st.dataframe(returns_df, use_container_width=True)
                    else:
                        st.warning("Historical price data is not available for this ticker.")
                        
                else:
                    st.error("Data not found. Check the symbol.")
            except Exception as e:
                st.error("Error fetching market data. Please ensure the ticker symbol is correct.")

# ==========================================
# 3. DYNAMIC AGRONOMY & FIELD TUTOR
# ==========================================
with tab2:
    st.header("Dynamic Viticulture Expert")
    st.write("Ask about ANY table grape variety. The system will pull agronomic details AND commercial market analysis tailored for the San Joaquin Valley.")
    
    variety_input = st.text_input("Enter a table grape variety (e.g., Autumn King, Cotton Candy):")
    
    if st.button("Generate Agronomy Manual & Quiz"):
        if variety_input:
            with st.spinner(f"Compiling agronomic and commercial data for {variety_input}..."):
                model = genai.GenerativeModel('gemini-2.5-flash') 
                
                # --- UPDATED PROMPT: ADDED COMMERCIAL MARKET ANALYSIS ---
                prompt = f"""
                You are a master viticulturist and table grape agronomist operating in the San Joaquin Valley (specifically Tulare and Fresno Counties, CA).
                Provide a highly detailed, comprehensive report for the table grape variety '{variety_input}'.
                
                You MUST format the report into two distinct sections:
                
                SECTION 1: CHRONOLOGICAL AGRONOMY
                Present the growing information in strict chronological order based on the typical growing season.
                - Pruning (Winter)
                - Fertilizers (Timing & Needs)
                - Herbicides
                - Preventative Fungicides
                - Shoot Thinning (Spring)
                - Bunch Thinning
                - Gibberellic Acid (GA3) Ratios/Timing
                - Insecticides
                - Leaf Removal & Cluster Tipping
                - Brix Harvesting Numbers & Visual Inspections
                
                SECTION 2: ### Commercial & Market Analysis
                Provide a brutal, honest commercial assessment of this variety covering:
                1. Harvest Competitors: What other prominent varieties hit the market at the exact same time?
                2. Yield Comparison: How does its tonnage per acre naturally compare to its direct competitors?
                3. Ease of Growing: Is it grower-friendly (forgiving) or highly technical (high risk of shatter, poor color, or rot)?
                4. Pricing Power: Does it command a premium box price or is it a heavily commoditized grape?
                5. Market Saturation: Is the market flooded with this variety, or is there still unmet retailer demand?

                SECTION 3: ### Field Quiz
                Ask ONE highly specific, challenging question about the technical data you just provided to test my knowledge. DO NOT provide the answer to the quiz question.
                """
                
                response = model.generate_content(prompt)
                
                st.session_state.agronomy_report = response.text
                st.session_state.variety_quizzed = variety_input

    # --- VOICE ACTIVATED INTERACTION ZONE ---
    if "agronomy_report" in st.session_state:
        st.markdown(st.session_state.agronomy_report)
        st.divider()
        
        st.subheader("🎤 Voice-Activated Field Quiz")
        
        report_text = st.session_state.agronomy_report
        if "### Field Quiz" in report_text:
            quiz_question = report_text.split("### Field Quiz")[1].strip()
        else:
            quiz_question = "Please summarize the main points of this agronomy manual."
            
        if st.button("🔊 Read Question Aloud"):
            with st.spinner("Generating audio..."):
                tts = gTTS(text=quiz_question, lang='en')
                audio_fp = io.BytesIO()
                tts.write_to_fp(audio_fp)
                st.audio(audio_fp, format='audio/mp3', autoplay=True)
                
        st.write("Press the microphone icon below to record your spoken answer:")
        
        audio_value = st.audio_input("Record Answer")
        
        if audio_value:
            with st.spinner("Listening to your response and grading..."):
                grader_model = genai.GenerativeModel('gemini-2.5-flash')
                
                audio_part = {
                    "mime_type": "audio/wav",
                    "data": audio_value.getvalue()
                }
                
                grading_prompt = f"""
                You are a strict viticulture instructor. 
                The student is answering a question about the grape variety '{st.session_state.variety_quizzed}'.
                The context manual is here: {st.session_state.agronomy_report}
                
                The student has provided an audio response. Listen to their audio.
                Tell the student if they are correct or incorrect, and provide the exact correct answer with a brief explanation based on the manual.
                """
                
                grade = grader_model.generate_content([grading_prompt, audio_part])
                st.info(grade.text)