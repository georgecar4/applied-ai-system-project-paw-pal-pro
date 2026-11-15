
import html
from datetime import date, timedelta

import streamlit as st
from pawpal_system import save_tasks
from state import init_state, set_background

# Categorical palette (validated for colorblind-safety), one hue per pet.
PALETTE_LIGHT = [
    "#2a78d6", "#eb6834", "#1baf7a", "#eda100",
    "#e87ba4", "#008300", "#6250d6", "#e34948",
]
PALETTE_DARK = [
    "#3987e5", "#d95926", "#199e70", "#c98500",
    "#d55181", "#0ca30c", "#9085e9", "#e66767",
]
# Label text stays white on every fill except the yellow slot (index 3).
TEXT_ON_FILL = ["#fff", "#fff", "#fff", "#0b0b0b", "#fff", "#fff", "#fff", "#fff"]

# Fallback hour range for a week with no scheduled tasks at all.
DEFAULT_START_HOUR = 7
DEFAULT_END_HOUR = 20


def _week_start(day):
    """Return the Monday on or before `day`."""
    return day - timedelta(days=day.weekday())


def _format_week_range(start, end):
    """Format a Monday-Sunday span, e.g. 'Nov 9 - 15, 2026' or 'Nov 30 - Dec 6, 2026'."""
    if start.month != end.month:
        return f"{start.strftime('%b')} {start.day} - {end.strftime('%b')} {end.day}, {end.year}"
    return f"{start.strftime('%b')} {start.day} - {end.day}, {end.year}"


def _format_hour(hour):
    """Format an hour (0-23) as a 12-hour label, e.g. '1 PM'."""
    period = "AM" if hour < 12 else "PM"
    display_hour = hour % 12
    if display_hour == 0:
        display_hour = 12
    return f"{display_hour} {period}"


