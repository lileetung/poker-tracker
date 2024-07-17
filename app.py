import streamlit as st
import os
import pandas as pd
import plotly.express as px
from datetime import datetime

# credentials
user_credentials_dict = st.secrets["credentials"]

# Check if the user is logged in
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    # Create input boxes in the sidebar
    st.sidebar.title('Login')
    username = st.sidebar.text_input('Username')
    password = st.sidebar.text_input('Password', type='password')

    with st.sidebar:
        # Create a button to verify user credentials
        if st.sidebar.button('Login'):
            if username in user_credentials_dict and user_credentials_dict[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error('Invalid username or password')
        st.divider()
        st.markdown(
            '<h6>Made in &nbsp<img src="https://streamlit.io/images/brand/streamlit-mark-color.png" alt="Streamlit logo" height="16">&nbsp by <a href="https://www.instagram.com/raviiiiiiiiiii/">@leetung</a></h6>',
            unsafe_allow_html=True,
        )
else:
    with st.sidebar:
        st.header(f'Hi, {st.session_state.username}')
        
    # st.sidebar.write(f'Logged in as: {st.session_state.username}')
        if st.sidebar.button('Logout'):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()
        st.divider()
        st.markdown(
            '<h6>Made in &nbsp<img src="https://streamlit.io/images/brand/streamlit-mark-color.png" alt="Streamlit logo" height="16">&nbsp by <a href="https://www.instagram.com/raviiiiiiiiiii/">@leetung</a></h6>',
            unsafe_allow_html=True,
        )
    

# Display main content
if st.session_state.logged_in:
    # Get the current logged-in username
    username = st.session_state["username"]
    # Title
    st.title(f'Poker Tournament Record')
    # Data
    file_path = f'{username}_poker_records.csv'
    try:
        df = pd.read_csv(file_path)
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
        df['Tournament Name'] = df['Tournament Name'].astype(str)
    except FileNotFoundError:
        df = pd.DataFrame({
            'Date': pd.Series(dtype='str'),
            'Tournament Name': pd.Series(dtype='str'),
            'Entry Fee': pd.Series(dtype='float'),
            'Profit/Loss': pd.Series(dtype='float')
        })

    # Display total profit/loss
    if not df.empty:
        # 計算總利潤/損失
        total_profit = df['Profit/Loss'].sum()
        
        # 計算 ROI
        total_entry_fees = df['Entry Fee'].sum()
        roi = (total_profit / total_entry_fees) * 100 if total_entry_fees != 0 else 0
        
        # 計算錢圈率（假設 Profit/Loss > 0 表示進入錢圈）
        in_the_money = (df['Profit/Loss'] > 0).sum()
        total_tournaments = len(df)
        itm_rate = (in_the_money / total_tournaments) * 100 if total_tournaments != 0 else 0

        # 使用 columns 來顯示多個指標
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Profit/Loss", f"${total_profit:,.0f}")
        with col2:
            st.metric("ROI", f"{roi:.2f}%")
        with col3:
            st.metric("ITM Rate", f"{itm_rate:.2f}%")

    with st.expander("Add New Record"):
        # Form to add new record
        with st.form("New Record"):
            date = st.date_input("Date", datetime.now())
            tournament_name = st.text_input("Tournament Name", "")
            entry_fee = st.number_input("Entry Fee", min_value=0, step=100)
            amount = st.number_input("Profit/Loss Amount", step=100)
            submitted = st.form_submit_button("Add Record")
            if submitted:
                new_record = pd.DataFrame({
                    'Date': [date.strftime('%Y-%m-%d')],
                    'Tournament Name': [tournament_name],
                    'Entry Fee': [entry_fee],
                    'Profit/Loss': [amount]
                })
                # 確保新記錄的數據類型與現有 DataFrame 匹配
                for column in df.columns:
                    new_record[column] = new_record[column].astype(df[column].dtype)
                
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
        col1, col2, col3, col4, col5 = st.columns([3, 3, 2, 2, 1])
        with col1:
            st.write("Date")
        with col2:
            st.write("Tournament Name")
        with col3:
            st.write("Entry Fee")
        with col4:
            st.write("Profit/Loss")
        with col5:
            st.write("Action")

        # Handle delete action
        for idx, row in df.iterrows():
            col1, col2, col3, col4, col5 = st.columns([3, 3, 2, 2, 1])
            with col1:
                st.write(f"{row['Date']}")
            with col2:
                st.write(f"{row['Tournament Name']}")
            with col3:
                st.write(f"${row['Entry Fee']}")
            with col4:
                st.write(f"${row['Profit/Loss']}")
            with col5:
                if st.button("x", key=f"delete_{idx}"):
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
    st.title(f'Poker Tournament Record')
    st.write('Please log in to view the content')