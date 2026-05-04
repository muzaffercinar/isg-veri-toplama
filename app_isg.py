import streamlit as st
import pandas as pd
import os

# --- AYARLAR ---
DOSYA_YOLU = "öncelikdereceliokulbilgi.xls"
ANAHTAR_SUTUN = "KURUM KODU"
ORTAK_SIFRE = "ISG2027"  # Her iki ilçe için ortak şifre

st.set_page_config(page_title="İSG VERİ TOPLAMA", page_icon="🛡️")
st.title("🛡️ İSG VERİ TOPLAMA")

# Veri yükleme fonksiyonu
@st.cache_data
def veri_yukle():
    if os.path.exists(DOSYA_YOLU):
        try:
            return pd.read_excel(DOSYA_YOLU)
        except Exception as e:
            st.error(f"Excel okuma hatası: {e}")
            return None
    return None

df = veri_yukle()

if df is not None:
    # 1. ADIM: TEK ŞİFRE DOĞRULAMA
    st.sidebar.header("🔐 Yetkili Girişi")
    girilen_sifre = st.sidebar.text_input("Sistem Şifresini Giriniz:", type="password")

    if girilen_sifre == ORTAK_SIFRE:
        st.sidebar.success("Erişim Onaylandı")
        
        # 2. ADIM: KURUM KODU SORGULAMA
        kurum_kodu = st.text_input("Kurum Kodunuzu Giriniz:", placeholder="Örn: 776379")
        
        if kurum_kodu:
            # Kodları metne çevirip temizle
            df[ANAHTAR_SUTUN] = df[ANAHTAR_SUTUN].astype(str).str.strip()
            sonuc = df[df[ANAHTAR_SUTUN] == kurum_kodu.strip()]
            
            if not sonuc.empty:
                idx = sonuc.index[0]
                okul_adi = df.at[idx, 'OKUL ADI']
                st.success(f"📌 Kurum: {okul_adi}")
                
                with st.form("isg_form_tek"):
                    st.subheader("İSG Veri Giriş Formu")
                    
                    g_sayisi = st.number_input("Özel Güvenlik Görevlisi Sayısı", 
                                               min_value=0, 
                                               value=int(df.at[idx, 'ÖZEL GÜVENLİK \nGÖREVLİSİ SAYISI']) if pd.notna(df.at[idx, 'ÖZEL GÜVENLİK \nGÖREVLİSİ SAYISI']) else 0)
                    
                    sabit = st.selectbox("Sabit Okul Görevlisi", ["VAR", "YOK"], 
                                         index=0 if str(df.at[idx, 'SABİT OKUL GÖREVLİSİ\n(VAR/YOK)']).upper() == "VAR" else 1)
                    
                    cihaz = st.selectbox("Elektronik İnceleme Cihazı", ["VAR", "YOK"], 
                                         index=0 if str(df.at[idx, 'ELEKTRONİK İNCELEME CİHAZI\n(VAR/YOK)']).upper() == "VAR" else 1)
                    
                    turnike = st.selectbox("Güvenlik Amaçlı Turnike", ["VAR", "YOK"], 
                                           index=0 if str(df.at[idx, 'GÜVENLİK AMAÇLI TURNİKE\n(VAR/YOK)']).upper() == "VAR" else 1)
                    
                    if st.form_submit_button("Bilgileri Sisteme İşle"):
                        # Veriyi güncelle
                        df.at[idx, 'ÖZEL GÜVENLİK \nGÖREVLİSİ SAYISI'] = g_sayisi
                        df.at[idx, 'SABİT OKUL GÖREVLİSİ\n(VAR/YOK)'] = sabit
                        df.at[idx, 'ELEKTRONİK İNCELEME CİHAZI\n(VAR/YOK)'] = cihaz
                        df.at[idx, 'GÜVENLİK AMAÇLI TURNİKE\n(VAR/YOK)'] = turnike
                        
                        # Dosyayı kaydet
                        df.to_excel(DOSYA_YOLU, index=False)
                        st.balloons()
                        st.success(f"{okul_adi} verileri başarıyla güncellendi.")
            else:
                st.warning("Bu kurum koduna ait bir kayıt bulunamadı.")
    
    elif girilen_sifre != "":
        st.sidebar.error("Hatalı Şifre!")
    else:
        st.info("İşlem yapmak için lütfen sol taraftaki menüden sistem şifresini giriniz.")
else:
    st.error("Sistem dosyası yüklenemedi.")
