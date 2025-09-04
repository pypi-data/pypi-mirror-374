from typing import Iterator

COLOR_CODES = {
    'WHITE': 'ÿc0',
    'RED': 'ÿc1',
    'LIGHTGREEN': 'ÿc2',
    'BLUE': 'ÿc3',
    'GOLD': 'ÿc4',
    'GRAY': 'ÿc5',
    'BLACK': 'ÿc6',
    'LIGHTGOLD': 'ÿc7',
    'ORANGE': 'ÿc8',
    'YELLOW': 'ÿc9',
    'PURPLE': 'ÿc;'
}


def split_text(text: str, sep: str) -> list[str]:
    left, found, right = text.partition(sep)
    return [left.strip(), right.strip()] if found else [left.strip()]


def filter_irrelevant_lines(lines: list[str]) -> Iterator[str]:
    for raw in lines:
        line = raw.strip()
        if line and not line.startswith('#'):
            yield line
