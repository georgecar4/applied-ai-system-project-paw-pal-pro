
from datetime import date, timedelta

from pawpal_system import Owner, Pet, Task, Scheduler, save_tasks, load_tasks


def create_scheduler():
    """Create an owner, pet, and scheduler for testing."""
    owner = Owner(name="Jordan", email="jordan@example.com")
    pet = Pet(name="Mochi", species="Dog", age=3)
    owner.add_pet(pet)
    return owner, pet, Scheduler(owner)


def test_sorting_correctness():
    """Tasks should be ordered from earliest to latest."""
    owner, pet, scheduler = create_scheduler()

    pet.add_task(Task("Walk", "09:00", "Daily"))
    pet.add_task(Task("Breakfast", "07:00", "Daily"))
    pet.add_task(Task("Medication", "08:00", "Daily"))

    schedule = scheduler.get_schedule()

    times = [task.time for pet_name, task in schedule]

    assert times == ["07:00", "08:00", "09:00"]


def test_daily_task_recurrence():
    """Completing a daily task creates the next day's occurrence."""
    owner, pet, scheduler = create_scheduler()

    task = Task(
        description="Morning walk",
        time="08:00",
        frequency="Daily",
        due_date=date(2026, 10, 20)
    )
    pet.add_task(task)

    scheduler.mark_task_complete(task)

    assert task.completed is True
    assert len(pet.tasks) == 2

    new_task = pet.tasks[1]
    assert new_task.description == "Morning walk"
    assert new_task.due_date == date(2026, 10, 21)
    assert new_task.completed is False


def test_conflict_detection():
    """Two tasks at the same date and time should trigger a warning."""
    owner, pet, scheduler = create_scheduler()

    pet.add_task(Task("Walk", "08:00", "Daily"))
    pet.add_task(Task("Medication", "08:00", "Daily"))

    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1
    assert "Warning" in conflicts[0]


def test_filter_by_pet_name():
    """Filtering should return tasks for the selected pet only."""
    owner, pet, scheduler = create_scheduler()

    luna = Pet(name="Luna", species="Cat", age=2)
    owner.add_pet(luna)

    pet.add_task(Task("Walk", "08:00", "Daily"))
    luna.add_task(Task("Feed cat", "07:00", "Daily"))

    results = scheduler.filter_tasks(pet_name="Mochi")

    assert len(results) == 1
    assert results[0][0] == "Mochi"


def test_empty_schedule():
    """An owner with no tasks should have an empty schedule."""
    owner, pet, scheduler = create_scheduler()

    assert scheduler.get_schedule() == []
    assert scheduler.detect_conflicts() == []
    assert scheduler.get_pending_tasks() == []


def test_weekly_task_recurrence():
    """Completing a weekly task creates an occurrence 7 days later."""
    owner, pet, scheduler = create_scheduler()

    task = Task("Grooming", "10:00", "Weekly", due_date=date(2026, 10, 20))
    pet.add_task(task)

    scheduler.mark_task_complete(task)

    assert len(pet.tasks) == 2
    assert pet.tasks[1].due_date == date(2026, 10, 27)


def test_once_frequency_does_not_recur():
    """Completing a one-off task should not create a follow-up occurrence."""
    owner, pet, scheduler = create_scheduler()

    task = Task("Vet visit", "09:00", "Once", due_date=date(2026, 10, 20))
    pet.add_task(task)

    scheduler.mark_task_complete(task)

    assert task.completed is True
    assert len(pet.tasks) == 1


def test_completing_already_completed_task_is_noop():
    """Completing a task twice should not create duplicate follow-ups."""
    owner, pet, scheduler = create_scheduler()

    task = Task("Walk", "09:00", "Daily", due_date=date(2026, 10, 20))
    pet.add_task(task)

    scheduler.mark_task_complete(task)
    scheduler.mark_task_complete(task)

    assert len(pet.tasks) == 2


def test_frequency_is_case_insensitive():
    """'daily'/'weekly' in any case should still trigger recurrence."""
    owner, pet, scheduler = create_scheduler()

    task = Task("Walk", "09:00", "DAILY", due_date=date(2026, 10, 20))
    pet.add_task(task)

    scheduler.mark_task_complete(task)

    assert len(pet.tasks) == 2
    assert pet.tasks[1].due_date == date(2026, 10, 21)


def test_filter_by_completed_true():
    """Filtering for completed=True should exclude pending tasks."""
    owner, pet, scheduler = create_scheduler()

    done = Task("Walk", "08:00", "Daily", completed=True)
    pending = Task("Feed", "09:00", "Daily", completed=False)
    pet.add_task(done)
    pet.add_task(pending)

    results = scheduler.filter_tasks(completed=True)

    assert len(results) == 1
    assert results[0][1].description == "Walk"


def test_three_way_conflict_detection():
    """Three tasks at the same date/time should produce 3 pairwise warnings."""
    owner, pet, scheduler = create_scheduler()

    same_time = {"time": "08:00", "frequency": "Daily", "due_date": date(2026, 10, 20)}
    pet.add_task(Task("Walk", **same_time))
    pet.add_task(Task("Medication", **same_time))
    pet.add_task(Task("Feed", **same_time))

    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 3


def test_no_conflict_when_same_time_different_date():
    """Same time but different due dates should not be flagged as a conflict."""
    owner, pet, scheduler = create_scheduler()

    pet.add_task(Task("Walk", "08:00", "Daily", due_date=date(2026, 10, 20)))
    pet.add_task(Task("Medication", "08:00", "Daily", due_date=date(2026, 10, 21)))

    assert scheduler.detect_conflicts() == []


def test_save_and_load_roundtrip(tmp_path):
    """Saving then loading should reconstruct owner, pets (even taskless ones), and tasks."""
    owner, pet, scheduler = create_scheduler()
    pet.add_task(Task("Walk", "08:00", "Daily", due_date=date(2026, 10, 20)))

    empty_pet = Pet(name="Shadow", species="Cat", age=1)
    owner.add_pet(empty_pet)

    csv_path = tmp_path / "tasks.csv"
    save_tasks(owner, path=csv_path)
    reloaded = load_tasks(path=csv_path)

    assert reloaded.name == "Jordan"
    assert {p.name for p in reloaded.pets} == {"Mochi", "Shadow"}

    mochi = next(p for p in reloaded.pets if p.name == "Mochi")
    assert len(mochi.tasks) == 1
    assert mochi.tasks[0].due_date == date(2026, 10, 20)

    shadow = next(p for p in reloaded.pets if p.name == "Shadow")
    assert shadow.tasks == []


def test_load_tasks_missing_file_returns_none(tmp_path):
    """Loading from a path that doesn't exist should return None, not raise."""
    missing_path = tmp_path / "does_not_exist.csv"

    assert load_tasks(path=missing_path) is None


