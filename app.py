import streamlit as st
import pandas as pd
import google.generativeai as genai

# إعدادات الصفحة
st.set_page_config(page_title="مستشار الإيرادات الذكي", layout="wide")

# --- جزء الربط بالذكاء الاصطناعي ---
# نحاول جلب المفتاح من الخزنة السرية (Secrets)
api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
    except Exception as e:
        model = None
        st.error(f"فشل في إعداد المستشار: {e}")
else:
    model = None
    st.warning("⚠️ تنبيه: مفتاح الـ API غير موجود في إعدادات Secrets. لن يعمل المستشار الذكي حالياً.")

# --- واجهة التطبيق ---
st.title("📊 نظام هندسة الإيرادات الذكي")
st.markdown("---")

uploaded_file = st.file_uploader("ارفع سجل المبيعات (Excel أو CSV)", type=["csv", "xlsx"])

if uploaded_file:
    try:
        # قراءة البيانات وتنظيفها
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
        df.columns = [c.strip().capitalize() for c in df.columns]

        if all(col in df.columns for col in ['Price', 'Cost', 'Product']):
            df['Net_Profit'] = df['Price'] - df['Cost']
            
            # عرض المقاييس الأساسية
            col1, col2 = st.columns(2)
            col1.metric("إجمالي المبيعات", f"{df['Price'].sum():,.2f} ج.م")
            col2.metric("صافي الربح", f"{df['Net_Profit'].sum():,.2f} ج.م")
            
            # الرسم البياني
            st.subheader("تحليل الأداء للمنتجات")
            st.bar_chart(df.set_index('Product')['Net_Profit'])
            
            # --- تفعيل زر المستشار الذكي ---
            st.divider()
            if st.button("✨ اطلب نصيحة المستشار الذكي"):
                if model:
                    with st.spinner("جاري تحليل البيانات واستخراج الرؤى..."):
                        # تجهيز البيانات للإرسال
                        summary = f"المبيعات {df['Price'].sum()}, الربح {df['Net_Profit'].sum()}, أفضل منتج {df.loc[df['Net_Profit'].idxmax(), 'Product']}"
                        prompt = f"بناءً على هذه الأرقام لورشة صغيرة: {summary}. قدم 3 نصائح عملية لزيادة الربح بلهجة مصرية مهنية."
                        
                        response = model.generate_content(prompt)
                        st.success("💡 رؤية المستشار الذكي:")
                        st.write(response.text)
                else:
                    st.error("المستشار غير مفعل. يرجى التأكد من وضع GEMINI_API_KEY في Secrets.")
            
            st.write("جدول البيانات المنظم:")
            st.dataframe(df)
            
    except Exception as e:
        st.error(f"حدث خطأ في معالجة الملف: {e}")
