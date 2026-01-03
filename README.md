# Warehouse Inventory Manager (Web v4.0)

### Welcome!
This is a robust **Web-based** tool designed to help retail owners manage their stock.
It is built with **Streamlit** for an intuitive web interface, using Python data structures for real-time management.

> **Note:** This is Version 4.0. It runs in the browser and stores data persistently in a SQLite database. Data is saved automatically.

---

## Key Features
* **Visual Analytics:** Interactive charts and graphs for sales trends, expense analysis, and inventory insights with color-coded dashboards using Streamlit's built-in charting.
* **Smart Validation:** Prevents duplicate Product IDs. Allows multiple products with the same name (differentiated by ID).
* **Comprehensive Product Details:** Add products with ID, Name, Category, Price, Quantity (with measurement categories: Units, Kilograms, Liters, Packets), and Expiry Date.
* **Automatic Expiry Tracking:** Products automatically marked as "expired" when their expiry date passes.
* **Flexible Stock Management:** Easily **Add** new stock or **Sell** existing stock (with validation to prevent negative inventory). Sales are tracked for reporting.
* **Sales Interface:** Dedicated sell product feature with bill receipt generation for customer transactions.
* **Purchase Tracking:** Record stock purchases with expense tracking for cost management.
* **Low Stock Alerts:** Automatic alerts for products with quantity below 5.
* **Search Engine:** Find product details instantly by typing its name (handles multiples by letting you choose the ID).
* **Sales & Expenses Reporting:** View detailed sales history, revenue, and purchase expenses.
* **Formatted View:** Displays inventory in a clean, aligned table with all details, separated by active/expired status.
* **Export Functionality:** Export full inventory to CSV for external analysis.
* **CRUD Operations:** Create, Read, Update, and Delete products seamlessly.
* **Data Persistence:** All changes are saved to `inventory.db` SQLite database and loaded on startup.

---

## The Tech Stack
* **Language:** Python 3.x
* **Framework:** Streamlit (for web UI)
* **Core Concepts:**
    * **Relational Database:** SQLite for structured data storage.
    * **Error Handling:** Built-in Streamlit validations.
    * **Data Visualization:** Pandas DataFrames for tables.
    * **Date Handling:** Automatic expiry checks using `datetime`.

---

## 🚀 How to Run
1. **Clone the Repository:**
    ```bash
    git clone https://github.com/jassbhatia20/Smart_Inventory_Dashboard.git
    ```
2. **Navigate to the Folder:**
    ```bash
    cd Smart_Inventory_Dashboard
    ```
3. **Activate Virtual Environment (if using):**
    ```bash
    venv\Scripts\activate  # On Windows
    ```
4. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
5. **Run the App:**
    ```bash
    streamlit run app.py
    ```
6. **Open in Browser:** The app will open at `http://localhost:8501`

### Menu Options:
- **View Inventory**: See active/expired products with summaries and low stock alerts.
- **Add Products**: Form to add new products with validation.
- **Sell Product**: Select product, enter quantity, generate bill receipt, and complete sale.
- **Purchase Stock**: Record stock purchases with cost tracking.
- **Update Stock**: Manual stock updates (sell/add) for existing products.
- **Update Price**: Change product price.
- **Remove Product**: Delete a product.
- **Search Product**: Search by name and view results.
- **View Sales Report**: Interactive sales analytics with revenue trends, top products, and transaction insights.
- **View Expenses**: Comprehensive expense analysis with supplier breakdowns and cost trends.
- **Export to CSV**: Download inventory as CSV.

### Menu Options:
- 1. Add Products
- 2. Remove Product
- 3. View Inventory (with summaries and low stock alerts)
- 4. Update Inventory Stock
- 5. Search Product
- 6. Update Product Price
- 7. View Sales Report
- 8. Export to CSV
- 9. Exit

---

## Future Roadmap
I am actively working on the next versions:
* [x] **v2.0 (Persistence):** Added JSON storage so data is saved forever. ✅ Completed
* [x] **v3.0 (Advanced Features):** Added categories, sales tracking, low stock alerts, CSV export. ✅ Completed
* [x] **v4.0 (Web UI):** Converted to Streamlit web app for browser access. ✅ Completed
* [ ] **v5.0 (Advanced Analytics):** Add charts, forecasts, and multi-user support.

---
*Created by Jaspreet Bhatia (`jassbhatia20`)*