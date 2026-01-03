# Smart Inventory Dashboard with Streamlit UI
import streamlit as st
import os
import json
from datetime import datetime
import csv
import pandas as pd
import io
def load_data():
    file_name = "inventory_db.json" 
    if not os.path.exists(file_name):
        return [], []  # Return empty lists for active and expired
    try:
        with open(file_name, "r") as file:
            data = json.load(file)  # Load all data
        # Check and update expired products
        current_date = datetime.now().date()
        updated = False
        for product in data:
            if "Expiry Date" in product and product["Expiry Date"] != "expired":
                try:
                    expiry_date = datetime.strptime(product["Expiry Date"], "%d-%m-%Y").date()
                    if expiry_date < current_date:
                        product["Expiry Date"] = "expired"
                        updated = True
                except ValueError:
                    pass  # Invalid date format, skip
        if updated:
            # Save the updated data back to file
            with open(file_name, "w") as file:
                json.dump(data, file, indent=4)
        
        # Separate into active and expired
        active_products = [p for p in data if p.get("Expiry Date") != "expired"]
        expired_products = [p for p in data if p.get("Expiry Date") == "expired"]
        return active_products, expired_products
    except (json.JSONDecodeError, IOError):
        return [], []  # Return empty lists if error

def save_data():
    all_products = active_products + expired_products
    with open("inventory_db.json", "w") as file:
        json.dump(all_products, file, indent=4)

active_products, expired_products = load_data()  # Separate lists
sales = []  # List to track sales

#function to add products to inventory
def add_product(num_product):
    for i in range(num_product):
        print(f"Enter details of product {i+1}:")
        data={}                            #to create a dictionary for each product
        while True:
            try:
                product_id=int(input("Product ID: "))
                duplicate=False
                for j in active_products:
                    if j['ID']==product_id:
                        print("Product ID already exists. Please enter a unique Product ID.")
                        duplicate=True
                        break
                if not duplicate:
                    data["ID"]=product_id
                    break
            except ValueError:
                print("Invalid input. Please enter a numeric value for Product ID.")
        name=input("Product Name: ")
        data["Name"]=name.title()
        category = input("Product Category (e.g., Food, Electronics): ")
        data["Category"] = category.title()
        #to check for valid price input
        while True:
            try:
                price=float(input("Product Price (INR): "))
                data["Price"]=price
                break
            except ValueError:
                print("Invalid input. Please enter a numeric/decimal value for price.")
        
        #to check for valid quantity input
        while True:
            measurements = input("Is the quantity in units(u) or kilograms(kg) or liters(l) or packet(p) of any measurement? (Type u/kg/l/p): ").lower()
            if measurements not in ['u', 'kg', 'l', 'p']:
                print("Invalid input. Please enter 'u' for units, 'kg' for kilograms, 'l' for liters, or 'p' for packets.")
                continue
            else:
                if measurements == 'u':
                    data["Measurement Category"] = "Units"
                elif measurements == 'kg':
                    data["Measurement Category"] = "Kilograms"
                elif measurements == 'l':
                    data["Measurement Category"] = "Liters"
                else:
                    data["Measurement Category"] = "Packets"
                break
        
        while True:
            try:
                quantity = float(input("Quantity: "))
                if quantity <= 0:
                    print("Invalid input. Quantity must be a positive number.")
                    continue
                # Convert to int for discrete measurements, keep float for continuous
                if measurements in ['u', 'p']:
                    data["Quantity"] = int(quantity)
                else:
                    data["Quantity"] = round(quantity,3)  # rounding to 3 decimal places for kg and l
                break
            except ValueError:
                print("Invalid input. Please enter a numeric value for quantity.")
        
        # to check for valid expiry date input
        while True:
            try:
                expiry = input("Expiry Date (DD-MM-YYYY): ")
                datetime.strptime(expiry, "%d-%m-%Y")  # Validate format
                data["Expiry Date"] = expiry
                break
            except ValueError:
                print("Invalid date format. Please enter in DD-MM-YYYY format.")
        
        #adding dictionary to the product list
        active_products.append(data)
        save_data()  # Save data after each addition

        print(f"Product {name.title()} added to inventory.\n")

    print("All products added successfully to inventory.\n")

#to ask user if they want to add product when not found
def add_if_not_found():
    add_prod=input("Do you want to add this product to inventory? (yes/no): ")
    if add_prod.lower()=="yes" or add_prod.lower()=="y":
        add_product(1)
        save_data()
    else:
        print("Returning to main menu.\n")

