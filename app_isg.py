import streamlit as st
import pandas as pd
import os

# --- AYARLAR ---
DOSYA_YOLU = "öncelikdereceliokulbilgi.xls"
ANAHTAR_SUTUN = "KURUM KODU"

st.set_page_config(page_title="İSG VERİ TOPLAMA", page_icon="🛡️")
st.title("🛡️ İSG VERİ TOPLAMA")
st.info("Kurum kodunuzu girerek bilgilerinizi güncelleyebilirsiniz.")

# Veri yükleme fonksiyonu
@st.cache_data
def veri_yukle():
    if os.path.exists(DOSYA_YOLU):
        try:
            # Excel dosyasını oku
            return pd.read_excel(DOSYA_YOLU)
        except Exception as e:
            st.error(f"Excel okuma hatası: {e}")
            return None
    return None

df = veri_yukle()

if df is not None:
    kurum_kodu = st.text_input("Kurum Kodu:", placeholder="Örn: 776379")
    
    if kurum_kodu:
        # Kodları metne çevirip temizle
        df[ANAHTAR_SUTUN] = df[ANAHTAR_SUTUN].astype(str).str.strip()
        sonuc = df[df[ANAHTAR_SUTUN] == kurum_kodu.strip()]
        
        if not sonuc.empty:
            idx = sonuc.index[0]
            st.success(f"Okul: {df.at[idx, 'OKUL ADI']}")
            
            with st.form("isg_form"):
                st.subheader("Güncellenecek Bilgiler")
                
                # Excel'deki mevcut değerleri çek (hata payını azaltmak için)
                def get_val(col):
                    val = df.at[idx, col]
                    return val if pd.notna(val) else ""

                g_sayisi = st.number_input("Özel Güvenlik Görevlisi Sayısı", 
                                           min_value=0, 
                                           value=int(df.at[idx, 'ÖZEL GÜVENLİK \nGÖREVLİSİ SAYISI']) if pd.notna(df.at[idx, 'ÖZEL GÜVENLİK \nGÖREVLİSİ SAYISI']) else 0)
                
                sabit = st.selectbox("Sabit Okul Görevlisi", ["VAR", "YOK"], 
                                     index=0 if str(get_val('SABİT OKUL GÖREVLİSİ\n(VAR/YOK)')).upper() == "VAR" else 1)
                
                cihaz = st.selectbox("Elektronik İnceleme Cihazı", ["VAR", "YOK"], 
                                     index=0 if str(get_val('ELEKTRONİK İNCELEME CİHAZI\n(VAR/YOK)')).upper() == "VAR" else 1)
                
                turnike = st.selectbox("Güvenlik Amaçlı Turnike", ["VAR", "YOK"], 
                                       index=0 if str(get_val('GÜVENLİK AMAÇLI TURNİKE\n(VAR/YOK)')).upper() == "VAR" else 1)
                
                if st.form_submit_button("Verileri Kaydet"):
                    # DataFrame'i güncelle
                    df.at[idx, 'ÖZEL GÜVENLİK \nGÖREVLİSİ SAYISI'] = g_sayisi
                    df.at[idx, 'SABİT OKUL GÖREVLİSİ\n(VAR/YOK)'] = sabit
                    df.at[idx, 'ELEKTRONİK İNCELEME CİHAZI\n(VAR/YOK)'] = cihaz
                    df.at[idx, 'GÜVENLİK AMAÇLI TURNİKE\n(VAR/YOK)'] = turnike
                    
                    # Dosyayı kaydet
                    df.to_excel(DOSYA_YOLU, index=False)
                    st.balloons()
                    st.success("Bilgiler başarıyla kaydedildi!")
        else:
            st.warning("Bu kurum koduna ait bir okul bulunamadı.")
else:
    st.error("Excel dosyası (öncelikdereceliokulbilgi.xls) bulunamadı!")
