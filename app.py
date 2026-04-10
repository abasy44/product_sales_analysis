import streamlit as st
import pandas as pd

# إعدادات الواجهة
st.set_page_config(page_title="مستشار الإيرادات الذكي", layout="wide")

st.title("📊 نظام هندسة الإيرادات الذكي")
st.markdown("---")

# رفع البيانات - يدعم الآن Excel و CSV
uploaded_file = st.file_uploader("ارفع سجل مبيعات الورشة (Excel أو CSV)", type=["csv", "xlsx"])

if uploaded_file:
    try:
        # تحديد طريقة القراءة بناءً على نوع الملف
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
    
        # تنظيف أسماء الأعمدة وتحويلها لحروف صغيرة للمقارنة فقط
        df.columns = [c.strip().capitalize() for c in df.columns]

        if 'Product' in df.columns:
           st.subheader("تحليل الأداء للمنتجات")
           st.bar_chart(df.set_index('Product')['Net_Profit'])
        else:
           st.warning("لم يتم العثور على عمود باسم Product لرسم البياني.")


        # حساب المقاييس الأساسية
        if 'Price' in df.columns and 'Cost' in df.columns:
            df['Net_Profit'] = df['Price'] - df['Cost']
            total_rev = df['Price'].sum()
            total_profit = df['Net_Profit'].sum()
            
            # عرض النتائج في بطاقات (Metrics)
            col1, col2 = st.columns(2)
            col1.metric("إجمالي المبيعات", f"{total_rev:,.2f} ج.م")
            col2.metric("صافي الربح", f"{total_profit:,.2f} ج.م")
            
            st.divider()
            
            # عرض رسم بياني بسيط (لمسة إضافية للمحترفين)
            st.subheader("تحليل الأداء للمنتجات")
            st.bar_chart(df.set_index('Product')['Net_Profit'])
            
            st.dataframe(df) 
            st.success("تم التحليل الرقمي بنجاح.")
        else:
            st.error("تأكد من وجود أعمدة (Price) و (Cost) في الملف.")
            st.info(f"الأعمدة المكتشفة هي: {list(df.columns)}")
    except Exception as e:
        st.error(f"حدث خطأ أثناء قراءة الملف: {e}")