def render_calendar(tasks_with_pets, pet_colors, show_pet_name, week_days):
    """Render a full 7-day week as a Google Calendar-style grid: days across the top, hours down the side."""
    week_day_set = set(week_days)
    parsed = []
    for pet_name, task in tasks_with_pets:
        if task.due_date not in week_day_set:
            continue
        try:
            hour, minute = (int(part) for part in task.time.split(":"))
        except ValueError:
            continue
        parsed.append((pet_name, task, hour, minute))

    days = week_days

    if parsed:
        hours_used = [hour for _, _, hour, _ in parsed]
        start_hour = max(0, min(hours_used) - 1)
        end_hour = min(23, max(hours_used) + 1)
    else:
        start_hour = DEFAULT_START_HOUR
        end_hour = DEFAULT_END_HOUR
    rows_hours = list(range(start_hour, end_hour + 1))

    cells = {}
    for pet_name, task, hour, minute in parsed:
        cells.setdefault((task.due_date, hour), []).append((pet_name, task, minute))
    for bucket in cells.values():
        bucket.sort(key=lambda item: item[2])

    today = date.today()
    n_days = len(days)

    style_rules = []
    for index in range(len(PALETTE_LIGHT)):
        style_rules.append(
            f".ps-pet-{index} {{ background:{PALETTE_LIGHT[index]}; color:{TEXT_ON_FILL[index]}; }}"
        )
    dark_rules = []
    for index in range(len(PALETTE_DARK)):
        dark_rules.append(
            f".ps-pet-{index} {{ background:{PALETTE_DARK[index]}; color:{TEXT_ON_FILL[index]}; }}"
        )

    css = f"""
<style>
.ps-cal-wrap {{
  overflow-x: auto;
  border: 1px solid #e1e0d9;
  border-radius: 8px;
  margin-top: 0.5rem;
}}
.ps-cal {{
  display: grid;
  grid-template-columns: 64px repeat({n_days}, minmax(140px, 1fr));
  grid-auto-rows: minmax(48px, auto);
  background: #fcfcfb;
  color: #0b0b0b;
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  min-width: {64 + n_days * 140}px;
}}
.ps-cal-corner, .ps-cal-head, .ps-cal-time {{
  background: #fcfcfb;
  border-bottom: 1px solid #e1e0d9;
  border-right: 1px solid #e1e0d9;
}}
.ps-cal-corner {{ position: sticky; top: 0; left: 0; z-index: 3; }}
.ps-cal-head {{
  position: sticky; top: 0; z-index: 2;
  padding: 8px 6px; text-align: center; font-weight: 600; font-size: 13px;
}}
.ps-cal-head.today {{ color: #2a78d6; }}
.ps-cal-time {{
  position: sticky; left: 0; z-index: 1;
  padding: 4px 6px; font-size: 11px; color: #898781; text-align: right;
  white-space: nowrap;
}}
.ps-cal-cell {{
  border-right: 1px solid #e1e0d9; border-bottom: 1px solid #e1e0d9;
  padding: 3px; display: flex; flex-direction: column; gap: 3px;
}}
.ps-cal-cell.today {{ background: rgba(42, 120, 214, 0.06); }}
.ps-chip {{
  border-radius: 6px; padding: 3px 6px; font-size: 11.5px; line-height: 1.3;
  overflow: hidden;
}}
.ps-chip.done {{ opacity: 0.55; text-decoration: line-through; }}
{chr(10).join(style_rules)}
@media (prefers-color-scheme: dark) {{
  .ps-cal {{ background: #1a1a19; color: #f0efec; }}
  .ps-cal-corner, .ps-cal-head, .ps-cal-time {{
    background: #1a1a19; border-color: #2c2c2a;
  }}
  .ps-cal-cell {{ border-color: #2c2c2a; }}
  .ps-cal-head {{ color: #f0efec; }}
  .ps-cal-head.today {{ color: #3987e5; }}
  .ps-cal-time {{ color: #c3c2b7; }}
  .ps-cal-cell.today {{ background: rgba(57, 135, 229, 0.08); }}
  {chr(10).join(dark_rules)}
}}
</style>
"""

    parts = [css, '<div class="ps-cal-wrap"><div class="ps-cal">', '<div class="ps-cal-corner"></div>']

    for day in days:
        head_cls = "ps-cal-head today" if day == today else "ps-cal-head"
        label = f"{day.strftime('%a')} {day.month}/{day.day}"
        parts.append(f'<div class="{head_cls}">{html.escape(label)}</div>')

    for hour in rows_hours:
        parts.append(f'<div class="ps-cal-time">{_format_hour(hour)}</div>')
        for day in days:
            cell_cls = "ps-cal-cell today" if day == today else "ps-cal-cell"
            chips = []
            for pet_name, task, minute in cells.get((day, hour), []):
                color_index = pet_colors.get(pet_name, 0)
                done_cls = " done" if task.completed else ""
                prefix = f"{html.escape(pet_name)} — " if show_pet_name else ""
                chips.append(
                    f'<div class="ps-chip ps-pet-{color_index}{done_cls}">'
                    f"<b>{hour:02d}:{minute:02d}</b> {prefix}{html.escape(task.description)}"
                    f"</div>"
                )
            parts.append(f'<div class="{cell_cls}">{"".join(chips)}</div>')

    parts.append("</div></div>")
    st.markdown("".join(parts), unsafe_allow_html=True)


st.set_page_config(
    page_title="Smart Schedule - PawPal+",
    page_icon="🐾",
    layout="centered"
)

init_state()
set_background("paw_prints.png", tile=True)

st.title("🐾 Smart Schedule")

# Choose which tasks to display.
all_tasks = st.session_state.owner.get_all_tasks()
pet_names = sorted({pet_name for pet_name, task in all_tasks})

selected_pet = st.selectbox(
    "Filter by pet",
    ["All pets"] + pet_names
)

selected_status = st.selectbox(
    "Filter by status",
    ["All tasks", "Pending", "Completed"]
)

if selected_pet == "All pets":
    filtered_tasks = st.session_state.scheduler.get_schedule()
else:
    filtered_tasks = st.session_state.scheduler.filter_tasks(
        pet_name=selected_pet
    )

