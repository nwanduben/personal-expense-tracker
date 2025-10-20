import os
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def connect_db():
    """Connect securely to PostgreSQL (Aiven or Local)."""
    return psycopg2.connect(
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"),
        dbname=os.getenv("PG_DB"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        sslmode=os.getenv("PG_SSLMODE", "require")
    )

def main():
    # 1️⃣ Load the Excel file
    file_path = "data/benjamin chidubem nwandu_8066508017_20251014161656.xlsx"
    df = pd.read_excel(file_path, skiprows=2)

    # 2️⃣ Drop empty/unnamed columns
    df = df.dropna(how="all")
    df = df.loc[:, ~df.columns.str.contains("Unnamed")]

    # 3️⃣ Standardize column names
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"[\s/₦()]+", "_", regex=True)
    )
    print("✅ Columns after cleaning:", df.columns.tolist())

    # 4️⃣ Ensure essential columns exist
    for col in ["debit_credit_", "balance_", "channel", "transaction_reference", "counterparty"]:
        if col not in df.columns:
            df[col] = None

    # 5️⃣ Convert date columns safely
    df["trans_date"] = (
        pd.to_datetime(df["trans._date"], errors="coerce")
        if "trans._date" in df.columns
        else pd.to_datetime(df["trans_date"], errors="coerce")
        if "trans_date" in df.columns
        else pd.NaT
    )
    df["value_date"] = pd.to_datetime(df.get("value_date", pd.NaT), errors="coerce")

    # 6️⃣ Split Debit & Credit using signs (+/-)
    def extract_debit(x):
        try:
            val = str(x).replace(",", "").replace("₦", "").strip()
            return abs(float(val)) if val.startswith("-") else 0
        except:
            return 0

    def extract_credit(x):
        try:
            val = str(x).replace(",", "").replace("₦", "").strip()
            return float(val.replace("+", "")) if val.startswith("+") else 0
        except:
            return 0

    df["debit"] = df["debit_credit_"].apply(extract_debit)
    df["credit"] = df["debit_credit_"].apply(extract_credit)

    # 7️⃣ Clean Balance column
    df["balance_"] = (
        df["balance_"]
        .astype(str)
        .str.replace(",", "")
        .str.replace("₦", "")
        .str.strip()
    )
    df["balance_"] = pd.to_numeric(df["balance_"], errors="coerce")

    # 8️⃣ Clean Channel column
    df["channel"] = (
        df["channel"]
        .astype(str)
        .str.strip()
        .str.upper()
        .replace({"NAN": "UNKNOWN", "": "UNKNOWN"})
    )

    # 9️⃣ Select and reorder columns
    final_cols = [
        "trans_date", "value_date", "description",
        "debit", "credit", "balance_", "channel",
        "transaction_reference", "counterparty"
    ]
    final_df = df[[c for c in final_cols if c in df.columns]]

    print(f"📊 Final dataset shape: {final_df.shape}")

    # 🔟 Connect to PostgreSQL and load
    conn = connect_db()
    cur = conn.cursor()

    print("📦 Creating table: bank_transactions ...")
    cur.execute("DROP TABLE IF EXISTS bank_transactions;")
    cur.execute("""
        CREATE TABLE bank_transactions (
            id SERIAL PRIMARY KEY,
            trans_date DATE,
            value_date DATE,
            description TEXT,
            debit NUMERIC,
            credit NUMERIC,
            balance NUMERIC,
            channel TEXT,
            transaction_reference TEXT,
            counterparty TEXT
        );
    """)

    # 11️⃣ Convert NumPy datetime64 → Python datetime
    final_df["trans_date"] = pd.to_datetime(final_df["trans_date"], errors="coerce").dt.to_pydatetime()
    final_df["value_date"] = pd.to_datetime(final_df["value_date"], errors="coerce").dt.to_pydatetime()

    # Replace NaT and NaN with None
    final_df = final_df.where(pd.notnull(final_df), None)

    # Prepare tuples for bulk insert
    records = [tuple(x) for x in final_df.to_numpy()]

    execute_values(
        cur,
        """
        INSERT INTO bank_transactions
        (trans_date, value_date, description, debit, credit, balance, channel, transaction_reference, counterparty)
        VALUES %s
        """,
        records
    )

    # ✅ Commit and close
    conn.commit()
    cur.close()
    conn.close()
    print("🎉 Data successfully loaded into PostgreSQL!")

if __name__ == "__main__":
    main()
