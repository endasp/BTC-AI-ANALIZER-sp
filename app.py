import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

# --- PENGATURAN TAMPILAN WEB ---
st.set_page_config(page_title="AI Crypto Analyzer", layout="wide")
st.title("🤖 AI Dashboard: Analisa BTC Otomatis")
st.write("Aplikasi ini otomatis menarik data harga Bitcoin dan memberikan sinyal teknikal dasar.")

# --- FUNGSI MENGAMBIL DATA HARGA ---
@st.cache_data(ttl=300) # Data di-refresh otomatis setiap 5 menit
def load_data():
    btc = yf.Ticker("BTC-USD")
    # Ambil data 60 hari terakhir
    df = btc.history(period="60d")
    return df

# --- FUNGSI ANALISA TEKNIKAL & SINYAL ---
def analyze_data(df):
    # Menghitung Simple Moving Average (SMA)
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    
    # Menentukan Sinyal Jual/Beli (Strategi Crossover sederhana)
    last_close = df['Close'].iloc[-1]
    last_sma20 = df['SMA_20'].iloc[-1]
    last_sma50 = df['SMA_50'].iloc[-1]
    
    if last_sma20 > last_sma50 and last_close > last_sma20:
        signal = "🟢 BELI (Uptrend)"
    elif last_sma20 < last_sma50 and last_close < last_sma20:
        signal = "🔴 JUAL (Downtrend)"
    else:
        signal = "🟡 TAHAN (Sideways / Konsolidasi)"
        
    return last_close, signal, df

# --- PROSES & TAMPILKAN DI WEB ---
try:
    with st.spinner('Menganalisa pasar...'):
        data = load_data()
        current_price, trading_signal, processed_data = analyze_data(data)
        
        # Tampilkan Harga dan Sinyal
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Harga BTC Saat Ini (USD)", value=f"${current_price:,.2f}")
        with col2:
            st.subheader("Sinyal AI Saat Ini:")
            st.title(trading_signal)
            
        st.markdown("---")
        
        # Tampilkan Grafik Harga
        st.subheader("Grafik Pergerakan Harga (Dengan SMA 20 & 50)")
        st.line_chart(processed_data[['Close', 'SMA_20', 'SMA_50']])
        
except Exception as e:
    st.error(f"Gagal mengambil data: {e}")

st.caption("Peringatan: Ini adalah analisa teknikal dasar. Trading kripto memiliki risiko tinggi.")
