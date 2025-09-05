"""
Display utilities for rich tables and formatting
"""

from rich.console import Console
from rich.table import Table

console = Console()


def create_table(title: str, columns: list) -> Table:
    """Create a rich table with standard styling"""
    table = Table(title=title)
    for col in columns:
        table.add_column(**col)
    return table


def format_timestamp(timestamp, format_str="%m/%d %H:%M"):
    """Format unix timestamp to readable string"""
    import time
    try:
        return time.strftime(format_str, time.localtime(timestamp)) if timestamp else 'N/A'
    except (ValueError, TypeError):
        return 'N/A'


def truncate_id(id_string: str, max_length: int = 12) -> str:
    """Truncate long IDs for display"""
    if len(id_string) > max_length:
        return id_string[:max_length] + "..."
    return id_string