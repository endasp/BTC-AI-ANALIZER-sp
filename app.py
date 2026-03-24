import streamlit as st
import yfinance as yf
import google.generativeai as genai

# CONFIG
genai.configure(api_key="AIzaSyB4n5rDd0HTwMMFNPw5Vq--3aVMXDBNf9E")

# --- TRIK ANTI ERROR 404 ---
try:
    # Coba model terbaru dulu
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    # Kalau gagal, pakai model standar yang paling stabil
    model = genai.GenerativeModel('gemini-pro')

st.title("☁️ Cloud AI Commander")

try:
    df = yf.Ticker("BTC-USD").history(period="1d", interval="5m")
    price = df['Close'].iloc[-1]
    st.metric("Harga BTC Sekarang", f"${price:,.2f}")

    # Tombol Analisa Darurat
    if st.button("CEK INSTRUKSI PENYELAMATAN"):
        prompt = f"BTC sekarang {price}. Saya nyangkut SHORT di 69742. Kasih instruksi CUT LOSS atau HOLD? Jawab tegas dalam Bahasa Indonesia!"
        response = model.generate_content(prompt)
        st.error(response.text)
except Exception as e:
    st.info("Sedang menyambungkan ke satelit pasar... Refresh dalam 5 detik.")