if selected_status == "Pending":
    filtered_tasks = [
        (pet_name, task)
        for pet_name, task in filtered_tasks
        if not task.completed
    ]
elif selected_status == "Completed":
    filtered_tasks = [
        (pet_name, task)
        for pet_name, task in filtered_tasks
        if task.completed
    ]

pet_colors = {name: index % len(PALETTE_LIGHT) for index, name in enumerate(pet_names)}

# Week navigation: default to the week of the earliest scheduled task, or this week.
if "calendar_week_start" not in st.session_state:
    anchor = min(
        (task.due_date for _, task in filtered_tasks),
        default=date.today(),
    )
    st.session_state.calendar_week_start = _week_start(anchor)

nav_prev, nav_label, nav_today, nav_next = st.columns([1.2, 2.4, 1, 1.2])

with nav_prev:
    if st.button("← Previous week", use_container_width=True):
        st.session_state.calendar_week_start -= timedelta(days=7)

with nav_today:
    if st.button("Today", use_container_width=True):
        st.session_state.calendar_week_start = _week_start(date.today())

with nav_next:
    if st.button("Next week →", use_container_width=True):
        st.session_state.calendar_week_start += timedelta(days=7)

week_start = st.session_state.calendar_week_start
week_days = [week_start + timedelta(days=i) for i in range(7)]

with nav_label:
    st.markdown(
        f"<div style='text-align:center;font-weight:600;padding-top:0.4rem;'>"
        f"{_format_week_range(week_start, week_days[-1])}</div>",
        unsafe_allow_html=True,
    )

if selected_pet == "All pets" and len(pet_names) > 1:
    legend_items = "".join(
        f'<span style="display:inline-flex;align-items:center;gap:4px;margin-right:12px;">'
        f'<span style="width:10px;height:10px;border-radius:3px;background:{PALETTE_LIGHT[pet_colors[name]]};'
        f'display:inline-block;"></span>{html.escape(name)}</span>'
        for name in pet_names
    )
    st.markdown(legend_items, unsafe_allow_html=True)

render_calendar(
    filtered_tasks,
    pet_colors,
    show_pet_name=(selected_pet == "All pets"),
    week_days=week_days,
)

if filtered_tasks:
    with st.expander("View as list"):
        schedule_rows = [
            {
                "Date": str(task.due_date),
                "Time": task.time,
                "Pet": pet_name,
                "Task": task.description,
                "Frequency": task.frequency,
                "Status": "Completed" if task.completed else "Pending",
            }
            for pet_name, task in filtered_tasks
        ]
        st.table(schedule_rows)
else:
    st.info("No tasks match these filters.")

# Check the full schedule for conflicts, regardless of the filters.
st.subheader("Schedule Conflict Check")
conflicts = st.session_state.scheduler.detect_conflicts()

if conflicts:
    for warning in conflicts:
        st.warning(warning)
else:
    st.success("No scheduling conflicts detected.")

# Allow the user to complete a pending task.
pending_tasks = [
    (pet_name, task)
    for pet_name, task in st.session_state.scheduler.get_pending_tasks()
]

if pending_tasks:
    st.subheader("Complete a Task")

    task_options = {
        f"{pet_name} — {task.description} ({task.due_date} {task.time})":
        (pet_name, task)
        for pet_name, task in pending_tasks
    }

    chosen_task_label = st.selectbox(
        "Choose a task to mark complete",
        list(task_options.keys())
    )

    if st.button("Mark Task Complete"):
        pet_name, chosen_task = task_options[chosen_task_label]
        st.session_state.scheduler.mark_task_complete(chosen_task)
        save_tasks(st.session_state.owner)
        st.success(f"Marked '{chosen_task.description}' for {pet_name} as complete.")

        if chosen_task.frequency.lower() in ("daily", "weekly"):
            st.info(
                "The next occurrence has been added to the schedule. "
                "The schedule will refresh when you rerun the app."
            )

        st.rerun()
