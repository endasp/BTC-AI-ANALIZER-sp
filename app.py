import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --- PENGATURAN TAMPILAN WEB ---
st.set_page_config(page_title="Ultimate Crypto AI", layout="wide")
st.title("💎 AI Crypto Pro: Ultimate Dashboard")
st.write("Analisa Multi-Timeframe, Candlestick Interaktif, MACD, dan Auto TP/SL.")

# --- MENU PILIHAN ---
col_menu1, col_menu2 = st.columns(2)
with col_menu1:
    pilihan_tf = st.selectbox(
        "Pilih Mode Trading (Timeframe):",
        ("🏃 Scalping Normal (5 Menit)", "🚶 Day Trading (15 Menit)", "⏱️ Day Trading Santai (1 Jam)", "📅 Swing Trading (1 Hari)")
    )

# Konfigurasi Timeframe Yahoo Finance
if pilihan_tf == "🏃 Scalping Normal (5 Menit)":
    interval_yf, period_yf = "5m", "5d"
elif pilihan_tf == "🚶 Day Trading (15 Menit)":
    interval_yf, period_yf = "15m", "5d"
elif pilihan_tf == "⏱️ Day Trading Santai (1 Jam)":
    interval_yf, period_yf = "1h", "1mo"
else:
    interval_yf, period_yf = "1d", "6mo"

# --- FUNGSI MENGAMBIL DATA ---
@st.cache_data(ttl=60)
def load_data(interval, period):
    btc = yf.Ticker("BTC-USD")
    df = btc.history(period=period, interval=interval)
    # Ambil berita terbaru (jika tersedia dari yfinance)
    news = btc.news
    return df, news

# --- FUNGSI ANALISA TEKNIKAL LENGKAP ---
def analyze_data(df):
    # 1. EMA 9 & 21
    df['EMA_9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['EMA_21'] = df['Close'].ewm(span=21, adjust=False).mean()
    
    # 2. RSI 14
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # 3. MACD
    df['MACD'] = df['Close'].ewm(span=12, adjust=False).mean() - df['Close'].ewm(span=26, adjust=False).mean()
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()

    # Ambil data harga terakhir
    last_close = df['Close'].iloc[-1]
    
    # 4. Auto TP & SL (Contoh: Risk 1%, Reward 2% dari harga saat ini)
    # Persentase disesuaikan dengan timeframe agar logis
    if "Menit" in pilihan_tf:
        risk_pct = 0.005 # 0.5% untuk scalping
        reward_pct = 0.01 # 1% untuk scalping
    else:
        risk_pct = 0.02 # 2% untuk harian
        reward_pct = 0.05 # 5% untuk harian

    take_profit = last_close * (1 + reward_pct)
    stop_loss = last_close * (1 - risk_pct)
    
    return last_close, df, take_profit, stop_loss

# --- TAMPILAN DASHBOARD ---
try:
    with st.spinner(f'Mengambil data pasar pro untuk {pilihan_tf}...'):
        data, news_data = load_data(interval_yf, period_yf)
        current_price, processed_data, tp, sl = analyze_data(data)
        
        last_rsi = processed_data['RSI'].iloc[-1]
        last_macd = processed_data['MACD'].iloc[-1]
        last_signal = processed_data['Signal_Line'].iloc[-1]
        
        # Penentuan Sinyal Utama
        if last_rsi < 35 and last_macd > last_signal:
            rekomendasi = "🟢 BELI KUAT (Momentum Naik & Harga Murah)"
        elif last_rsi > 65 and last_macd < last_signal:
            rekomendasi = "🔴 JUAL KUAT (Momentum Turun & Harga Mahal)"
        elif processed_data['EMA_9'].iloc[-1] > processed_data['EMA_21'].iloc[-1]:
            rekomendasi = "↗️ TREN NAIK (Cari Posisi Long)"
        else:
            rekomendasi = "↘️ TREN TURUN (Cari Posisi Short)"

        # --- TAMPILAN ATAS: METRIK ---
        st.markdown("### 📊 Ringkasan Pasar Saat Ini")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Harga BTC", f"${current_price:,.2f}")
        with col2:
            st.metric("RSI (Jenuh Beli/Jual)", f"{last_rsi:.1f}")
        with col3:
            st.metric("Target Profit (TP)", f"${tp:,.2f}")
        with col4:
            st.metric("Batas Rugi (SL)", f"${sl:,.2f}")
            
        st.success(f"**Rekomendasi AI:** {rekomendasi}")
        st.markdown("---")
        
        # --- TAMPILAN TENGAH: GRAFIK CANDLESTICK ---
        st.markdown(f"### 📈 Grafik Candlestick Interaktif ({pilihan_tf})")
        # Buat grafik Plotly
        fig = go.Figure(data=[go.Candlestick(x=processed_data.index,
                        open=processed_data['Open'],
                        high=processed_data['High'],
                        low=processed_data['Low'],
                        close=processed_data['Close'],
                        name='Candlestick')])
        # Tambahkan Garis EMA ke dalam grafik
        fig.add_trace(go.Scatter(x=processed_data.index, y=processed_data['EMA_9'], line=dict(color='blue', width=1), name='EMA 9'))
        fig.add_trace(go.Scatter(x=processed_data.index, y=processed_data['EMA_21'], line=dict(color='orange', width=1), name='EMA 21'))
        fig.update_layout(height=500, margin=dict(l=0, r=0, t=0, b=0), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # --- TAMPILAN BAWAH: BERITA TERKINI ---
        st.markdown("---")
        st.markdown("### 📰 Berita Pasar Terkini (Sentimen)")
        if news_data:
            # Tampilkan 3 berita terbaru
            for article in news_data[:3]:
                st.write(f"- **[{article['title']}]({article['link']})**")
        else:
            st.write("Belum ada update berita signifikan hari ini.")

except Exception as e:
    st.error(f"Terjadi kesalahan teknis: {e}")
