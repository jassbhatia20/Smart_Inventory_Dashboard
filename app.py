# Smart Inventory Dashboard with Streamlit UI
import streamlit as st
import os
import json
from datetime import datetime, timedelta
import csv
import pandas as pd
import io
import sqlite3
import random
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.model_selection import train_test_split
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Authentication imports
import bcrypt
import streamlit_authenticator as stauth
from streamlit_authenticator import Authenticate

def round_quantity(quantity, measurement_category):
    """Round quantity based on measurement category"""
    if measurement_category in ['Units', 'Packets']:
        return round(quantity, 0)
    else:  # Kilograms, Liters
        return round(quantity, 3)

# Database functions
def get_products(user_id=None):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    if user_id:
        cursor.execute('SELECT id, name, category, price, purchase_price, quantity, measurement_category, expiry_date FROM products WHERE user_id = ?', (user_id,))
    else:
        cursor.execute('SELECT id, name, category, price, purchase_price, quantity, measurement_category, expiry_date FROM products')
    rows = cursor.fetchall()
    products = []
    for row in rows:
        products.append({
            'ID': row[0],
            'Name': row[1],
            'Category': row[2],
            'Price': row[3],
            'Purchase Price': row[4],
            'Quantity': round_quantity(row[5], row[6]),
            'Measurement Category': row[6],
            'Expiry Date': row[7]
        })
    conn.close()
    return products

def get_active_products(user_id=None):
    products = get_products(user_id)
    current_date = datetime.now().date()
    active = []
    expired = []
    for p in products:
        if p['Expiry Date'] == 'expired':
            expired.append(p)
        else:
            try:
                expiry = datetime.strptime(p['Expiry Date'], '%d-%m-%Y').date()
                if expiry >= current_date:
                    active.append(p)
                else:
                    expired.append(p)
                    update_expiry(p['ID'], 'expired', user_id)
            except:
                active.append(p)
    return active, expired

def update_expiry(product_id, expiry, user_id=None):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    if user_id:
        cursor.execute('UPDATE products SET expiry_date = ? WHERE id = ? AND user_id = ?', (expiry, product_id, user_id))
    else:
        cursor.execute('UPDATE products SET expiry_date = ? WHERE id = ?', (expiry, product_id))
    conn.commit()
    conn.close()

def get_sales(user_id=None):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    if user_id:
        cursor.execute('SELECT date, product, quantity, revenue, bill_id FROM sales WHERE user_id = ? ORDER BY date DESC', (user_id,))
    else:
        cursor.execute('SELECT date, product, quantity, revenue, bill_id FROM sales ORDER BY date DESC')
    rows = cursor.fetchall()
    sales = []
    for row in rows:
        sales.append({
            'date': row[0],
            'product': row[1],
            'quantity': row[2],
            'revenue': row[3],
            'bill_id': row[4]
        })
    conn.close()
    return sales

def get_expenses(user_id=None):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    if user_id:
        cursor.execute('SELECT date, product, quantity, cost, supplier FROM expenses WHERE user_id = ? ORDER BY date DESC', (user_id,))
    else:
        cursor.execute('SELECT date, product, quantity, cost, supplier FROM expenses ORDER BY date DESC')
    rows = cursor.fetchall()
    expenses = []
    for row in rows:
        expenses.append({
            'date': row[0],
            'product': row[1],
            'quantity': row[2],
            'cost': row[3],
            'supplier': row[4]
        })
    conn.close()
    return expenses

def save_product(product, user_id):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    rounded_quantity = round_quantity(product['Quantity'], product['Measurement Category'])
    purchase_price = product.get('Purchase Price', 0)  # Default to 0 if not provided
    cursor.execute('INSERT OR REPLACE INTO products (id, user_id, name, category, price, purchase_price, quantity, measurement_category, expiry_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                   (product['ID'], user_id, product['Name'], product['Category'], product['Price'], purchase_price, rounded_quantity, product['Measurement Category'], product['Expiry Date']))
    conn.commit()
    conn.close()

def update_quantity(product_id, qty_change, user_id):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE products SET quantity = quantity + ? WHERE id = ? AND user_id = ?', (qty_change, product_id, user_id))
    conn.commit()
    conn.close()

def add_sale(sale, user_id):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO sales (user_id, date, product, quantity, revenue, bill_id) VALUES (?, ?, ?, ?, ?, ?)',
                   (user_id, sale['date'], sale['product'], sale['quantity'], sale['revenue'], sale.get('bill_id', '')))
    conn.commit()
    conn.close()

def add_expense(expense, user_id):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO expenses (user_id, date, product, quantity, cost, supplier) VALUES (?, ?, ?, ?, ?, ?)',
                   (user_id, expense['date'], expense['product'], expense['quantity'], expense['cost'], expense.get('supplier', '')))
    conn.commit()
    conn.close()

def delete_product_db(product_id, user_id):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM products WHERE id = ? AND user_id = ?', (product_id, user_id))
    conn.commit()
    conn.close()

# User Management Functions
def init_user_database():
    """Initialize user database tables"""
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            full_name TEXT,
            email TEXT,
            created_date TEXT DEFAULT CURRENT_TIMESTAMP,
            last_login TEXT,
            is_active INTEGER DEFAULT 1
        )
    ''')

    # Create user_sessions table for activity tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            details TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Create products table with user_id
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            category TEXT,
            price REAL,
            purchase_price REAL DEFAULT 0,
            quantity REAL,
            measurement_category TEXT,
            expiry_date TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Create sales table with user_id
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT,
            product TEXT,
            quantity REAL,
            revenue REAL,
            bill_id TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Create expenses table with user_id
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT,
            product TEXT,
            quantity REAL,
            cost REAL,
            supplier TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # Add user_id columns to existing tables if they don't exist (for migration)
    try:
        cursor.execute("ALTER TABLE products ADD COLUMN user_id INTEGER")
        cursor.execute("ALTER TABLE sales ADD COLUMN user_id INTEGER")
        cursor.execute("ALTER TABLE expenses ADD COLUMN user_id INTEGER")
    except sqlite3.OperationalError:
        # Columns already exist
        pass

    # Create default admin user if no users exist
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        # Create default admin user
        admin_password = "admin123"
        admin_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute('''
            INSERT INTO users (username, password_hash, role, full_name, email)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', admin_hash, 'admin', 'System Administrator', 'admin@inventory.com'))

        # Get admin user ID and assign existing data to admin if any exists
        cursor.execute('SELECT id FROM users WHERE username = ?', ('admin',))
        admin_id = cursor.fetchone()[0]

        # Assign existing products to admin user
        cursor.execute('UPDATE products SET user_id = ? WHERE user_id IS NULL', (admin_id,))
        cursor.execute('UPDATE sales SET user_id = ? WHERE user_id IS NULL', (admin_id,))
        cursor.execute('UPDATE expenses SET user_id = ? WHERE user_id IS NULL', (admin_id,))

    conn.commit()
    conn.close()

