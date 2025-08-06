import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import io
import os
from collections import defaultdict
import numpy as np

st.set_page_config(page_title="Student Expense Tracker", layout="wide")

# File path for persistent storage
DATA_FILE = "expenses.csv"

# Load data from CSV or initialize if not exists
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["Date", "Category", "Amount", "Note"])

# Save data to CSV
def save_data(data):
    data.to_csv(DATA_FILE, index=False)

# Initialize or load data
if 'df' not in st.session_state:
    st.session_state.df = load_data()

# Get category suggestions based on note
def get_category_suggestion(note, existing_mappings):
    if isinstance(note, str) and note.strip():
        note_lower = note.lower()
        if note_lower in existing_mappings:
            return existing_mappings[note_lower]
    return ""

# Create category-note mappings from existing data
note_category_mapping = {}
if not st.session_state.df.empty:
    for _, row in st.session_state.df.iterrows():
        if pd.notna(row['Note']) and isinstance(row['Note'], str):
            note_category_mapping[row['Note'].lower()] = row['Category']

st.title("💰 Student Expense Tracker")

# --- Sidebar form for adding expense ---
st.sidebar.header("Add New Expense")
with st.sidebar.form("expense_form"):
    date = st.date_input("Date", datetime.today())
    note = st.text_input("Note")
    
    # Suggest category based on note
    suggested_category = get_category_suggestion(note, note_category_mapping)
    category = st.text_input("Category", value=suggested_category)
    
    amount = st.number_input("Amount", min_value=0.0, format="%.2f")
    submitted = st.form_submit_button("Add Expense")
    
    if submitted and category and amount > 0:
        new_expense = pd.DataFrame({
            "Date": [str(date)],
            "Category": [category],
            "Amount": [amount],
            "Note": [note]
        })
        st.session_state.df = pd.concat([st.session_state.df, new_expense], ignore_index=True)
        save_data(st.session_state.df)
        st.success("Expense added!")

# Main content
if not st.session_state.df.empty:
    df = st.session_state.df.copy()
    df['Date'] = pd.to_datetime(df['Date'])
    
    # --- Smart Insights Dashboard ---
    st.header("📊 Smart Insights Dashboard")
    
    # Create three columns for metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_spend = df['Amount'].sum()
        st.metric("Total Spend", f"₹{total_spend:.2f}")
    
    with col2:
        top_category = df.groupby('Category')['Amount'].sum().idxmax()
        top_category_amount = df.groupby('Category')['Amount'].sum().max()
        st.metric("Top Spending Category", f"{top_category}\n(₹{top_category_amount:.2f})")
    
    with col3:
        # This month vs last month comparison
        current_month = datetime.now().replace(day=1)
        last_month = (current_month - timedelta(days=1)).replace(day=1)
        
        this_month_spend = df[df['Date'] >= current_month]['Amount'].sum()
        last_month_spend = df[(df['Date'] >= last_month) & (df['Date'] < current_month)]['Amount'].sum()
        
        delta = ((this_month_spend - last_month_spend) / last_month_spend * 100) if last_month_spend != 0 else 0
        st.metric("This Month vs Last Month", 
                 f"₹{this_month_spend:.2f}", 
                 f"{delta:+.1f}%")
    
   
    # --- Filter by category ---
    categories = ["All"] + sorted(df["Category"].unique())
    selected_category = st.selectbox("Filter by Category", categories)

    if selected_category != "All":
        df = df[df["Category"] == selected_category]

    # --- Show table ---
    st.subheader("Recent Expenses")
    
    # Display expenses in a more interactive way with delete buttons
    expenses_df = df.sort_values('Date', ascending=False).reset_index().head(10)
    for _, row in expenses_df.iterrows():
        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 4, 1])
        with col1:
            st.write(row['Date'].strftime('%Y-%m-%d'))
        with col2:
            st.write(row['Category'])
        with col3:
            st.write(f"₹{row['Amount']:.2f}")
        with col4:
            st.write(row['Note'] if pd.notna(row['Note']) else "")
        with col5:
            original_index = row['index']
            if st.button("🗑️", key=f"delete_{original_index}"):
                # Remove the record from the dataframe using the original index
                st.session_state.df = st.session_state.df.drop(index=original_index)
                # Save the updated dataframe
                save_data(st.session_state.df)
                st.rerun()
    
    st.markdown("---")  # Add a separator

    # Create two columns for charts
    col1, col2 = st.columns(2)

    # --- Pie Chart by Category ---
    with col1:
        st.subheader("Expenses by Category")
        category_totals = df.groupby("Category")["Amount"].sum()

        if not category_totals.empty:
            fig1, ax1 = plt.subplots(figsize=(6, 4))
            category_totals.plot.pie(autopct="%1.1f%%", ax=ax1)
            plt.tight_layout()
            st.pyplot(fig1)

    # --- Monthly Report (Bar Chart) ---
    with col2:
        st.subheader("Monthly Expenses Report")
        monthly_totals = df.resample('M', on='Date')['Amount'].sum()
        
        if not monthly_totals.empty:
            fig2, ax2 = plt.subplots(figsize=(6, 4))
            monthly_totals.plot.bar(ax=ax2, color="skyblue")
            plt.xticks(rotation=0)
            plt.ylabel("Amount (₹)")
            plt.tight_layout()
            st.pyplot(fig2)

    # --- Export to CSV ---
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    st.download_button(
        label="📥 Download as CSV",
        data=csv_buffer.getvalue(),
        file_name="expenses.csv",
        mime="text/csv"
    )

else:
    st.info("No expenses added yet. Use the form in the sidebar to get started!")
