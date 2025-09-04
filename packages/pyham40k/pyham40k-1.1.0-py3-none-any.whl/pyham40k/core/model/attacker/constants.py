ATTACKER_STAT_COL_WIDTH = 11

ATTACKER_STAT_HEADER = "|".join(
    map(
        lambda x: f"{x:^{ATTACKER_STAT_COL_WIDTH}}",
        "AHSPD"
    )
)
