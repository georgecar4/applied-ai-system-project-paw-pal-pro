
import csv
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path


@dataclass
class Task:
    """Represent a pet-care task and when it is due."""

    description: str
    time: str
    frequency: str
    completed: bool = False
    due_date: date = field(default_factory=date.today)

    def mark_complete(self):
        """Mark this task as completed."""
        self.completed = True


@dataclass
class Pet:
    """Store a pet's information and care tasks."""

    name: str
    species: str
    age: int
    tasks: list = field(default_factory=list)

    def add_task(self, task):
        """Add a care task to this pet."""
        self.tasks.append(task)


@dataclass
class Owner:
    """Store an owner's information and pets."""

    name: str
    email: str
    pets: list = field(default_factory=list)

    def add_pet(self, pet):
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_all_tasks(self):
        """Return all tasks paired with the pet they belong to."""
        all_tasks = []

        for pet in self.pets:
            for task in pet.tasks:
                all_tasks.append((pet.name, task))

        return all_tasks


class Scheduler:
    """Sort, filter, repeat, and check pet-care tasks."""

    def __init__(self, owner):
        self.owner = owner

    def sort_by_time(self, tasks=None):
        """Sort tasks by due date and then by time."""
        if tasks is None:
            tasks = self.owner.get_all_tasks()

        return sorted(
            tasks,
            key=lambda item: (item[1].due_date, item[1].time)
        )

    def get_schedule(self):
        """Return all tasks in chronological order."""
        return self.sort_by_time()

    def filter_tasks(self, pet_name=None, completed=None):
        """Filter tasks by pet name, completion status, or both."""
        tasks = self.owner.get_all_tasks()

        if pet_name is not None:
            tasks = [
                (name, task)
                for name, task in tasks
                if name.lower() == pet_name.lower()
            ]

        if completed is not None:
            tasks = [
                (name, task)
                for name, task in tasks
                if task.completed == completed
            ]

        return self.sort_by_time(tasks)

    def get_pending_tasks(self):
        """Return tasks that have not been completed."""
        return self.filter_tasks(completed=False)

    def mark_task_complete(self, task):
        """Complete a task and create its next daily or weekly occurrence."""
        if task.completed:
            return

        task.mark_complete()

        if task.frequency.lower() == "daily":
            next_date = task.due_date + timedelta(days=1)
        elif task.frequency.lower() == "weekly":
            next_date = task.due_date + timedelta(weeks=1)
        else:
            return

        # Find the pet that owns this task.
        for pet in self.owner.pets:
            if task in pet.tasks:
                next_task = Task(
                    description=task.description,
                    time=task.time,
                    frequency=task.frequency,
                    completed=False,
                    due_date=next_date
                )
                pet.add_task(next_task)
                break

    def detect_conflicts(self):
        """Return warnings for tasks sharing the same date and time."""
        tasks = self.sort_by_time()
        conflicts = []

        for i in range(len(tasks)):
            pet1, task1 = tasks[i]

            for j in range(i + 1, len(tasks)):
                pet2, task2 = tasks[j]

                if (
                    task1.due_date == task2.due_date
                    and task1.time == task2.time
                ):
                    conflicts.append(
                        f"Warning: {pet1}'s '{task1.description}' and "
                        f"{pet2}'s '{task2.description}' are both scheduled "
                        f"for {task1.due_date} at {task1.time}."
                    )

        return conflicts


TASKS_CSV_PATH = Path(__file__).parent / "tasks.csv"

CSV_FIELDS = [
    "owner_name", "owner_email", "pet_name", "species", "age",
    "description", "time", "frequency", "completed", "due_date",
]


def save_tasks(owner, path=TASKS_CSV_PATH):
    """Write every pet and task for this owner to a CSV file."""
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()

        for pet in owner.pets:
            # Keep pets with no tasks yet so they aren't lost on reload.
            if not pet.tasks:
                writer.writerow({
                    "owner_name": owner.name,
                    "owner_email": owner.email,
                    "pet_name": pet.name,
                    "species": pet.species,
                    "age": pet.age,
                    "description": "",
                    "time": "",
                    "frequency": "",
                    "completed": "",
                    "due_date": "",
                })
                continue

            for task in pet.tasks:
                writer.writerow({
                    "owner_name": owner.name,
                    "owner_email": owner.email,
                    "pet_name": pet.name,
                    "species": pet.species,
                    "age": pet.age,
                    "description": task.description,
                    "time": task.time,
                    "frequency": task.frequency,
                    "completed": task.completed,
                    "due_date": task.due_date.isoformat(),
                })


def load_tasks(path=TASKS_CSV_PATH):
    """Rebuild an Owner (with pets and tasks) from a CSV file, or None if it doesn't exist."""
    path = Path(path)
    if not path.exists():
        return None

    owner = None
    pets_by_name = {}

    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            if owner is None:
                owner = Owner(name=row["owner_name"], email=row["owner_email"])

            pet = pets_by_name.get(row["pet_name"])
            if pet is None:
                pet = Pet(
                    name=row["pet_name"],
                    species=row["species"],
                    age=int(row["age"]),
                )
                pets_by_name[row["pet_name"]] = pet
                owner.add_pet(pet)

            if row["description"]:
                pet.add_task(Task(
                    description=row["description"],
                    time=row["time"],
                    frequency=row["frequency"],
                    completed=row["completed"] == "True",
                    due_date=date.fromisoformat(row["due_date"]),
                ))

    return owner
