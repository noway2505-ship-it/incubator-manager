import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

FILE_NAME = "batches_web.csv"

birds = {
    "فراخ": (18, 3),
    "رومي": (25, 3),
    "بط بلدي": (25, 3),
    "بط مسكوفي": (32, 3),
    "بط شرشير": (22, 3),
    "سمان": (14, 3),
    "وز": (28, 3),
    "حمام": (15, 2),
    "نعامة": (39, 3),
}

st.set_page_config(page_title="Incubator Manager", layout="wide")
st.title("🐣 نظام إدارة مكنة التفريخ")

# إنشاء الملف لو مش موجود
if not os.path.exists(FILE_NAME):
    df_init = pd.DataFrame(columns=[
        "صاحب الدفعة",
        "النوع",
        "عدد البيض",
        "تاريخ البداية",
        "تاريخ الفرز",
        "تاريخ النزول",
        "تاريخ الفقس"
    ])
    df_init.to_csv(FILE_NAME, index=False)

df = pd.read_csv(FILE_NAME)

# =========================
# إضافة دفعة جديدة
# =========================
with st.form("add_batch"):
    col1, col2, col3, col4 = st.columns(4)

    owner = col1.text_input("اسم صاحب الدفعة")
    bird = col2.selectbox("نوع الطائر", list(birds.keys()))
    eggs = col3.number_input("عدد البيض", min_value=1, step=1)
    start_date = col4.date_input("تاريخ البداية")

    submit = st.form_submit_button("➕ إضافة دفعة")

    if submit:
        if owner.strip() == "":
            st.error("من فضلك اكتب اسم صاحب الدفعة")
        else:
            incub_days, transfer_days = birds[bird]

            sort_date = start_date + timedelta(days=10)
            transfer_date = start_date + timedelta(days=incub_days)
            hatch_date = transfer_date + timedelta(days=transfer_days)

            new_row = {
                "صاحب الدفعة": owner,
                "النوع": bird,
                "عدد البيض": eggs,
                "تاريخ البداية": start_date,
                "تاريخ الفرز": sort_date,
                "تاريخ النزول": transfer_date,
                "تاريخ الفقس": hatch_date,
            }

            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(FILE_NAME, index=False)
            st.success("تمت إضافة الدفعة بنجاح")

# =========================
# عرض الدفعات
# =========================
st.subheader("📋 الدفعات الحالية")

if not df.empty:

    today = datetime.today().date()
    df_display = df.copy()
    df_display["الحالة"] = "🟢 شغال"

    for i in df_display.index:
        transfer_date = pd.to_datetime(df_display.loc[i, "تاريخ النزول"]).date()
        sort_date = pd.to_datetime(df_display.loc[i, "تاريخ الفرز"]).date()

        days_to_transfer = (transfer_date - today).days

        if today == transfer_date:
            df_display.loc[i, "الحالة"] = "🔴 انزل للتحضين"
        elif 0 < days_to_transfer <= 2:
            df_display.loc[i, "الحالة"] = "🟡 قرب النزول"
        elif today == sort_date:
            df_display.loc[i, "الحالة"] = "🟡 فرز اليوم"

    st.dataframe(df_display, use_container_width=True)

    # =========================
    # إحصائيات
    # =========================
    st.markdown("### 📊 الإحصائيات")

    total_eggs = df_display["عدد البيض"].sum()
    st.write(f"🔢 إجمالي عدد البيض الكلي: **{total_eggs}**")

    eggs_per_owner = df_display.groupby("صاحب الدفعة")["عدد البيض"].sum()
    st.write("👤 إجمالي البيض لكل صاحب دفعة:")
    st.dataframe(eggs_per_owner)

else:
    st.info("لا يوجد دفعات حالياً")