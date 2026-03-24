import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import google.generativeai as genai

# --- KUNCI OTAK AI ---
GOOGLE_API_KEY = "AIzaSyB4n5rDd0HTwMMFNPw5Vq--3aVMXDBNf9E"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

st.set_page_config(page_title="AI Trading Commander", layout="wide")
st.title("🤖 AI Commander: Keputusan Trading Otomatis")

pilihan_tf = st.sidebar.selectbox("Pilih Timeframe:", ("5m", "15m", "1h", "1d"))

# --- AMBIL DATA ---
@st.cache_data(ttl=60)
def get_data(tf):
    df = yf.Ticker("BTC-USD").history(period="3d", interval=tf)
    return df

try:
    df = get_data(pilihan_tf)
    last_price = df['Close'].iloc[-1]
    
    # --- PROSES BERPIKIR AI ---
    with st.spinner('AI sedang menganalisa grafik dan menentukan posisi...'):
        prompt = f"""
        Kamu adalah trader Bitcoin profesional yang sangat agresif tapi akurat.
        Data harga BTC saat ini: {last_price}
        Trend 5 candle terakhir: {df['Close'].tail(5).tolist()}
        
        Berikan instruksi perintah yang sangat tegas untuk trader:
        1. KEPUTUSAN: (WAJIB pilih salah satu: OPEN LONG / OPEN SHORT / WAIT)
        2. ANALISA: (Alasan teknikal singkat maksimal 2 kalimat)
        3. HARGA ENTRY: (Sebutkan harga sekarang)
        4. TARGET PROFIT (TP): (Sebutkan angka pastinya)
        5. STOP LOSS (SL): (Sebutkan angka pastinya)
        
        Format jawaban harus rapi dan gunakan Bahasa Indonesia yang garang.
        """
        response = model.generate_content(prompt)
        ai_decision = response.text

    # --- TAMPILAN INSTRUKSI AI ---
    st.markdown("### 📢 INSTRUKSI EKSEKUSI AI:")
    st.info(ai_decision)
    
    st.markdown("---")
    
    # --- GRAFIK KONFIRMASI ---
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
    fig.update_layout(title=f"Grafik Konfirmasi Real-Time ({pilihan_tf})", xaxis_rangeslider_visible=False, height=500)
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Terjadi masalah koneksi ke Otak AI: {e}")
