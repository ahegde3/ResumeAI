
def escape_latex_special_chars(text: str) -> str:
    """
    Escape special characters in text for LaTeX formatting.
    Replaces special characters with their escaped versions using backslashes.
    """
    # Dictionary of LaTeX special characters and their escaped versions
    latex_special_chars = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '^': r'\^{}',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
    }
    
    # Replace each special character with its escaped version
    for char, escaped in latex_special_chars.items():
        text = text.replace(char, escaped)
    
    return text


def unescape_latex_special_chars(text: str) -> str:
    """
    Unescape LaTeX special characters back to normal text.
    """
    # Dictionary of escaped LaTeX characters and their unescaped versions
    latex_escaped_chars = {
        r'\&': '&',
        r'\%': '%',
        r'\$': '$',
        r'\#': '#',
        r'\^{}': '^',
        r'\_': '_',
        r'\{': '{',
        r'\}': '}',
    }
    
    # Replace each escaped character with its unescaped version
    for escaped, char in latex_escaped_chars.items():
        text = text.replace(escaped, char)
    
    return text


def escape_data(data):
    """
    Recursively escape LaTeX special characters in all string fields of the  data.
    Handles nested dictionaries, lists, and string values.
    """
    if isinstance(data, dict):
        return {key: escape_data(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [escape_data(item) for item in data]
    elif isinstance(data, str):
        return escape_latex_special_chars(data)
    else:
        # Return other types (int, float, bool, None) unchanged
        return data