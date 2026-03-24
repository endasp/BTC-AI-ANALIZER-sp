import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import google.generativeai as genai

# --- CONFIG CLOUD AI ---
GOOGLE_API_KEY = "AIzaSyB4n5rDd0HTwMMFNPw5Vq--3aVMXDBNf9E"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# --- UI SETTINGS ---
st.set_page_config(page_title="Cloud AI Trading Commander", layout="wide")
st.title("☁️ Cloud AI: Strategic Trading Commander")
st.markdown("---")

# Sidebar untuk pilihan
st.sidebar.header("Pusat Kendali")
pilihan_tf = st.sidebar.selectbox("Pilih Timeframe:", ("5m", "15m", "1h", "1d"))

@st.cache_data(ttl=60)
def get_data(tf):
    # Mengambil data 3 hari terakhir untuk dianalisa
    df = yf.Ticker("BTC-USD").history(period="3d", interval=tf)
    return df

try:
    df = get_data(pilihan_tf)
    last_price = df['Close'].iloc[-1]
    
    # Bagian Analisa AI
    with st.spinner('Menghubungkan ke Cloud AI untuk analisa mendalam...'):
        prompt = f"""
        Bertindaklah sebagai Senior Trader profesional. Analisa data BTC-USD ini:
        Harga Sekarang: ${last_price:,.2f}
        Trend 5 Candle terakhir: {df['Close'].tail(5).tolist()}
        
        Berikan instruksi EKSEKUSI yang SANGAT TEGAS dan GARANG:
        1. KEPUTUSAN: (WAJIB pilih salah satu: OPEN LONG / OPEN SHORT / WAIT)
        2. ENTRY: (Harga saat ini)
        3. TAKE PROFIT (TP): (Berikan angka pastinya)
        4. STOP LOSS (SL): (Berikan angka pastinya)
        5. ANALISA SINGKAT: (Maksimal 15 kata kenapa ambil posisi itu)
        
        Gunakan Bahasa Indonesia yang to-the-point dan profesional.
        """
        response = model.generate_content(prompt)
        ai_output = response.text

    # Tampilan Output AI dalam Kotak Berwarna
    st.subheader("📢 INSTRUKSI EKSEKUSI CLOUD AI")
    st.info(ai_output)
    
    st.markdown("---")
    
    # Grafik Candlestick Konfirmasi
    st.subheader(f"📊 Grafik Konfirmasi Pasar ({pilihan_tf})")
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'],
        low=df['Low'], close=df['Close'],
        name='Market Data'
    )])
    fig.update_layout(xaxis_rangeslider_visible=False, height=600, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Sistem sedang sinkronisasi. Jika error berlanjut, silakan klik 'Reboot App' di menu kanan bawah. Detail: {e}")

st.caption("Gunakan sinyal ini sebagai referensi tambahan. Selalu gunakan manajemen risiko yang ketat!")
