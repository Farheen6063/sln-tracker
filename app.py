import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Salon Management Dashboard", layout="wide")

st.title("✂️ Salon Management & Tracker Dashboard")
st.write("Upload your salon's monthly excel sheet to filter records by Date, Worker, or Department.")

uploaded_file = st.file_uploader("Upload Salon Excel File (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Check if 'TOTAL WORK' master sheet exists
        xls = pd.ExcelFile(uploaded_file)
        
        if 'TOTAL WORK' in xls.sheet_names:
            # Load the main master sheet
            df = pd.read_excel(uploaded_file, sheet_name='TOTAL WORK', skiprows=2)
        else:
            # Fallback to the first sheet if TOTAL WORK isn't found
            df = pd.read_excel(uploaded_file, sheet_name=0, skiprows=2)
            
        # Clean column names (strip spaces and convert to string)
        df.columns = [str(c).strip() for c in df.columns]
        
        # Drop rows where essential columns are completely null
        df = df.dropna(subset=['WORK', 'AMOUNT'], how='all')
        
        # Forward fill the Date column since Excel leaves merged/blank rows for same day
        df['DATE'] = df['DATE'].ffill()
        
        # Clean up Worker Name column
        if 'WORKER NAME' in df.columns:
            df['WORKER NAME'] = df['WORKER NAME'].astype(str).str.strip()
            # Remove filler stars or empty names
            df = df[~df['WORKER NAME'].isin(['*', 'nan', ''])]
            
        # Clean Amount column (convert to numeric, handle errors gracefully)
        df['AMOUNT'] = pd.to_numeric(df['AMOUNT'], errors='coerce').fillna(0)
        
        st.success("Aunt's Salon Sheet loaded successfully!")
        
        # --- 📅 DATE FILTER ---
        # Get unique dates/days available
        unique_days = sorted(df['DATE'].dropna().unique())
        selected_day = st.selectbox("📅 Select Day/Date of the Month:", unique_days)
        
        # Filter dataframe by selected day
        df_date = df[df['DATE'] == selected_day]
        
        if df_date.empty:
            st.warning(f"No records found for Day: {selected_day}")
        else:
            # Create Tabs for Views
            tab1, tab2 = st.tabs(["👤 Individual Worker View", "📋 Complete Day Overview"])
            
            with tab1:
                st.subheader(f"Filter Worker Data for Day {selected_day}")
                if 'WORKER NAME' in df_date.columns:
                    unique_workers = sorted(df_date['WORKER NAME'].unique())
                    selected_worker = st.selectbox("Select salon worker:", unique_workers)
                    
                    worker_df = df_date[df_date['WORKER NAME'] == selected_worker]
                    
                    # Metrics
                    total_tickets = len(worker_df)
                    total_revenue = worker_df['AMOUNT'].sum()
                    
                    col1, col2 = st.columns(2)
                    col1.metric("Total Services Done", f"{total_tickets}")
                    col2.metric("Total Revenue Earned", f"Rs. {total_revenue:,.0f}")
                    
                    # Display Table cleanly
                    display_cols = [c for c in ['DATE', 'WORK', 'SLIP NO.', 'BY. NAME', 'AMOUNT', 'CILENT NAME'] if c in worker_df.columns]
                    st.dataframe(worker_df[display_cols], use_container_width=True)
                    
                    # Download Button for specific worker on that day
                    csv = worker_df[display_cols].to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label=f"📥 Download {selected_worker}'s Report (Day {selected_day})",
                        data=csv,
                        file_name=f"{selected_worker}_Day_{selected_day}_Report.csv",
                        mime="text/csv",
                    )
                else:
                    st.error("Worker Name column missing in the sheet.")
                
            with tab2:
                st.subheader(f"All Salon Activities for Day {selected_day}")
                
                # Overall metrics for the day
                day_tickets = len(df_date)
                day_revenue = df_date['AMOUNT'].sum()
                
                col1, col2 = st.columns(2)
                col1.metric("Total Salon Services (Day)", f"{day_tickets}")
                col2.metric("Total Salon Revenue (Day)", f"Rs. {day_revenue:,.0f}")
                
                # Display full table for that day
                st.dataframe(df_date, use_container_width=True)
                
                # Download Button for full day
                csv_day = df_date.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=f"📥 Download Full Dataset (Day {selected_day})",
                    data=csv_day,
                    file_name=f"Full_Salon_Day_{selected_day}_Report.csv",
                    mime="text/csv",
                )
    except Exception as e:
        st.error(f"Error processing file: {e}. Please ensure the sheet structure is correct.")
else:
    st.info("Awaiting Excel file upload. Please upload 'Month Of July Work.xlsx' to begin.")
