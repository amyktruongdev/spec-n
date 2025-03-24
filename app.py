#Select app.py to deploy to streamlit
import streamlit as st
import pandas as pd
from io import StringIO

st.set_page_config(page_title="Spec Negotiation", layout="centered")

st.title("📊 Upload Spec Negotiation File")

uploaded_file = st.file_uploader("Upload your Excel (.xlsx) file", type=["xlsx"])

if uploaded_file:
    all_sheets = pd.read_excel(uploaded_file, sheet_name=None, header=1)  #Read all sheets using row 2 as header

    result_df = pd.DataFrame()

    for sheet_name, df in all_sheets.items():
        if sheet_name.strip().lower() == "summary":  # Skip "Summary" sheet, safely
            continue

        # Clean column names
        df.columns = df.columns.str.strip()

        # Filter desired columns
        required_cols = ['Spec Number', 'Min', 'Avg', 'Max', 'Result']

        for sheet_name, df in all_sheets.items():
            if sheet_name.strip().lower() == "summary":
                continue

            df.columns = df.columns.astype(str).str.strip().str.replace('\n', ' ')

            # Build a new DataFrame with guaranteed columns
            cleaned_df = pd.DataFrame()

            for col in required_cols:
                if col in df.columns:
                    cleaned_df[col] = df[col]
                else:
                    cleaned_df[col] = ""  # Fill missing columns with empty strings

            result_df = pd.concat([result_df, cleaned_df], ignore_index=True)

    if not result_df.empty:
        st.write("✅ Preview of Extracted Data:")
        st.dataframe(result_df.head())

        from io import StringIO
        csv_buffer = StringIO()
        result_df.to_csv(csv_buffer, index=False)
        st.download_button("📥 Download CSV", csv_buffer.getvalue(), file_name="combinedspec.csv", mime="text/csv")
    else:
        st.warning("No matching data found across sheets.")
