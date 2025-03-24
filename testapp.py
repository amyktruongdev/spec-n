import streamlit as st
import pandas as pd
from io import StringIO

st.set_page_config(page_title="Spec Merge Tool", layout="centered")
st.title("📊 Excel-to-CSV Spec Merger")

# Upload section
xlsx_file = st.file_uploader("Upload the Excel (.xlsx) file", type=["xlsx"])
csv_file = st.file_uploader("Upload the Base CSV file", type=["csv"])

if xlsx_file and csv_file:
    # Step 1: Load the Excel and CSV files
    excel_df = pd.read_excel(xlsx_file, header=[0, 1])
    csv_df = pd.read_csv(csv_file)

    # Flatten Excel columns
    excel_df.columns = pd.MultiIndex.from_tuples([
        (str(level0).strip(), str(level1).strip().replace("\n", " "))
        for level0, level1 in excel_df.columns
    ])

    # Extract base columns
    base_cols = [col for col in excel_df.columns if col[1] in ["Spec Number", "Min", "Avg", "Max"]]
    flat_df = excel_df[base_cols].copy()
    flat_df.columns = [col[1] for col in base_cols]  # Flatten column names

    # Drop rows with missing Spec Number
    flat_df = flat_df.dropna(subset=["Spec Number"])

    # Step 2: Parse Spec Number into spec_number and vendor_notes
    flat_df[["spec_number", "vendor_notes"]] = flat_df["Spec Number"].astype(str).str.split("|", n=1, expand=True)

    # Step 3: Merge Min/Avg/Max into CSV
    insert_after = "vendor_notes"
    insert_pos = csv_df.columns.get_loc(insert_after) + 1

    # Merge values by spec_number + vendor_notes
    for index, row in flat_df.iterrows():
        spec = row.get("spec_number")
        vendor = row.get("vendor_notes")
        min_val = row.get("Min")
        avg_val = row.get("Avg")
        max_val = row.get("Max")

        match = (csv_df["spec_number"] == spec) & (csv_df["vendor_notes"] == vendor)
        if match.any():
            # Insert values at the right place
            for col, val in zip(["Min", "Avg", "Max"], [min_val, avg_val, max_val]):
                if col not in csv_df.columns:
                    csv_df.insert(insert_pos, col, "")
                    insert_pos += 1
                csv_df.loc[match, col] = val

    st.success("✅ Matching complete! Here's a preview:")
    st.dataframe(csv_df.head())

    # Allow download
    file_name = st.text_input("Enter a name for your output CSV file (without .csv):", value="merged_output")
    csv_buffer = StringIO()
    csv_df.to_csv(csv_buffer, index=False)

    st.download_button(
        "📥 Download Updated CSV",
        data=csv_buffer.getvalue(),
        file_name=f"{file_name}.csv",
        mime="text/csv"
    )
