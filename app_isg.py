import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="İSG VERİ SİSTEMİ", page_icon="🛡️", layout="centered")

# --- BAŞLIK ---
st.markdown("<h1 style='text-align: center;'>🛡️ İSG VERİ TOPLAMA SİSTEMİ</h1>", unsafe_allow_html=True)
st.info("Kurum kodunuzu girerek bilgilerinizi güncelleyebilirsiniz. Hatalı giriş yaparsanız doğru bilgileri yazıp tekrar kaydetmeniz yeterlidir.")

# --- GOOGLE SHEETS BAĞLANTISI ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Veriyi oku ve temizle
    @st.cache_data(ttl=5)
    def veri_yukle():
        data = conn.read()
        # Sütun isimlerindeki gizli Enter (\n) karakterlerini ve boşlukları temizle
        data.columns = [str(c).replace('\n', ' ').strip() for c in data.columns]
        # Hata önleyici: Tüm tabloyu metin/nesne formatına çevir (Sayı sütununa metin yazabilmek için)
        return data.astype(object)

    df = veri_yukle()

except Exception as e:
    st.error(f"⚠️ Bağlantı Hatası: {e}")
    st.warning("Lütfen Streamlit Secrets ayarlarını ve Google Tablo paylaşım izinlerini (Düzenleyici/Editor) kontrol edin.")
    st.stop()

# --- SORGULAMA EKRANI ---
st.subheader("🔍 Kurum Sorgulama")
kurum_kodu = st.text_input("Kurum Kodunu Giriniz:", placeholder="Örn: 776379")

if kurum_kodu:
    # Arama yapılacak sütunu hazırla
    ANAHTAR = "KURUM KODU"
    df[ANAHTAR] = df[ANAHTAR].astype(str).str.strip()
    
    # Kurumu ara
    sonuc = df[df[ANAHTAR] == kurum_kodu.strip()]
    
    if not sonuc.empty:
        idx = sonuc.index[0]
        st.success(f"🏫 **KURUM:** {df.at[idx, 'OKUL ADI']}")
        st.divider()
        
        # --- VERİ GİRİŞ FORMU ---
        with st.form("isg_form_v2"):
            st.markdown("### 📝 Güncel Bilgileri Giriniz")
            
            # Sütun İsimleri (Tablonuzla birebir uyumlu)
            col1 = 'ÖZEL GÜVENLİK GÖREVLİSİ SAYISI'
            col2 = 'SABİT OKUL GÖREVLİSİ (VAR/YOK)'
            col3 = 'ELEKTRONİK İNCELEME CİHAZI (VAR/YOK)'
            col4 = 'GÜVENLİK AMAÇLI TURNİKE (VAR/YOK)'

            # Mevcut değerleri güvenli şekilde çekme
            def safe_val(c):
                v = df.at[idx, c]
                return v if pd.notna(v) else ""

            # Girdiler
            v_g_sayisi = st.number_input("Özel Güvenlik Görevlisi Sayısı", 
                                         min_value=0, 
                                         value=int(df.at[idx, col1]) if str(df.at[idx, col1]).isdigit() else 0)
            
            v_sabit = st.selectbox("Sabit Okul Görevlisi", ["VAR", "YOK"], 
                                   index=0 if str(safe_val(col2)).upper() == "VAR" else 1)
            
            v_cihaz = st.selectbox("Elektronik İnceleme Cihazı", ["VAR", "YOK"], 
                                   index=0 if str(safe_val(col3)).upper() == "VAR" else 1)
            
            v_turnike = st.selectbox("Güvenlik Amaçlı Turnike", ["VAR", "YOK"], 
                                     index=0 if str(safe_val(col4)).upper() == "VAR" else 1)

            # Kaydet Butonu
            submit = st.form_submit_button("💾 SİSTEME İŞLE VE KAYDET", use_container_width=True)

            if submit:
                # Veriyi DataFrame üzerine yaz
                df.at[idx, col1] = v_g_sayisi
                df.at[idx, col2] = v_sabit
                df.at[idx, col3] = v_cihaz
                df.at[idx, col4] = v_turnike
                
                # Google Sheets'e gönder
                conn.update(data=df)
                st.cache_data.clear() # Önbelleği temizle
                
                st.balloons()
                st.info(f"✅ KAYDEDİLDİ: {df.at[idx, 'OKUL ADI']} verileri başarıyla güncellenmiştir.")
    else:
        st.error("❌ Bu kurum koduna ait bir kayıt bulunamadı.")

# Alt Bilgi (Gizli Tablo Görüntüleme)
with st.expander("📊 Güncel Veri Tablosu"):
    st.dataframe(df)
