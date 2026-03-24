import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import google.generativeai as genai

# --- CONFIG CLOUD AI ---
# API Key sudah terpasang
GOOGLE_API_KEY = "AIzaSyB4n5rDd0HTwMMFNPw5Vq--3aVMXDBNf9E"
genai.configure(api_key=GOOGLE_API_KEY)

# MENGGUNAKAN MODEL TERBARU & STABIL
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="Cloud AI Trading Commander", layout="wide")
st.title("☁️ Cloud AI: Strategic Trading Commander")

pilihan_tf = st.sidebar.selectbox("Pilih Timeframe:", ("5m", "15m", "1h", "1d"))

@st.cache_data(ttl=30) # Refresh lebih cepat (30 detik)
def get_data(tf):
    df = yf.Ticker("BTC-USD").history(period="2d", interval=tf)
    return df

try:
    df = get_data(pilihan_tf)
    last_price = df['Close'].iloc[-1]
    
    with st.spinner('Menghubungkan ke Otak AI...'):
        # Prompt instruksi tegas
        prompt = f"Harga BTC saat ini ${last_price:,.2f}. Data 5 candle terakhir: {df['Close'].tail(5).tolist()}. Berikan instruksi tegas: OPEN LONG, OPEN SHORT, atau WAIT? Sebutkan Entry, TP, dan SL. Gunakan Bahasa Indonesia yang singkat."
        
        response = model.generate_content(prompt)
        ai_output = response.text

    st.subheader("📢 INSTRUKSI EKSEKUSI AI")
    st.success(ai_output)
    
    st.markdown("---")
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.update_layout(xaxis_rangeslider_visible=False, height=500)
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Koneksi AI Sedang Sinkronisasi... Tunggu 10 detik lalu refresh. (Detail: {e})")
