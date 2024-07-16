import streamlit as st
import os
import pandas as pd
import plotly.express as px
from datetime import datetime

# 獲取用戶憑據
user_credentials_dict = st.secrets["credentials"]

# Create input boxes in the sidebar
st.sidebar.title('Login')

# Check if the user is logged in
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    username = st.sidebar.text_input('Username')
    password = st.sidebar.text_input('Password', type='password')

    # Create a button to verify user credentials
    if st.sidebar.button('Login'):
        if username in user_credentials_dict and user_credentials_dict[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error('Invalid username or password')
else:
    st.sidebar.write(f'Logged in as: {st.session_state.username}')
    if st.sidebar.button('Logout'):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()

# Display main content
if st.session_state.logged_in:
    # Get the current logged-in username
    username = st.session_state["username"]
    # Title
    st.title(f'Poker Profit/Loss Record')
    # Data
    file_path = os.path.join('data', f'{username}_poker_records.csv')
    try:
        df = pd.read_csv(file_path)
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
    except FileNotFoundError:
        df = pd.DataFrame(columns=['Date', 'Profit/Loss'])

    # Display total profit/loss
    total_profit = df['Profit/Loss'].sum()
    st.metric("Total Profit/Loss", f"${total_profit}")

    with st.expander("Add New Record"):
        # Form to add new record
        with st.form("New Record"):
            date = st.date_input("Date", datetime.now())
            amount = st.number_input("Profit/Loss Amount", step=100)
            submitted = st.form_submit_button("Add Record")
            if submitted:
                new_record = pd.DataFrame({'Date': [date.strftime('%Y-%m-%d')], 'Profit/Loss': [amount]})
                df = pd.concat([df, new_record], ignore_index=True)
                df['Date'] = pd.to_datetime(df['Date'])
                df = df.sort_values(by='Date', ascending=False)  # Sort by date descending
                df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
                df.to_csv(file_path, index=False)
                st.rerun()

    with st.expander("History of Profit/Loss Records"):
        # Display history of records
        st.subheader("History of Profit/Loss Records")

        # Add column names
        col1, col2, col3 = st.columns([3, 3, 1])
        with col1:
            st.write("Date")
        with col2:
            st.write("Profit/Loss")
        with col3:
            st.write("Action")

        # Handle delete action
        for idx, row in df.iterrows():
            col1, col2, col3 = st.columns([3, 3, 1])
            with col1:
                st.write(f"{row['Date']}")
            with col2:
                st.write(f"{row['Profit/Loss']}")
            with col3:
                if st.button("Delete", key=f"delete_{idx}"):
                    df = df.drop(idx).reset_index(drop=True)
                    df['Date'] = pd.to_datetime(df['Date'])
                    df = df.sort_values(by='Date', ascending=False)  # Sort by date descending
                    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
                    df.to_csv(file_path, index=False)
                    st.rerun()

    # Plot profit/loss trend
    if not df.empty:
        df['Date'] = pd.to_datetime(df['Date'])  # Ensure the date format is correct
        fig = px.line(df, x='Date', y='Profit/Loss', title='Profit/Loss Trend', markers=True)
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Profit/Loss',
            title={
                'text': 'Profit/Loss Trend',
                'y': 0.9,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            xaxis=dict(
                tickformat='%Y-%m-%d',
            ),
            yaxis=dict(
                tickformat=','
            )
        )
        st.plotly_chart(fig)
else:
    st.title(f'Poker Profit/Loss Record')
    st.write('Please log in to view the content')
