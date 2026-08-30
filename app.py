import streamlit as st
from agent import load_data, answer_question


# ------------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------------

st.set_page_config(
    page_title="Skylark Drones BI Agent",
    page_icon="📊",
    layout="wide"
)


# ------------------------------------------------
# TITLE
# ------------------------------------------------

st.title("📊 Skylark Drones BI Agent")

st.write(
    "Ask business questions about Deals and Work Orders "
    "stored in Monday.com."
)


# ------------------------------------------------
# LOAD DATA
# ------------------------------------------------

@st.cache_data(ttl=300)
def get_data():

    work_orders, deals = load_data()

    return work_orders, deals


# ------------------------------------------------
# LOAD DATA WITH ERROR HANDLING
# ------------------------------------------------

try:

    work_orders, deals = get_data()

except Exception as e:

    st.error(
        "Unable to retrieve data from Monday.com."
    )

    st.code(str(e))

    st.stop()


# ------------------------------------------------
# SIDEBAR
# ------------------------------------------------

st.sidebar.header("Data Overview")

st.sidebar.metric(
    "Deals",
    len(deals)
)

st.sidebar.metric(
    "Work Orders",
    len(work_orders)
)

st.sidebar.markdown("---")

st.sidebar.write(
    "Data source: Monday.com"
)

st.sidebar.write(
    "The agent retrieves live board data "
    "through the Monday.com API."
)


# ------------------------------------------------
# EXAMPLE QUESTIONS
# ------------------------------------------------

st.subheader("Try asking")

examples = [
    "How is our pipeline looking?",
    "How is our energy pipeline?",
    "How much is receivable?",
    "What is the work order status?",
    "Give me a leadership update"
]

for example in examples:

    if st.button(example):

        st.session_state["question"] = example


# ------------------------------------------------
# QUESTION INPUT
# ------------------------------------------------

question = st.text_input(
    "Ask a business question:",
    value=st.session_state.get(
        "question",
        ""
    ),
    placeholder=(
        "Example: How is our energy pipeline?"
    )
)


# ------------------------------------------------
# ASK BUTTON
# ------------------------------------------------

if st.button(
    "Ask Agent",
    type="primary"
):

    if not question.strip():

        st.warning(
            "Please enter a business question."
        )

    else:

        with st.spinner(
            "Analyzing Monday.com data..."
        ):

            try:

                answer = answer_question(
                    question,
                    deals,
                    work_orders
                )

                st.subheader(
                    "Business Intelligence Answer"
                )

                st.write(answer)

            except Exception as e:

                st.error(
                    "Something went wrong while "
                    "processing your question."
                )

                st.code(str(e))