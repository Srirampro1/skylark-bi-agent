import os
import requests
from dotenv import load_dotenv

load_dotenv()

MONDAY_API_TOKEN = os.getenv("MONDAY_API_TOKEN")
MONDAY_URL = "https://api.monday.com/v2"

HEADERS = {
    "Authorization": MONDAY_API_TOKEN,
    "Content-Type": "application/json"
}


def get_all_board_items(board_id):
    """Retrieve all items from a Monday.com board."""

    all_items = []
    cursor = None

    while True:

        query = """
        query ($board_id: ID!, $cursor: String) {
            boards(ids: [$board_id]) {
                name
                items_page(
                    limit: 100
                    cursor: $cursor
                ) {
                    cursor
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
            "board_id": str(board_id),
            "cursor": cursor
        }

        response = requests.post(
            MONDAY_URL,
            json={
                "query": query,
                "variables": variables
            },
            headers=HEADERS,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        if "errors" in data:
            raise Exception(data["errors"])

        boards = data["data"]["boards"]

        if not boards:
            raise Exception(
                f"Board {board_id} was not found."
            )

        board = boards[0]
        page = board["items_page"]

        items = page["items"]

        all_items.extend(items)

        cursor = page["cursor"]

        print(
            f"Retrieved {len(items)} items "
            f"(total: {len(all_items)})"
        )

        if not cursor:
            break

    return {
        "name": board["name"],
        "items": all_items
    }


if __name__ == "__main__":

    print("Fetching Work Orders...")
    work_orders = get_all_board_items(5030967820)

    print()
    print("Fetching Deals...")
    deals = get_all_board_items(5030967822)

    print()
    print("=" * 50)

    print(
        "Work Orders Board:",
        work_orders["name"]
    )

    print(
        "Total Work Orders:",
        len(work_orders["items"])
    )

    print()

    print(
        "Deals Board:",
        deals["name"]
    )

    print(
        "Total Deals:",
        len(deals["items"])
    )

    print("=" * 50)