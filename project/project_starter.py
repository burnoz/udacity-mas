import pandas as pd
import numpy as np
import os
import time
import dotenv
import ast
from sqlalchemy.sql import text
from datetime import datetime, timedelta
from typing import Dict, List, Union
from sqlalchemy import create_engine, Engine

# Create an SQLite database
db_engine = create_engine("sqlite:///beaver_difflin.db")

# List containing the different kinds of papers 
paper_supplies = [
    # Paper Types (priced per sheet unless specified)
    {"item_name": "A4 paper",                         "category": "paper",        "unit_price": 0.05},
    {"item_name": "Letter-sized paper",              "category": "paper",        "unit_price": 0.06},
    {"item_name": "Cardstock",                        "category": "paper",        "unit_price": 0.15},
    {"item_name": "Colored paper",                    "category": "paper",        "unit_price": 0.10},
    {"item_name": "Glossy paper",                     "category": "paper",        "unit_price": 0.20},
    {"item_name": "Matte paper",                      "category": "paper",        "unit_price": 0.18},
    {"item_name": "Recycled paper",                   "category": "paper",        "unit_price": 0.08},
    {"item_name": "Eco-friendly paper",               "category": "paper",        "unit_price": 0.12},
    {"item_name": "Poster paper",                     "category": "paper",        "unit_price": 0.25},
    {"item_name": "Banner paper",                     "category": "paper",        "unit_price": 0.30},
    {"item_name": "Kraft paper",                      "category": "paper",        "unit_price": 0.10},
    {"item_name": "Construction paper",               "category": "paper",        "unit_price": 0.07},
    {"item_name": "Wrapping paper",                   "category": "paper",        "unit_price": 0.15},
    {"item_name": "Glitter paper",                    "category": "paper",        "unit_price": 0.22},
    {"item_name": "Decorative paper",                 "category": "paper",        "unit_price": 0.18},
    {"item_name": "Letterhead paper",                 "category": "paper",        "unit_price": 0.12},
    {"item_name": "Legal-size paper",                 "category": "paper",        "unit_price": 0.08},
    {"item_name": "Crepe paper",                      "category": "paper",        "unit_price": 0.05},
    {"item_name": "Photo paper",                      "category": "paper",        "unit_price": 0.25},
    {"item_name": "Uncoated paper",                   "category": "paper",        "unit_price": 0.06},
    {"item_name": "Butcher paper",                    "category": "paper",        "unit_price": 0.10},
    {"item_name": "Heavyweight paper",                "category": "paper",        "unit_price": 0.20},
    {"item_name": "Standard copy paper",              "category": "paper",        "unit_price": 0.04},
    {"item_name": "Bright-colored paper",             "category": "paper",        "unit_price": 0.12},
    {"item_name": "Patterned paper",                  "category": "paper",        "unit_price": 0.15},

    # Product Types (priced per unit)
    {"item_name": "Paper plates",                     "category": "product",      "unit_price": 0.10},  # per plate
    {"item_name": "Paper cups",                       "category": "product",      "unit_price": 0.08},  # per cup
    {"item_name": "Paper napkins",                    "category": "product",      "unit_price": 0.02},  # per napkin
    {"item_name": "Disposable cups",                  "category": "product",      "unit_price": 0.10},  # per cup
    {"item_name": "Table covers",                     "category": "product",      "unit_price": 1.50},  # per cover
    {"item_name": "Envelopes",                        "category": "product",      "unit_price": 0.05},  # per envelope
    {"item_name": "Sticky notes",                     "category": "product",      "unit_price": 0.03},  # per sheet
    {"item_name": "Notepads",                         "category": "product",      "unit_price": 2.00},  # per pad
    {"item_name": "Invitation cards",                 "category": "product",      "unit_price": 0.50},  # per card
    {"item_name": "Flyers",                           "category": "product",      "unit_price": 0.15},  # per flyer
    {"item_name": "Party streamers",                  "category": "product",      "unit_price": 0.05},  # per roll
    {"item_name": "Decorative adhesive tape (washi tape)", "category": "product", "unit_price": 0.20},  # per roll
    {"item_name": "Paper party bags",                 "category": "product",      "unit_price": 0.25},  # per bag
    {"item_name": "Name tags with lanyards",          "category": "product",      "unit_price": 0.75},  # per tag
    {"item_name": "Presentation folders",             "category": "product",      "unit_price": 0.50},  # per folder

    # Large-format items (priced per unit)
    {"item_name": "Large poster paper (24x36 inches)", "category": "large_format", "unit_price": 1.00},
    {"item_name": "Rolls of banner paper (36-inch width)", "category": "large_format", "unit_price": 2.50},

    # Specialty papers
    {"item_name": "100 lb cover stock",               "category": "specialty",    "unit_price": 0.50},
    {"item_name": "80 lb text paper",                 "category": "specialty",    "unit_price": 0.40},
    {"item_name": "250 gsm cardstock",                "category": "specialty",    "unit_price": 0.30},
    {"item_name": "220 gsm poster paper",             "category": "specialty",    "unit_price": 0.35},
]

# Given below are some utility functions you can use to implement your multi-agent system

def generate_sample_inventory(paper_supplies: list, coverage: float = 0.4, seed: int = 137) -> pd.DataFrame:
    """
    Generate inventory for exactly a specified percentage of items from the full paper supply list.

    This function randomly selects exactly `coverage` × N items from the `paper_supplies` list,
    and assigns each selected item:
    - a random stock quantity between 200 and 800,
    - a minimum stock level between 50 and 150.

    The random seed ensures reproducibility of selection and stock levels.

    Args:
        paper_supplies (list): A list of dictionaries, each representing a paper item with
                               keys 'item_name', 'category', and 'unit_price'.
        coverage (float, optional): Fraction of items to include in the inventory (default is 0.4, or 40%).
        seed (int, optional): Random seed for reproducibility (default is 137).

    Returns:
        pd.DataFrame: A DataFrame with the selected items and assigned inventory values, including:
                      - item_name
                      - category
                      - unit_price
                      - current_stock
                      - min_stock_level
    """
    # Ensure reproducible random output
    np.random.seed(seed)

    # Calculate number of items to include based on coverage
    num_items = int(len(paper_supplies) * coverage)

    # Randomly select item indices without replacement
    selected_indices = np.random.choice(
        range(len(paper_supplies)),
        size=num_items,
        replace=False
    )

    # Extract selected items from paper_supplies list
    selected_items = [paper_supplies[i] for i in selected_indices]

    # Construct inventory records
    inventory = []
    for item in selected_items:
        inventory.append({
            "item_name": item["item_name"],
            "category": item["category"],
            "unit_price": item["unit_price"],
            "current_stock": np.random.randint(200, 800),  # Realistic stock range
            "min_stock_level": np.random.randint(50, 150)  # Reasonable threshold for reordering
        })

    # Return inventory as a pandas DataFrame
    return pd.DataFrame(inventory)

