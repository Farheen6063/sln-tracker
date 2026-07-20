import streamlit as st
import pandas as pd

st.set_page_config(page_title="Salon Management Dashboard", layout="wide")

st.title("✂️ Salon Management & Tracker Dashboard")
st.write("Filter salon records easily by Worker Name, Department, or View Everything!")

uploaded_file = st.file_uploader("Upload Salon Excel File (.xlsx)", type=["xlsx"])

# Automatic mapping of workers to their departments based on your excel structure
WORKER_DEPT_MAPPING = {
    'SAFINA': 'HAIR DEPARTMENT', 'SARA': 'HAIR DEPARTMENT',
    'SAMINA': 'SKIN DEPARTMENT', 'FARZANA': 'SKIN DEPARTMENT', 'NABEELA': 'SKIN DEPARTMENT', 'MARYAM': 'SKIN DEPARTMENT',
    'SIMRAN': 'MANI & PEDI DEPARTMENT', 'TAYYABA': 'MANI & PEDI DEPARTMENT', 'AQSA': 'MANI & PEDI DEPARTMENT', 
    'DIYA': 'MANI & PEDI DEPARTMENT', 'ANUM': 'MANI & PEDI DEPARTMENT', 'FIZA': 'MANI & PEDI DEPARTMENT', 'AYESHA MP': 'MANI & PEDI DEPARTMENT',
    'AYESHA': 'ALL / GENERAL', 'MEHNAZ': 'ALL / GENERAL', 'KINZA': 'ALL / GENERAL', 'LAIBA': 'ALL / GENERAL', 'AMBREEN': 'ALL / GENERAL'
}

if uploaded_file is not None:
    try:
        # Load 'TOTAL WORK' master sheet
        xls = pd.ExcelFile(uploaded_file)
        target_sheet = 'TOTAL WORK' if 'TOTAL WORK' in xls.sheet_names else xls.sheet_names[0]
        
        # Load raw data first to locate the header row dynamically
        df_raw = pd.read_excel(uploaded_file, sheet_name=target_sheet)
        
        # Find the row that contains 'DATE' or 'WORK'
        header_row_index = 0
        for i in range(len(df_raw)):
            row_values = [str(val).strip().upper() for val in df_raw.iloc[i].values]
            if 'DATE' in row_values or 'WORK' in row_values:
                header_row_index = i + 1  # exact index for header
                break
        
        # Re-read the dataframe with the correct header row
        df = pd.read_excel(uploaded_file, sheet_name=target_sheet, skiprows=header_row_index)
        
        # Clean column names
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        if 'WORKER NAME' in df.columns:
            # Clean up names and remove trailing characters/spaces
            df['WORKER NAME'] = df['WORKER NAME'].astype(str).str.strip().str.upper()
            df['WORKER NAME'] = df['WORKER NAME'].str.replace(r'\s+G$', '', regex=True) # Cleans 'SAMINA G' to 'SAMINA'
            df = df[~df['WORKER NAME'].isin(['*', 'NAN', '', 'NONE'])]
            
            # Auto-assign Department to each row based on worker name
            df['DEPARTMENT'] = df['WORKER NAME'].map(WORKER_DEPT_MAPPING).fillna('OTHER / DEALS')
        else:
            st.error("Could not find 'WORKER NAME' column. Please check column headers.")
            st.stop()

        # Clean Date and Amount columns
        if 'DATE' in df.columns:
            df['DATE'] = df['DATE'].ffill()
        if 'AMOUNT' in df.columns:
            df['AMOUNT'] = pd.to_numeric(df['AMOUNT'], errors='coerce').fillna(0)
            
        st.success(f"Successfully loaded and formatted '{target_sheet}' data!")
        
        # --- Create Tabs for your Main Concerns ---
        tab1, tab2, tab3 = st.tabs(["👤 Individual Worker View", "🏢 Department-Wise View", "📋 Complete Master Sheet"])
        
        # 1. INDIVIDUAL WORKER VIEW
        with tab1:
            st.subheader("Extract Individual Worker Records")
            unique_workers = sorted(df['WORKER NAME'].unique())
            selected_worker = st.selectbox("Select Salon Worker:", unique_workers)
            
            worker_df = df[df['WORKER NAME'] == selected_worker]
            
            # Metrics
            st.columns(2)[0].metric(f"Total Services by {selected_worker}", len(worker_df))
            st.columns(2)[1].metric(f"Total Revenue Generated", f"Rs. {worker_df['AMOUNT'].sum():,.0f}")
            
            st.dataframe(worker_df, use_container_width=True)
            
            # Download specific worker list
            csv_worker = worker_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"📥 Download {selected_worker}'s Complete List",
                data=csv_worker,
                file_name=f"{selected_worker}_Report.csv",
                mime="text/csv"
            )
            
        # 2. DEPARTMENT-WISE VIEW
        with tab2:
            st.subheader("Extract Department Records")
            unique_depts = sorted(df['DEPARTMENT'].unique())
            selected_dept = st.selectbox("Select Department:", unique_depts)
            
            dept_df = df[df['DEPARTMENT'] == selected_dept]
            
            # Metrics
            st.columns(2)[0].metric(f"Total Services in {selected_dept}", len(dept_df))
            st.columns(2)[1].metric(f"Total Department Revenue", f"Rs. {dept_df['AMOUNT'].sum():,.0f}")
            
            st.dataframe(dept_df, use_container_width=True)
            
            # Download department list
            csv_dept = dept_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label=f"📥 Download {selected_dept} Full List",
                data=csv_dept,
                file_name=f"{selected_dept}_Report.csv",
                mime="text/csv"
            )
            
        # 3. COMPLETE MASTER SHEET VIEW
        with tab3:
            st.subheader("Full Salon Master Record")
            st.columns(2)[0].metric("Total Salon Services (Overall)", len(df))
            st.columns(2)[1].metric("Total Salon Gross Income", f"Rs. {df['AMOUNT'].sum():,.0f}")
            st.dataframe(df, use_container_width=True)
            
    except Exception as e:
        st.error(f"Error reading file structure: {e}")
else:
    st.info("Awaiting Excel file upload. Please upload 'Month Of July Work.xlsx' to view dashboards.")
