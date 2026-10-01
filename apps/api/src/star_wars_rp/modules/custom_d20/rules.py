def resolve_check(natural_roll: int, modifier: int, dc: int) -> tuple[int, bool]:
    if not 1 <= natural_roll <= 20:
        raise ValueError("natural_roll must be between 1 and 20")
    total = natural_roll + modifier
    return total, total >= dc
