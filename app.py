import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. إعدادات الصفحة والذكاء الاصطناعي
st.set_page_config(page_title="مستشار الإيرادات الذكي", layout="wide")

# جلب المفتاح بأمان من إعدادات Streamlit
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    st.warning("يرجى ضبط مفتاح الـ API في الإعدادات لتفعيل المستشار الذكي.")

st.title("📊 نظام هندسة الإيرادات + المستشار الذكي")
st.markdown("---")

uploaded_file = st.file_uploader("ارفع سجل المبيعات (Excel أو CSV)", type=["csv", "xlsx"])

if uploaded_file:
    try:
        # قراءة البيانات وتنظيفها
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('.xlsx') else pd.read_csv(uploaded_file)
        df.columns = [c.strip().capitalize() for c in df.columns]

        if all(col in df.columns for col in ['Price', 'Cost', 'Product']):
            df['Net_Profit'] = df['Price'] - df['Cost']
            
            # عرض المقاييس
            col1, col2 = st.columns(2)
            col1.metric("إجمالي المبيعات", f"{df['Price'].sum():,.2f} ج.م")
            col2.metric("صافي الربح", f"{df['Net_Profit'].sum():,.2f} ج.م")
            
            # الرسم البياني
            st.bar_chart(df.set_index('Product')['Net_Profit'])
            
            # تفعيل المستشار الذكي
            st.divider()
            if st.button("✨ اطلب نصيحة المستشار الذكي"):
                with st.spinner("جاري تحليل البيانات..."):
                    # إرسال ملخص الأرقام للـ AI
                    summary = f"المبيعات {df['Price'].sum()}, الربح {df['Net_Profit'].sum()}, أفضل منتج {df.loc[df['Net_Profit'].idxmax(), 'Product']}"
                    prompt = f"أنت خبير أعمال، بناءً على هذه الأرقام لورشة صغيرة: {summary}. قدم نصيحتين لزيادة الربح بلهجة مصرية عملية."
                    
                    response = model.generate_content(prompt)
                    st.success("تحليل المستشار الذكي:")
                    st.write(response.text)
        
    except Exception as e:
        st.error(f"خطأ: {e}")
