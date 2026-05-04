import streamlit as st
import pandas as pd
import os

# --- AYARLAR ---
DOSYA_YOLU = "öncelikdereceliokulbilgi.xls"
ANAHTAR_SUTUN = "KURUM KODU"
ORTAK_SIFRE = "İSGVERİ35" 

st.set_page_config(page_title="İSG VERİ TOPLAMA", page_icon="🛡️", layout="centered")

# --- BAŞLIK ---
st.title("🛡️ İSG VERİ TOPLAMA")

# --- 1. ADIM: ANA EKRANDA ŞİFRE KONTROLÜ ---
if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("🔐 Yetkili Girişi")
        girilen_sifre = st.text_input("Sistem Şifresini Giriniz:", type="password")
        if st.button("Sisteme Giriş Yap", use_container_width=True):
            if girilen_sifre == ORTAK_SIFRE:
                st.session_state["auth"] = True
                st.rerun()
            else:
                st.error("Hatalı Şifre!")
    st.stop()

# --- 2. ADIM: VERİ YÜKLEME ---
@st.cache_data
def veri_yukle():
    if os.path.exists(DOSYA_YOLU):
        try:
            # Okurken tüm sütunları esnek (object) yapıyoruz ki TypeError vermesin
            data = pd.read_excel(DOSYA_YOLU)
            return data.astype(object)
        except Exception as e:
            st.error(f"Excel okuma hatası: {e}")
            return None
    return None

df = veri_yukle()

if df is not None:
    st.success("✅ Erişim Onaylandı.")
    kurum_kodu = st.text_input("Kurum Kodunuzu Giriniz:", placeholder="Örn: 776379")
    
    if kurum_kodu:
        df[ANAHTAR_SUTUN] = df[ANAHTAR_SUTUN].astype(str).str.strip()
        sonuc = df[df[ANAHTAR_SUTUN] == kurum_kodu.strip()]
        
        if not sonuc.empty:
            idx = sonuc.index[0]
            st.info(f"🏫 Okul: {df.at[idx, 'OKUL ADI']}")
            
            with st.form("isg_form_yeni"):
                st.subheader("Güncellenecek Bilgiler")
                
                # Excel'deki orijinal sütun isimleri (Kodun tanıdığı haliyle)
                c1 = 'ÖZEL GÜVENLİK \nGÖREVLİSİ SAYISI'
                c2 = 'SABİT OKUL GÖREVLİSİ\n(VAR/YOK)'
                c3 = 'ELEKTRONİK İNCELEME CİHAZI\n(VAR/YOK)'
                c4 = 'GÜVENLİK AMAÇLI TURNİKE\n(VAR/YOK)'

                # Mevcut değerleri güvenli çekme
                def get_val(col):
                    val = df.at[idx, col]
                    return val if pd.notna(val) else ""

                g_sayisi = st.number_input("Özel Güvenlik Görevlisi Sayısı", 
                                           min_value=0, 
                                           value=int(df.at[idx, c1]) if str(df.at[idx, c1]).isdigit() else 0)
                
                sabit = st.selectbox("Sabit Okul Görevlisi", ["VAR", "YOK"], 
                                     index=0 if str(get_val(c2)).upper() == "VAR" else 1)
                
                cihaz = st.selectbox("Elektronik İnceleme Cihazı", ["VAR", "YOK"], 
                                     index=0 if str(get_val(c3)).upper() == "VAR" else 1)
                
                turnike = st.selectbox("Güvenlik Amaçlı Turnike", ["VAR", "YOK"], 
                                       index=0 if str(get_val(c4)).upper() == "VAR" else 1)
                
                if st.form_submit_button("Verileri Kaydet", use_container_width=True):
                    # DataFrame'i güncelle
                    df.at[idx, c1] = g_sayisi
                    df.at[idx, c2] = sabit
                    df.at[idx, c3] = cihaz
                    df.at[idx, c4] = turnike
                    
                    # Dosyayı kaydet
                    df.to_excel(DOSYA_YOLU, index=False)
                    st.cache_data.clear() # Önbelleği temizle ki yeni veriyi görsün
                    st.balloons()
                    st.success("Bilgiler başarıyla kaydedildi!")
        else:
            st.warning("Bu kurum koduna ait bir okul bulunamadı.")
else:
    st.error(f"Sistem dosyası ({DOSYA_YOLU}) bulunamadı!")
