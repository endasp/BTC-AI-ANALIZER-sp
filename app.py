import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# --- PENGATURAN TAMPILAN WEB ---
st.set_page_config(page_title="Pro Crypto AI", layout="wide")
st.title("⚡ AI Crypto Pro: Multi-Timeframe")
st.write("Pilih gaya tradingmu di bawah ini, AI akan otomatis menyesuaikan analisa pasar.")

# --- PILIHAN TIMEFRAME DARI USER ---
pilihan_tf = st.selectbox(
    "Pilih Mode Trading (Timeframe):",
    (
        "⚡ Scalping Super Cepat (1 Menit)", 
        "🏃 Scalping Normal (5 Menit)", 
        "🚶 Day Trading (15 Menit)", 
        "⏱️ Day Trading Santai (1 Jam)", 
        "📅 Swing Trading (1 Hari)"
    )
)

# Menentukan parameter Yahoo Finance berdasarkan pilihan user
if pilihan_tf == "⚡ Scalping Super Cepat (1 Menit)":
    interval_yf = "1m"
    period_yf = "1d" # yfinance cuma bisa narik 1m maksimal 7 hari terakhir
elif pilihan_tf == "🏃 Scalping Normal (5 Menit)":
    interval_yf = "5m"
    period_yf = "5d"
elif pilihan_tf == "🚶 Day Trading (15 Menit)":
    interval_yf = "15m"
    period_yf = "5d"
elif pilihan_tf == "⏱️ Day Trading Santai (1 Jam)":
    interval_yf = "1h"
    period_yf = "1mo"
else:
    interval_yf = "1d"
    period_yf = "6mo"

# --- FUNGSI MENGAMBIL DATA ---
@st.cache_data(ttl=60) # Refresh tiap 60 detik
def load_data(interval, period):
    btc = yf.Ticker("BTC-USD")
    df = btc.history(period=period, interval=interval)
    return df

# --- FUNGSI ANALISA TEKNIKAL ---
def analyze_data(df):
    # EMA 9 & 21
    df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
    
    # RSI 14
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    last_close = df['Close'].iloc[-1]
    last_ema9 = df['EMA_9'].iloc[-1]
    last_ema21 = df['EMA_21'].iloc[-1]
    last_rsi = df['RSI'].iloc[-1]
    
    # Logika Sinyal
    if last_rsi >= 70:
        signal = "⚠️ JENUH BELI (Siap-siap Take Profit / Jual)"
    elif last_rsi <= 30:
        signal = "⚠️ JENUH JUAL (Potensi Pantulan Naik / Beli)"
    elif last_ema9 > last_ema21:
        signal = "🟢 TREN NAIK (Fokus Cari Beli)"
    elif last_ema9 < last_ema21:
        signal = "🔴 TREN TURUN (Fokus Cari Jual)"
    else:
        signal = "🟡 KONSOLIDASI (Tunggu Konfirmasi)"
        
    return last_close, signal, last_rsi, df

# --- PROSES & TAMPILKAN DI WEB ---
try:
    with st.spinner(f'Menarik data {pilihan_tf}...'):
        data = load_data(interval_yf, period_yf)
        
        if data.empty:
            st.error("Gagal menarik data dari server. Coba beberapa saat lagi.")
        else:
            current_price, trading_signal, current_rsi, processed_data = analyze_data(data)
            
            # Tampilkan Angka
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(label="Harga BTC (USD)", value=f"${current_price:,.2f}")
            with col2:
                st.metric(label="RSI (Kekuatan)", value=f"{current_rsi:.2f}", delta=">70 Overbought | <30 Oversold", delta_color="off")
            with col3:
                st.subheader(f"Sinyal {interval_yf}:")
                st.write(f"**{trading_signal}**")
                
            st.markdown("---")
            
            # Tampilkan Grafik
            st.subheader(f"Grafik Pergerakan Harga ({pilihan_tf})")
            # Menampilkan 100 data terakhir agar grafik tidak terlalu padat
            st.line_chart(processed_data[['Close', 'EMA_9', 'EMA_21']].tail(100))
            
except Exception as e:
    st.error(f"Terjadi kesalahan: {e}")
