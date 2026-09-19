import os

from monday_client import get_board_items
from data_cleaner import clean_items
from analytics import (
    rename_columns,
    DEAL_COLUMNS,
    WORK_ORDER_COLUMNS,
    deal_summary,
    work_order_summary
)
from ai_agent import ask_ai


# Get live data from Monday.com
deals_board = get_board_items(os.getenv("DEALS_BOARD_ID"))
work_orders_board = get_board_items(os.getenv("WORK_ORDERS_BOARD_ID"))

# Clean data
deals = clean_items(deals_board)
work_orders = clean_items(work_orders_board)

# Rename columns
deals = [
    rename_columns(record, DEAL_COLUMNS)
    for record in deals
]

work_orders = [
    rename_columns(record, WORK_ORDER_COLUMNS)
    for record in work_orders
]

# Calculate real business metrics
deal_data = deal_summary(deals)
work_order_data = work_order_summary(work_orders)

business_data = {
    "deals": deal_data,
    "work_orders": work_order_data
}

# Ask AI
question = input("\nAsk your business question: ")

answer = ask_ai(question, business_data)

print("\nAI RESPONSE:\n")
print(answer)