DEFENDER_STAT_COL_WIDTH = 11

DEFENDER_STAT_HEADER = "|".join(
    map(
        lambda x: f"{x:^{DEFENDER_STAT_COL_WIDTH}}",
        "TSIF"
    )
)