def authenticate_user(username, password):
    """Authenticate user credentials"""
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, password_hash, role, full_name FROM users WHERE username = ? AND is_active = 1', (username,))
    user = cursor.fetchone()
    conn.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
        return {
            'id': user[0],
            'username': username,
            'role': user[2],
            'full_name': user[3]
        }
    return None

def add_user(username, password, role, full_name, email):
    """Add a new user"""
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    try:
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute('''
            INSERT INTO users (username, password_hash, role, full_name, email)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, password_hash, role, full_name, email))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_users():
    """Get all users"""
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, role, full_name, email, created_date, last_login, is_active FROM users')
    rows = cursor.fetchall()
    conn.close()

    users = []
    for row in rows:
        users.append({
            'id': row[0],
            'username': row[1],
            'role': row[2],
            'full_name': row[3],
            'email': row[4],
            'created_date': row[5],
            'last_login': row[6],
            'is_active': row[7]
        })
    return users

def log_user_action(user_id, action, details=""):
    """Log user activity"""
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO user_sessions (user_id, action, details) VALUES (?, ?, ?)',
                   (user_id, action, details))
    conn.commit()
    conn.close()

def update_last_login(user_id):
    """Update user's last login time"""
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

# Enhanced Chart Functions
def create_revenue_trend_chart(df_sales):
    """Create an interactive revenue trend chart"""
    fig = px.line(df_sales, x='date', y='revenue',
                  title='Revenue Trend Over Time',
                  labels={'revenue': 'Revenue (₹)', 'date': 'Date'})
    fig.update_traces(mode='lines+markers', line_color='#1f77b4')
    fig.update_layout(hovermode='x unified')
    return fig

def create_category_pie_chart(products):
    """Create an interactive pie chart for product categories"""
    df = pd.DataFrame(products)
    category_counts = df['Category'].value_counts().reset_index()
    category_counts.columns = ['Category', 'Count']

    fig = px.pie(category_counts, values='Count', names='Category',
                 title='Product Distribution by Category',
                 color_discrete_sequence=px.colors.qualitative.Set3)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def create_inventory_heatmap(products):
    """Create a heatmap showing inventory levels"""
    df = pd.DataFrame(products)
    pivot_table = df.pivot_table(values='Quantity', index='Category', columns='Measurement Category', aggfunc='sum', fill_value=0)

    fig = px.imshow(pivot_table,
                    title='Inventory Heatmap by Category and Measurement',
                    labels=dict(x="Measurement Category", y="Category", color="Quantity"),
                    color_continuous_scale='RdYlGn')
    return fig

def create_forecast_chart(historical_data, forecast_data, title):
    """Create an interactive forecast chart"""
    fig = go.Figure()

    # Historical data
    fig.add_trace(go.Scatter(x=historical_data['date'], y=historical_data['revenue'],
                            mode='lines+markers', name='Historical',
                            line=dict(color='#1f77b4')))

    # Forecast data
    fig.add_trace(go.Scatter(x=forecast_data['date'], y=forecast_data['predicted_revenue'],
                            mode='lines+markers', name='Forecast',
                            line=dict(color='#ff7f0e', dash='dash')))

    fig.update_layout(title=title,
                     xaxis_title='Date',
                     yaxis_title='Revenue (₹)',
                     hovermode='x unified')
    return fig

def create_profit_loss_waterfall(profit_data):
    """Create a waterfall chart for profit/loss analysis"""
    fig = go.Figure(go.Waterfall(
        name="Profit/Loss Analysis",
        orientation="v",
        measure=["relative"] * len(profit_data),
        x=profit_data['category'],
        y=profit_data['amount'],
        text=profit_data['amount'].round(2),
        connector={"line":{"color":"rgb(63, 63, 63)"}},
    ))

    fig.update_layout(title="Profit/Loss Waterfall Chart",
                     waterfallgap=0.3)
    return fig

# Function to export inventory to CSV (in-memory)
def export_to_csv(user_id):
    csv_data = io.StringIO()
    writer = csv.DictWriter(csv_data, fieldnames=["ID", "Name", "Category", "Purchase Price", "Selling Price", "Quantity", "Measurement Category", "Expiry Date", "Status"])
    writer.writeheader()
    for p in active_products:
        p_copy = p.copy()
        p_copy["Selling Price"] = p_copy["Price"]
        p_copy["Status"] = "Active"
        writer.writerow({k: p_copy.get(k, "") for k in writer.fieldnames})
    for p in expired_products:
        p_copy = p.copy()
        p_copy["Selling Price"] = p_copy["Price"]
        p_copy["Status"] = "Expired"
        writer.writerow({k: p_copy.get(k, "") for k in writer.fieldnames})
    return csv_data.getvalue()

# Initialize user database
init_user_database()

# Authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None

# Login Page
if not st.session_state.authenticated:
    st.title("🔐 Smart Inventory Dashboard - Login")

    # Add registration option
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])

    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")

            if login_button:
                user = authenticate_user(username, password)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    update_last_login(user['id'])
                    log_user_action(user['id'], 'login', f"User {username} logged in")
                    st.success(f"Welcome back, {user['full_name']}!")
                    st.rerun()
                else:
                    st.error("Invalid username or password")

    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("Username")
            new_password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            full_name = st.text_input("Full Name")
            email = st.text_input("Email (optional)")

            register_button = st.form_submit_button("Create Account")

            if register_button:
                if new_password != confirm_password:
                    st.error("Passwords do not match!")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters long!")
                elif len(new_username) < 3:
                    st.error("Username must be at least 3 characters long!")
                else:
                    if add_user(new_username, new_password, 'user', full_name, email):
                        st.success("Account created successfully! Please login with your credentials.")
                        log_user_action(1, 'user_registration', f"New user {new_username} registered")
                    else:
                        st.error("Username already exists! Please choose a different username.")

    st.markdown("---")
    st.markdown("**Default Admin Credentials:**")
    st.code("Username: admin\nPassword: admin123")

    st.stop()  # Stop execution if not authenticated

# Load user-specific data after authentication
user_id = st.session_state.user['id']
active_products, expired_products = get_active_products(user_id)
sales = get_sales(user_id)
expenses = get_expenses(user_id)

# Streamlit App
st.set_page_config(
    page_title="🏪 Smart Inventory Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(45deg, #1e3c72, #2a5298);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .sidebar-header {
        background: linear-gradient(45deg, #ff6b6b, #ee5a24);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .success-msg {
        background: linear-gradient(45deg, #56ab2f, #a8e6cf);
        color: white;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #4CAF50;
    }
    .warning-msg {
        background: linear-gradient(45deg, #ff9a9e, #fecfef);
        color: #d32f2f;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #f44336;
    }
    .info-msg {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #2196F3;
    }
    .stButton>button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🏪 Smart Inventory Dashboard</h1>', unsafe_allow_html=True)

# Sidebar header
st.sidebar.markdown("""
<div class="sidebar-header">
    <h2 style="margin: 0; color: white;">📋 Operations Menu</h2>
    <p style="margin: 5px 0 0 0; opacity: 0.9;">Choose your action</p>
</div>
""", unsafe_allow_html=True)

# Sidebar with user info and logout
st.sidebar.markdown(f"""
<div class="sidebar-header">
    <h3 style="margin: 0; color: white;">👤 Welcome, {st.session_state.user['full_name']}</h3>
    <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 0.9em;">Role: {st.session_state.user['role'].title()}</p>
    <p style="margin: 2px 0 0 0; opacity: 0.7; font-size: 0.8em;">Last login: {datetime.now().strftime('%d-%m-%Y')}</p>
</div>
""", unsafe_allow_html=True)

# Logout button
if st.sidebar.button("🚪 Logout", key="logout", help="Logout from the system"):
    log_user_action(st.session_state.user['id'], 'logout', f"User {st.session_state.user['username']} logged out")
    st.session_state.authenticated = False
    st.session_state.user = None
    st.rerun()

st.sidebar.markdown("---")

# Operations Menu
st.sidebar.markdown("### 📋 Operations Menu")

# All users now have access to all features
full_menu = [
    "➕ Add Product & Purchase",
    "💰 Sell Product",
    "🛒 Purchase Stock",
    "🔄 Update Stock",
    "💲 Update Price",
    "🗑️ Remove Product",
    "📦 View Inventory",
    "🔍 Search Product",
    "📊 View Sales Report",
    "💸 View Expenses",
    "📈 Advanced Analytics",
    "📥 Export to CSV"
]

# Admin-only features
if st.session_state.user['role'] == 'admin':
    full_menu.append("👥 User Management")

menu = st.sidebar.selectbox("Select Operation", full_menu, key="main_menu")

if menu == "📦 View Inventory":
    st.header("📦 Inventory Overview Dashboard")

    total_active = len(active_products)
    total_expired = len(expired_products)
    total_active_qty = sum(p.get("Quantity", 0) for p in active_products)
    total_expired_qty = sum(p.get("Quantity", 0) for p in expired_products)

    # Color-coded metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Active Products", f"{total_active:,}", delta=f"{total_active}")
    with col2:
        st.metric("Expired Products", f"{total_expired:,}", delta=f"{total_expired}")
    with col3:
        st.metric("Active Quantity", f"{total_active_qty:,.1f}", delta=f"{total_active_qty:.0f}")
    with col4:
        st.metric("Expired Quantity", f"{total_expired_qty:,.1f}", delta=f"{total_expired_qty:.0f}")

    # Inventory Status Overview
    if active_products or expired_products:
        st.subheader("📊 Inventory Status")

        # Create status data
        status_data = pd.DataFrame({
            'Status': ['Active', 'Expired'],
            'Count': [total_active, total_expired],
            'Quantity': [total_active_qty, total_expired_qty]
        })

        col1, col2 = st.columns(2)

        with col1:
            # Enhanced bar chart for status count
            fig_count = px.bar(status_data, x='Status', y='Count',
                             title='Products by Status',
                             color='Status',
                             color_discrete_map={'Active': '#4CAF50', 'Expired': '#F44336'})
            fig_count.update_layout(showlegend=False)
            st.plotly_chart(fig_count, width="stretch")

        with col2:
            # Interactive pie chart for quantity distribution
            fig_pie = px.pie(status_data, values='Quantity', names='Status',
                           title='Quantity Distribution by Status',
                           color='Status',
                           color_discrete_map={'Active': '#4CAF50', 'Expired': '#F44336'})
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, width="stretch")

    # Category Distribution
    if active_products:
        st.subheader("🏷️ Product Categories")
        df_active = pd.DataFrame(active_products)
        category_counts = df_active['Category'].value_counts().reset_index()
        category_counts.columns = ['Category', 'Count']

        # Enhanced category distribution with multiple chart types
        col1, col2 = st.columns(2)

        with col1:
            fig_bar = px.bar(category_counts, x='Category', y='Count',
                           title='Products by Category',
                           color='Count',
                           color_continuous_scale='Blues')
            fig_bar.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_bar, use_container_width=True)

        with col2:
            fig_pie_cat = create_category_pie_chart(active_products)
            st.plotly_chart(fig_pie_cat, use_container_width=True)

        # Inventory heatmap
        st.subheader("🔥 Inventory Heatmap")
        fig_heatmap = create_inventory_heatmap(active_products + expired_products)
        st.plotly_chart(fig_heatmap, use_container_width=True)

    if active_products:
        st.subheader("✅ Active Inventory Details")
        df_active = pd.DataFrame(active_products)

        # Color-code the dataframe based on quantity
        def color_quantity(val):
            if val < 5:
                return 'background-color: #FF6B6B'  # Red for low stock
            elif val < 20:
                return 'background-color: #FFE66D'  # Yellow for medium
            else:
                return 'background-color: #4ECDC4'  # Green for good stock

        styled_df = df_active.style.applymap(color_quantity, subset=['Quantity'])
        st.dataframe(styled_df, use_container_width=True)

    if expired_products:
        st.subheader("❌ Expired Inventory Details")
        df_expired = pd.DataFrame(expired_products)
        st.dataframe(df_expired.style.applymap(lambda x: 'background-color: #FF6B6B', subset=['Expiry Date']), use_container_width=True)

    # Enhanced Low Stock Alert with colors
    low_stock = [p for p in active_products if p.get("Quantity", 0) < 5]
    if low_stock:
        st.error("🚨 **CRITICAL: Low Stock Alert** (Quantity < 5)")
        for p in low_stock:
            st.write(f"🔴 **{p['Name']}** (ID: {p['ID']}, Quantity: {p['Quantity']}) - **REPLENISH IMMEDIATELY**")
    else:
        st.success("✅ All products have sufficient stock levels!")

elif menu == "➕ Add Product & Purchase":
    st.header("Add New Product & Record Initial Purchase")
    with st.form("add_product_form"):
        col1, col2 = st.columns(2)

        with col1:
            product_id = st.number_input("Product ID", min_value=1, step=1)
            name = st.text_input("Product Name")
            category = st.text_input("Product Category")
            measurements = st.selectbox("Measurement Category", ["Units", "Kilograms", "Liters", "Packets"])

        with col2:
            purchase_price = st.number_input("Purchase Price per Unit (INR)", min_value=0.0, step=0.01)
            selling_price = st.number_input("Selling Price per Unit (INR)", min_value=0.0, step=0.01)
            quantity = st.number_input("Initial Quantity Purchased", min_value=0.01, step=0.01)
            expiry_input = st.text_input("Expiry Date (DD-MM-YYYY)", placeholder="DD-MM-YYYY")

        # Calculate total cost
        total_cost = purchase_price * quantity
        st.write(f"**Total Purchase Cost: INR {total_cost:.2f}**")

        submitted = st.form_submit_button("Add Product & Record Purchase")
        if submitted:
            try:
                datetime.strptime(expiry_input, "%d-%m-%Y")
                # Check duplicate ID
                if any(p["ID"] == product_id for p in active_products + expired_products):
                    st.error("Product ID already exists.")
                else:
                    # Create product data
                    data = {
                        "ID": int(product_id),
                        "Name": name.title(),
                        "Category": category.title(),
                        "Price": selling_price,  # Selling price
                        "Quantity": int(quantity) if measurements in ['Units', 'Packets'] else round(quantity, 3),
                        "Measurement Category": measurements,
                        "Expiry Date": expiry_input,
                        "Purchase Price": purchase_price  # Store purchase price for profit calculations
                    }

                    # Add product to inventory
                    active_products.append(data)
                    save_product(data, user_id)

                    # Record the initial purchase as an expense
                    expense = {
                        "date": datetime.now().strftime("%d-%m-%Y"),
                        "product": name.title(),
                        "quantity": quantity,
                        "cost": total_cost,
                        "supplier": f"Supplier-{random.randint(1, 10)}"
                    }
                    expenses.append(expense)
                    add_expense(expense, user_id)

                    st.success(f"✅ Product '{name.title()}' added successfully!")
                    st.success(f"✅ Initial purchase of {quantity} {measurements} recorded (Cost: INR {total_cost:.2f})")
                    st.rerun()
            except ValueError:
                st.error("Invalid date format. Please enter expiry date in DD-MM-YYYY format.")

elif menu == "💰 Sell Product":
    st.header("Sell Product")
    product_names = [p["Name"] for p in active_products]
    if product_names:
        selected_name = st.selectbox("Select Product", product_names)
        product = next(p for p in active_products if p["Name"] == selected_name)
        st.write(f"Available Quantity: {product['Quantity']} {product['Measurement Category']}")
        st.write(f"Price: INR {product['Price']} per {product['Measurement Category']}")
        qty = st.number_input("Quantity to Sell", min_value=0.01, step=0.01)
        if qty > 0:
            total = qty * product["Price"]
            st.write("### Bill Receipt")
            st.write(f"**Product:** {product['Name']}")
            st.write(f"**Quantity:** {qty} {product['Measurement Category']}")
            st.write(f"**Price per unit:** INR {product['Price']}")
            st.write(f"**Total:** INR {total}")
            if st.button("Confirm Sale"):
                if qty > product["Quantity"]:
                    st.error("Insufficient stock.")
                else:
                    product["Quantity"] -= qty
                    sale = {
                        "date": datetime.now().strftime("%d-%m-%Y"),
                        "product": product["Name"],
                        "quantity": qty,
                        "revenue": total,
                        "bill_id": f"BILL-{random.randint(1000, 9999)}"
                    }
                    sales.append(sale)
                    update_quantity(product['ID'], -qty, user_id)
                    add_sale(sale, user_id)
                    st.success("Sale completed!")
                    st.rerun()
    else:
        st.write("No active products available.")

elif menu == "🛒 Purchase Stock":
    st.header("Purchase Stock")
    product_names = [p["Name"] for p in active_products + expired_products]
    if product_names:
        selected_name = st.selectbox("Select Product to Restock", product_names)
        product = next((p for p in active_products + expired_products if p["Name"] == selected_name), None)
        qty = st.number_input("Quantity Purchased", min_value=0.01, step=0.01)
        cost = st.number_input("Total Cost (INR)", min_value=0.0, step=0.01)
        if st.button("Confirm Purchase"):
            product["Quantity"] += qty
            expense = {
                "date": datetime.now().strftime("%d-%m-%Y"),
                "product": product["Name"],
                "quantity": qty,
                "cost": cost,
                "supplier": f"Supplier-{random.randint(1, 10)}"
            }
            expenses.append(expense)
            update_quantity(product['ID'], qty, user_id)
            add_expense(expense, user_id)
            st.success("Purchase recorded!")
            st.rerun()
    else:
        st.write("No products available.")

elif menu == "🔄 Update Stock":
    st.header("Update Inventory Stock")
    product_input = st.text_input("Enter Product ID or Name")
    if product_input:
        if product_input.isdigit():
            product = next((p for p in active_products if p["ID"] == int(product_input)), None)
        else:
            matching = [p for p in active_products if p["Name"] == product_input.title()]
            if len(matching) == 1:
                product = matching[0]
            elif len(matching) > 1:
                selected_id = st.selectbox("Select Product ID", [p["ID"] for p in matching])
                product = next(p for p in matching if p["ID"] == selected_id)
            else:
                product = None
        
        if product:
            st.write(f"Updating: {product['Name']} (Current Quantity: {product['Quantity']})")
            action = st.selectbox("Action", ["Sell", "Add"])
            qty = st.number_input("Quantity", min_value=1, step=1)
            if st.button("Update Stock"):
                if action == "Sell":
                    if qty > product["Quantity"]:
                        st.error("Cannot sell more than available.")
                    else:
                        product["Quantity"] -= qty
                        sale = {
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "product": product["Name"],
                            "quantity": qty,
                            "revenue": qty * product["Price"]
                        }
                        sales.append(sale)
                        update_quantity(product['ID'], -qty, user_id)
                        add_sale(sale, user_id)
                        st.success("Stock updated!")
                        st.rerun()
                else:
                    product["Quantity"] += qty
                    update_quantity(product['ID'], qty, user_id)
                    st.success("Stock updated!")
                    st.rerun()
        else:
            st.error("Product not found.")

elif menu == "💲 Update Price":
    st.header("Update Product Price")
    product_input = st.text_input("Enter Product ID or Name")
    if product_input:
        if product_input.isdigit():
            product = next((p for p in active_products if p["ID"] == int(product_input)), None)
        else:
            matching = [p for p in active_products if p["Name"] == product_input.title()]
            if len(matching) == 1:
                product = matching[0]
            elif len(matching) > 1:
                selected_id = st.selectbox("Select Product ID", [p["ID"] for p in matching])
                product = next(p for p in matching if p["ID"] == selected_id)
            else:
                product = None
        
        if product:
            new_price = st.number_input("New Price (INR)", min_value=0.01, step=0.01)
            if st.button("Update Price"):
                product["Price"] = new_price
                save_product(product, user_id)
                st.success("Price updated!")
                st.rerun()
        else:
            st.error("Product not found.")

elif menu == "🗑️ Remove Product":
    st.header("Remove Product")
    product_input = st.text_input("Enter Product ID or Name")
    if product_input:
        if product_input.isdigit():
            product = next((p for p in active_products if p["ID"] == int(product_input)), None)
        else:
            matching = [p for p in active_products if p["Name"] == product_input.title()]
            if len(matching) == 1:
                product = matching[0]
            elif len(matching) > 1:
                selected_id = st.selectbox("Select Product ID", [p["ID"] for p in matching])
                product = next(p for p in matching if p["ID"] == selected_id)
            else:
                product = None
        
        if product:
            if st.button("Remove Product"):
                active_products.remove(product)
                delete_product_db(product['ID'], user_id)
                st.success("Product removed!")
                st.rerun()
        else:
            st.error("Product not found.")

elif menu == "🔍 Search Product":
    st.header("Search Product")
    search_name = st.text_input("Enter Product Name")
    if search_name:
        all_products = active_products + expired_products
        found = [p for p in all_products if p['Name'] == search_name.title()]
        if found:
            df = pd.DataFrame(found)
            st.dataframe(df)
        else:
            st.error("Product not found.")

elif menu == "📊 View Sales Report":
    st.header("📊 Sales Analytics Dashboard")

    if sales:
        df_sales = pd.DataFrame(sales)

        # Convert date strings to datetime for better plotting
        df_sales['date'] = pd.to_datetime(df_sales['date'], format='%d-%m-%Y', errors='coerce')

        # Summary metrics with colors
        col1, col2, col3 = st.columns(3)
        with col1:
            total_sales = len(sales)
            st.metric("Total Transactions", f"{total_sales:,}", delta=f"+{total_sales}")
        with col2:
            total_revenue = sum(s["revenue"] for s in sales)
            st.metric("Total Revenue", f"₹{total_revenue:,.2f}", delta=f"+₹{total_revenue:,.0f}")
        with col3:
            avg_sale = total_revenue / total_sales if total_sales > 0 else 0
            st.metric("Average Sale", f"₹{avg_sale:.2f}")

elif menu == "📊 View Sales Report":
    st.header("📊 Sales Analytics Dashboard")

    if sales:
        df_sales = pd.DataFrame(sales)

        # Convert date strings to datetime for better plotting
        df_sales['date'] = pd.to_datetime(df_sales['date'], format='%d-%m-%Y', errors='coerce')

        # Summary metrics with colors
        col1, col2, col3 = st.columns(3)
        with col1:
            total_sales = len(sales)
            st.metric("Total Transactions", f"{total_sales:,}", delta=f"+{total_sales}")
        with col2:
            total_revenue = sum(s["revenue"] for s in sales)
            st.metric("Total Revenue", f"₹{total_revenue:,.2f}", delta=f"+₹{total_revenue:,.0f}")
        with col3:
            avg_sale = total_revenue / total_sales if total_sales > 0 else 0
            st.metric("Average Sale", f"₹{avg_sale:.2f}")

        # Enhanced Revenue Over Time
        st.subheader("💰 Revenue Trend")
        daily_revenue = df_sales.groupby(df_sales['date'].dt.date)['revenue'].sum().reset_index()
        daily_revenue.columns = ['Date', 'Revenue']

        fig_revenue = create_revenue_trend_chart(daily_revenue)
        st.plotly_chart(fig_revenue, use_container_width=True)

        # Top Selling Products with enhanced visualization
        st.subheader("🏆 Top Selling Products")
        product_sales = df_sales.groupby('product')['revenue'].sum().reset_index()
        product_sales = product_sales.sort_values('revenue', ascending=False).head(10)

        col1, col2 = st.columns(2)

        with col1:
            fig_top_products = px.bar(product_sales, x='product', y='revenue',
                                    title='Top Products by Revenue',
                                    color='revenue',
                                    color_continuous_scale='Viridis')
            fig_top_products.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_top_products, use_container_width=True)

        with col2:
            # Revenue distribution pie chart
            fig_revenue_pie = px.pie(product_sales.head(5), values='revenue', names='product',
                                   title='Revenue Share (Top 5 Products)')
            fig_revenue_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_revenue_pie, use_container_width=True)

        # Sales Distribution Analysis
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📦 Sales by Quantity")
            quantity_sales = df_sales.groupby('product')['quantity'].sum().reset_index()
            quantity_sales = quantity_sales.sort_values('quantity', ascending=False).head(8)

            fig_quantity = px.bar(quantity_sales, x='product', y='quantity',
                                title='Products by Quantity Sold',
                                color='quantity',
                                color_continuous_scale='Blues')
            fig_quantity.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_quantity, use_container_width=True)

        with col2:
            st.subheader("📈 Transaction Frequency")
            # Group by date and count transactions
            daily_transactions = df_sales.groupby(df_sales['date'].dt.date).size().reset_index(name='transactions')

            fig_transactions = px.area(daily_transactions, x='date', y='transactions',
                                     title='Daily Transaction Frequency',
                                     color_discrete_sequence=['#FF6B6B'])
            st.plotly_chart(fig_transactions, use_container_width=True)

        # Sales correlation analysis
        st.subheader("🔍 Sales Correlation Analysis")
        if len(df_sales) > 10:
            # Create correlation matrix for quantity vs revenue
            corr_data = df_sales[['quantity', 'revenue']].corr()

            fig_corr = px.imshow(corr_data,
                               title='Correlation Matrix: Quantity vs Revenue',
                               color_continuous_scale='RdBu',
                               zmin=-1, zmax=1)
            st.plotly_chart(fig_corr, use_container_width=True)

        # Detailed Data Table with enhanced styling
        st.subheader("📋 Detailed Sales Data")
        styled_df = df_sales.style.highlight_max(axis=0, subset=['revenue', 'quantity'])
        st.dataframe(styled_df, use_container_width=True)

    else:
        st.warning("📭 No sales data available. Start selling products to see analytics!")

elif menu == "💸 View Expenses":
    st.header("💸 Expense Analytics Dashboard")

    if expenses:
        df_expenses = pd.DataFrame(expenses)

        # Convert date strings to datetime
        df_expenses['date'] = pd.to_datetime(df_expenses['date'], format='%d-%m-%Y', errors='coerce')

        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            total_expenses = len(expenses)
            st.metric("Total Purchases", f"{total_expenses:,}", delta=f"+{total_expenses}")
        with col2:
            total_cost = sum(e["cost"] for e in expenses)
            st.metric("Total Expenses", f"₹{total_cost:,.2f}", delta=f"+₹{total_cost:,.0f}")
        with col3:
            avg_cost = total_cost / total_expenses if total_expenses > 0 else 0
            st.metric("Average Purchase", f"₹{avg_cost:.2f}")

        # Expense Trend Over Time
        st.subheader("📉 Expense Trend")
        daily_expenses = df_expenses.groupby(df_expenses['date'].dt.date)['cost'].sum().reset_index()
        daily_expenses.columns = ['Date', 'Cost']

        st.area_chart(daily_expenses.set_index('Date')['Cost'], use_container_width=True)

        # Expenses by Supplier
        st.subheader("🏢 Expenses by Supplier")
        if 'supplier' in df_expenses.columns:
            supplier_expenses = df_expenses.groupby('supplier')['cost'].sum().reset_index()
            supplier_expenses = supplier_expenses.sort_values('cost', ascending=False)

            st.bar_chart(supplier_expenses.set_index('supplier')['cost'], use_container_width=True)

        # Cost vs Quantity Analysis
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 Cost Distribution")
            product_expenses = df_expenses.groupby('product')['cost'].sum().reset_index()
            product_expenses = product_expenses.sort_values('cost', ascending=False).head(8)

            # Create a simple bar chart for cost distribution
            st.bar_chart(product_expenses.set_index('product')['cost'], use_container_width=True)

        with col2:
            st.subheader("⚖️ Cost vs Quantity Analysis")
            # Create a scatter plot data
            scatter_data = df_expenses[['quantity', 'cost']].copy()
            scatter_data.columns = ['Quantity', 'Cost']
            st.scatter_chart(scatter_data, x='Quantity', y='Cost', use_container_width=True)

        # Detailed Data Table
        st.subheader("📋 Detailed Expense Data")
        st.dataframe(df_expenses.style.highlight_max(axis=0), use_container_width=True)

    else:
        st.info("💰 No expense data available. Start purchasing stock to see analytics!")

elif menu == "� Advanced Analytics":
    st.header("📈 Advanced Analytics Dashboard")

    # Import additional libraries for advanced analysis
    import numpy as np
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import r2_score
    import warnings
    warnings.filterwarnings('ignore')

    # Prepare data for advanced analysis
    if sales and expenses:
        df_sales = pd.DataFrame(sales)
        df_expenses = pd.DataFrame(expenses)
        df_products = pd.DataFrame(active_products + expired_products)

        # Convert dates
        df_sales['date'] = pd.to_datetime(df_sales['date'], format='%d-%m-%Y', errors='coerce')
        df_expenses['date'] = pd.to_datetime(df_expenses['date'], format='%d-%m-%Y', errors='coerce')

        # Create tabs for different analysis types
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["💰 Profit Analysis", "📊 Inventory Turnover", "🔮 Forecasting", "📈 ABC Analysis", "📋 KPIs & Metrics"])

        with tab1:
            st.subheader("💰 Profit & Loss Analysis")

            # Calculate profit/loss over time
            sales_by_date = df_sales.groupby(df_sales['date'].dt.date)['revenue'].sum().reset_index()
            sales_by_date.columns = ['date', 'revenue']

            expenses_by_date = df_expenses.groupby(df_expenses['date'].dt.date)['cost'].sum().reset_index()
            expenses_by_date.columns = ['date', 'cost']

            # Merge sales and expenses
            profit_df = pd.merge(sales_by_date, expenses_by_date, on='date', how='outer').fillna(0)
            profit_df['profit'] = profit_df['revenue'] - profit_df['cost']
            profit_df['cumulative_profit'] = profit_df['profit'].cumsum()

            col1, col2, col3 = st.columns(3)
            with col1:
                total_revenue = profit_df['revenue'].sum()
                st.metric("Total Revenue", f"₹{total_revenue:,.2f}")
            with col2:
                total_cost = profit_df['cost'].sum()
                st.metric("Total Cost", f"₹{total_cost:,.2f}")
            with col3:
                total_profit = profit_df['profit'].sum()
                st.metric("Net Profit", f"₹{total_profit:,.2f}", delta=f"{total_profit:.0f}")

            # Profit trend chart
            st.subheader("Profit Trend Over Time")
            st.line_chart(profit_df.set_index('date')[['revenue', 'cost', 'profit']], use_container_width=True)

            # Cumulative profit chart
            st.subheader("Cumulative Profit")
            st.area_chart(profit_df.set_index('date')['cumulative_profit'], use_container_width=True)

            # Profit margin analysis
            st.subheader("Profit Margin by Product")
            product_profit = df_sales.groupby('product')['revenue'].sum().reset_index()
            product_cost = df_expenses.groupby('product')['cost'].sum().reset_index()

            profit_margin_df = pd.merge(product_profit, product_cost, on='product', how='outer').fillna(0)
            profit_margin_df['profit'] = profit_margin_df['revenue'] - profit_margin_df['cost']
            profit_margin_df['margin'] = (profit_margin_df['profit'] / profit_margin_df['revenue'] * 100).round(2)
            profit_margin_df = profit_margin_df.sort_values('profit', ascending=False)

            st.dataframe(profit_margin_df.style.highlight_max(axis=0, subset=['profit', 'margin']), use_container_width=True)

        with tab2:
            st.subheader("📊 Inventory Turnover Analysis")

            # Calculate inventory turnover
            total_sales_qty = df_sales['quantity'].sum()
            avg_inventory = df_products['Quantity'].mean()

            if avg_inventory > 0:
                turnover_ratio = total_sales_qty / avg_inventory
                st.metric("Inventory Turnover Ratio", f"{turnover_ratio:.2f}")

                # Turnover by product category
                st.subheader("Turnover by Category")
                category_turnover = df_sales.merge(df_products[['Name', 'Category']], left_on='product', right_on='Name', how='left')
                category_turnover = category_turnover.groupby('Category').agg({
                    'quantity': 'sum',
                    'revenue': 'sum'
                }).reset_index()

                # Calculate average inventory by category
                category_inventory = df_products.groupby('Category')['Quantity'].mean().reset_index()
                category_analysis = pd.merge(category_turnover, category_inventory, on='Category', how='left')
                category_analysis['turnover_ratio'] = category_analysis['quantity'] / category_analysis['Quantity']
                category_analysis = category_analysis.sort_values('turnover_ratio', ascending=False)

                st.dataframe(category_analysis.style.highlight_max(axis=0), use_container_width=True)

                # Inventory aging analysis
                st.subheader("Inventory Aging Analysis")
                current_date = pd.Timestamp.now()
                df_products_copy = df_products.copy()
                df_products_copy['Expiry Date'] = pd.to_datetime(df_products_copy['Expiry Date'], format='%d-%m-%Y', errors='coerce')
                df_products_copy['days_to_expiry'] = (df_products_copy['Expiry Date'] - current_date).dt.days

                # Categorize inventory age
                conditions = [
                    (df_products_copy['days_to_expiry'] < 0),
                    (df_products_copy['days_to_expiry'] <= 30),
                    (df_products_copy['days_to_expiry'] <= 90),
                    (df_products_copy['days_to_expiry'] > 90)
                ]
                choices = ['Expired', 'Critical (≤30 days)', 'Warning (≤90 days)', 'Good (>90 days)']
                df_products_copy['age_category'] = np.select(conditions, choices, default='Unknown')

                age_distribution = df_products_copy['age_category'].value_counts()
                st.bar_chart(age_distribution, use_container_width=True)

        with tab3:
            st.subheader("🔮 Advanced Sales Forecasting")

            if len(df_sales) > 14:  # Need more data points for robust forecasting
                # Prepare data for advanced forecasting
                daily_sales = df_sales.groupby(df_sales['date'].dt.date)['revenue'].sum().reset_index()
                daily_sales.columns = ['date', 'revenue']
                daily_sales = daily_sales.sort_values('date')

                # Add time-based features
                daily_sales['day_of_week'] = daily_sales['date'].dt.dayofweek
                daily_sales['month'] = daily_sales['date'].dt.month
                daily_sales['day_of_month'] = daily_sales['date'].dt.day
                daily_sales['day'] = range(len(daily_sales))

                # Prepare features for ML model
                features = ['day', 'day_of_week', 'month', 'day_of_month']
                X = daily_sales[features]
                y = daily_sales['revenue']

                # Split data for training and testing
                if len(daily_sales) > 20:
                    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

                    # Train Random Forest model
                    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
                    rf_model.fit(X_train, y_train)

                    # Evaluate model
                    rf_predictions = rf_model.predict(X_test)
                    rf_r2 = r2_score(y_test, rf_predictions)
                    rf_mae = mean_absolute_error(y_test, rf_predictions)

                    # Also train Linear Regression for comparison
                    lr_model = LinearRegression()
                    lr_model.fit(X_train, y_train)
                    lr_predictions = lr_model.predict(X_test)
                    lr_r2 = r2_score(y_test, lr_predictions)
                    lr_mae = mean_absolute_error(y_test, lr_predictions)

                    # Display model comparison
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Random Forest R²", f"{rf_r2:.3f}")
                        st.metric("Random Forest MAE", f"₹{rf_mae:.2f}")
                    with col2:
                        st.metric("Linear Regression R²", f"{lr_r2:.3f}")
                        st.metric("Linear Regression MAE", f"₹{lr_mae:.2f}")

                    # Use the better model for forecasting
                    best_model = rf_model if rf_r2 > lr_r2 else lr_model
                    model_name = "Random Forest" if rf_r2 > lr_r2 else "Linear Regression"
                else:
                    # Use Linear Regression if insufficient data
                    best_model = LinearRegression()
                    best_model.fit(X, y)
                    model_name = "Linear Regression"
                    rf_r2 = r2_score(y, best_model.predict(X))

                st.info(f"🎯 Using {model_name} model for forecasting")

                # Forecast next 14 days
                last_date = daily_sales['date'].max()
                future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=14)

                future_features = pd.DataFrame({
                    'day': range(len(daily_sales), len(daily_sales) + 14),
                    'day_of_week': [d.weekday() for d in future_dates],
                    'month': [d.month for d in future_dates],
                    'day_of_month': [d.day for d in future_dates]
                })

                predictions = best_model.predict(future_features)

                # Create forecast chart
                forecast_df = pd.DataFrame({
                    'date': future_dates,
                    'predicted_revenue': predictions
                })

                fig_forecast = create_forecast_chart(daily_sales, forecast_df, f'14-Day Sales Forecast ({model_name})')
                st.plotly_chart(fig_forecast, use_container_width=True)

                # Forecast summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    avg_predicted = predictions.mean()
                    st.metric("Avg Daily Forecast", f"₹{avg_predicted:.2f}")
                with col2:
                    total_forecast = predictions.sum()
                    st.metric("14-Day Total Forecast", f"₹{total_forecast:.2f}")
                with col3:
                    trend = "📈 Upward" if predictions[-1] > predictions[0] else "📉 Downward"
                    st.metric("Trend Direction", trend)

                # Forecast breakdown by day of week
                st.subheader("📅 Forecast by Day of Week")
                forecast_with_days = forecast_df.copy()
                forecast_with_days['day_name'] = forecast_with_days['date'].dt.day_name()

                day_forecast = forecast_with_days.groupby('day_name')['predicted_revenue'].mean().reset_index()
                day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                day_forecast['day_name'] = pd.Categorical(day_forecast['day_name'], categories=day_order, ordered=True)
                day_forecast = day_forecast.sort_values('day_name')

                fig_days = px.bar(day_forecast, x='day_name', y='predicted_revenue',
                                title='Average Forecast by Day of Week',
                                color='predicted_revenue',
                                color_continuous_scale='Greens')
                st.plotly_chart(fig_days, use_container_width=True)

            else:
                st.warning("Need at least 14 days of sales data for advanced forecasting. Current data: {} days".format(len(df_sales.groupby(df_sales['date'].dt.date))))

        with tab4:
            st.subheader("📈 ABC Analysis (Pareto Principle)")

            # ABC Analysis for products by revenue
            product_revenue = df_sales.groupby('product')['revenue'].sum().reset_index()
            product_revenue = product_revenue.sort_values('revenue', ascending=False)
            product_revenue['cumulative_revenue'] = product_revenue['revenue'].cumsum()
            product_revenue['cumulative_percentage'] = (product_revenue['cumulative_revenue'] / product_revenue['revenue'].sum() * 100)

            # Classify products
            conditions = [
                (product_revenue['cumulative_percentage'] <= 80),
                (product_revenue['cumulative_percentage'] <= 95),
                (product_revenue['cumulative_percentage'] > 95)
            ]
            choices = ['A (High Value)', 'B (Medium Value)', 'C (Low Value)']
            product_revenue['abc_class'] = np.select(conditions, choices)

            # Display ABC analysis
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Product Classification")
                abc_counts = product_revenue['abc_class'].value_counts()
                st.bar_chart(abc_counts, use_container_width=True)

            with col2:
                st.subheader("Revenue Distribution")
                st.dataframe(product_revenue[['product', 'revenue', 'cumulative_percentage', 'abc_class']].style.highlight_max(axis=0), use_container_width=True)

            # ABC insights
            a_products = product_revenue[product_revenue['abc_class'] == 'A (High Value)']
            a_revenue_pct = (a_products['revenue'].sum() / product_revenue['revenue'].sum() * 100)

            st.success(f"🎯 **A-Class Products** ({len(a_products)} products) generate **{a_revenue_pct:.1f}%** of total revenue")
            st.info("💡 **Recommendation:** Focus inventory management efforts on A-class products")

        with tab5:
            st.subheader("📋 Key Performance Indicators (KPIs)")

            # Calculate various KPIs
            kpi_data = {}

            # Financial KPIs
            total_revenue = df_sales['revenue'].sum()
            total_cost = df_expenses['cost'].sum()
            gross_profit = total_revenue - total_cost
            profit_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0

            kpi_data['Total Revenue'] = f"₹{total_revenue:,.2f}"
            kpi_data['Total Cost'] = f"₹{total_cost:,.2f}"
            kpi_data['Gross Profit'] = f"₹{gross_profit:,.2f}"
            kpi_data['Profit Margin'] = f"{profit_margin:.2f}%"

            # Inventory KPIs
            total_products = len(df_products)
            active_products_count = len(active_products)
            inventory_accuracy = (active_products_count / total_products * 100) if total_products > 0 else 0

            kpi_data['Total Products'] = total_products
            kpi_data['Active Products'] = active_products_count
            kpi_data['Inventory Accuracy'] = f"{inventory_accuracy:.1f}%"

            # Sales KPIs
            total_transactions = len(df_sales)
            avg_transaction_value = total_revenue / total_transactions if total_transactions > 0 else 0
            unique_products_sold = df_sales['product'].nunique()

            kpi_data['Total Transactions'] = total_transactions
            kpi_data['Avg Transaction Value'] = f"₹{avg_transaction_value:.2f}"
            kpi_data['Products Sold'] = unique_products_sold

            # Efficiency KPIs
            total_sales_qty = df_sales['quantity'].sum()
            avg_inventory_level = df_products['Quantity'].mean()
            inventory_turnover = total_sales_qty / avg_inventory_level if avg_inventory_level > 0 else 0

            kpi_data['Inventory Turnover'] = f"{inventory_turnover:.2f}"
            kpi_data['Avg Inventory Level'] = f"{avg_inventory_level:.2f}"

            # Display KPIs in a nice format
            col1, col2, col3 = st.columns(3)

            with col1:
                st.subheader("💰 Financial KPIs")
                st.metric("Revenue", kpi_data['Total Revenue'])
                st.metric("Profit Margin", kpi_data['Profit Margin'])
                st.metric("Avg Transaction", kpi_data['Avg Transaction Value'])

            with col2:
                st.subheader("📦 Inventory KPIs")
                st.metric("Active Products", kpi_data['Active Products'])
                st.metric("Inventory Turnover", kpi_data['Inventory Turnover'])
                st.metric("Inventory Accuracy", kpi_data['Inventory Accuracy'])

            with col3:
                st.subheader("📊 Sales KPIs")
                st.metric("Total Transactions", kpi_data['Total Transactions'])
                st.metric("Products Sold", kpi_data['Products Sold'])
                st.metric("Avg Inventory Level", kpi_data['Avg Inventory Level'])

            # KPI Trends (if enough historical data)
            if len(df_sales) > 10:
                st.subheader("📈 KPI Trends")

                # Calculate weekly KPIs
                df_sales_copy = df_sales.copy()
                df_sales_copy['week'] = df_sales_copy['date'].dt.isocalendar().week
                weekly_revenue = df_sales_copy.groupby('week')['revenue'].sum()

                st.line_chart(weekly_revenue, use_container_width=True)

    else:
        st.warning("📊 Advanced analytics require both sales and expense data. Start recording transactions to unlock these features!")

elif menu == "👥 User Management":
    st.header("👥 User Management")

    tab1, tab2, tab3 = st.tabs(["👤 User List", "➕ Add User", "📊 User Activity"])

    with tab1:
        st.subheader("Registered Users")
        users = get_users()
        if users:
            df_users = pd.DataFrame(users)
            df_users['is_active'] = df_users['is_active'].map({1: 'Active', 0: 'Inactive'})
            st.dataframe(df_users, width="stretch")
        else:
            st.info("No users found.")

    with tab2:
        st.subheader("Add New User")
        with st.form("add_user_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            full_name = st.text_input("Full Name")
            email = st.text_input("Email")
            role = st.selectbox("Role", ["user", "admin"])

            submitted = st.form_submit_button("Add User")
            if submitted:
                if password != confirm_password:
                    st.error("Passwords do not match!")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters long!")
                else:
                    if add_user(username, password, role, full_name, email):
                        log_user_action(st.session_state.user['id'], 'add_user', f"Added user {username}")
                        st.success(f"User {username} added successfully!")
                        st.rerun()
                    else:
                        st.error("Username already exists!")

    with tab3:
        st.subheader("User Activity Log")
        conn = sqlite3.connect('inventory.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT u.username, us.action, us.details, us.timestamp
            FROM user_sessions us
            JOIN users u ON us.user_id = u.id
            ORDER BY us.timestamp DESC
            LIMIT 100
        ''')
        activities = cursor.fetchall()
        conn.close()

        if activities:
            df_activities = pd.DataFrame(activities, columns=['User', 'Action', 'Details', 'Timestamp'])
            df_activities['Timestamp'] = pd.to_datetime(df_activities['Timestamp'])
            st.dataframe(df_activities, use_container_width=True)
        else:
            st.info("No user activities recorded yet.")

elif menu == "📥 Export to CSV":
    st.header("Export Inventory to CSV")
    csv_content = export_to_csv(user_id)
    st.download_button("Download CSV", csv_content, "inventory.csv", "text/csv")