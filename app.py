
import json
from pathlib import Path

import streamlit as st

from src.outsidein import generate_mission, save_observation

JOURNAL_FILE = Path(__file__).resolve().parent / "observations.json"

st.set_page_config(
    page_title="OutsideIn | Nature quests",
    page_icon="🌿",
    layout="centered",
)

st.title("OutsideIn")
st.subheader("A little AI. A little fresh air. A different perspective.")
st.write(
    "Get one small nature mission, step away from your screen, "
    "and record what you discover."
)

with st.form("quest_form"):
    environment = st.selectbox(
        "Where are you going?",
        ["Garden", "College campus", "Park", "Neighbourhood"],
    )
    minutes = st.select_slider(
        "How much time do you have?",
        options=[5, 10, 15, 20],
        value=10,
        format_func=lambda value: f"{value} minutes",
    )
    interest = st.selectbox(
        "What would you like to explore?",
        ["Biodiversity", "Plants", "Sounds", "Observation and mindfulness"],
    )
    submitted = st.form_submit_button("Generate my nature quest")

if submitted:
    with st.spinner("Preparing your nature quest..."):
        mission, source = generate_mission(environment, minutes, interest)
    st.session_state["mission"] = mission
    st.session_state["mission_source"] = source

if "mission" in st.session_state:
    mission = st.session_state["mission"]
    st.divider()
    st.caption(f"Quest source: {st.session_state['mission_source']}")
    st.header(mission["title"])
    st.write(f"**Duration:** {mission['duration_minutes']} minutes")
    st.write(mission["mission"])

    st.markdown("**Your steps**")
    for step in mission["steps"]:
        st.markdown(f"- {step}")

    st.info(f"Safety: {mission['safety_note']}")
    st.success("Your mission is ready. Put your phone away and explore.")

    with st.form("observation_form"):
        note = st.text_area(
            "What did you notice? Write this after your mission.",
            placeholder="I noticed...",
        )
        completed = st.form_submit_button("Save my observation")

    if completed:
        try:
            save_observation(mission, note, JOURNAL_FILE)
            st.success("Observation saved locally.")
        except ValueError as exc:
            st.warning(str(exc))

    if JOURNAL_FILE.exists():
        with st.expander("View your local nature journal"):
            try:
                records = json.loads(
                    JOURNAL_FILE.read_text(encoding="utf-8")
                )
                if isinstance(records, list):
                    for record in reversed(records):
                        st.markdown(f"**{record['mission_title']}**")
                        st.caption(record["completed_at"])
                        st.write(record["observation"])
                        st.divider()
            except (json.JSONDecodeError, OSError):
                st.warning("The journal could not be read.")
