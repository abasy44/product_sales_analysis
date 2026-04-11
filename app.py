import streamlit as st
import google.generativeai as genai

# 1. محاولة جلب المفتاح
api_key = st.secrets.get("GEMINI_API_KEY")

st.title("🧪 فحص اتصال Google AI")

if not api_key:
    st.error("❌ المفتاح السري (API Key) غير موجود في إعدادات Secrets.")
else:
    try:
        genai.configure(api_key=api_key)
        st.info("🔄 جاري الاتصال بسيرفرات جوجل وكشف الموديلات المتاحة...")
        
        # 2. طلب قائمة الموديلات من جوجل
        models = genai.list_models()
        
        st.write("### ✅ قائمة الموديلات التي تدعم حسابك حالياً:")
        found_any = False
        for m in models:
            if 'generateContent' in m.supported_generation_methods:
                # عرض اسم الموديل داخل صندوق كود لسهولة النسخ
                st.code(m.name)
                found_any = True
        
        if not found_any:
            st.warning("⚠️ تم الاتصال، ولكن جوجل لم ترجع أي موديلات تدعم توليد المحتوى لهذا الحساب.")

    except Exception as e:
        st.error(f"❌ فشل الاتصال بالخدمة.")
        st.exception(e) # هذا سيعطينا تفاصيل الخطأ التقني بالكامل
