import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- AYARLAR ---
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

# --- 2. ADIM: GOOGLE SHEETS BAĞLANTISI ---
@st.cache_resource
def baglanti_kur():
    return st.connection("gsheets", type=GSheetsConnection)

try:
    conn = baglanti_kur()
    
    @st.cache_data(ttl=5)
    def veri_yukle():
        # Veriyi oku ve tüm tabloyu esnek (object) tipine çevir (TypeError hatasını önler)
        data = conn.read()
        return data.astype(object)

    df = veri_yukle()
except Exception as e:
    st.error("Veri tabanına (Google Sheets) bağlanılamadı.")
    st.stop()

# --- 3. ADIM: SORGULAMA VE FORM ---
if df is not None:
    st.success("✅ Erişim Onaylandı.")
    kurum_kodu = st.text_input("Kurum Kodunuzu Giriniz:", placeholder="Örn: 776379")
    
    if kurum_kodu:
        # Kodları metne çevirip temizle
        df[ANAHTAR_SUTUN] = df[ANAHTAR_SUTUN].astype(str).str.strip()
        sonuc = df[df[ANAHTAR_SUTUN] == kurum_kodu.strip()]
        
        if not sonuc.empty:
            idx = sonuc.index[0]
            st.info(f"🏫 Okul: {df.at[idx, 'OKUL ADI']}")
            
            with st.form("isg_google_form"):
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

                # Sayısal veri kontrolü
                raw_v1 = df.at[idx, c1]
                v_g_sayisi = st.number_input("Özel Güvenlik Görevlisi Sayısı", 
                                             min_value=0, 
                                             value=int(raw_v1) if str(raw_v1).isdigit() else 0)
                
                v_sabit = st.selectbox("Sabit Okul Görevlisi", ["VAR", "YOK"], 
                                     index=0 if str(get_val(c2)).upper() == "VAR" else 1)
                
                v_cihaz = st.selectbox("Elektronik İnceleme Cihazı", ["VAR", "YOK"], 
                                     index=0 if str(get_val(c3)).upper() == "VAR" else 1)
                
                v_turnike = st.selectbox("Güvenlik Amaçlı Turnike", ["VAR", "YOK"], 
                                       index=0 if str(get_val(c4)).upper() == "VAR" else 1)
                
                if st.form_submit_button("Bilgileri Google Tabloya İşle", use_container_width=True):
                    # DataFrame'i güncelle
                    df.at[idx, c1] = v_g_sayisi
                    df.at[idx, c2] = v_sabit
                    df.at[idx, c3] = v_cihaz
                    df.at[idx, c4] = v_turnike
                    
                    # Google Sheets'i güncelle
                    conn.update(data=df)
                    st.cache_data.clear() # Yeni verinin hemen görünmesi için
                    st.balloons()
                    st.success("Bilgiler Google Tabloya başarıyla kaydedildi!")
        else:
            st.warning("Bu kurum koduna ait bir okul bulunamadı.")
