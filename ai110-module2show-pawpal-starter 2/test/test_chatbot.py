
from pawpal_system import Owner, Pet

import chatbot


def create_owner_with_pet():
    """Create an owner with one pet for testing tool execution directly."""
    owner = Owner(name="Jordan", email="jordan@example.com")
    owner.add_pet(Pet(name="Mochi", species="Dog", age=3))
    return owner


def test_high_confidence_add_task_is_applied(tmp_path, monkeypatch):
    """A confident, well-formed request should add the task immediately."""
    owner = create_owner_with_pet()
    monkeypatch.setattr(chatbot, "save_tasks", lambda owner: None)

    result = chatbot._tool_add_task(owner, {
        "pet_name": "Mochi",
        "description": "Walk",
        "time": "08:00",
        "frequency": "Daily",
        "confidence": 95,
    })

    assert "Added task" in result
    assert len(owner.pets[0].tasks) == 1


def test_low_confidence_add_task_is_held_back(tmp_path, monkeypatch):
    """A low-confidence guess should not be written, and should ask for confirmation."""
    owner = create_owner_with_pet()
    monkeypatch.setattr(chatbot, "save_tasks", lambda owner: None)

    result = chatbot._tool_add_task(owner, {
        "pet_name": "Mochi",
        "description": "Walk",
        "time": "08:00",
        "frequency": "Daily",
        "confidence": 40,
    })

    assert "Confidence too low" in result
    assert len(owner.pets[0].tasks) == 0


def test_missing_confidence_defaults_to_zero_and_is_held_back(monkeypatch):
    """If the model omits confidence entirely, treat it as 0 (don't silently write)."""
    owner = create_owner_with_pet()
    monkeypatch.setattr(chatbot, "save_tasks", lambda owner: None)

    result = chatbot._tool_add_task(owner, {
        "pet_name": "Mochi",
        "description": "Walk",
        "time": "08:00",
        "frequency": "Daily",
    })

    assert "Confidence too low" in result
    assert len(owner.pets[0].tasks) == 0


def test_confidence_is_clamped_to_0_100():
    """Out-of-range or garbage confidence values should clamp instead of erroring."""
    assert chatbot._parse_confidence(150) == 100
    assert chatbot._parse_confidence(-20) == 0
    assert chatbot._parse_confidence("not a number") == 0
    assert chatbot._parse_confidence(None) == 0