#to display inventory stock
def view_inventory():
    total_active = len(active_products)
    total_expired = len(expired_products)
    total_active_qty = sum(p.get("Quantity", 0) for p in active_products)
    total_expired_qty = sum(p.get("Quantity", 0) for p in expired_products)
    
    print("Inventory Stock Summary:")
    print(f"Total Active Products: {total_active} (Total Quantity: {total_active_qty})")
    print(f"Total Expired Products: {total_expired} (Total Quantity: {total_expired_qty})")
    print()
    
    if active_products:
        print("Active Inventory:")
        print("P_ID |      Name       | Category |  Price (INR)  | Quantity | Expiry Date")
        print("----------------------------------------------------------------------------")
        for i in active_products:
            print(f"{i['ID']:5}| {i['Name']:<15} | {i.get('Category', 'N/A'):<8} | {i['Price']:<13} | {i['Quantity']:<8} | {i.get('Expiry Date', 'N/A')}")
        print()
    
    if expired_products:
        print("Expired Inventory:")
        print("P_ID |      Name       | Category |  Price (INR)  | Quantity | Expiry Date")
        print("----------------------------------------------------------------------------")
        for i in expired_products:
            print(f"{i['ID']:5}| {i['Name']:<15} | {i.get('Category', 'N/A'):<8} | {i['Price']:<13} | {i['Quantity']:<8} | {i['Expiry Date']}")
        print()
    
    # Low Stock Alert
    low_stock = [p for p in active_products if p.get("Quantity", 0) < 5]
    if low_stock:
        print("Low Stock Alert (Quantity < 5):")
        for p in low_stock:
            print(f"- {p['Name']} (ID: {p['ID']}, Quantity: {p['Quantity']})")
        print()

#to update stock of a product
def update_stock(search_id):
    if isinstance(search_id, str):
        matching_products = [p for p in active_products if p["Name"] == search_id.title()]
        if not matching_products:
            print(f"No active product found with name: {search_id}\n")
            return
        elif len(matching_products) == 1:
            product = matching_products[0]
        else:
            print(f"Multiple active products found with name '{search_id.title()}':")
            for p in matching_products:
                print(f"ID: {p['ID']}, Quantity: {p['Quantity']}, Price: {p['Price']}, Expiry: {p.get('Expiry Date', 'N/A')}")
            while True:
                chosen_id = input("Enter the ID of the product to update: ")
                if chosen_id.isdigit():
                    chosen_id = int(chosen_id)
                    product = next((p for p in matching_products if p["ID"] == chosen_id), None)
                    if product:
                        break
                print("Invalid ID. Please choose from the list.")
    else:
        product = next((p for p in active_products if p["ID"] == search_id), None)
        if not product:
            print(f"No active product found with ID: {search_id}\n")
            return

    # Now update the selected product
    while True:
        sold_or_added = input(f"{product['Name']} sold or added to the inventory?\n(Type 'sold' or 'added' / 1 for sold, 2 for added): ")
        if sold_or_added.lower() == 'sold' or sold_or_added == '1':
            while True:
                try:
                    quantity_sold = int(input(f"How many {product['Name']} sold: "))
                    if quantity_sold <= 0:
                        print("Quantity must be positive.")
                        continue
                    if quantity_sold > product["Quantity"]:
                        print("Cannot sell more than available stock.")
                        continue
                    product["Quantity"] -= quantity_sold
                    # Record sale
                    sale = {
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "product": product["Name"],
                        "quantity": quantity_sold,
                        "revenue": quantity_sold * product["Price"]
                    }
                    sales.append(sale)
                    print(f"Stock updated. New quantity: {product['Quantity']}")
                    save_data()
                    return
                except ValueError:
                    print("Invalid input. Please enter an integer.")
        elif sold_or_added.lower() == 'added' or sold_or_added == '2':
            while True:
                try:
                    quantity_added = int(input(f"How many {product['Name']} added: "))
                    if quantity_added <= 0:
                        print("Quantity must be positive.")
                        continue
                    product["Quantity"] += quantity_added
                    print(f"Stock updated. New quantity: {product['Quantity']}")
                    save_data()
                    return
                except ValueError:
                    print("Invalid input. Please enter an integer.")
        else:
            print("Invalid choice. Please choose 'sold' or 'added'.")
            continue

