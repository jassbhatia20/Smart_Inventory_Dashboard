# Smart Inventory Dashboard with Streamlit UI
import streamlit as st
import os
import json
from datetime import datetime
import csv
import pandas as pd
import io
import sqlite3
import random

def round_quantity(quantity, measurement_category):
    """Round quantity based on measurement category"""
    if measurement_category in ['Units', 'Packets']:
        return round(quantity, 0)
    else:  # Kilograms, Liters
        return round(quantity, 3)

# Database functions
def get_products():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, category, price, quantity, measurement_category, expiry_date FROM products')
    rows = cursor.fetchall()
    products = []
    for row in rows:
        products.append({
            'ID': row[0],
            'Name': row[1],
            'Category': row[2],
            'Price': row[3],
            'Quantity': round_quantity(row[4], row[5]),
            'Measurement Category': row[5],
            'Expiry Date': row[6]
        })
    conn.close()
    return products

def get_active_products():
    products = get_products()
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
                    update_expiry(p['ID'], 'expired')
            except:
                active.append(p)
    return active, expired

def update_expiry(product_id, expiry):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE products SET expiry_date = ? WHERE id = ?', (expiry, product_id))
    conn.commit()
    conn.close()

def get_sales():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
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

def get_expenses():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
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

def save_product(product):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    rounded_quantity = round_quantity(product['Quantity'], product['Measurement Category'])
    cursor.execute('INSERT OR REPLACE INTO products (id, name, category, price, quantity, measurement_category, expiry_date) VALUES (?, ?, ?, ?, ?, ?, ?)',
                   (product['ID'], product['Name'], product['Category'], product['Price'], rounded_quantity, product['Measurement Category'], product['Expiry Date']))
    conn.commit()
    conn.close()

def update_quantity(product_id, qty_change):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE products SET quantity = quantity + ? WHERE id = ?', (qty_change, product_id))
    conn.commit()
    conn.close()

def add_sale(sale):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO sales (date, product, quantity, revenue, bill_id) VALUES (?, ?, ?, ?, ?)',
                   (sale['date'], sale['product'], sale['quantity'], sale['revenue'], sale.get('bill_id', '')))
    conn.commit()
    conn.close()

def add_expense(expense):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO expenses (date, product, quantity, cost, supplier) VALUES (?, ?, ?, ?, ?)',
                   (expense['date'], expense['product'], expense['quantity'], expense['cost'], expense.get('supplier', '')))
    conn.commit()
    conn.close()

def delete_product_db(product_id):
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()

# Function to export inventory to CSV (in-memory)
def export_to_csv():
    csv_data = io.StringIO()
    writer = csv.DictWriter(csv_data, fieldnames=["ID", "Name", "Category", "Price", "Quantity", "Measurement Category", "Expiry Date", "Status"])
    writer.writeheader()
    for p in active_products:
        p_copy = p.copy()
        p_copy["Status"] = "Active"
        writer.writerow({k: p_copy.get(k, "") for k in writer.fieldnames})
    for p in expired_products:
        p_copy = p.copy()
        p_copy["Status"] = "Expired"
        writer.writerow({k: p_copy.get(k, "") for k in writer.fieldnames})
    return csv_data.getvalue()

# Load data
active_products, expired_products = get_active_products()
sales = get_sales()
expenses = get_expenses()

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

menu = st.sidebar.selectbox("Select Operation", [
    "📦 View Inventory",
    "➕ Add Products",
    "💰 Sell Product",
    "🛒 Purchase Stock",
    "🔄 Update Stock",
    "💲 Update Price",
    "🗑️ Remove Product",
    "🔍 Search Product",
    "📊 View Sales Report",
    "💸 View Expenses",
    "📥 Export to CSV"
])

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
            st.bar_chart(status_data.set_index('Status')['Count'], use_container_width=True)

        with col2:
            # Simple pie chart representation using bars
            st.bar_chart(status_data.set_index('Status')['Quantity'], use_container_width=True)

    # Category Distribution
    if active_products:
        st.subheader("🏷️ Product Categories")
        df_active = pd.DataFrame(active_products)
        category_counts = df_active['Category'].value_counts().reset_index()
        category_counts.columns = ['Category', 'Count']

        st.bar_chart(category_counts.set_index('Category')['Count'], use_container_width=True)

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

