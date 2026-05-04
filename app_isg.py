import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Proje Kimliği
st.set_page_config(page_title="İSG VERİ TOPLAMA PRO", page_icon="🛡️")

st.title("🛡️ İSG VERİ TOPLAMA - PROFESYONEL")
st.markdown("---")

# Google Sheets Bağlantısı (En konforlu yol)
# Not: secrets.toml dosyasında url tanımlanmalıdır
conn = st.connection("gsheets", type=GSheetsConnection)

# Veriyi canlı oku
df = conn.read()

# Giriş Ekranı
kurum_kodu = st.text_input("Kurum Kodunuzu Giriniz:", placeholder="Örn: 752280")

if kurum_kodu:
    # Okulu bul
    df['KURUM KODU'] = df['KURUM KODU'].astype(str)
    row = df[df['KURUM KODU'] == kurum_kodu.strip()]

    if not row.empty:
        idx = row.index[0]
        st.success(f"Kurum Doğrulandı: **{df.at[idx, 'OKUL ADI']}**")
        
        with st.form("isg_pro_form"):
            st.subheader("Güvenlik ve İSG Veri Girişi")
            
            # Dinamik Alanlar
            g_sayisi = st.number_input("Özel Güvenlik Görevlisi Sayısı", value=0)
            sabit = st.selectbox("Sabit Okul Görevlisi", ["VAR", "YOK"])
            cihaz = st.selectbox("Elektronik İnceleme Cihazı", ["VAR", "YOK"])
            turnike = st.selectbox("Güvenlik Amaçlı Turnike", ["VAR", "YOK"])
            
            submit = st.form_submit_button("Sisteme Gönder")
            
            if submit:
                # Veriyi DataFrame üzerinde güncelle
                df.at[idx, 'ÖZEL GÜVENLİK \nGÖREVLİSİ SAYISI'] = g_sayisi
                df.at[idx, 'SABİT OKUL GÖREVLİSİ\n(VAR/YOK)'] = sabit
                df.at[idx, 'ELEKTRONİK İNCELEME CİHAZI\n(VAR/YOK)'] = cihaz
                df.at[idx, 'GÜVENLİK AMAÇLI TURNİKE\n(VAR/YOK)'] = turnike
                
                # Google Sheets'e geri yaz (En konforlu an burası)
                conn.update(data=df)
                st.balloons()
                st.success("Veriler merkeze iletildi. Teşekkür ederiz.")
    else:
        st.error("Kayıt bulunamadı. Lütfen kurum kodunu kontrol ediniz.")

# Admin İzleme (Sadece size özel)
if st.sidebar.checkbox("Canlı İzleme Paneli"):
    st.sidebar.write("Toplam Kayıt:", len(df))
    st.sidebar.dataframe(df)