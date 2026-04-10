import streamlit as st
import pandas as pd

# إعدادات الواجهة
st.set_page_config(page_title="مستشار الإيرادات الذكي", layout="wide")

st.title("📊 نظام هندسة الإيرادات الذكي")
st.markdown("---")

uploaded_file = st.file_uploader("ارفع سجل مبيعات الورشة (Excel أو CSV)", type=["csv", "xlsx"])

if uploaded_file:
    try:
        # قراءة الملف
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # تنظيف وتوحيد أسماء الأعمدة (أهم خطوة)
        # سيحول product لـ Product و price لـ Price تلقائياً
        df.columns = [c.strip().capitalize() for c in df.columns]

        # التأكد من وجود البيانات المطلوبة
        required_cols = ['Product', 'Price', 'Cost']
        if all(col in df.columns for col in required_cols):
            
            # حساب صافي الربح
            df['Net_Profit'] = df['Price'] - df['Cost']
            
            # عرض المقاييس الأساسية
            col1, col2 = st.columns(2)
            col1.metric("إجمالي المبيعات", f"{df['Price'].sum():,.2f} ج.م")
            col2.metric("صافي الربح", f"{df['Net_Profit'].sum():,.2f} ج.م")
            
            st.divider()
            
            # الرسم البياني
            st.subheader("تحليل الأداء للمنتجات")
            st.bar_chart(df.set_index('Product')['Net_Profit'])
            
            st.write("جدول البيانات المنظم:")
            st.dataframe(df) 
        else:
            st.error(f"الملف ينقصه بعض الأعمدة. تأكد من وجود: {required_cols}")
            st.info(f"الأعمدة الموجودة حالياً في ملفك هي: {list(df.columns)}")
            
    except Exception as e:
        st.error(f"حدث خطأ في معالجة البيانات: {e}")
