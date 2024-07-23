import streamlit as st
import uuid
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
import time
import re

def cleanup_old_files():
    current_time = int(time.time())
    cleanup_threshold = current_time - (1 * 60 * 60)  # 1 小時前

    file_pattern = re.compile(r'user_(\d+)_.*_poker_records\.csv')

    for filename in os.listdir('.'):
        match = file_pattern.match(filename)
        if match:
            file_timestamp = int(match.group(1))
            if file_timestamp < cleanup_threshold:
                file_path = os.path.join('.', filename)
                os.remove(file_path)
                print(f"Deleted old file: {filename}")

# 在應用啟動時執行清理 user 體驗用的帳號
cleanup_old_files()

# credentials
user_credentials_dict = st.secrets["credentials"]

# Check if the user is logged in
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'file_uploader_key' not in st.session_state:
    st.session_state.file_uploader_key = 0

if not st.session_state.logged_in:
    # Create input boxes in the sidebar
    st.sidebar.title('Login')
    username = st.sidebar.text_input('Username', placeholder="user")
    password = st.sidebar.text_input('Password', type='password', placeholder="0000")

    with st.sidebar:
        # Create a button to verify user credentials
        if st.sidebar.button('Login'):
            if username in user_credentials_dict and user_credentials_dict[username] == password:
                if username == 'user': # 體驗用帳號
                    st.session_state.logged_in = True
                    current_timestamp = int(time.time())
                    username = f'user_{current_timestamp}_{str(uuid.uuid4())[:8]}'
                    st.session_state.username = username
                    file_path = f'{username}_poker_records.csv'
                    df = pd.DataFrame({
                        'Date': ['2024/07/23', '2024/07/22', '2024/07/20', '2024/07/19', '2024/07/7'],
                        'Tournament Name': ['永和巨籌', '台北日常', '永和深籌', '林口MEGA', '台北超日'],
                        'Entry Fee': [1500, 1500, 1500, 1500, 2000],
                        'Profit/Loss': [4500, -1500, 2600, -1500, 8000]
                    })
                    df.to_csv(file_path, index=False, encoding="utf_8_sig")
                    st.rerun()
                else:
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
        
        if st.sidebar.button('Logout'):
            if st.session_state.get('is_test_user', False):
                file_path = f'{st.session_state.username}_poker_records.csv'
                import os
                if os.path.exists(file_path):
                    os.remove(file_path)
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.is_test_user = False  # 重置測試用戶標記
            st.rerun()
        
        st.divider()

        # 新增 CSV 上傳功能
        st.subheader("Upload CSV")
        # Data
        username = st.session_state["username"]
        file_path = f'{username}_poker_records.csv'
        # 提供 CSV 格式說明
        st.info("""
        You may download the template CSV for quick usage.
                
        CSV file should contain the following columns:
        - Date
        - Tournament Name
        - Entry Fee
        - Profit/Loss
        """)
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv", key=st.session_state.file_uploader_key)
        if uploaded_file is not None:
            df_new = pd.read_csv(uploaded_file)
            if set(df_new.columns) == set(['Date', 'Tournament Name', 'Entry Fee', 'Profit/Loss']):
                df_new['Date'] = pd.to_datetime(df_new['Date']).dt.strftime('%Y-%m-%d')
                
                # 直接将上传的文件保存为用户的记录文件
                df_new.to_csv(file_path, index=False, encoding="utf_8_sig")
                st.success(f"CSV file uploaded and saved as {file_path}")
                
                # 重置上传状态
                st.session_state.file_uploader_key += 1
                st.rerun()
            else:
                st.error("The CSV file does not have the correct columns. Please check the format.")
        
        st.divider()
        # 添加下载模板按钮
        st.subheader("Download Template")
        
        # 创建模板数据
        template_data = pd.DataFrame({
            'Date': ['2024/07/23', '2024/07/22', '2024/07/20', '2024/07/19', '2024/07/7'],
            'Tournament Name': ['永和巨籌', '台北日常', '永和深籌', '林口MEGA', '台北超日'],
            'Entry Fee': [1500, 1500, 1500, 1500, 2000],
            'Profit/Loss': [4500, -1500, 2600, -1500, 8000]
        })
        
        @st.cache_data
        def convert_df(df):
            # IMPORTANT: Cache the conversion to prevent computation on every rerun
            return df.to_csv(index=False).encode("utf_8_sig")
        
        # 将数据转换为 CSV 字符串
        csv = convert_df(template_data)
        
        # 创建下载按钮
        st.download_button(
            label="Download CSV template",
            data=csv,
            file_name="poker_records_template.csv",
            mime="text/csv"
        )
        
        st.divider()
        st.markdown(
            '<h5>Made by <a href="https://www.instagram.com/raviiiiiiiiiii/">lileetung</a></h5>',
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
            'Entry Fee': pd.Series(dtype='int'),
            'Profit/Loss': pd.Series(dtype='int')
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
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Profit/Loss", f"${total_profit}")
        with col2:
            st.metric("ROI", f"{roi:.2f}%")
        with col3:
            st.metric("ITM", f"{in_the_money} / {total_tournaments}")
        with col4:
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
                df.to_csv(file_path, index=False, encoding="utf_8_sig")
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
                    df.to_csv(file_path, index=False, encoding="utf_8_sig")
                    st.rerun()

    # Plot profit/loss trend
    if not df.empty:
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values(by='Date', ascending=True)  # Sort by date ascending

        # 计算累计利润/损失
        df['Cumulative Profit/Loss'] = df['Profit/Loss'].cumsum()
        # 计算y轴的上下限
        y_min = df['Cumulative Profit/Loss'].min()
        y_max = df['Cumulative Profit/Loss'].max()
        y_range = y_max - y_min
        y_lower = y_min - 0.1 * y_range
        y_upper = y_max + 0.1 * y_range

        fig = px.line(df, x='Date', y='Cumulative Profit/Loss', markers=True, 
                    hover_data={'Date', 'Tournament Name', 'Profit/Loss', 'Entry Fee'})
        fig.update_traces(line_color='green', marker=dict(color='green'))
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Cumulative Profit/Loss',
            title={
                'text': 'Cumulative Profit/Loss',
                'y': 0.9,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            xaxis=dict(
                tickformat='%Y-%m-%d',
            ),
            yaxis=dict(
            tickformat='$,.0f',
            range=[y_lower, y_upper]
            ),
        )
        st.plotly_chart(fig)
else:
    st.title(f'Poker Tournament Record APP')
    st.error("⚠️ 注意：系統目前處於測試階段\n\n在此階段，數據可能不會被永久保存，且系統可能隨時進行更新或維護。請謹慎使用，並定期備份重要數據，將 csv 檔案儲存於您的電腦中。")
    st.markdown("""以下說明將幫助您快速上手並使用這個 Poker Tournament Record APP。祝您使用愉快！

### 登入
1. 在側邊欄的登入區域輸入您的用戶名和密碼。
2. 點擊 "Login" 按鈕以登入系統。
3. 如果您是新用戶，可以使用體驗帳號：
    - 帳號：user
    - 密碼：0000
4. 如需創建自己的帳號，請洽詢 <a href="https://www.instagram.com/raviiiiiiiiiii/">@leetung</a>

### 快速上手步驟
1. **登入系統**

2. **下載 CSV 模板**
   - 在側邊欄找到 "Download Template" 部分
   - 點擊 "Download CSV template" 按鈕下載模板

3. **填寫您的比賽記錄**
   - 打開下載的 CSV 模板
   - 按照模板格式填寫您的比賽記錄
   - 保存文件

4. **上傳您的記錄**
   - 在側邊欄找到 "Upload CSV" 部分
   - 點擊 "Choose a CSV file" 按鈕
   - 選擇您填寫好的 CSV 文件
                
5. **查看您的記錄和統計**
   - 上傳成功後，頁面會自動刷新
   - 您可以在主頁面查看您的比賽記錄和統計數據
""",
unsafe_allow_html=True,)