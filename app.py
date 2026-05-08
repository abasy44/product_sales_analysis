import streamlit as st
import pandas as pd
import hashlib
import google.generativeai as genai

# ============================================
# إعدادات الصفحة
# ============================================
st.set_page_config(page_title="نظام هندسة الإيرادات", layout="wide")

api_key = st.secrets.get("GEMINI_API_KEY")
if api_key:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
    except:
        model = None
else:
    model = None

# ============================================
# Layer 1: Smart File Processing مع Caching
# ============================================

@st.cache_data
def load_and_enrich_file(file_bytes: bytes, file_name: str) -> pd.DataFrame:
    """
    بتقرأ الملف مرة واحدة بس — حتى لو المستخدم
    ضغط ١٠٠ زرار، مش هتتنفذ غير لو الملف اتغير
    """
    if file_name.endswith('xlsx'):
        df = pd.read_excel(pd.io.common.BytesIO(file_bytes))
    else:
        df = pd.read_csv(pd.io.common.BytesIO(file_bytes))

    df.columns = [c.strip().capitalize() for c in df.columns]

    # الحسابات الأساسية
    if 'Price' in df.columns and 'Cost' in df.columns:
        df['Profit']       = df['Price'] - df['Cost']
        df['Margin_%']     = (df['Profit'] / df['Price'] * 100).round(2)
        df['Profit_flag']  = df['Profit'].apply(
            lambda x: '🔴 خسارة' if x < 0 else ('🟡 هامش ضعيف' if x < df['Profit'].mean() * 0.5 else '🟢 كويس')
        )

    return df


@st.cache_data
def build_smart_summary(file_hash: str, df_json: str) -> dict:
    """
    بتبني ملخص ذكي وشامل للداتا —
    الـ file_hash بيضمن إن لو الملف اتغير نعمل حساب جديد
    """
    df = pd.read_json(pd.io.common.StringIO(df_json))

    summary = {
        "total_revenue":    round(df['Price'].sum(), 2),
        "total_profit":     round(df['Profit'].sum(), 2),
        "total_cost":       round(df['Cost'].sum(), 2),
        "avg_margin":       round(df['Margin_%'].mean(), 2),
        "operations_count": len(df),
        "loss_count":       int((df['Profit'] < 0).sum()),
        "weak_margin_count":int(
            ((df['Profit'] >= 0) & (df['Profit'] < df['Profit'].mean() * 0.5)).sum()
        ),
        "best_operation":   round(df['Profit'].max(), 2),
        "worst_operation":  round(df['Profit'].min(), 2),
        "profit_std":       round(df['Profit'].std(), 2),
    }

    # لو في عمود اسم المنتج أو الخدمة
    for col in ['Product', 'Item', 'Service', 'Category', 'Name']:
        if col in df.columns:
            top = df.groupby(col)['Profit'].sum().idxmax()
            summary['top_performer'] = f"{top}"
            break

    return summary


# ============================================
# Layer 2: Gemini Call مع Caching
# ============================================

@st.cache_data(ttl=3600)
def get_gemini_insight(summary: dict, file_hash: str) -> str:
    """
    مش هتكلم Gemini غير لو:
    ١. الملف اتغير (file_hash مختلف)
    ٢. أو فات أكتر من ساعة (ttl=3600)
    """
    if not api_key:
        return "المفتاح غير متاح"

    prompt = f"""
    بصفتك خبير تحليل إيرادات متخصص في الورش والمحلات الصغيرة في مصر،
    حلل الأرقام دي وقدم تقرير عملي باللهجة المصرية:

    📊 الأرقام:
    - إجمالي الإيراد: {summary['total_revenue']:,} ج.م
    - إجمالي الربح: {summary['total_profit']:,} ج.م
    - إجمالي التكلفة: {summary['total_cost']:,} ج.م
    - متوسط هامش الربح: {summary['avg_margin']}%
    - عدد العمليات: {summary['operations_count']}
    - عمليات بخسارة: {summary['loss_count']}
    - عمليات بهامش ضعيف: {summary['weak_margin_count']}
    - أعلى ربح في عملية: {summary['best_operation']:,} ج.م
    - أدنى ربح في عملية: {summary['worst_operation']:,} ج.م
    - تشتت الأرباح: {summary['profit_std']:,} (مقياس الاتساق)
    {f"- أعلى منتج/خدمة ربحاً: {summary.get('top_performer', 'غير محدد')}"}

    المطلوب:
    ١. تشخيص سريع لأهم ٣ مشاكل في الأرقام
    ٢. نصيحة عملية واحدة لزيادة الربح الشهر الجاي
    ٣. تحذير واحد لو في خطر على الكاش فلو
    """

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(prompt)
    return response.text


# ============================================
# الواجهة
# ============================================

st.title("📊 مستشار الإيرادات والأتمتة الذكي")
st.markdown("---")

uploaded_file = st.file_uploader(
    "ارفع ملف سجل العمليات (Excel/CSV)",
    type=["xlsx", "csv"]
)

if uploaded_file:
    try:
        file_bytes = uploaded_file.read()
        file_hash  = hashlib.md5(file_bytes).hexdigest()

        # Layer 1: قراءة ومعالجة مع cache
        df = load_and_enrich_file(file_bytes, uploaded_file.name)

        if 'Price' in df.columns and 'Cost' in df.columns:

            # Layer 2: ملخص ذكي مع cache
            summary = build_smart_summary(file_hash, df.to_json())

            # عرض الـ KPIs
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("إجمالي الإيراد",   f"{summary['total_revenue']:,} ج.م")
            c2.metric("إجمالي الربح",     f"{summary['total_profit']:,} ج.م")
            c3.metric("متوسط الهامش",     f"{summary['avg_margin']}%")
            c4.metric("عمليات بخسارة",    f"{summary['loss_count']}")

            # تحذير لو في خسائر
            if summary['loss_count'] > 0:
                st.warning(
                    f"⚠️ عندك {summary['loss_count']} عملية بخسارة — "
                    f"راجع التفاصيل في الجدول تحت"
                )

            # الرسم البياني
            st.subheader("توزيع الأرباح")
            st.bar_chart(df['Profit'])

            st.divider()

            # Layer 3: Gemini مع cache
            if st.button("✨ اطلب تحليل المستشار الذكي"):
                if model:
                    with st.spinner("جاري التحليل..."):
                        insight = get_gemini_insight(summary, file_hash)
                    st.success("💡 رؤية المستشار:")
                    st.write(insight)
                    
                    # ده بيحفظ الـ insight في الـ session
                    # عشان ما يختفيش لو المستخدم عمل أي interaction
                    st.session_state['last_insight'] = insight
                else:
                    st.error("الموديل غير متاح.")

            # عرض آخر insight لو موجود في الـ session
            elif 'last_insight' in st.session_state:
                st.info("💡 آخر تحليل:")
                st.write(st.session_state['last_insight'])

            st.write("بيانات السجل:")
            st.dataframe(df)

        else:
            st.warning("يرجى التأكد من وجود أعمدة Price و Cost في الملف.")

    except Exception as e:
        st.error(f"حدث خطأ: {e}")

if not api_key:
    st.warning("⚠️ يرجى إضافة GEMINI_API_KEY في إعدادات Secrets.")
