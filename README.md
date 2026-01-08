# Smart Inventory Dashboard (Web v5.0)

### Welcome!
This is a robust **Web-based** tool designed to help retail owners manage their stock with advanced analytics and multi-user support.
It is built with **Streamlit** for an intuitive web interface, using Python data structures for real-time management.

> **Note:** This is Version 5.0. It runs in the browser and stores data persistently in a SQLite database. Data is saved automatically with multi-user authentication and advanced forecasting capabilities.

---

## Key Features
* **🔐 Multi-User Authentication:** Secure login system with role-based access control (Admin/User roles) and user activity logging.
* **📊 Advanced Visual Analytics:** Interactive Plotly charts, heatmaps, pie charts, and advanced graphs for sales trends, expense analysis, and inventory insights.
* **🔮 Machine Learning Forecasting:** 14-day sales forecasting using Random Forest and Linear Regression models with accuracy metrics and trend analysis.
* **💰 Profit & Loss Analysis:** Comprehensive P&L tracking with waterfall charts, margin analysis, and cumulative profit visualization.
* **📈 ABC Analysis:** Pareto principle implementation for inventory optimization (A-class high value, B-class medium value, C-class low value products).
* **📊 Inventory Turnover Analysis:** Efficiency metrics, aging analysis, and turnover ratio calculations.
* **🎯 KPI Dashboard:** Key Performance Indicators including revenue, profit margins, inventory turnover, and transaction metrics.
* **Smart Validation:** Prevents duplicate Product IDs. Allows multiple products with the same name (differentiated by ID).
* **Comprehensive Product Details:** Add products with ID, Name, Category, Price, Quantity (with measurement categories: Units, Kilograms, Liters, Packets), and Expiry Date.
* **Automatic Expiry Tracking:** Products automatically marked as "expired" when their expiry date passes.
* **Flexible Stock Management:** Easily **Add** new stock or **Sell** existing stock (with validation to prevent negative inventory). Sales are tracked for reporting.
* **Sales Interface:** Dedicated sell product feature with bill receipt generation for customer transactions.
* **Purchase Tracking:** Record stock purchases with expense tracking for cost management.
* **Low Stock Alerts:** Automatic alerts for products with quantity below 5.
* **Search Engine:** Find product details instantly by typing its name (handles multiples by letting you choose the ID).
* **Sales & Expenses Reporting:** View detailed sales history, revenue, and purchase expenses with advanced analytics.
* **👥 User Management:** Admin panel for managing users, roles, and permissions.
* **Formatted View:** Displays inventory in a clean, aligned table with all details, separated by active/expired status.
* **Export Functionality:** Export full inventory to CSV for external analysis.
* **CRUD Operations:** Create, Read, Update, and Delete products seamlessly.
* **Data Persistence:** All changes are saved to `inventory.db` SQLite database and loaded on startup.

---

## The Tech Stack
* **Language:** Python 3.x
* **Framework:** Streamlit (for web UI)
* **Machine Learning:** scikit-learn (Random Forest, Linear Regression for forecasting)
* **Data Visualization:** Plotly (interactive charts), Matplotlib, Seaborn
* **Authentication:** bcrypt (password hashing), streamlit-authenticator
* **Core Concepts:**
    * **Relational Database:** SQLite for structured data storage with multi-user support.
    * **Authentication & Security:** bcrypt password hashing, role-based access control.
    * **Machine Learning:** Time series forecasting, regression analysis.
    * **Advanced Analytics:** ABC analysis, inventory turnover, KPI calculations.
    * **Interactive Visualizations:** Plotly charts, heatmaps, waterfall charts.
    * **Error Handling:** Built-in Streamlit validations with custom error messages.
    * **Data Visualization:** Pandas DataFrames, interactive Plotly charts.
    * **Date Handling:** Automatic expiry checks using `datetime` with timezone support.

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
- **📦 View Inventory**: See active/expired products with interactive charts, summaries, and low stock alerts.
- **➕ Add Products**: Form to add new products with validation (Admin only).
- **💰 Sell Product**: Select product, enter quantity, generate bill receipt, and complete sale (Admin only).
- **🛒 Purchase Stock**: Record stock purchases with cost tracking (Admin only).
- **🔄 Update Stock**: Manual stock updates (sell/add) for existing products (Admin only).
- **💲 Update Price**: Change product price (Admin only).
- **🗑️ Remove Product**: Delete a product (Admin only).
- **🔍 Search Product**: Search by name and view results.
- **📊 View Sales Report**: Advanced sales analytics with interactive charts, revenue trends, top products, and transaction insights.
- **💸 View Expenses**: Comprehensive expense analysis with supplier breakdowns, cost trends, and correlation analysis.
- **📈 Advanced Analytics**: Machine learning forecasting, profit/loss analysis, ABC analysis, inventory turnover, and KPI dashboard.
- **👥 User Management**: Admin panel for managing users, roles, and permissions (Admin only).
- **📥 Export to CSV**: Download inventory as CSV.

### Default Login Credentials:
- **Username:** admin
- **Password:** admin123
- **Role:** Administrator

### User Roles:
- **Admin:** Full access to all features including user management, inventory operations, and advanced analytics.
- **User:** Read-only access to inventory viewing, search, and basic reporting features.
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
* [x] **v5.0 (Advanced Analytics):** Added interactive charts, ML forecasting, and multi-user support. ✅ Completed
* [ ] **v6.0 (Cloud Integration):** Add cloud storage, backup/restore, and multi-device sync.
* [ ] **v7.0 (Mobile App):** Native mobile applications for iOS and Android.
* [ ] **v8.0 (AI-Powered Insights):** Advanced AI recommendations, automated reordering, and predictive maintenance.
* [ ] **v9.0 (IoT Integration):** Smart sensors for real-time inventory tracking, automated stock counting, and environmental monitoring.
* [ ] **v10.0 (Blockchain Security):** Immutable transaction ledger, supply chain transparency, and secure audit trails.
* [ ] **v11.0 (Voice Commands):** Natural language processing for voice-activated inventory management and hands-free operations.
* [ ] **v12.0 (AR/VR Interface):** Augmented reality for warehouse navigation, virtual product placement, and immersive training.
* [ ] **v13.0 (Multi-Store Management):** Centralized dashboard for multiple store locations with cross-store analytics and inventory transfer.
* [ ] **v14.0 (Sustainability Analytics):** Carbon footprint tracking, waste reduction insights, and eco-friendly inventory optimization.
* [ ] **v15.0 (Quantum Computing):** Ultra-fast optimization algorithms for complex inventory scenarios and real-time decision making.

---
*Created by Jaspreet Bhatia (`jassbhatia20`)*