def init_database(db_engine: Engine = db_engine, seed: int = 137) -> Engine:    
    """
    Set up the database with all required tables and initial records.

    This function performs the following tasks:
    - Creates the 'transactions' table for logging stock orders and sales
    - Loads customer inquiries from 'quote_requests.csv' into a 'quote_requests' table
    - Loads previous quotes from 'quotes.csv' into a 'quotes' table, extracting useful metadata
    - Generates a random subset of paper inventory using `generate_sample_inventory`
    - Inserts initial financial records including available cash and starting stock levels

    Args:
        db_engine (Engine): A SQLAlchemy engine connected to the SQLite database.
        seed (int, optional): A random seed used to control reproducibility of inventory stock levels.
                              Default is 137.

    Returns:
        Engine: The same SQLAlchemy engine, after initializing all necessary tables and records.

    Raises:
        Exception: If an error occurs during setup, the exception is printed and raised.
    """
    try:
        # ----------------------------
        # 1. Create an empty 'transactions' table schema
        # ----------------------------
        transactions_schema = pd.DataFrame({
            "id": [],
            "item_name": [],
            "transaction_type": [],  # 'stock_orders' or 'sales'
            "units": [],             # Quantity involved
            "price": [],             # Total price for the transaction
            "transaction_date": [],  # ISO-formatted date
        })
        transactions_schema.to_sql("transactions", db_engine, if_exists="replace", index=False)

        # Set a consistent starting date
        initial_date = datetime(2025, 1, 1).isoformat()

        # ----------------------------
        # 2. Load and initialize 'quote_requests' table
        # ----------------------------
        quote_requests_df = pd.read_csv("quote_requests.csv")
        quote_requests_df["id"] = range(1, len(quote_requests_df) + 1)
        quote_requests_df.to_sql("quote_requests", db_engine, if_exists="replace", index=False)

        # ----------------------------
        # 3. Load and transform 'quotes' table
        # ----------------------------
        quotes_df = pd.read_csv("quotes.csv")
        quotes_df["request_id"] = range(1, len(quotes_df) + 1)
        quotes_df["order_date"] = initial_date

        # Unpack metadata fields (job_type, order_size, event_type) if present
        if "request_metadata" in quotes_df.columns:
            quotes_df["request_metadata"] = quotes_df["request_metadata"].apply(
                lambda x: ast.literal_eval(x) if isinstance(x, str) else x
            )
            quotes_df["job_type"] = quotes_df["request_metadata"].apply(lambda x: x.get("job_type", ""))
            quotes_df["order_size"] = quotes_df["request_metadata"].apply(lambda x: x.get("order_size", ""))
            quotes_df["event_type"] = quotes_df["request_metadata"].apply(lambda x: x.get("event_type", ""))

        # Retain only relevant columns
        quotes_df = quotes_df[[
            "request_id",
            "total_amount",
            "quote_explanation",
            "order_date",
            "job_type",
            "order_size",
            "event_type"
        ]]
        quotes_df.to_sql("quotes", db_engine, if_exists="replace", index=False)

        # ----------------------------
        # 4. Generate inventory and seed stock
        # ----------------------------
        inventory_df = generate_sample_inventory(paper_supplies, seed=seed)

        # Seed initial transactions
        initial_transactions = []

        # Add a starting cash balance via a dummy sales transaction
        initial_transactions.append({
            "item_name": None,
            "transaction_type": "sales",
            "units": None,
            "price": 50000.0,
            "transaction_date": initial_date,
        })

        # Add one stock order transaction per inventory item
        for _, item in inventory_df.iterrows():
            initial_transactions.append({
                "item_name": item["item_name"],
                "transaction_type": "stock_orders",
                "units": item["current_stock"],
                "price": item["current_stock"] * item["unit_price"],
                "transaction_date": initial_date,
            })

        # Commit transactions to database
        pd.DataFrame(initial_transactions).to_sql("transactions", db_engine, if_exists="append", index=False)

        # Save the inventory reference table
        inventory_df.to_sql("inventory", db_engine, if_exists="replace", index=False)

        return db_engine

    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

def create_transaction(
    item_name: str,
    transaction_type: str,
    quantity: int,
    price: float,
    date: Union[str, datetime],
) -> int:
    """
    This function records a transaction of type 'stock_orders' or 'sales' with a specified
    item name, quantity, total price, and transaction date into the 'transactions' table of the database.

    Args:
        item_name (str): The name of the item involved in the transaction.
        transaction_type (str): Either 'stock_orders' or 'sales'.
        quantity (int): Number of units involved in the transaction.
        price (float): Total price of the transaction.
        date (str or datetime): Date of the transaction in ISO 8601 format.

    Returns:
        int: The ID of the newly inserted transaction.

    Raises:
        ValueError: If `transaction_type` is not 'stock_orders' or 'sales'.
        Exception: For other database or execution errors.
    """
    try:
        # Convert datetime to ISO string if necessary
        date_str = date.isoformat() if isinstance(date, datetime) else date

        # Validate transaction type
        if transaction_type not in {"stock_orders", "sales"}:
            raise ValueError("Transaction type must be 'stock_orders' or 'sales'")

        # Prepare transaction record as a single-row DataFrame
        transaction = pd.DataFrame([{
            "item_name": item_name,
            "transaction_type": transaction_type,
            "units": quantity,
            "price": price,
            "transaction_date": date_str,
        }])

        # Insert the record into the database
        transaction.to_sql("transactions", db_engine, if_exists="append", index=False)

        # Fetch and return the ID of the inserted row
        result = pd.read_sql("SELECT last_insert_rowid() as id", db_engine)
        return int(result.iloc[0]["id"])

    except Exception as e:
        print(f"Error creating transaction: {e}")
        raise

