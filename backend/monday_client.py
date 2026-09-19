import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("MONDAY_API_TOKEN")

HEADERS = {
    "Authorization": API_TOKEN,
    "Content-Type": "application/json"
}

URL = "https://api.monday.com/v2"


def get_board_items(board_id):
    query = """
    query ($board_id: ID!) {
        boards(ids: [$board_id]) {
            id
            name
            items_page(limit: 500) {
                items {
                    id
                    name
                    column_values {
                        id
                        text
                        value
                    }
                }
            }
        }
    }
    """

    variables = {
        "board_id": str(board_id)
    }

    response = requests.post(
        URL,
        json={
            "query": query,
            "variables": variables
        },
        headers=HEADERS
    )

    response.raise_for_status()

    data = response.json()

    if "errors" in data:
        raise Exception(data["errors"])

    return data["data"]["boards"][0]

def get_board_columns(board_id):
    query = """
    query ($board_id: ID!) {
        boards(ids: [$board_id]) {
            id
            name
            columns {
                id
                title
                type
            }
        }
    }
    """

    variables = {
        "board_id": str(board_id)
    }

    response = requests.post(
        URL,
        json={
            "query": query,
            "variables": variables
        },
        headers=HEADERS
    )

    response.raise_for_status()

    data = response.json()

    if "errors" in data:
        raise Exception(data["errors"])

    return data["data"]["boards"][0]

if __name__ == "__main__":
    deals_board = get_board_items(
        os.getenv("DEALS_BOARD_ID")
    )

    work_orders_board = get_board_items(
        os.getenv("WORK_ORDERS_BOARD_ID")
    )

    print("\nDEALS BOARD:")
    print(deals_board["name"])
    print("Records:", len(deals_board["items_page"]["items"]))

    print("\nWORK ORDERS BOARD:")
    print(work_orders_board["name"])
    print("Records:", len(work_orders_board["items_page"]["items"]))

    print("\nDEALS COLUMNS:")
for column in get_board_columns(os.getenv("DEALS_BOARD_ID"))["columns"]:
    print(column["id"], "→", column["title"], "→", column["type"])


print("\nWORK ORDER COLUMNS:")
for column in get_board_columns(os.getenv("WORK_ORDERS_BOARD_ID"))["columns"]:
    print(column["id"], "→", column["title"], "→", column["type"])