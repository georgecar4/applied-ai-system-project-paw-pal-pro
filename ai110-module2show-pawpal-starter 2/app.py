
import streamlit as st
from datetime import time
from pawpal_system import Pet, Task, save_tasks
from state import init_state, set_background

st.set_page_config(
    page_title="PawPal+",
    page_icon="🐾",
    layout="centered"
)

init_state()
set_background("paw_prints.png", tile=True)

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to PawPal+.
"""
)

st.divider()


st.subheader("Pet Care Manager")

owner_name = st.text_input(
    "Owner name",
    value=st.session_state.owner.name
)

owner_email = st.text_input(
    "Owner email",
    value=st.session_state.owner.email
)

if st.button("Update owner"):
    st.session_state.owner.name = owner_name
    st.session_state.owner.email = owner_email
    save_tasks(st.session_state.owner)
    st.success("Owner information updated!")

st.markdown("### Add a Pet")

with st.form("add_pet_form"):
    pet_name = st.text_input("Pet name")
    species = st.selectbox(
        "Species",
        ["dog", "cat", "other"]
    )
    age = st.number_input(
        "Age",
        min_value=0,
        max_value=100,
        value=1,
        step=1
    )

    add_pet = st.form_submit_button("Add pet")

    if add_pet:
        if not pet_name.strip():
            st.error("Please enter a pet name.")
        else:
            pet = Pet(
                name=pet_name.strip(),
                species=species,
                age=int(age)
            )

            st.session_state.owner.add_pet(pet)
            save_tasks(st.session_state.owner)
            st.success(f"{pet.name} was added!")


st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")


st.markdown("### Tasks")

pets = st.session_state.owner.pets

if pets:
    with st.form("add_task_form"):
        selected_pet_name = st.selectbox(
            "Choose a pet",
            [pet.name for pet in pets]
        )

        task_title = st.text_input("Task title")

        task_time = st.time_input(
            "Task time",
            value=time(8, 0)
        )

        frequency = st.selectbox(
            "Frequency",
            ["Once", "Daily", "Twice daily", "Weekly"]
        )

        add_task = st.form_submit_button("Add task")

        if add_task:
            if not task_title.strip():
                st.error("Please enter a task title.")
            else:
                selected_pet = next(
                    pet for pet in pets
                    if pet.name == selected_pet_name
                )

                task = Task(
                    description=task_title.strip(),
                    time=task_time.strftime("%H:%M"),
                    frequency=frequency
                )

                selected_pet.add_task(task)
                save_tasks(st.session_state.owner)
                st.success(
                    f"Task added for {selected_pet.name}!"
                )
else:
    st.info("Add a pet before creating tasks.")

st.markdown("### Your Pets")

for pet in st.session_state.owner.pets:
    st.write(f"**{pet.name}** — {pet.species}, age {pet.age}")
    st.write(f"Tasks: {len(pet.tasks)}")

    

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")

st.info("Head to the **Smart Schedule** page in the sidebar to view, filter, and complete tasks.")