def get_all_inventory(as_of_date: str) -> Dict[str, int]:
    """
    Retrieve a snapshot of available inventory as of a specific date.

    This function calculates the net quantity of each item by summing 
    all stock orders and subtracting all sales up to and including the given date.

    Only items with positive stock are included in the result.

    Args:
        as_of_date (str): ISO-formatted date string (YYYY-MM-DD) representing the inventory cutoff.

    Returns:
        Dict[str, int]: A dictionary mapping item names to their current stock levels.
    """
    # SQL query to compute stock levels per item as of the given date
    query = """
        SELECT
            item_name,
            SUM(CASE
                WHEN transaction_type = 'stock_orders' THEN units
                WHEN transaction_type = 'sales' THEN -units
                ELSE 0
            END) as stock
        FROM transactions
        WHERE item_name IS NOT NULL
        AND transaction_date <= :as_of_date
        GROUP BY item_name
        HAVING stock > 0
    """

    # Execute the query with the date parameter
    result = pd.read_sql(query, db_engine, params={"as_of_date": as_of_date})

    # Convert the result into a dictionary {item_name: stock}
    return dict(zip(result["item_name"], result["stock"]))

def get_stock_level(item_name: str, as_of_date: Union[str, datetime]) -> pd.DataFrame:
    """
    Retrieve the stock level of a specific item as of a given date.

    This function calculates the net stock by summing all 'stock_orders' and 
    subtracting all 'sales' transactions for the specified item up to the given date.

    Args:
        item_name (str): The name of the item to look up.
        as_of_date (str or datetime): The cutoff date (inclusive) for calculating stock.

    Returns:
        pd.DataFrame: A single-row DataFrame with columns 'item_name' and 'current_stock'.
    """
    # Convert date to ISO string format if it's a datetime object
    if isinstance(as_of_date, datetime):
        as_of_date = as_of_date.isoformat()

    # SQL query to compute net stock level for the item
    stock_query = """
        SELECT
            item_name,
            COALESCE(SUM(CASE
                WHEN transaction_type = 'stock_orders' THEN units
                WHEN transaction_type = 'sales' THEN -units
                ELSE 0
            END), 0) AS current_stock
        FROM transactions
        WHERE item_name = :item_name
        AND transaction_date <= :as_of_date
    """

    # Execute query and return result as a DataFrame
    return pd.read_sql(
        stock_query,
        db_engine,
        params={"item_name": item_name, "as_of_date": as_of_date},
    )

def get_supplier_delivery_date(input_date_str: str, quantity: int) -> str:
    """
    Estimate the supplier delivery date based on the requested order quantity and a starting date.

    Delivery lead time increases with order size:
        - ≤10 units: same day
        - 11–100 units: 1 day
        - 101–1000 units: 4 days
        - >1000 units: 7 days

    Args:
        input_date_str (str): The starting date in ISO format (YYYY-MM-DD).
        quantity (int): The number of units in the order.

    Returns:
        str: Estimated delivery date in ISO format (YYYY-MM-DD).
    """
    # Debug log (comment out in production if needed)
    print(f"FUNC (get_supplier_delivery_date): Calculating for qty {quantity} from date string '{input_date_str}'")

    # Attempt to parse the input date
    try:
        input_date_dt = datetime.fromisoformat(input_date_str.split("T")[0])
    except (ValueError, TypeError):
        # Fallback to current date on format error
        print(f"WARN (get_supplier_delivery_date): Invalid date format '{input_date_str}', using today as base.")
        input_date_dt = datetime.now()

    # Determine delivery delay based on quantity
    if quantity <= 10:
        days = 0
    elif quantity <= 100:
        days = 1
    elif quantity <= 1000:
        days = 4
    else:
        days = 7

    # Add delivery days to the starting date
    delivery_date_dt = input_date_dt + timedelta(days=days)

    # Return formatted delivery date
    return delivery_date_dt.strftime("%Y-%m-%d")

def get_cash_balance(as_of_date: Union[str, datetime]) -> float:
    """
    Calculate the current cash balance as of a specified date.

    The balance is computed by subtracting total stock purchase costs ('stock_orders')
    from total revenue ('sales') recorded in the transactions table up to the given date.

    Args:
        as_of_date (str or datetime): The cutoff date (inclusive) in ISO format or as a datetime object.

    Returns:
        float: Net cash balance as of the given date. Returns 0.0 if no transactions exist or an error occurs.
    """
    try:
        # Convert date to ISO format if it's a datetime object
        if isinstance(as_of_date, datetime):
            as_of_date = as_of_date.isoformat()

        # Query all transactions on or before the specified date
        transactions = pd.read_sql(
            "SELECT * FROM transactions WHERE transaction_date <= :as_of_date",
            db_engine,
            params={"as_of_date": as_of_date},
        )

        # Compute the difference between sales and stock purchases
        if not transactions.empty:
            total_sales = transactions.loc[transactions["transaction_type"] == "sales", "price"].sum()
            total_purchases = transactions.loc[transactions["transaction_type"] == "stock_orders", "price"].sum()
            return float(total_sales - total_purchases)

        return 0.0

    except Exception as e:
        print(f"Error getting cash balance: {e}")
        return 0.0


def generate_financial_report(as_of_date: Union[str, datetime]) -> Dict:
    """
    Generate a complete financial report for the company as of a specific date.

    This includes:
    - Cash balance
    - Inventory valuation
    - Combined asset total
    - Itemized inventory breakdown
    - Top 5 best-selling products

    Args:
        as_of_date (str or datetime): The date (inclusive) for which to generate the report.

    Returns:
        Dict: A dictionary containing the financial report fields:
            - 'as_of_date': The date of the report
            - 'cash_balance': Total cash available
            - 'inventory_value': Total value of inventory
            - 'total_assets': Combined cash and inventory value
            - 'inventory_summary': List of items with stock and valuation details
            - 'top_selling_products': List of top 5 products by revenue
    """
    # Normalize date input
    if isinstance(as_of_date, datetime):
        as_of_date = as_of_date.isoformat()

    # Get current cash balance
    cash = get_cash_balance(as_of_date)

    # Get current inventory snapshot
    inventory_df = pd.read_sql("SELECT * FROM inventory", db_engine)
    inventory_value = 0.0
    inventory_summary = []

    # Compute total inventory value and summary by item
    for _, item in inventory_df.iterrows():
        stock_info = get_stock_level(item["item_name"], as_of_date)
        stock = stock_info["current_stock"].iloc[0]
        item_value = stock * item["unit_price"]
        inventory_value += item_value

        inventory_summary.append({
            "item_name": item["item_name"],
            "stock": stock,
            "unit_price": item["unit_price"],
            "value": item_value,
        })

    # Identify top-selling products by revenue
    top_sales_query = """
        SELECT item_name, SUM(units) as total_units, SUM(price) as total_revenue
        FROM transactions
        WHERE transaction_type = 'sales' AND transaction_date <= :date
        GROUP BY item_name
        ORDER BY total_revenue DESC
        LIMIT 5
    """
    top_sales = pd.read_sql(top_sales_query, db_engine, params={"date": as_of_date})
    top_selling_products = top_sales.to_dict(orient="records")

    return {
        "as_of_date": as_of_date,
        "cash_balance": cash,
        "inventory_value": inventory_value,
        "total_assets": cash + inventory_value,
        "inventory_summary": inventory_summary,
        "top_selling_products": top_selling_products,
    }


