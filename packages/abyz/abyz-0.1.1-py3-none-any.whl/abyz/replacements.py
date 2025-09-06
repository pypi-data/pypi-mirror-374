import json
from .global_constants import NUMBERS_PATH, SINGLES_PATH

with open(NUMBERS_PATH) as f:
    numbers = json.load(f)

with open(SINGLES_PATH) as f:
    singles = json.load(f)

def find_all_occurrences(string: str, substring: str) -> list[int]:
    """Function to find all occurrences of a substring in a string (not used right now)"""

    indices = []
    start = 0
    while start < len(string):
        # Find the next occurrence of the substring
        start = string.find(substring, start)
        if start == -1:  # No more occurrences
            break
        indices.append(start)
        start += len(substring)  # Move past the current occurrence
    return indices

def replace_singles(content: list[str], type: str) -> list[str]:
    """Function to replace single elements, such as symbols and numbers"""

    if type=="symbols":
        reserved = singles
    elif type=="numbers":
        reserved = numbers
    
    compiled = []
    for row in content:
        for word in reserved:
            if word in row:
                row = row.replace(word, str(reserved[word]))
        compiled.append(row)
    return compiled
