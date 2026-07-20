import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Salon Management Dashboard", layout="wide")

st.title("✂️ Salon Management & Tracker Dashboard")
st.write("Upload your salon's monthly excel sheet to filter records by Date, Worker, or Department.")

uploaded_file = st.file_uploader("Upload Salon Excel File (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Load the Excel file
        xls = pd.ExcelFile(uploaded_file)
        
        # Check if 'TOTAL WORK' exists, otherwise take the first sheet
        target_sheet = 'TOTAL WORK' if 'TOTAL WORK' in xls.sheet_names else xls.sheet_names[0]
        
        # Read data starting right from where headers are (Row index 2)
        df = pd.read_excel(uploaded_file, sheet_name=target_sheet, skiprows=2)
        
        # Clean column names (strip spaces and uppercase for safety)
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # Forward fill the DATE column (Excel merged cells fix)
        if 'DATE' in df.columns:
            df['DATE'] = df['DATE'].ffill()
            
        # Clean Worker Name column if exists
        if 'WORKER NAME' in df.columns:
            df['WORKER NAME'] = df['WORKER NAME'].astype(str).str.strip()
            df = df[~df['WORKER NAME'].isin(['*', 'nan', '', 'None'])]
            
        # Clean Amount column if exists
        if 'AMOUNT' in df.columns:
            df['AMOUNT'] = pd.to_numeric(df['AMOUNT'], errors='coerce').fillna(0)
            
        st.success(f"Successfully loaded '{target_sheet}' sheet!")
        
        # --- 📅 DATE FILTER ---
        if 'DATE' in df.columns:
            unique_days = sorted(df['DATE'].dropna().unique())
            selected_day = st.selectbox("📅 Select Day/Date of the Month:", unique_days)
            
            # Filter rows for that day
            df_date = df[df['DATE'] == selected_day]
            
            if df_date.empty:
                st.warning(f"No records found for Day: {selected_day}")
            else:
                # Create Tabs
                tab1, tab2 = st.tabs(["👤 Individual Worker View", "📋 Complete Day Overview"])
                
                with tab1:
                    st.subheader(f"Filter Worker Data for Day {selected_day}")
                    if 'WORKER NAME' in df_date.columns:
                        unique_workers = sorted(df_date['WORKER NAME'].unique())
                        selected_worker = st.selectbox("Select salon worker:", unique_workers)
                        
                        worker_df = df_date[df_date['WORKER NAME'] == selected_worker]
                        
                        # Metrics
                        total_tickets = len(worker_df)
                        total_revenue = worker_df['AMOUNT'].sum() if 'AMOUNT' in worker_df.columns else 0
                        
                        col1, col2 = st.columns(2)
                        col1.metric("Total Services Done", f"{total_tickets}")
                        col2.metric("Total Revenue Earned", f"Rs. {total_revenue:,.0f}")
                        
                        # Show Clean Table
                        st.dataframe(worker_df, use_container_width=True)
                        
                        # Download button
                        csv = worker_df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label=f"📥 Download {selected_worker}'s Report (Day {selected_day})",
                            data=csv,
                            file_name=f"{selected_worker}_Day_{selected_day}.csv",
                            mime="text/csv",
                        )
                    else:
                        st.error("WORKER NAME column not found in this sheet.")
                        
                with tab2:
                    st.subheader(f"All Salon Activities for Day {selected_day}")
                    day_tickets = len(df_date)
                    day_revenue = df_date['AMOUNT'].sum() if 'AMOUNT' in df_date.columns else 0
                    
                    col1, col2 = st.columns(2)
                    col1.metric("Total Salon Services (Day)", f"{day_tickets}")
                    col2.metric("Total Salon Revenue (Day)", f"Rs. {day_revenue:,.0f}")
                    
                    st.dataframe(df_date, use_container_width=True)
                    
                    csv_day = df_date.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label=f"📥 Download Full Dataset (Day {selected_day})",
                        data=csv_day,
                        file_name=f"Full_Salon_Day_{selected_day}.csv",
                        mime="text/csv",
                    )
        else:
            st.error("DATE column not found in the sheet. Please make sure the sheet has a DATE column.")
            
    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("Awaiting Excel file upload. Please upload your salon file to begin.")