def search_quote_history(search_terms: List[str], limit: int = 5) -> List[Dict]:
    """
    Retrieve a list of historical quotes that match any of the provided search terms.

    The function searches both the original customer request (from `quote_requests`) and
    the explanation for the quote (from `quotes`) for each keyword. Results are sorted by
    most recent order date and limited by the `limit` parameter.

    Args:
        search_terms (List[str]): List of terms to match against customer requests and explanations.
        limit (int, optional): Maximum number of quote records to return. Default is 5.

    Returns:
        List[Dict]: A list of matching quotes, each represented as a dictionary with fields:
            - original_request
            - total_amount
            - quote_explanation
            - job_type
            - order_size
            - event_type
            - order_date
    """
    conditions = []
    params = {}

    # Build SQL WHERE clause using LIKE filters for each search term
    for i, term in enumerate(search_terms):
        param_name = f"term_{i}"
        conditions.append(
            f"(LOWER(qr.response) LIKE :{param_name} OR "
            f"LOWER(q.quote_explanation) LIKE :{param_name})"
        )
        params[param_name] = f"%{term.lower()}%"

    # Combine conditions; fallback to always-true if no terms provided
    where_clause = " AND ".join(conditions) if conditions else "1=1"

    # Final SQL query to join quotes with quote_requests
    query = f"""
        SELECT
            qr.response AS original_request,
            q.total_amount,
            q.quote_explanation,
            q.job_type,
            q.order_size,
            q.event_type,
            q.order_date
        FROM quotes q
        JOIN quote_requests qr ON q.request_id = qr.id
        WHERE {where_clause}
        ORDER BY q.order_date DESC
        LIMIT {limit}
    """

    # Execute parameterized query
    with db_engine.connect() as conn:
        result = conn.execute(text(query), params)
        return [dict(row._mapping) for row in result]

########################
########################
########################
# YOUR MULTI AGENT STARTS HERE
########################
########################
########################

import json
import re
import types
import requests
from smolagents import ToolCallingAgent, OpenAIServerModel, tool

# Ensure working directory is the project directory so relative CSV/DB paths work
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
if os.getcwd() != PROJECT_DIR:
    os.chdir(PROJECT_DIR)

# Set up and load your env parameters and instantiate your model.
dotenv.load_dotenv(dotenv_path=os.path.join(PROJECT_DIR, ".env"))
dotenv.load_dotenv()

openai_api_key = os.getenv("UDACITY_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")
openai_base_url = os.getenv("OPENAI_BASE_URL", "https://openai.vocareum.com/v1")


class _RequestsChatCompletions:
    """Fallback OpenAI-compatible chat completions endpoint using `requests` if `openai` package is missing."""

    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = (base_url or "https://openai.vocareum.com/v1").rstrip("/")

    def create(self, **kwargs):
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {k: v for k, v in kwargs.items() if v is not None}
        resp = requests.post(url, headers=headers, json=payload, timeout=90)
        if resp.status_code >= 400:
            raise RuntimeError(f"OpenAI API error {resp.status_code}: {resp.text}")
        data = resp.json()
        choices = []
        for c in data.get("choices", []):
            msg = c.get("message", {})
            choices.append(
                types.SimpleNamespace(
                    message=types.SimpleNamespace(
                        role=msg.get("role", "assistant"),
                        content=msg.get("content"),
                        tool_calls=msg.get("tool_calls"),
                    ),
                    finish_reason=c.get("finish_reason"),
                )
            )
        usage = data.get("usage", {})
        return types.SimpleNamespace(
            choices=choices,
            usage=types.SimpleNamespace(
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
            ),
        )


def _build_openai_client(api_key: str, base_url: str):
    try:
        import openai
        return openai.OpenAI(api_key=api_key, base_url=base_url)
    except ModuleNotFoundError:
        return types.SimpleNamespace(
            chat=types.SimpleNamespace(
                completions=_RequestsChatCompletions(api_key=api_key, base_url=base_url)
            )
        )


model = OpenAIServerModel(
    model_id="gpt-4o-mini",
    api_base=openai_base_url,
    api_key=openai_api_key,
    client=_build_openai_client(openai_api_key, openai_base_url),
)

# Catalog lookup dictionaries & synonym resolution for Beaver's Choice Paper Company
CATALOG_BY_LOWER = {item["item_name"].lower(): item for item in paper_supplies}

ITEM_SYNONYMS = {
    "a4 glossy paper": "Glossy paper",
    "glossy a4 paper": "Glossy paper",
    "high-quality glossy paper": "Glossy paper",
    "a3 glossy paper": "Glossy paper",
    "a4 matte paper": "Matte paper",
    "matte a3 paper": "Matte paper",
    "a3 matte paper": "Matte paper",
    "heavy cardstock": "250 gsm cardstock",
    "heavy cardstock (white)": "250 gsm cardstock",
    "heavyweight cardstock": "250 gsm cardstock",
    "sturdy cardstock": "Cardstock",
    "white cardstock": "Cardstock",
    "high-quality white cardstock": "Cardstock",
    "cardstock in various colors": "Cardstock",
    "cardstock in assorted colors": "Cardstock",
    "colorful cardstock": "Cardstock",
    "recycled cardstock": "Cardstock",
    "high-quality, recycled cardstock in various colors": "Cardstock",
    "colored paper (assorted colors)": "Colored paper",
    "8.5\"x11\" colored paper": "Colored paper",
    "a3 colored paper": "Colored paper",
    "a3 colored paper (assorted colors)": "Colored paper",
    "a5 colored paper": "Colored paper",
    "colored paper in assorted colors": "Colored paper",
    "colorful poster paper": "Poster paper",
    "poster paper in various colors": "Poster paper",
    "posters": "Poster paper",
    "poster board": "Large poster paper (24x36 inches)",
    "poster boards": "Large poster paper (24x36 inches)",
    "poster boards (24\" x 36\")": "Large poster paper (24x36 inches)",
    "large poster paper": "Large poster paper (24x36 inches)",
    "streamers": "Party streamers",
    "roll of streamers": "Party streamers",
    "rolls of streamers": "Party streamers",
    "printer paper": "Standard copy paper",
    "reams of printer paper": "Standard copy paper",
    "white printer paper": "Standard copy paper",
    "standard printer paper": "Standard copy paper",
    "standard printing paper": "Standard copy paper",
    "a4 white printer paper": "A4 paper",
    "a4 printer paper": "A4 paper",
    "a4 size printer paper": "A4 paper",
    "a4 printing paper": "A4 paper",
    "a4 white paper": "A4 paper",
    "a4 recycled paper": "Recycled paper",
    "washi tape": "Decorative adhesive tape (washi tape)",
    "decorative washi tape": "Decorative adhesive tape (washi tape)",
    "rolls of decorative washi tape": "Decorative adhesive tape (washi tape)",
    "colorful construction paper": "Construction paper",
    "kraft paper envelopes": "Envelopes",
    "100% recycled kraft paper envelopes": "Envelopes",
    "packets of 100% recycled kraft paper envelopes": "Envelopes",
    "table napkins": "Paper napkins",
    "table napkins (white)": "Paper napkins",
    "paper cups (biodegradable)": "Paper cups",
    "biodegradable paper cups": "Paper cups",
    "paper plates (biodegradable)": "Paper plates",
    "biodegradable paper plates": "Paper plates",
    "cardboard for signage": "Heavyweight paper",
    "reams of cardboard for signage": "Heavyweight paper",
}

