# Smart Inventory Dashboard — app.py

# Description:
# A command-line interface (CLI) application to manage a warehouse inventory.

# Features:
# - CLI Warehouse Inventory Manager for adding, viewing, updating, deleting products
# - Maintains `products` list of dicts with keys: ID, Name, Price, Quantity
# - Ensures unique product IDs on add
# - Input validation for price and quantity
# - Search by name, update price by ID or name, update stock (sold/added)
# - Prompts to add product when not found
# - Simple text-menu UI via `menu()` function

# Usage:
# - Run `python app.py` and follow the interactive menu prompts

# Top-level functions:
# - `add_product(num_product)`
# - `add_if_not_found()`
# - `view_inventory()`
# - `update_stock(search_id)`
# - `delete_product(prod_id)`
# - `search_product(search_name)`
# - `update_price(P_id)`
# - `menu()`

# At the end of the file `menu()` is called to start the program.

products=[] #to store multiple dictionaries

#function to add products to inventory
def add_product(num_product):
    for i in range(num_product):
        data={}                             #to create a dictionary for each product
        id=int(input("Product ID: "))
        if len(products)==0:
            data["ID"]=id
        else:
            unique_id_found=False
            while not unique_id_found:       #loop until a unique ID is provided
                for j in products:
                    if j["ID"]==id:            
                        print("A product already exists with this ID.")
                        id=int(input("New Product ID: "))
                        break
                else:
                    data["ID"]=id  
                    unique_id_found=True
        
        #checking for non duplicate name of product
        name=input("Product Name: ")
        if len(products)==0:
            data["Name"]=name.title()
        else:
            unique_name_found=False
            while not unique_name_found:  #loop until a unique Name is provided
                for j in products:
                    if j["Name"]==name.title():            
                        print("A product already exists with this Name.")
                        name=input("New Product Name: ")
                        break
                else:
                    data["Name"]=name.title()
                    unique_name_found=True
        
        #to check for valid price input
        while True:
            try:
                price=float(input("Product Price (INR): "))
                data["Price"]=price
                break
            except ValueError:
                print("Invalid input. Please enter a numeric value for price.")
        
        #to check for valid quantity input
        while True:
            try:
                quantity=int(input("Product Quantity: "))
                data["Quantity"]=quantity
                break
            except ValueError:
                print("Invalid input. Please enter an integer value for quantity.")
        
        #adding dictionary to the product list
        products.append(data)

        print(f"Product {name.title()} added to inventory.\n")

    print("All products added successfully to inventory.\n")

#to ask user if they want to add product when not found
def add_if_not_found():
    add_prod=input("Do you want to add this product to inventory? (yes/no): ")
    if add_prod.lower()=="yes" or add_prod.lower()=="y":
        add_product(1)
    else:
        print("Returning to main menu.\n")

#to display inventory stock
def view_inventory():

    print("Inventory Stock:\nTotal Products:",len(products))
    print("P_ID |      Name       |  Price (INR)  | Quantity")
    print("-------------------------------------------")
    for i in products:
        print(f"{i['ID']:5}| {i['Name']:<15} | {i['Price']:<13} | {i['Quantity']}")
    print()

#to update stock of a product
def update_stock(search_id):
    found=False
    for i in products:
        if i["ID"]==search_id:
            sold_or_added=input(f"{i['Name']} sold or added to the inventory?\n(Type 'sold' or 'added' / 1 for sold, 2 for added): ")
            if  sold_or_added.lower()=='sold' or sold_or_added== '1':
                quantity_sold=int(input(f"How many {i['Name']} sold: "))
                i["Quantity"]-=quantity_sold
                found=True
            elif sold_or_added.lower()=='added' or sold_or_added=='2':
                quantity_added=int(input(f"How many {i['Name']} added: "))
                i["Quantity"]+=quantity_added
                found=True
            else:
                print("Invalid choice.\nMake sure to choose between 1 or 2, or sold or added.")
                update_stock(search_id)

    print(f"Total stock quantity of {i['Name']} is {i['Quantity']} in the inventory.")

    if not found:
        print(f"No product exists with product ID {search_id}\n")
        add_if_not_found()

#to delete product from inventory
def delete_product(prod_id):
    found=False
    for i in products:
        if i["ID"]==prod_id:    #matching by ID
            name=i["Name"]
            products.remove(i)    #removing the product dictionary from the list
            print(f"Product {name} with ID {prod_id} has been deleted from inventory.")
            found=True
            break
    if not found:
        print(f"No product exists with product ID {prod_id}\n")
        add_if_not_found()

#to search product by name
def search_product(search_name):
    found=False
    for i in products:
        if i['Name']==search_name.title():   #matching by name
            print(f"Here are details of {i['Name']}:")
            print("ID : ",i["ID"],"\nPrice : ",i["Price"],"\nQuantity : ",i["Quantity"])
            found=True
            break
    if not found:
        print(f"Sorry, we do not have {search_name} in our inventory.\n")
        add_if_not_found()

#to update product price
def update_price(P_id):
    found=False
    for i in products:
        if i["ID"]==int(P_id) or i["Name"]==P_id.title(): #matching by ID or Name
            new_price=float(input(f"New price of {i['Name']} (INR): "))
            i["Price"]=new_price
            print(f"Price of {i['Name']} updated to INR {new_price}.\n")
            found=True
            break
    if not found:
        print(f"No product found with ID or Name: {P_id}\n")
        add_if_not_found()

#to display menu and take user input
def menu():
    print("Welcome to the Warehouse Inventory Management.")
    while True:
        ch=int(input("1. Add Products\n2. Remove Product\n3. View Inventory\n4. Update Inventory Stock\n5. Search Product\n6. Update Product Price\n7. Exit\nSelect any operation to perform (write any number between 1 and 7):\n"))
        if ch==1:
            num_product=int(input("How many products you wnt to add to the inventory: "))
            add_product(num_product)
        elif ch==2:
            prod_id=int(input("Product ID to delete: "))
            delete_product(prod_id)
        elif ch==3:
            view_inventory()
        elif ch==4:
            search_id=int(input("Product ID to update stock: "))
            update_stock(search_id)
        elif ch==5:
            search_name=input("Product name to search: ")
            search_product(search_name)
        elif ch==6:
            P_id=input("Product ID or Name to update price: ")
            update_price(P_id)
        elif ch==7:
            print("Exiting the program. Goodbye!")
            break  #to exit the while loop and end program
        else:
            print("Invalid choice. Please select a number between 1 and 7.\n")
            menu() #Restarting the menu function for valid input
#Running the menu function to start the program
menu()