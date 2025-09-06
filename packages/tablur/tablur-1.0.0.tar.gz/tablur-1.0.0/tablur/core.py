"""
Core table formatting functions for tablur.
"""

from typing import List, Tuple, Any, Optional

DEFAULT_CHARS = ["╭", "╮", "╰", "╯", "├", "┤", "┬", "┴", "┼", "─", "│"]


def tablur(
    data: List[Tuple[str, List[Any]]],
    header: Optional[str] = None,
    footer: Optional[str] = None,
    chars: Optional[List[str]] = DEFAULT_CHARS,
) -> str:
    """Create a formatted table with box-drawing characters and return as string."""
    if not data:
        return "No data provided for table."

    assert chars is not None and len(chars) == 11, "chars must be a list of 11 characters"

    column_names = [col[0] for col in data]
    column_data = [col[1] for col in data]
    max_length = max(len(col) for col in column_data)

    padded_data = [col + [""] * (max_length - len(col)) for col in column_data]
    rows = [[col[i] for col in padded_data] for i in range(max_length)]

    all_data = [column_names] + rows
    col_widths = [max(len(str(item)) for item in col) for col in zip(*all_data)]

    min_width = 0
    if header:
        min_width = max(min_width, len(header))
    if footer:
        min_width = max(min_width, len(footer))

    current_width = sum(col_widths) + 3 * (len(col_widths) - 1)
    if min_width > current_width:
        extra_width = min_width - current_width
        extra_per_col = extra_width // len(col_widths)
        remainder = extra_width % len(col_widths)

        for i in range(len(col_widths)):
            col_widths[i] += extra_per_col
            if i < remainder:
                col_widths[i] += 1

    row_format = (
        f"{chars[10]} {f' {chars[10]} '.join(f'{{:<{w}}}' for w in col_widths)} {chars[10]}"
    )
    separators = [chars[9] * (w + 2) for w in col_widths]
    total_width = sum(col_widths) + 3 * (len(col_widths) - 1)

    lines = []

    if header:
        lines.append(f"{chars[0]}{chars[9].join(separators)}{chars[1]}")
        lines.append(f"{chars[10]} {header:^{total_width}} {chars[10]}")
        lines.append(f"{chars[4]}{chars[6].join(separators)}{chars[5]}")
    else:
        lines.append(f"{chars[0]}{chars[6].join(separators)}{chars[1]}")

    lines.append(row_format.format(*column_names))
    lines.append(f"{chars[4]}{chars[8].join(separators)}{chars[5]}")

    for row in rows:
        lines.append(row_format.format(*row))

    if footer:
        lines.append(f"{chars[4]}{chars[7].join(separators)}{chars[5]}")
        lines.append(f"{chars[10]} {footer:^{total_width}} {chars[10]}")
        lines.append(f"{chars[2]}{chars[9].join(separators)}{chars[3]}")
    else:
        lines.append(f"{chars[2]}{chars[7].join(separators)}{chars[3]}")

    return "\n".join(lines)


def simple(
    data: List[List[Any]],
    headers: Optional[List[str]] = None,
    header: Optional[str] = None,
    footer: Optional[str] = None,
    chars: Optional[List[str]] = DEFAULT_CHARS,
) -> str:
    """Create a table from a list of rows (each row is a list of values)."""
    if not data:
        return "No data provided for table."

    if not headers:
        headers = [str(i) for i in range(len(data[0]))] if data else []

    formatted_data = [
        (header, [row[i] if i < len(row) else "" for row in data])
        for i, header in enumerate(headers)
    ]

    return tablur(formatted_data, header, footer, chars)
