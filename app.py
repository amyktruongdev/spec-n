# app.py - Upload Spec Negotiation File & Extract Key Summary Data

import streamlit as st
import pandas as pd
from io import StringIO

st.set_page_config(page_title="Spec Negotiation", layout="centered")

st.title("📊 Upload Spec Negotiation File")

uploaded_file = st.file_uploader("Upload your Excel (.xlsx) file", type=["xlsx"])

if uploaded_file:
    # Read all sheets with MultiIndex headers (row 1 and 2 in Excel)
    all_sheets = pd.read_excel(uploaded_file, sheet_name=None, header=[0, 1])

    result_df = pd.DataFrame()
    target_summary = "58452-Summary"
    summary_cols = ["Min", "Avg", "Max", "Result"]
    base_cols = ["Spec Number"]

    for sheet_name, df in all_sheets.items():
        if sheet_name.strip().lower() == "summary":
            continue

        # Strip spaces and line breaks from headers
        df.columns = pd.MultiIndex.from_tuples([
            (str(level0).strip(), str(level1).strip().replace('\n', ' '))
            for level0, level1 in df.columns
        ])

        # Extract Spec Number & Description from unnamed group header
        base_data = pd.DataFrame()
        for col in base_cols:
            match = [c for c in df.columns if c[1] == col]
            if match:
                base_data[col] = df[match[0]]
            else:
                base_data[col] = ""

        # Extract summary data only under 58452-Summary
        summary_data = pd.DataFrame()
        for col in summary_cols:
            key = (target_summary, col)
            if key in df.columns:
                summary_data[col] = df[key]
            else:
                summary_data[col] = ""

        # Combine Spec + Summary
        combined = pd.concat([base_data, summary_data], axis=1)
        result_df = pd.concat([result_df, combined], ignore_index=True)

    if not result_df.empty:
        st.write("✅ Preview of Extracted Data:")
        st.dataframe(result_df.head())

        csv_buffer = StringIO()
        result_df.to_csv(csv_buffer, index=False)
        st.download_button("📥 Download CSV", csv_buffer.getvalue(), file_name="combinedspec.csv", mime="text/csv")
    else:
        st.warning("No matching data found across sheets.")
