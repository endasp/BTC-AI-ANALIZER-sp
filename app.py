import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import google.generativeai as genai
from datetime import datetime

# --- CONFIG AI ---
API_KEY = "AIzaSyB4n5rDd0HTwMMFNPw5Vq--3aVMXDBNf9E"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

st.set_page_config(page_title="AI PRO COMMANDER", layout="wide")

# --- SIDEBAR (PUSAT KENDALI) ---
st.sidebar.title("🚀 KONTROL TRADING")
coin = st.sidebar.selectbox("Pilih Koin:", ("BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "DOGE-USD"))
tf_pilihan = st.sidebar.selectbox("Timeframe:", ("5m", "15m", "1h", "4h", "1d", "1wk"))

st.title(f"🤖 AI Commander: {coin} Strategic Analysis")
st.caption(f"Update Terakhir: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# --- FUNGSI AMBIL DATA & INDIKATOR ---
def get_market_data(symbol, tf):
    period = "1mo" if tf in ["1d", "1wk"] else "3d"
    df = yf.Ticker(symbol).history(period=period, interval=tf)
    # Kalkulasi Indikator Dasar
    df['EMA9'] = df['Close'].ewm(span=9).mean()
    df['EMA21'] = df['Close'].ewm(span=21).mean()
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

try:
    df = get_market_data(coin, tf_pilihan)
    last_price = df['Close'].iloc[-1]
    rsi_now = df['RSI'].iloc[-1]
    ema9 = df['EMA9'].iloc[-1]
    ema21 = df['EMA21'].iloc[-1]

    # --- TAMPILAN HARGA & ALERT ---
    c1, c2, c3 = st.columns(3)
    c1.metric("Harga Saat Ini", f"${last_price:,.2f}")
    c2.metric("RSI (14)", f"{rsi_now:.2f}")
    
    # Logic Warna Alarm
    if last_price > ema9 and rsi_now < 70:
        status = "🟢 SINYAL: STRONG BUY"
        warna = "success"
    elif last_price < ema9 and rsi_now > 30:
        status = "🔴 SINYAL: STRONG SELL"
        warna = "error"
    else:
        status = "🟡 SINYAL: WAIT / NEUTRAL"
        warna = "warning"
    
    st.sidebar.markdown(f"### Status Market\n**{status}**")

    # --- ANALISA AI OTOMATIS ---
    with st.expander("📢 ANALISA STRATEGIS AI (SCALPING & LONG TERM)", expanded=True):
        if st.button("MULAI ANALISA MENDALAM"):
            prompt = f"""
            Bertindaklah sebagai Master Trader & Whale Tracker. Analisa {coin} pada Timeframe {tf_pilihan}.
            Data Saat Ini: Harga ${last_price}, RSI {rsi_now:.2f}, EMA9 {ema9:.2f}.
            Tugas:
            1. Tentukan tren Paus (Akumulasi atau Distribusi?).
            2. Berikan instruksi OPEN POSISI: (Entry, TP, SL).
            3. Berikan saran untuk Scalping vs Swing.
            4. Berikan peringatan bahaya jika ada.
            Jawab dengan sangat tegas dalam Bahasa Indonesia.
            """
            response = model.generate_content(prompt)
            st.write(response.text)

    # --- FITUR TANYA JAWAB ---
    st.markdown("---")
    user_ask = st.text_input("💬 Tanya AI Commander (Contoh: 'Kenapa paus lagi jual?' atau 'Target BTC minggu depan?')")
    if user_ask:
        with st.spinner("AI sedang berpikir..."):
            res = model.generate_content(f"Data Market: {coin} ${last_price}. Pertanyaan User: {user_ask}")
            st.info(res.text)

    # --- GRAFIK INTERAKTIF ---
    fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price')])
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA9'], line=dict(color='blue', width=1), name='EMA 9'))
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA21'], line=dict(color='orange', width=1), name='EMA 21'))
    fig.update_layout(height=600, xaxis_rangeslider_visible=False, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Sistem sedang sinkronisasi. Tunggu sebentar lalu refresh. Error: {e}")