elif menu == "➕ Add Products":
    st.header("Add New Product")
    with st.form("add_product_form"):
        product_id = st.number_input("Product ID", min_value=1, step=1)
        name = st.text_input("Product Name")
        category = st.text_input("Product Category")
        price = st.number_input("Product Price (INR)", min_value=0.0, step=0.01)
        measurements = st.selectbox("Measurement Category", ["Units", "Kilograms", "Liters", "Packets"])
        quantity = st.number_input("Quantity", min_value=0.0, step=0.01)
        expiry_input = st.text_input("Expiry Date (DD-MM-YYYY)")
        
        submitted = st.form_submit_button("Add Product")
        if submitted:
            try:
                datetime.strptime(expiry_input, "%d-%m-%Y")
                # Check duplicate ID
                if any(p["ID"] == product_id for p in active_products + expired_products):
                    st.error("Product ID already exists.")
                else:
                    data = {
                        "ID": int(product_id),
                        "Name": name.title(),
                        "Category": category.title(),
                        "Price": price,
                        "Quantity": int(quantity) if measurements in ['Units', 'Packets'] else round(quantity, 3),
                        "Measurement Category": measurements,
                        "Expiry Date": expiry_input
                    }
                    active_products.append(data)
                    save_product(data)
                    st.success(f"Product {name.title()} added successfully!")
                    st.rerun()
            except ValueError:
                st.error("Invalid date format. Please enter in DD-MM-YYYY format.")

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
                    update_quantity(product['ID'], -qty)
                    add_sale(sale)
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
            update_quantity(product['ID'], qty)
            add_expense(expense)
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
                        update_quantity(product['ID'], -qty)
                        add_sale(sale)
                        st.success("Stock updated!")
                        st.rerun()
                else:
                    product["Quantity"] += qty
                    update_quantity(product['ID'], qty)
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
                save_product(product)
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
                delete_product_db(product['ID'])
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

        # Revenue Over Time
        st.subheader("💰 Revenue Trend")
        daily_revenue = df_sales.groupby(df_sales['date'].dt.date)['revenue'].sum().reset_index()
        daily_revenue.columns = ['Date', 'Revenue']

        st.line_chart(daily_revenue.set_index('Date')['Revenue'], use_container_width=True)

        # Top Selling Products
        st.subheader("🏆 Top Selling Products")
        product_sales = df_sales.groupby('product')['revenue'].sum().reset_index()
        product_sales = product_sales.sort_values('revenue', ascending=False).head(10)

        st.bar_chart(product_sales.set_index('product')['revenue'], use_container_width=True)

        # Sales Distribution
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🥧 Sales by Quantity")
            quantity_sales = df_sales.groupby('product')['quantity'].sum().reset_index()
            quantity_sales = quantity_sales.sort_values('quantity', ascending=False).head(8)

            # Create a simple bar chart for quantity
            st.bar_chart(quantity_sales.set_index('product')['quantity'], use_container_width=True)

        with col2:
            st.subheader("📈 Transaction Frequency")
            # Group by date and count transactions
            daily_transactions = df_sales.groupby(df_sales['date'].dt.date).size().reset_index(name='transactions')

            st.bar_chart(daily_transactions.set_index('date')['transactions'], use_container_width=True)

        # Detailed Data Table
        st.subheader("📋 Detailed Sales Data")
        st.dataframe(df_sales.style.highlight_max(axis=0), use_container_width=True)

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

elif menu == "📥 Export to CSV":
    st.header("Export Inventory to CSV")
    csv_content = export_to_csv()
    st.download_button("Download CSV", csv_content, "inventory.csv", "text/csv")