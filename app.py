# Save this as app.py
import streamlit as st
import pandas as pd
from io import StringIO

st.set_page_config(page_title="Excel to CSV Converter", layout="centered")

st.title("📊 Excel to CSV Converter")

uploaded_file = st.file_uploader("Upload your Excel (.xlsx) file", type=["xlsx"])

if uploaded_file:
    all_sheets = pd.read_excel(uploaded_file, sheet_name=None, header=1)  # Use row 2 as header

    result_df = pd.DataFrame()

    for sheet_name, df in all_sheets.items():
        # Check if required columns are present
        required_cols = ['Spec Number', 'Min', 'Avg', 'Max', 'Result']
        available_cols = [col for col in required_cols if col in df.columns]

        if len(available_cols) < len(required_cols):
            st.warning(f"Sheet '{sheet_name}' is missing some of the required columns.")
            continue

        filtered = df[available_cols]
        result_df = pd.concat([result_df, filtered], ignore_index=True)

    if not result_df.empty:
        st.write("✅ Preview of Extracted Data:")
        st.dataframe(result_df.head())

        from io import StringIO
        csv_buffer = StringIO()
        result_df.to_csv(csv_buffer, index=False)
        st.download_button("📥 Download CSV", csv_buffer.getvalue(), file_name="combinedspecs.csv", mime="text/csv")
    else:
        st.warning("No matching data found across sheets.")
