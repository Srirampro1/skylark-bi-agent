import os
import requests


# ============================================================
# MONDAY.COM CONFIGURATION
# ============================================================

MONDAY_API_URL = "https://api.monday.com/v2"

DEALS_BOARD_ID = 5030967822
WORK_ORDERS_BOARD_ID = 5030967820


# ============================================================
# LOAD LOCAL ENVIRONMENT FILE
# ============================================================

def load_local_env():

    env_file = ".env"

    if not os.path.exists(env_file):
        return

    try:

        with open(
            env_file,
            "r",
            encoding="utf-8"
        ) as file:

            for line in file:

                line = line.strip()

                if not line:
                    continue

                if line.startswith("#"):
                    continue

                if "=" not in line:
                    continue

                key, value = line.split(
                    "=",
                    1
                )

                key = key.strip()
                value = value.strip()

                value = value.strip('"')
                value = value.strip("'")

                if key and value:

                    os.environ.setdefault(
                        key,
                        value
                    )

    except Exception:
        pass


load_local_env()


# ============================================================
# GET MONDAY API TOKEN
# ============================================================

def get_monday_token():

    # Streamlit Cloud
    try:

        import streamlit as st

        token = st.secrets.get(
            "MONDAY_API_TOKEN",
            None
        )

        if token:

            return str(token).strip()

    except Exception:
        pass

    # Local .env
    token = os.getenv(
        "MONDAY_API_TOKEN"
    )

    if token:

        return token.strip()

    return None


# ============================================================
# MONDAY API REQUEST
# ============================================================

def monday_request(
    query,
    variables=None
):

    token = get_monday_token()

    if not token:

        raise RuntimeError(
            "MONDAY_API_TOKEN is missing. "
            "Add it to Streamlit Secrets or .env."
        )

    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }

    payload = {
        "query": query,
        "variables": variables or {}
    }

    try:

        response = requests.post(
            MONDAY_API_URL,
            json=payload,
            headers=headers,
            timeout=60
        )

        response.raise_for_status()

    except requests.RequestException as e:

        raise RuntimeError(
            f"Could not connect to Monday.com: {e}"
        )

    try:

        result = response.json()

    except ValueError:

        raise RuntimeError(
            "Monday.com returned an invalid response."
        )

    if "errors" in result:

        messages = []

        for error in result["errors"]:

            messages.append(
                error.get(
                    "message",
                    "Unknown Monday.com error"
                )
            )

        raise RuntimeError(
            "Monday.com API error: "
            + " | ".join(messages)
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

    if cursor is None:

        query = """
        query (
            $board_id: ID!,
            $limit: Int!
        ) {

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

        boards = (
            result
            .get("data", {})
            .get("boards", [])
        )

        if not boards:

            raise RuntimeError(
                f"Monday.com board {board_id} "
                "could not be found."
            )

        return boards[0].get(
            "items_page",
            {}
        )

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

    return (
        result
        .get("data", {})
        .get("next_items_page", {})
    )


# ============================================================
# GET ALL BOARD ITEMS
# ============================================================

def get_all_board_items(
    board_id,
    page_size=100
):

    all_items = []

    cursor = None

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

        all_items.extend(items)

        print(
            f"Retrieved {len(items)} items "
            f"(total: {len(all_items)})"
        )

        cursor = page.get(
            "cursor"
        )

        if not cursor:
            break

    return {
        "items": all_items
    }


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

    user = (
        result
        .get("data", {})
        .get("me")
    )

    if not user:

        raise RuntimeError(
            "Monday.com authentication failed."
        )

    return user


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

    boards = (
        result
        .get("data", {})
        .get("boards", [])
    )

    if not boards:

        raise RuntimeError(
            f"Board {board_id} not found."
        )

    return boards[0]


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    print(
        "Testing Monday.com connection..."
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
            DEALS_BOARD_ID
        )

        print(
            "Deals:",
            len(deals["items"])
        )

        print(
            "\nTesting Work Orders board..."
        )

        work_orders = get_all_board_items(
            WORK_ORDERS_BOARD_ID
        )

        print(
            "Work Orders:",
            len(work_orders["items"])
        )

        print(
            "\nMonday.com integration working!"
        )

    except Exception as e:

        print(
            "\nERROR:"
        )

        print(str(e))
