# Smart Inventory Dashboard
import os
import json
from datetime import datetime
def load_data():
    file_name = "inventory_db.json" 
    if not os.path.exists(file_name):
        return [] # Returns empty list if file does not exist
    try:
        with open(file_name, "r") as file:
            data = json.load(file) # Converts JSON string back to Python List
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
        return data
    except (json.JSONDecodeError, IOError):
        return [] # Returns empty list if file is corrupted or empty

def save_data():
    with open("inventory_db.json", "w") as file:
        # indent=4 makes it look pretty and readable like a real database
        json.dump(products, file, indent=4)
products=load_data() #to store multiple dictionaries

#function to add products to inventory
def add_product(num_product):
    for i in range(num_product):
        print(f"Enter details of product {i+1}:")
        data={}                            #to create a dictionary for each product
        while True:
            try:
                product_id=int(input("Product ID: "))
                duplicate=False
                for j in products:
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
        products.append(data)
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

    print("Inventory Stock:\nTotal Products:",len(products))
    print("P_ID |      Name       |  Price (INR)  | Quantity | Expiry Date")
    print("-------------------------------------------------------------")
    for i in products:
        print(f"{i['ID']:5}| {i['Name']:<15} | {i['Price']:<13} | {i['Quantity']:<8} | {i.get('Expiry Date', 'N/A')}")
    print()

#to update stock of a product
def update_stock(search_id):
    if isinstance(search_id, str):
        matching_products = [p for p in products if p["Name"] == search_id.title()]
        if not matching_products:
            print(f"No product found with name: {search_id}\n")
            add_if_not_found()
            return
        elif len(matching_products) == 1:
            product = matching_products[0]
        else:
            print(f"Multiple products found with name '{search_id.title()}':")
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
        product = next((p for p in products if p["ID"] == search_id), None)
        if not product:
            print(f"No product found with ID: {search_id}\n")
            add_if_not_found()
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
        matching_products = [p for p in products if p["Name"] == prod_id.title()]
        if not matching_products:
            print(f"No product found with name: {prod_id}\n")
            add_if_not_found()
            return
        print(f"Found {len(matching_products)} product(s) with name '{prod_id.title()}':")
        for p in matching_products:
            print(f"ID: {p['ID']}, Quantity: {p['Quantity']}, Price: {p['Price']}, Expiry: {p.get('Expiry Date', 'N/A')}")
        choice = input("Delete all products with this name? (y/n): ")
        if choice.lower() == 'y':
            for p in matching_products:
                products.remove(p)
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
                        products.remove(product)
                        save_data()
                        print(f"Product {product['Name']} with ID {chosen_id} has been deleted.")
                        return
                print("Invalid ID. Please choose from the list.")
    else:
        product = next((p for p in products if p["ID"] == prod_id), None)
        if not product:
            print(f"No product found with ID: {prod_id}\n")
            add_if_not_found()
            return
        products.remove(product)
        save_data()
        print(f"Product {product['Name']} with ID {prod_id} has been deleted.")

#to search product by name
def search_product(search_name):
    found=False
    for i in products:
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
        matching_products = [p for p in products if p["Name"] == product_id.title()]
        if not matching_products:
            print(f"No product found with name: {product_id}\n")
            add_if_not_found()
            return
        elif len(matching_products) == 1:
            product = matching_products[0]
        else:
            print(f"Multiple products found with name '{product_id.title()}':")
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
        product = next((p for p in products if p["ID"] == product_id), None)
        if not product:
            print(f"No product found with ID: {product_id}\n")
            add_if_not_found()
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

#to display menu and take user input
def main():
    print("Welcome to the Warehouse Inventory Management.")
    while True:
        while True:
            ch = input("1. Add Products\n2. Remove Product\n3. View Inventory\n4. Update Inventory Stock\n5. Search Product\n6. Update Product Price\n7. Exit\nSelect any operation to perform (write any number between 1 and 7):\n")
            try:
                ch = int(ch)
                break
            except ValueError:
                print("Invalid input. Please enter a number between 1 and 7.")
        if ch == 1:
            while True:
                num_product=input("How many products you want to add in the inventory: ")
                if num_product.isdigit():
                    add_product(int(num_product))
                    break
                else:
                    print("Invalid input. Please enter a numeric value for number of products.\n")
        elif ch == 2:
            item = input("Product ID or name to delete: ")
            delete_product(int(item) if item.isdigit() else item.title())
        elif ch == 3:
            view_inventory()
        elif ch == 4:
            update_item = input("Product ID or name to update stock: ")
            update_stock(int(update_item) if update_item.isdigit() else update_item.title())
        elif ch == 5:
            search_name=input("Product name to search: ")
            search_product(search_name)
        elif ch == 6:
            product_item=input("Product ID or Name to update price: ")
            update_price(product_item)
        elif ch == 7:
            print("Exiting the program. Goodbye!")
            break  #to exit the while loop and end program
        else:
            print("Invalid choice. Please select a number between 1 and 7.\n")
#Running the menu function to start the program
main()