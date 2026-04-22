SLOT_IDS = (1, 2, 3)

SLOT_LABELS = {
    1: "Fach 1",
    2: "Fach 2",
    3: "Fach 3",
}


def get_slot_label(slot_id: int) -> str:
    return SLOT_LABELS.get(slot_id, f"Fach {slot_id}")