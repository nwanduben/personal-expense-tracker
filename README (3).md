#  Personal Expense Tracker Dashboard

A Streamlit-powered interactive dashboard that tracks, visualizes, and analyzes your personal bank transactions — with automated categorization, savings tracking, and PostgreSQL database integration.


## Overview

This project reads your **bank statement (Excel format)**, cleans and loads it into a **PostgreSQL (Aiven)** database, and displays your financial summary via a Streamlit web app.

It gives you insights into:
- Total Spending  
- Total Income 
- Total Saved 
- Spending by Category   
- Monthly Transaction Trends 

---

##  Features

- **Automated Categorization** — Classifies transactions into *Airtime, Savings, Transfers,* etc.  
- **Savings Tracking** — Calculates how much money you’ve saved or withdrawn.  
- **KPI Cards** — Shows Total Spent, Income, Net Flow, and Savings at a glance.  
- **Dynamic Filtering** — Analyze by Month or All Time.  
- **Interactive Charts** — Built with Matplotlib, Seaborn, and Streamlit’s native plotting tools.  
- **PostgreSQL Integration** — Data is stored securely and reusable for other analytics projects.  
- **Download Button** — Export filtered data as CSV instantly.  

---





##  Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/<your-username>/bank-expense-tracker.git
cd bank-expense-tracker
```

### 2️⃣ Create a Virtual Environment
```bash
python -m venv env
source env/bin/activate  # On macOS/Linux
env\Scripts\activate    # On Windows
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Run the Streamlit App
```bash
streamlit run streamlit_app/app.py
```

### 5️⃣ Set Up .env File
```bash
PG_HOST=<your-host>
PG_PORT=5432
PG_DB=<your-database>
PG_USER=<your-username>
PG_PASSWORD=<your-password>
PG_SSLMODE=require
```


###  Data Loading (ETL Step)
```bash
python src/load_bank_data.py

```

## 📢 Contributing
Feel free to fork the repository, create a new branch, and submit a pull request with your improvements!








## Authors

- [@nwanduben](https://www.github.com/nwanduben)