UNSUPPORTED_ITEMS = {"balloons", "balloon", "tickets", "ticket", "a3 paper"}


def resolve_catalog_item(query_name: str) -> Union[Dict, None]:
    """Match a customer or agent item description to its exact entry in `paper_supplies`."""
    if not query_name:
        return None
    cleaned = query_name.strip().lower()

    if cleaned in UNSUPPORTED_ITEMS:
        return None

    # 1. Exact match in catalog
    if cleaned in CATALOG_BY_LOWER:
        return CATALOG_BY_LOWER[cleaned]

    # 2. Exact match in synonym table
    if cleaned in ITEM_SYNONYMS:
        target = ITEM_SYNONYMS[cleaned].lower()
        return CATALOG_BY_LOWER.get(target)

    # 3. Substring match in synonym table
    for syn_key, canonical_name in ITEM_SYNONYMS.items():
        if syn_key in cleaned or cleaned in syn_key:
            return CATALOG_BY_LOWER.get(canonical_name.lower())

    # 4. Substring/token match against `paper_supplies`
    for item in paper_supplies:
        cname = item["item_name"].lower()
        if cname in cleaned or cleaned in cname:
            return item

    return None


def get_inventory_record(item_name: str) -> Union[Dict, None]:
    """Return the row from the `inventory` table if the item is stocked in the warehouse."""
    try:
        df = pd.read_sql(
            "SELECT * FROM inventory WHERE item_name = :item_name",
            db_engine,
            params={"item_name": item_name},
        )
        if not df.empty:
            return df.iloc[0].to_dict()
    except Exception:
        pass
    return None


"""Set up tools for your agents to use, these should be methods that combine the database functions above
 and apply criteria to them to ensure that the flow of the system is correct."""


# ==========================================
# Tools for inventory agent
# ==========================================

@tool
def check_all_inventory(as_of_date: str) -> str:
    """Retrieve a complete snapshot of all currently stocked inventory items as of a given date.

    Args:
        as_of_date: ISO-formatted date string (YYYY-MM-DD) for the inventory check.

    Returns:
        A JSON string listing all available inventory items and their current stock counts.
    """
    stock_dict = get_all_inventory(as_of_date)
    return json.dumps({
        "as_of_date": as_of_date,
        "available_inventory": stock_dict,
        "total_stocked_skus": len(stock_dict),
    }, indent=2)


@tool
def check_item_stock(item_name: str, quantity_needed: int, as_of_date: str, delivery_deadline: str = "") -> str:
    """Check the stock level, minimum stock threshold, reorder need, and supplier delivery feasibility for an item.

    Args:
        item_name: The name or description of the paper item requested.
        quantity_needed: The number of units requested by the customer.
        as_of_date: The cutoff date (YYYY-MM-DD) for checking inventory.
        delivery_deadline: Optional customer delivery deadline in YYYY-MM-DD format.

    Returns:
        A JSON string with exact catalog item_name, current_stock, min_stock_level, unit_price,
        supplier delivery date, and whether the order can be fulfilled by the customer's deadline.
    """
    catalog_item = resolve_catalog_item(item_name)
    if catalog_item is None:
        return json.dumps({
            "requested_name": item_name,
            "in_catalog": False,
            "can_fulfill": False,
            "status": "REJECTED_NOT_IN_CATALOG",
            "reason": f"Beaver's Choice Paper Company does not carry '{item_name}' in its product catalog.",
        }, indent=2)

    exact_name = catalog_item["item_name"]
    unit_price = float(catalog_item["unit_price"])
    stock_df = get_stock_level(exact_name, as_of_date)
    current_stock = int(stock_df["current_stock"].iloc[0]) if not stock_df.empty else 0

    inv_rec = get_inventory_record(exact_name)
    is_warehouse_item = inv_rec is not None
    min_stock = int(inv_rec["min_stock_level"]) if is_warehouse_item else 0

    qty = int(quantity_needed)
    shortfall = max(0, qty - current_stock)
    projected_remaining = current_stock - qty
    needs_restock = shortfall > 0 or (is_warehouse_item and projected_remaining < min_stock)
    recommended_reorder_qty = (
        max(0, (qty + min_stock) - current_stock) if is_warehouse_item and needs_restock else shortfall
    )

    # Check supplier delivery date if current stock cannot cover the order immediately
    if shortfall > 0:
        estimated_delivery = get_supplier_delivery_date(as_of_date, recommended_reorder_qty)
    else:
        estimated_delivery = get_supplier_delivery_date(as_of_date, 1)  # In stock -> same-day dispatch

    can_fulfill = True
    rejection_reason = None
    if delivery_deadline and shortfall > 0 and estimated_delivery > delivery_deadline:
        can_fulfill = False
        rejection_reason = (
            f"Insufficient stock for '{exact_name}' (have {current_stock}, need {qty}) and supplier restock "
            f"of {recommended_reorder_qty} units ordered on {as_of_date} arrives on {estimated_delivery}, "
            f"which is after the requested deadline of {delivery_deadline}."
        )

    return json.dumps({
        "requested_name": item_name,
        "exact_item_name": exact_name,
        "in_catalog": True,
        "is_warehouse_stocked_item": is_warehouse_item,
        "unit_price": unit_price,
        "current_stock": current_stock,
        "quantity_needed": qty,
        "min_stock_level": min_stock,
        "shortfall": shortfall,
        "needs_restock": needs_restock,
        "recommended_reorder_qty": recommended_reorder_qty,
        "estimated_delivery_date": estimated_delivery,
        "delivery_deadline": delivery_deadline,
        "can_fulfill": can_fulfill,
        "rejection_reason": rejection_reason,
    }, indent=2)


