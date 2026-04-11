import streamlit as st
import pandas as pd
import google.generativeai as genai

# إعدادات الصفحة
st.set_page_config(page_title="نظام هندسة الإيرادات", layout="wide")

# جلب المفتاح من الخزنة
api_key = st.secrets.get("GEMINI_API_KEY")

if api_key:
    try:
        genai.configure(api_key=api_key)
        # استخدام الموديل المتاح في حسابك كما ظهر في الفحص (الصورة 23)
        model = genai.GenerativeModel('gemini-2.5-flash')
    except:
        model = None
else:
    model = None

# واجهة التطبيق
st.title("📊 مستشار الإيرادات والأتمتة الذكي")
st.markdown("---")

uploaded_file = st.file_uploader("ارفع ملف سجل العمليات (Excel/CSV)", type=["xlsx", "csv"])

if uploaded_file:
    try:
        # قراءة البيانات
        df = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file)
        df.columns = [c.strip().capitalize() for c in df.columns]

        # التأكد من وجود الأعمدة الحسابية
        if 'Price' in df.columns and 'Cost' in df.columns:
            df['Profit'] = df['Price'] - df['Cost']
            
            # عرض الأرقام الأساسية
            c1, c2, c3 = st.columns(3)
            c1.metric("إجمالي الإيراد", f"{df['Price'].sum():,.0f} ج.م")
            c2.metric("إجمالي الربح", f"{df['Profit'].sum():,.0f} ج.م")
            c3.metric("عدد العمليات", len(df))

            # الرسم البياني
            st.subheader("تحليل الأداء")
            st.bar_chart(df['Profit'])

            # تفعيل المستشار
            st.divider()
            if st.button("✨ اطلب نصيحة المستشار الذكي"):
                if model:
                    with st.spinner("جاري تحليل البيانات..."):
                        # تجهيز ملخص البيانات للموديل
                        data_summary = f"الايراد: {df['Price'].sum()}, الربح: {df['Profit'].sum()}, عدد العمليات: {len(df)}"
                        prompt = f"بصفتك خبير أتمتة، حلل هذه الأرقام لورشة عمل صغيرة: {data_summary}. قدم نصيحة واحدة لزيادة الربح ونصيحة لتجنب الهدر بلهجة مصرية عملية."
                        
                        response = model.generate_content(prompt)
                        st.success("💡 رؤية المستشار:")
                        st.write(response.text)
                else:
                    st.error("الموديل غير متاح، تأكد من إعدادات المفتاح.")
            
            st.write("بيانات السجل الحالية:")
            st.dataframe(df)
        else:
            st.warning("يرجى التأكد من وجود أعمدة باسم Price و Cost في الملف.")
            
    except Exception as e:
        st.error(f"حدث خطأ في قراءة الملف: {e}")

if not api_key:
    st.warning("⚠️ يرجى إضافة GEMINI_API_KEY في إعدادات Secrets لتفعيل الذكاء الاصطناعي.")
