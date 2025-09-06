# Some selected keywords
selected = ["return","def"]
control_struct = ["if","else","for","while"] # no need to include elif, already accounted in if

def correct(content: list[str]) -> list[str]:
    """Function to perform some corrections with semicolons and parentheses"""

    compiled = []
    for row in content:

        # Add extra space in defs and returns (not needed for now)
        """
        for word in selected:
            if word in row:
                row = row.replace(word,word+" ")
        """
        
        # Add ) at the end of the line when prints
        if "print(" in row:
            row += ")"

        # Add : at the end of the line in control structures
        for word in control_struct:
            if word in row:
                row += ":"

        # Add ) at the end of the line when prints
        if "def" in row:
            row += ":"

        compiled.append(row)

    return compiled