@tool
def check_supplier_delivery(input_date_str: str, quantity: int) -> str:
    """Check the estimated supplier delivery date for ordering a given quantity of stock.

    Args:
        input_date_str: The order date in ISO format (YYYY-MM-DD).
        quantity: The number of units to be ordered/delivered.

    Returns:
        A JSON string containing the input_date, quantity, and estimated supplier delivery date (YYYY-MM-DD).
    """
    estimated_date = get_supplier_delivery_date(input_date_str, int(quantity))
    return json.dumps({
        "order_date": input_date_str,
        "quantity": int(quantity),
        "estimated_delivery_date": estimated_date,
    }, indent=2)


# ==========================================
# Tools for quoting agent
# ==========================================

@tool
def get_quote_history(search_terms: List[str], limit: int = 5) -> str:
    """Search historical customer quotes matching keywords to inform pricing and bulk discount strategy.

    Args:
        search_terms: List of keywords (e.g. item names, event types, job types) to search for.
        limit: Maximum number of historical quotes to return (default 5).

    Returns:
        A JSON string containing matching historical quotes and their explanations.
    """
    records = search_quote_history(search_terms, limit=limit)
    return json.dumps(records, indent=2)


@tool
def calculate_bulk_quote(item_name: str, quantity: int, as_of_date: str) -> str:
    """Calculate an itemized price quote with strategic tiered bulk discounts for a catalog item.

    Bulk Discount Tiers:
    - 100 to 499 units: 5% discount
    - 500 to 999 units: 10% discount
    - 1000+ units: 15% discount

    Args:
        item_name: Name of the paper product.
        quantity: Quantity of units requested.
        as_of_date: Date of the quote request (YYYY-MM-DD).

    Returns:
        A JSON string with base unit price, discount percentage, discounted total, and current stock level.
    """
    catalog_item = resolve_catalog_item(item_name)
    if catalog_item is None:
        return json.dumps({
            "requested_name": item_name,
            "valid_item": False,
            "message": f"Item '{item_name}' is not in the Beaver's Choice Paper Company catalog.",
        }, indent=2)

    exact_name = catalog_item["item_name"]
    unit_price = float(catalog_item["unit_price"])
    qty = int(quantity)

    if qty >= 1000:
        discount_rate = 0.15
    elif qty >= 500:
        discount_rate = 0.10
    elif qty >= 100:
        discount_rate = 0.05
    else:
        discount_rate = 0.0

    gross_total = round(unit_price * qty, 2)
    discount_amount = round(gross_total * discount_rate, 2)
    net_total = round(gross_total - discount_amount, 2)

    return json.dumps({
        "exact_item_name": exact_name,
        "quantity": qty,
        "unit_price": unit_price,
        "discount_percent": int(discount_rate * 100),
        "gross_total": gross_total,
        "discount_saved": discount_amount,
        "discounted_total": net_total,
    }, indent=2)


# ==========================================
# Tools for ordering / transaction agent
# ==========================================

@tool
def check_company_cash(as_of_date: str) -> str:
    """Check the current cash balance of Beaver's Choice Paper Company as of a specific date.

    Args:
        as_of_date: The cutoff date in ISO format (YYYY-MM-DD).

    Returns:
        A JSON string reporting the available cash balance.
    """
    balance = get_cash_balance(as_of_date)
    return json.dumps({
        "as_of_date": as_of_date,
        "cash_balance": round(balance, 2),
    }, indent=2)


@tool
def record_order_transaction(
    item_name: str,
    transaction_type: str,
    quantity: int,
    price: float,
    date: str,
    delivery_deadline: str = "",
) -> str:
    """Record a 'sales' or 'stock_orders' transaction in the database after verifying stock, cash, and delivery deadlines.

    Args:
        item_name: Exact or common name of the catalog item.
        transaction_type: Must be either 'sales' (customer order) or 'stock_orders' (supplier restock).
        quantity: Number of units in the transaction.
        price: Total dollar amount for the transaction.
        date: Transaction date in ISO format (YYYY-MM-DD).
        delivery_deadline: Optional customer delivery deadline in YYYY-MM-DD format.

    Returns:
        A JSON string confirming the transaction ID and updated stock/cash balances, or a rejection reason if invalid.
    """
    catalog_item = resolve_catalog_item(item_name)
    if catalog_item is None:
        return json.dumps({
            "success": False,
            "status": "REJECTED_NOT_IN_CATALOG",
            "error": f"Item '{item_name}' does not exist in the Beaver's Choice Paper Company catalog.",
        }, indent=2)

    exact_name = catalog_item["item_name"]
    unit_cost = float(catalog_item["unit_price"])
    qty = int(quantity)
    tx_price = round(float(price), 2)

    if transaction_type == "stock_orders":
        current_cash = get_cash_balance(date)
        order_cost = round(qty * unit_cost, 2)
        if current_cash < order_cost:
            return json.dumps({
                "success": False,
                "status": "REJECTED_INSUFFICIENT_CASH",
                "error": f"Insufficient cash (${current_cash:.2f}) to restock {qty} units of '{exact_name}' (${order_cost:.2f}).",
            }, indent=2)
        tx_id = create_transaction(exact_name, "stock_orders", qty, order_cost, date)
        new_stock = int(get_stock_level(exact_name, date)["current_stock"].iloc[0])
        return json.dumps({
            "success": True,
            "transaction_id": tx_id,
            "transaction_type": "stock_orders",
            "item_name": exact_name,
            "quantity": qty,
            "total_cost": order_cost,
            "updated_stock": new_stock,
            "updated_cash_balance": round(get_cash_balance(date), 2),
        }, indent=2)

    elif transaction_type == "sales":
        stock_df = get_stock_level(exact_name, date)
        current_stock = int(stock_df["current_stock"].iloc[0]) if not stock_df.empty else 0
        inv_rec = get_inventory_record(exact_name)
        is_warehouse_item = inv_rec is not None
        min_stock = int(inv_rec["min_stock_level"]) if is_warehouse_item else 0

        restock_tx_id = None
        restock_qty = 0
        if current_stock < qty:
            shortfall = qty - current_stock
            restock_qty = shortfall + min_stock if is_warehouse_item else shortfall
            supplier_arrival = get_supplier_delivery_date(date, restock_qty)
            if delivery_deadline and supplier_arrival > delivery_deadline:
                return json.dumps({
                    "success": False,
                    "status": "REJECTED_DELIVERY_TIMELINE",
                    "error": (
                        f"Cannot fulfill {qty} units of '{exact_name}' by {delivery_deadline}: "
                        f"current stock is {current_stock} and supplier delivery for {restock_qty} units "
                        f"ordered on {date} will not arrive until {supplier_arrival}."
                    ),
                }, indent=2)

            restock_cost = round(restock_qty * unit_cost, 2)
            if get_cash_balance(date) < restock_cost:
                return json.dumps({
                    "success": False,
                    "status": "REJECTED_INSUFFICIENT_CASH",
                    "error": f"Insufficient cash to restock {restock_qty} units of '{exact_name}'.",
                }, indent=2)

            restock_tx_id = create_transaction(exact_name, "stock_orders", restock_qty, restock_cost, date)
            current_stock += restock_qty

        # Record the customer sale
        sale_tx_id = create_transaction(exact_name, "sales", qty, tx_price, date)
        remaining_stock = current_stock - qty

        # Proactive replenishment if warehouse item dropped below min_stock_level
        if is_warehouse_item and remaining_stock < min_stock and restock_tx_id is None:
            replenish_qty = (min_stock - remaining_stock) + 100
            replenish_cost = round(replenish_qty * unit_cost, 2)
            if get_cash_balance(date) >= replenish_cost:
                restock_tx_id = create_transaction(exact_name, "stock_orders", replenish_qty, replenish_cost, date)
                restock_qty = replenish_qty
                remaining_stock += replenish_qty

        return json.dumps({
            "success": True,
            "sale_transaction_id": sale_tx_id,
            "restock_transaction_id": restock_tx_id,
            "restocked_units": restock_qty,
            "item_name": exact_name,
            "quantity_sold": qty,
            "sale_price": tx_price,
            "remaining_stock": remaining_stock,
            "updated_cash_balance": round(get_cash_balance(date), 2),
        }, indent=2)

    return json.dumps({
        "success": False,
        "error": f"Invalid transaction_type '{transaction_type}'. Must be 'sales' or 'stock_orders'.",
    }, indent=2)


