import about_time


def human_throughput(value: float, unit: str = "", prec: int | None = None) -> str:
    throughput: about_time.HumanThroughput = about_time.HumanThroughput(value, unit)
    return throughput.as_human(prec)
