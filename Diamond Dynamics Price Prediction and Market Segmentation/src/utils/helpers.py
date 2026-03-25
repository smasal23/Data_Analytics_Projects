from datetime import datetime
import json

# Print a clean section header in console output.
def print_section(title: str, width: int = 60):
    print("\n" + "=" * width)
    print(title)
    print("=" * width)


# Return the current timestamp as a formatted string
def get_timestamp(fmt: str = "%Y-%m-%d %H:%M:%S"):
    return datetime.now().strftime(fmt)


# Return the current timestamp as a formatted string.
def to_pretty_json(data: dict):
    return json.dumps(data, indent = 2, ensure_ascii = False, default = str)