@tool
def get_company_financial_report(as_of_date: str) -> str:
    """Generate a financial and inventory summary report for Beaver's Choice Paper Company.

    Args:
        as_of_date: Report cutoff date in ISO format (YYYY-MM-DD).

    Returns:
        A JSON string with cash_balance, inventory_value, total_assets, and top_selling_products.
    """
    report = generate_financial_report(as_of_date)
    summary = {
        "as_of_date": report["as_of_date"],
        "cash_balance": round(report["cash_balance"], 2),
        "inventory_value": round(report["inventory_value"], 2),
        "total_assets": round(report["total_assets"], 2),
        "top_selling_products": report["top_selling_products"],
        "stocked_items_count": sum(1 for item in report["inventory_summary"] if item["stock"] > 0),
    }
    return json.dumps(summary, indent=2)


# ==========================================
# Set up your agents and create an orchestration agent that will manage them.
# (4 Agents Total: InventoryAgent, QuotingAgent, TransactionAgent, OrchestratorAgent)
# ==========================================

class InventoryAgent(ToolCallingAgent):
    """Worker Agent 1: Manages inventory queries, stock checks, restock thresholds, and supplier delivery dates."""

    def __init__(self, model: OpenAIServerModel):
        super().__init__(
            tools=[check_all_inventory, check_item_stock, check_supplier_delivery],
            model=model,
            name="inventory_agent",
            description=(
                "Specialist agent for Beaver's Choice Paper Company that checks inventory snapshots, "
                "verifies item stock levels and reorder needs, and estimates supplier delivery timelines."
            ),
            max_steps=4,
            verbosity_level=0,
        )


class QuotingAgent(ToolCallingAgent):
    """Worker Agent 2: Generates competitive customer quotes using historical quote data and bulk discounts."""

    def __init__(self, model: OpenAIServerModel):
        super().__init__(
            tools=[get_quote_history, calculate_bulk_quote],
            model=model,
            name="quoting_agent",
            description=(
                "Specialist agent for Beaver's Choice Paper Company that searches historical quotes "
                "and calculates itemized pricing with tiered bulk discounts (5%, 10%, 15%)."
            ),
            max_steps=4,
            verbosity_level=0,
        )


class TransactionAgent(ToolCallingAgent):
    """Worker Agent 3: Executes sales and restock transactions, checks cash balance, and generates financial reports."""

    def __init__(self, model: OpenAIServerModel):
        super().__init__(
            tools=[check_company_cash, record_order_transaction, get_company_financial_report],
            model=model,
            name="transaction_agent",
            description=(
                "Specialist agent for Beaver's Choice Paper Company that checks cash balances, "
                "records 'sales' and 'stock_orders' transactions in the database, and generates financial reports."
            ),
            max_steps=4,
            verbosity_level=0,
        )


