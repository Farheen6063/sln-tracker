import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Salon Management Dashboard", layout="wide")

st.title("✂️ Salon Management & Tracker Dashboard")
st.write("Upload your salon's daily sales excel sheet to filter records by Date, Worker, or Department.")

uploaded_file = st.file_uploader("Upload Excel File (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Read Excel Data
        df = pd.read_excel(uploaded_file)
        
        # Clean column names (remove spaces)
        df.columns = [c.strip() for c in df.columns]
        
        # Convert Date column to standard format for filtering
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        
        st.success("Master salon sheet parsed successfully!")
        
        # --- 📅 DATE FILTER (NEW FEATURE) ---
        all_dates = sorted(df['Date'].unique(), reverse=True)
        selected_date = st.date_input("📅 Select Date to View Records:", value=all_dates[0] if all_dates else datetime.today().date())
        
        # Filter data by the chosen date first
        df_date = df[df['Date'] == selected_date]
        
        if df_date.empty:
            st.warning(f"No records found for the selected date: {selected_date}")
        else:
            # Create Tabs for Views
            tab1, tab2 = st.tabs(["👤 Individual Worker View", "🏢 Department Deep-Dive"])
            
            with tab1:
                st.subheader(f"Filter Worker Data for {selected_date}")
                unique_workers = sorted(df_date['Worker Name'].dropna().unique())
                selected_worker = st.selectbox("Select salon worker:", unique_workers)
                
                worker_df = df_date[df_date['Worker Name'] == selected_worker]
                
                # Metrics
                total_tickets = len(worker_df)
                total_revenue = worker_df['Price'].sum()
                
                col1, col2 = st.columns(2)
                col1.metric("Total Tickets", f"{total_tickets}")
                col2.metric("Total Revenue", f"${total_revenue:,.2f}")
                
                # Display Table
                st.dataframe(worker_df, use_container_width=True)
                
                # Download Button for specific worker on that day
                csv = worker_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=f"📥 Download {selected_worker}'s Row Data ({selected_date})",
                    data=csv,
                    file_name=f"{selected_worker}_{selected_date}_report.csv",
                    mime="text/csv",
                )
                
            with tab2:
                st.subheader(f"Filter Whole Department Data for {selected_date}")
                unique_depts = sorted(df_date['Department'].dropna().unique())
                selected_dept = st.selectbox("Select salon department:", unique_depts)
                
                dept_df = df_date[df_date['Department'] == selected_dept]
                
                # Metrics
                dept_tickets = len(dept_df)
                dept_revenue = dept_df['Price'].sum()
                
                col1, col2 = st.columns(2)
                col1.metric(f"Total {selected_dept} Tickets", f"{dept_tickets}")
                col2.metric(f"Total {selected_dept} Revenue", f"${dept_revenue:,.2f}")
                
                # Display Table
                st.dataframe(dept_df, use_container_width=True)
                
                # Download Button for department
                csv_dept = dept_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label=f"📥 Download {selected_dept} Department Dataset ({selected_date})",
                    data=csv_dept,
                    file_name=f"{selected_dept}_{selected_date}_report.csv",
                    mime="text/csv",
                )
    except Exception as e:
        st.error(f"Error processing file: {e}. Please make sure column headers match 'Date', 'Worker Name', 'Service Rendered', 'Price', 'Client Name', 'Department'.")
else:
    st.info("Awaiting Excel file upload. Please upload the salon data sheet to begin.")
