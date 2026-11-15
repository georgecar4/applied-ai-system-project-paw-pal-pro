
import json
import os

import requests

from pawpal_system import Task, save_tasks

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3.5:4b")

SYSTEM_PROMPT = """
You are the PawPal+ chat assistant: a pet-care scheduling helper with a VERY happy,
bubbly, enthusiastic personality. Always respond with warmth, exclamation points, and
pet-themed emojis (such as 🐾🎉💖✨🐶🐱) — like a delighted puppy helping its favorite human!

You help the owner manage pet care tasks using the tools provided:
- add_task: create a new task for a pet
- list_tasks: look up tasks, optionally filtered by pet name and/or completion status
- list_pets: list the owner's pets
- check_conflicts: check whether any tasks are scheduled for the same date and time

Always use a tool when the user wants a task created or wants information looked up —
never invent task details or guess what's on the schedule. If the pet name, time, or
frequency needed for add_task is missing or unclear, ask a short clarifying question
(still in your bubbly voice) instead of guessing. Frequency must be exactly one of:
"Once", "Daily", "Twice daily", "Weekly". Time must be 24-hour "HH:MM" format.

When calling add_task, you must also pass "confidence": your own honest 0-100 rating
of how sure you are that you've correctly understood the pet, task, time, and
frequency from the user's message. Lower it when the user was vague, used a nickname
or typo'd pet name, left out details you had to infer, or the message was ambiguous.
If your confidence would be below 70, don't call add_task at all — ask a clarifying
question instead.
""".strip()

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new pet-care task for a specific pet.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pet_name": {
                        "type": "string",
                        "description": "The exact name of the pet this task is for.",
                    },
                    "description": {
                        "type": "string",
                        "description": "What the task is, e.g. 'Walk' or 'Give medication'.",
                    },
                    "time": {
                        "type": "string",
                        "description": "Time of day in 24-hour HH:MM format, e.g. '08:00'.",
                    },
                    "frequency": {
                        "type": "string",
                        "enum": ["Once", "Daily", "Twice daily", "Weekly"],
                        "description": "How often the task repeats.",
                    },
                    "confidence": {
                        "type": "integer",
                        "description": (
                            "0-100: how sure you are that you've correctly understood "
                            "which pet, task, time, and frequency the user wants. Lower "
                            "this if you had to guess, guessed a nickname, or the "
                            "request was ambiguous."
                        ),
                    },
                },
                "required": ["pet_name", "description", "time", "frequency", "confidence"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "Look up scheduled tasks, optionally filtered by pet name and/or completion status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pet_name": {
                        "type": "string",
                        "description": "Only show tasks for this pet. Omit to include every pet.",
                    },
                    "completed": {
                        "type": "boolean",
                        "description": "true for completed tasks only, false for pending only. Omit for all tasks.",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_pets",
            "description": "List the owner's pets and how many tasks each has.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_conflicts",
            "description": "Check whether any tasks are scheduled for the same date and time.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]

MAX_TOOL_ITERATIONS = 6
CONFIDENCE_THRESHOLD = 70


def get_response(owner, scheduler, history, user_message):
    """Send the user's message (plus prior turns) to Ollama and return its bubbly reply.

    `history` is the list of {"role", "content"} turns before this message; tool calls
    the model makes along the way (like adding a task) are executed against `owner`/`scheduler`.
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += [{"role": turn["role"], "content": turn["content"]} for turn in history]
    messages.append({"role": "user", "content": user_message})

    try:
        message = {}
        for _ in range(MAX_TOOL_ITERATIONS):
            message = _chat(messages)
            tool_calls = message.get("tool_calls")

            if not tool_calls:
                return message.get("content") or "All done! 🎉🐾"

            messages.append(message)

            for call in tool_calls:
                function = call.get("function", {})
                result = _execute_tool(owner, scheduler, function.get("name"), _parse_arguments(function))
                messages.append({"role": "tool", "content": result})
        else:
            return "Whew, that got a little tangled! 🐾 Could you try asking again, maybe a bit more simply? 💕"

    except requests.exceptions.ConnectionError:
        return _connection_error_message()
    except requests.exceptions.Timeout:
        return "Hmm, that's taking a while! 🐾 Ollama might be busy loading the model — try again in a moment! 💕"
    except requests.exceptions.HTTPError as e:
        if e.response is not None and e.response.status_code == 404:
            return (
                f"Oops, I can't find model '{OLLAMA_MODEL}' on your Ollama server! 🐾 "
                f"Try `ollama pull {OLLAMA_MODEL}` or set the OLLAMA_MODEL environment "
                f"variable to a model you already have. ✨"
            )
        return f"Oh no, Ollama had trouble with that! 😿 ({e})"


def _chat(messages):
    response = requests.post(
        f"{OLLAMA_HOST}/api/chat",
        json={
            "model": OLLAMA_MODEL,
            "messages": messages,
            "tools": TOOLS,
            "stream": False,
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["message"]


def _parse_arguments(function):
    arguments = function.get("arguments") or {}
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except json.JSONDecodeError:
            arguments = {}
    return arguments


def _connection_error_message():
    return (
        f"Oops, I can't reach Ollama at {OLLAMA_HOST}! 🐾💤 Make sure Ollama is installed and "
        f"running (`ollama serve`), and that you've pulled model '{OLLAMA_MODEL}' "
        f"(try `ollama pull {OLLAMA_MODEL}`). Then I'll be back to my bubbly self! ✨"
    )


def _execute_tool(owner, scheduler, name, arguments):
    if name == "add_task":
        return _tool_add_task(owner, arguments)
    if name == "list_tasks":
        return _tool_list_tasks(scheduler, arguments)
    if name == "list_pets":
        return _tool_list_pets(owner)
    if name == "check_conflicts":
        return _tool_check_conflicts(scheduler)
    return f"Unknown tool: {name}"


def _tool_add_task(owner, arguments):
    pet_name = arguments.get("pet_name")
    description = arguments.get("description")
    time_str = arguments.get("time")
    frequency = arguments.get("frequency")
    confidence = _parse_confidence(arguments.get("confidence"))

    missing = [
        field_name
        for field_name, value in [
            ("pet_name", pet_name),
            ("description", description),
            ("time", time_str),
            ("frequency", frequency),
        ]
        if not value
    ]
    if missing:
        return f"Missing required field(s): {', '.join(missing)}."

    if frequency not in ("Once", "Daily", "Twice daily", "Weekly"):
        return "Invalid frequency. Must be one of: Once, Daily, Twice daily, Weekly."

    pet = next((p for p in owner.pets if p.name.lower() == pet_name.lower()), None)
    if pet is None:
        names = ", ".join(p.name for p in owner.pets) or "none yet"
        return f"No pet named '{pet_name}' found. Available pets: {names}."

    if confidence < CONFIDENCE_THRESHOLD:
        return (
            f"Confidence too low ({confidence}%) to add this task automatically. "
            f"Ask the user to confirm: '{description}' for {pet.name} at {time_str} "
            f"({frequency}). Only call add_task again once they've confirmed or "
            f"corrected the details."
        )

    task = Task(description=description, time=time_str, frequency=frequency)
    pet.add_task(task)
    save_tasks(owner)

    return (
        f"Added task '{task.description}' for {pet.name} at {task.time} "
        f"({task.frequency}), due {task.due_date}. (confidence: {confidence}%)"
    )


def _parse_confidence(raw_confidence):
    try:
        confidence = int(raw_confidence)
    except (TypeError, ValueError):
        return 0
    return max(0, min(100, confidence))


def _tool_list_tasks(scheduler, arguments):
    tasks = scheduler.filter_tasks(
        pet_name=arguments.get("pet_name"),
        completed=arguments.get("completed"),
    )

    if not tasks:
        return "No matching tasks found."

    return "\n".join(
        f"{pet_name}: {task.description} at {task.time} on {task.due_date} "
        f"({task.frequency}, {'completed' if task.completed else 'pending'})"
        for pet_name, task in tasks
    )


def _tool_list_pets(owner):
    if not owner.pets:
        return "The owner has no pets yet."

    return "\n".join(
        f"{pet.name} ({pet.species}, age {pet.age}): {len(pet.tasks)} task(s)"
        for pet in owner.pets
    )


def _tool_check_conflicts(scheduler):
    conflicts = scheduler.detect_conflicts()
    return "\n".join(conflicts) if conflicts else "No scheduling conflicts found."
