import os
import requests
from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# MONDAY.COM CONFIGURATION
# ============================================================

MONDAY_API_URL = "https://api.monday.com/v2"


def get_monday_token():
    """
    Get the Monday.com API token.

    Priority:
    1. Streamlit Cloud Secrets
    2. Local .env file
    """

    # Try Streamlit Cloud secrets
    try:
        import streamlit as st

        token = st.secrets.get(
            "MONDAY_API_TOKEN",
            None
        )

        if token:
            return token

    except Exception:
        pass

    # Try environment variable
    token = os.getenv(
        "MONDAY_API_TOKEN"
    )

    if token:
        return token

    return None


# ============================================================
# API REQUEST
# ============================================================

def monday_request(
    query,
    variables=None
):

    token = get_monday_token()

    if not token:

        raise RuntimeError(
            "MONDAY_API_TOKEN is missing. "
            "Add it to your .env file locally "
            "or Streamlit Cloud Secrets."
        )

    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }

    payload = {
        "query": query,
        "variables": variables or {}
    }

    response = requests.post(
        MONDAY_API_URL,
        json=payload,
        headers=headers,
        timeout=60
    )

    # HTTP error
    response.raise_for_status()

    result = response.json()

    # GraphQL errors
    if "errors" in result:

        error_messages = []

        for error in result["errors"]:

            error_messages.append(
                error.get(
                    "message",
                    "Unknown Monday.com error"
                )
            )

        raise RuntimeError(
            "Monday.com API error: "
            + " | ".join(error_messages)
        )

    return result


# ============================================================
# GET BOARD ITEMS
# ============================================================

def get_board_items(
    board_id,
    cursor=None,
    limit=100
):

    # --------------------------------------------------------
    # First request
    # --------------------------------------------------------

    if cursor is None:

        query = """
        query ($board_id: ID!, $limit: Int!) {

            boards(ids: [$board_id]) {

                items_page(
                    limit: $limit
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
            "limit": limit
        }

        result = monday_request(
            query,
            variables
        )

        boards = result.get(
            "data",
            {}
        ).get(
            "boards",
            []
        )

        if not boards:

            raise RuntimeError(
                f"Board {board_id} was not found."
            )

        page = boards[0].get(
            "items_page",
            {}
        )

    # --------------------------------------------------------
    # Next pages
    # --------------------------------------------------------

    else:

        query = """
        query (
            $cursor: String!,
            $limit: Int!
        ) {

            next_items_page(
                cursor: $cursor,
                limit: $limit
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
        """

        variables = {
            "cursor": cursor,
            "limit": limit
        }

        result = monday_request(
            query,
            variables
        )

        page = result.get(
            "data",
            {}
        ).get(
            "next_items_page",
            {}
        )

    return page


# ============================================================
# GET ALL ITEMS FROM A BOARD
# ============================================================

def get_all_board_items(
    board_id,
    page_size=100
):

    all_items = []

    cursor = None

    page_number = 1

    while True:

        page = get_board_items(
            board_id=board_id,
            cursor=cursor,
            limit=page_size
        )

        items = page.get(
            "items",
            []
        )

        all_items.extend(
            items
        )

        print(
            f"Retrieved {len(items)} items "
            f"(total: {len(all_items)})"
        )

        cursor = page.get(
            "cursor"
        )

        # No more pages
        if not cursor:
            break

        page_number += 1

    return {
        "items": all_items
    }


# ============================================================
# GET BOARD INFORMATION
# ============================================================

def get_board_info(
    board_id
):

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

    result = monday_request(
        query,
        variables
    )

    boards = result.get(
        "data",
        {}
    ).get(
        "boards",
        []
    )

    if not boards:

        raise RuntimeError(
            f"Board {board_id} was not found."
        )

    return boards[0]


# ============================================================
# TEST CONNECTION
# ============================================================

def test_connection():

    query = """
    query {
        me {
            id
            name
            email
        }
    }
    """

    result = monday_request(
        query
    )

    user = result.get(
        "data",
        {}
    ).get(
        "me"
    )

    if not user:

        raise RuntimeError(
            "Could not authenticate with Monday.com."
        )

    return user


# ============================================================
# MAIN TEST
# ============================================================

if __name__ == "__main__":

    print(
        "\nTesting Monday.com connection..."
    )

    try:

        user = test_connection()

        print(
            "Connected successfully!"
        )

        print(
            "User:",
            user.get("name")
        )

        print(
            "Email:",
            user.get("email")
        )

        print(
            "\nTesting Deals board..."
        )

        deals = get_all_board_items(
            5030967822
        )

        print(
            f"Deals retrieved: "
            f"{len(deals['items'])}"
        )

        print(
            "\nTesting Work Orders board..."
        )

        work_orders = get_all_board_items(
            5030967820
        )

        print(
            f"Work Orders retrieved: "
            f"{len(work_orders['items'])}"
        )

        print(
            "\nMonday.com integration is working!"
        )

    except Exception as e:

        print(
            "\nERROR:"
        )

        print(
            str(e)
        )