class OrchestratorAgent(ToolCallingAgent):
    """Agent 4 (Orchestrator): Coordinates customer inquiries across Inventory, Quoting, and Transaction agents."""

    def __init__(self, model: OpenAIServerModel):
        self.inventory_agent = InventoryAgent(model)
        self.quoting_agent = QuotingAgent(model)
        self.transaction_agent = TransactionAgent(model)

        @tool
        def consult_inventory_agent(task_description: str) -> str:
            """Delegate an inventory check, stock level lookup, or supplier delivery date check to the Inventory Agent.

            Args:
                task_description: Detailed instructions including requested items, quantities, request date, and delivery deadline.

            Returns:
                The Inventory Agent's assessment of stock availability, reorder requirements, and supplier delivery dates.
            """
            return str(self.inventory_agent.run(task_description))

        @tool
        def consult_quoting_agent(task_description: str) -> str:
            """Delegate quote history lookup and bulk discount calculation to the Quoting Agent.

            Args:
                task_description: Detailed instructions including exact item names, quantities, event/job context, and request date.

            Returns:
                The Quoting Agent's itemized quote breakdown, bulk discounts applied, and historical quote context.
            """
            return str(self.quoting_agent.run(task_description))

        @tool
        def consult_transaction_agent(task_description: str) -> str:
            """Delegate order fulfillment ('sales' and 'stock_orders' database transactions) and financial checks to the Transaction Agent.

            Args:
                task_description: Detailed instructions specifying exact item names, quantities, final discounted prices, transaction date, and delivery deadline.

            Returns:
                The Transaction Agent's confirmation of recorded transactions, updated cash balance, and financial report summary.
            """
            return str(self.transaction_agent.run(task_description))

        super().__init__(
            tools=[consult_inventory_agent, consult_quoting_agent, consult_transaction_agent],
            model=model,
            name="orchestrator_agent",
            description=(
                "Lead Orchestrator Agent for Beaver's Choice Paper Company. Coordinates InventoryAgent, "
                "QuotingAgent, and TransactionAgent to handle customer inquiries end-to-end."
            ),
            max_steps=6,
            verbosity_level=0,
        )

    def handle_customer_inquiry(self, request_with_date: str) -> str:
        """Process a customer inquiry end-to-end by coordinating the Inventory, Quoting, and Transaction agents."""
        # Step 1: Inventory Agent checks stock snapshot, item stock levels, and supplier delivery dates
        inventory_prompt = f"""Customer Request:
{request_with_date}

In Step 1, call ALL of these tools together in one turn (do NOT call final_answer in Step 1):
- `check_all_inventory` for the request date (YYYY-MM-DD).
- `check_item_stock` for each requested item with `item_name`, `quantity_needed`, `as_of_date` (YYYY-MM-DD), and `delivery_deadline` (YYYY-MM-DD).
- `check_supplier_delivery` with `input_date_str` (request date) and `quantity` of the largest item.

In Step 2, call ONLY `final_answer` with a concise summary for each item: `exact_item_name`, `quantity_needed`, `current_stock`, `estimated_delivery_date`, `can_fulfill` (True/False), and `rejection_reason` (if any).
"""
        inventory_report = str(self.inventory_agent.run(inventory_prompt))

        # Step 2: Quoting Agent checks historical quotes and calculates bulk discount prices
        quoting_prompt = f"""Customer Request:
{request_with_date}

Inventory Assessment:
{inventory_report}

In Step 1, call ALL of these tools together in one turn (do NOT call final_answer in Step 1):
- `get_quote_history` using 2-3 keywords from the request.
- `calculate_bulk_quote` for every item in the Inventory Assessment where `can_fulfill` is True.

In Step 2, call ONLY `final_answer` with the itemized pricing breakdown (`exact_item_name`, `quantity`, `unit_price`, `discount_percent`, `discounted_total`, `can_fulfill`) and list any unfulfillable items with their `rejection_reason`.
"""
        quote_report = str(self.quoting_agent.run(quoting_prompt))

        # Step 3: Transaction Agent executes database transactions for fulfillable items and generates the final response
        transaction_prompt = f"""Customer Request:
{request_with_date}

Inventory Assessment:
{inventory_report}

Quote Assessment:
{quote_report}

In Step 1, call ALL of these tools together in one turn (do NOT call final_answer in Step 1):
- `check_company_cash` for the request date.
- For EVERY item where `can_fulfill` is True, call `record_order_transaction` with `item_name` (`exact_item_name`), `transaction_type='sales'`, `quantity`, `price` (`discounted_total`), `date` (request date YYYY-MM-DD), and `delivery_deadline` (YYYY-MM-DD). (Do NOT call `record_order_transaction` for items where `can_fulfill` is False.)
- `get_company_financial_report` for the request date.

In Step 2, call ONLY `final_answer` with the final customer-facing response from Beaver's Choice Paper Company:
- If items were fulfilled: provide the itemized quote and order confirmation (exact item names, quantities, unit prices, bulk discounts applied, final totals, and delivery date).
- If any items or the entire order could not be fulfilled: provide a clear, polite rejection reason explaining why (e.g., item not carried in catalog, or insufficient current stock where supplier delivery arrives after the customer's requested deadline).
"""
        final_response = str(self.transaction_agent.run(transaction_prompt))
        return final_response


# Run your test scenarios by writing them here. Make sure to keep track of them.

def run_test_scenarios():

    print("Initializing Database...")
    init_database(db_engine)
    try:
        quote_requests_sample = pd.read_csv("quote_requests_sample.csv")
        quote_requests_sample["request_date"] = pd.to_datetime(
            quote_requests_sample["request_date"], format="%m/%d/%y", errors="coerce"
        )
        quote_requests_sample = quote_requests_sample.dropna(subset=["request_date"])
        quote_requests_sample = quote_requests_sample.sort_values("request_date")
    except Exception as e:
        print(f"FATAL: Error loading test data: {e}")
        return

    # Get initial state
    initial_date = quote_requests_sample["request_date"].min().strftime("%Y-%m-%d")
    report = generate_financial_report(initial_date)
    current_cash = report["cash_balance"]
    current_inventory = report["inventory_value"]

    ############
    ############
    ############
    # INITIALIZE YOUR MULTI AGENT SYSTEM HERE
    ############
    ############
    ############
    orchestrator = OrchestratorAgent(model)

    results = []
    for idx, row in quote_requests_sample.iterrows():
        request_date = row["request_date"].strftime("%Y-%m-%d")

        print(f"\n=== Request {idx+1} ===")
        print(f"Context: {row['job']} organizing {row['event']}")
        print(f"Request Date: {request_date}")
        print(f"Cash Balance: ${current_cash:.2f}")
        print(f"Inventory Value: ${current_inventory:.2f}")

        # Process request
        request_with_date = f"{row['request']} (Date of request: {request_date})"

        ############
        ############
        ############
        # USE YOUR MULTI AGENT SYSTEM TO HANDLE THE REQUEST
        ############
        ############
        ############

        response = orchestrator.handle_customer_inquiry(request_with_date)

        # Update state
        report = generate_financial_report(request_date)
        current_cash = report["cash_balance"]
        current_inventory = report["inventory_value"]

        print(f"Response: {response}")
        print(f"Updated Cash: ${current_cash:.2f}")
        print(f"Updated Inventory: ${current_inventory:.2f}")

        results.append(
            {
                "request_id": idx + 1,
                "request_date": request_date,
                "cash_balance": current_cash,
                "inventory_value": current_inventory,
                "response": response,
            }
        )
        pd.DataFrame(results).to_csv("test_results.csv", index=False)

        time.sleep(0.1)

    # Final report
    final_date = quote_requests_sample["request_date"].max().strftime("%Y-%m-%d")
    final_report = generate_financial_report(final_date)
    print("\n===== FINAL FINANCIAL REPORT =====")
    print(f"Final Cash: ${final_report['cash_balance']:.2f}")
    print(f"Final Inventory: ${final_report['inventory_value']:.2f}")

    # Save results
    pd.DataFrame(results).to_csv("test_results.csv", index=False)
    return results


if __name__ == "__main__":
    results = run_test_scenarios()
