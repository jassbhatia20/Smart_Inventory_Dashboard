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
            'Quantity': row[4],
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
    cursor.execute('INSERT OR REPLACE INTO products (id, name, category, price, quantity, measurement_category, expiry_date) VALUES (?, ?, ?, ?, ?, ?, ?)',
                   (product['ID'], product['Name'], product['Category'], product['Price'], product['Quantity'], product['Measurement Category'], product['Expiry Date']))
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

active_products, expired_products = get_active_products()
sales = get_sales()
expenses = get_expenses()


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

# Streamlit App
st.title("Warehouse Inventory Management")

menu = st.sidebar.selectbox("Select Operation", [
    "View Inventory",
    "Add Products",
    "Sell Product",
    "Purchase Stock",
    "Update Stock",
    "Update Price",
    "Remove Product",
    "Search Product",
    "View Sales Report",
    "View Expenses",
    "Export to CSV"
])

if menu == "View Inventory":
    st.header("Inventory Stock")
    total_active = len(active_products)
    total_expired = len(expired_products)
    total_active_qty = sum(p.get("Quantity", 0) for p in active_products)
    total_expired_qty = sum(p.get("Quantity", 0) for p in expired_products)
    
    st.write(f"**Total Active Products:** {total_active} (Total Quantity: {total_active_qty})")
    st.write(f"**Total Expired Products:** {total_expired} (Total Quantity: {total_expired_qty})")
    
    if active_products:
        st.subheader("Active Inventory")
        df_active = pd.DataFrame(active_products)
        st.dataframe(df_active)
    
    if expired_products:
        st.subheader("Expired Inventory")
        df_expired = pd.DataFrame(expired_products)
        st.dataframe(df_expired)
    
    # Low Stock Alert
    low_stock = [p for p in active_products if p.get("Quantity", 0) < 5]
    if low_stock:
        st.warning("Low Stock Alert (Quantity < 5):")
        for p in low_stock:
            st.write(f"- {p['Name']} (ID: {p['ID']}, Quantity: {p['Quantity']})")

elif menu == "Add Products":
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

elif menu == "Sell Product":
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

elif menu == "Purchase Stock":
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

elif menu == "Update Stock":
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

elif menu == "Update Price":
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

elif menu == "Remove Product":
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

elif menu == "Search Product":
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

elif menu == "View Sales Report":
    st.header("Sales Report")
    if sales:
        df_sales = pd.DataFrame(sales)
        st.dataframe(df_sales)
        total_revenue = sum(s["revenue"] for s in sales)
        st.write(f"**Total Sales:** {len(sales)} | **Total Revenue:** INR {total_revenue}")
    else:
        st.write("No sales recorded yet.")

elif menu == "View Expenses":
    st.header("Expenses Report")
    if expenses:
        df_exp = pd.DataFrame(expenses)
        st.dataframe(df_exp)
        total_exp = sum(e["cost"] for e in expenses)
        st.write(f"**Total Expenses:** INR {total_exp}")
    else:
        st.write("No expenses recorded yet.")

elif menu == "Export to CSV":
    st.header("Export Inventory to CSV")
    csv_content = export_to_csv()
    st.download_button("Download CSV", csv_content, "inventory.csv", "text/csv")