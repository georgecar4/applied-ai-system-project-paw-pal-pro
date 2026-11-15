
from pawpal_system import Owner, Pet, Task, Scheduler


# 1. Create an owner.
owner = Owner(name="Alex", email="alex@example.com")

# 2. Create two pets.
dog = Pet(name="Buddy", species="Dog", age=3)
cat = Pet(name="Luna", species="Cat", age=2)

# 3. Give each pet some tasks.
dog.add_task(Task(
    description="Morning walk",
    time="08:00",
    frequency="Daily"
))

dog.add_task(Task(
    description="Feed Buddy",
    time="07:00",
    frequency="Twice daily"
))

cat.add_task(Task(
    description="Feed Luna",
    time="07:30",
    frequency="Twice daily"
))

# 4. Add the pets to the owner.
owner.add_pet(dog)
owner.add_pet(cat)

# 5. Create the scheduler.
scheduler = Scheduler(owner)

# 6. Print the schedule in time order.
print("Today's Schedule")
print("=" * 55)

for pet_name, task in scheduler.get_schedule():
    status = "Completed" if task.completed else "Pending"

    print(
        f"{task.time} | {pet_name} | {task.description} "
        f"| {task.frequency} | {status}"
    )