#to delete product from inventory
def delete_product(prod_id):
    if isinstance(prod_id, str):
        matching_products = [p for p in active_products if p["Name"] == prod_id.title()]
        if not matching_products:
            print(f"No active product found with name: {prod_id}\n")
            return
        print(f"Found {len(matching_products)} active product(s) with name '{prod_id.title()}':")
        for p in matching_products:
            print(f"ID: {p['ID']}, Quantity: {p['Quantity']}, Price: {p['Price']}, Expiry: {p.get('Expiry Date', 'N/A')}")
        choice = input("Delete all products with this name? (y/n): ")
        if choice.lower() == 'y':
            for p in matching_products:
                active_products.remove(p)
            save_data()
            print(f"All products with name '{prod_id.title()}' have been deleted.")
            return
        else:
            while True:
                chosen_id = input("Enter the ID of the product to delete: ")
                if chosen_id.isdigit():
                    chosen_id = int(chosen_id)
                    product = next((p for p in matching_products if p["ID"] == chosen_id), None)
                    if product:
                        active_products.remove(product)
                        save_data()
                        print(f"Product {product['Name']} with ID {chosen_id} has been deleted.")
                        return
                print("Invalid ID. Please choose from the list.")
    else:
        product = next((p for p in active_products if p["ID"] == prod_id), None)
        if not product:
            print(f"No active product found with ID: {prod_id}\n")
            return
        active_products.remove(product)
        save_data()
        print(f"Product {product['Name']} with ID {prod_id} has been deleted.")

#to search product by name
def search_product(search_name):
    all_products = active_products + expired_products
    found=False
    for i in all_products:
        if i['Name']==search_name.title():   #matching by name
            print(f"Here are details of {i['Name']}:")
            print("ID : ",i["ID"],"\nPrice : ",i["Price"],"\nQuantity : ",i["Quantity"],"\nExpiry Date : ",i.get("Expiry Date", "N/A"))
            found=True
            break
    if not found:
        print(f"Sorry, we do not have {search_name} in our inventory.\n")
        add_if_not_found()

#to update product price
def update_price(product_id):
    if isinstance(product_id, str):
        matching_products = [p for p in active_products if p["Name"] == product_id.title()]
        if not matching_products:
            print(f"No active product found with name: {product_id}\n")
            return
        elif len(matching_products) == 1:
            product = matching_products[0]
        else:
            print(f"Multiple active products found with name '{product_id.title()}':")
            for p in matching_products:
                print(f"ID: {p['ID']}, Quantity: {p['Quantity']}, Price: {p['Price']}, Expiry: {p.get('Expiry Date', 'N/A')}")
            while True:
                chosen_id = input("Enter the ID of the product to update: ")
                if chosen_id.isdigit():
                    chosen_id = int(chosen_id)
                    product = next((p for p in matching_products if p["ID"] == chosen_id), None)
                    if product:
                        break
                print("Invalid ID. Please choose from the list.")
    else:
        product = next((p for p in active_products if p["ID"] == product_id), None)
        if not product:
            print(f"No active product found with ID: {product_id}\n")
            return

    # Now update the selected product
    while True:
        try:
            new_price = float(input(f"New price of {product['Name']} (INR): "))
            if new_price <= 0:
                print("Price must be positive.")
                continue
            product["Price"] = new_price
            print(f"Price of {product['Name']} updated to INR {new_price}.\n")
            save_data()
            return
        except ValueError:
            print("Invalid input. Please enter a numeric value for price.")

# Function to view sales report
def view_sales_report():
    if not sales:
        print("No sales recorded yet.\n")
        return
    total_revenue = sum(s["revenue"] for s in sales)
    print("Sales Report:")
    print("Date/Time              | Product          | Qty | Revenue (INR)")
    print("-------------------------------------------------------------")
    for s in sales:
        print(f"{s['date']:<22} | {s['product']:<16} | {s['quantity']:<3} | {s['revenue']:<13}")
    print(f"\nTotal Sales: {len(sales)} | Total Revenue: INR {total_revenue}\n")

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

# Load sales if exists
if os.path.exists("sales.json"):
    with open("sales.json", "r") as file:
        sales = json.load(file)
else:
    sales = []

# Function to save sales
def save_sales():
    with open("sales.json", "w") as file:
        json.dump(sales, file, indent=4)

# Load expenses if exists
if os.path.exists("expenses.json"):
    with open("expenses.json", "r") as file:
        expenses = json.load(file)
else:
    expenses = []

# Function to save expenses
def save_expenses():
    with open("expenses.json", "w") as file:
        json.dump(expenses, file, indent=4)

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
                    save_data()
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
                        "revenue": total
                    }
                    sales.append(sale)
                    save_data()
                    save_sales()
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
                "cost": cost
            }
            expenses.append(expense)
            save_data()
            save_expenses()
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
                        save_data()
                        save_sales()
                        st.success("Stock updated!")
                        st.rerun()
                else:
                    product["Quantity"] += qty
                    save_data()
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
                save_data()
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
                save_data()
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