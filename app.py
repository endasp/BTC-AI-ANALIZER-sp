import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import google.generativeai as genai

# --- KUNCI OTAK AI ---
# Masukkan API Key kamu di sini
GOOGLE_API_KEY = "AIzaSyB4n5rDd0HTwMMFNPw5Vq--3aVMXDBNf9E"
genai.configure(api_key=GOOGLE_API_KEY)

# Cari model yang tersedia secara otomatis
model_name = 'gemini-pro' 

st.set_page_config(page_title="AI Trading Commander", layout="wide")
st.title("🤖 AI Commander: Keputusan Trading Otomatis")

pilihan_tf = st.sidebar.selectbox("Pilih Timeframe:", ("5m", "15m", "1h", "1d"))

@st.cache_data(ttl=60)
def get_data(tf):
    df = yf.Ticker("BTC-USD").history(period="3d", interval=tf)
    return df

try:
    df = get_data(pilihan_tf)
    last_price = df['Close'].iloc[-1]
    
    with st.spinner('AI sedang menganalisa pasar...'):
        # Gunakan cara pemanggilan paling dasar agar stabil
        model = genai.GenerativeModel(model_name)
        prompt = f"Harga BTC saat ini {last_price}. Data 5 candle terakhir: {df['Close'].tail(5).tolist()}. Berikan instruksi singkat: OPEN LONG, OPEN SHORT, atau WAIT? Berikan harga Entry, TP, dan SL. Gunakan Bahasa Indonesia yang tegas."
        
        response = model.generate_content(prompt)
        ai_decision = response.text

    st.markdown("### 📢 INSTRUKSI EKSEKUSI AI:")
    st.success(ai_decision)
    
    st.markdown("---")
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.update_layout(title=f"Grafik Konfirmasi ({pilihan_tf})", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Sistem sedang sinkronisasi. Jika error berlanjut, silakan klik 'Reboot App' di menu kanan bawah. Detail: {e}")
