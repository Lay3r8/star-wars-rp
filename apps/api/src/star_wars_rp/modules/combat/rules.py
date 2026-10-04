from star_wars_rp.modules.custom_d20.rules import resolve_check


def resolve_combat_attack(
    natural_roll: int,
    modifier: int,
    defence: int,
    fixed_damage: int,
) -> tuple[int, str, int]:
    total, hit = resolve_check(natural_roll, modifier, defence)
    return total, "HIT" if hit else "MISS", fixed_damage if hit else 0


def apply_fixed_damage(current: int, damage: int) -> int:
    return max(0, current - damage)


def advance_escape(progress: int, target: int) -> int:
    return min(target, progress + 1)
