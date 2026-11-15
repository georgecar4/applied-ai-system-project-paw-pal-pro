
import base64
from pathlib import Path

import streamlit as st
from pawpal_system import Owner, Scheduler, load_tasks

ASSETS_DIR = Path(__file__).resolve().parent


def init_state():
    """Ensure owner/scheduler/tasks exist in session state, loading saved tasks if present."""
    if "owner" not in st.session_state:
        st.session_state.owner = load_tasks() or Owner(
            name="PawPal User",
            email="user@example.com"
        )

    if "scheduler" not in st.session_state:
        st.session_state.scheduler = Scheduler(
            st.session_state.owner
        )

    if "tasks" not in st.session_state:
        st.session_state.tasks = []


@st.cache_data
def _encode_image(image_name):
    return base64.b64encode((ASSETS_DIR / image_name).read_bytes()).decode()


def set_background(image_name, tile=False):
    """Put an image behind the page, tinted (light or dark) so text stays readable.

    `tile` repeats a small pattern (e.g. paw prints) instead of covering the
    viewport with one scaled photo.
    """
    encoded = _encode_image(image_name)

    if tile:
        placement = "background-size: 220px; background-repeat: repeat;"
    else:
        placement = "background-size: cover; background-repeat: no-repeat; background-position: center top;"

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image:
                linear-gradient(rgba(255, 255, 255, 0.88), rgba(255, 255, 255, 0.88)),
                url("data:image/png;base64,{encoded}");
            {placement}
            background-attachment: fixed;
        }}

        [data-testid="stChatMessage"],
        [data-testid="stChatInput"] textarea {{
            background-color: rgba(255, 255, 255, 0.92);
        }}

        @media (prefers-color-scheme: dark) {{
            .stApp {{
                background-image:
                    linear-gradient(rgba(14, 17, 23, 0.88), rgba(14, 17, 23, 0.88)),
                    url("data:image/png;base64,{encoded}");
            }}

            [data-testid="stChatMessage"],
            [data-testid="stChatInput"] textarea {{
                background-color: rgba(38, 39, 48, 0.92);
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
