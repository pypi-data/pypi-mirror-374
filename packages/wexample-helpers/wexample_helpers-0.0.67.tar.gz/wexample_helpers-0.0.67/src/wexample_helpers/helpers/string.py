from __future__ import annotations

import re


def string_to_kebab_case(text: str) -> str:
    """
    Convert text to kebab case, converting spaces and underscores to dashes.
    """
    return re.sub(r"[_\s]+", "-", re.sub(r"([a-z])([A-Z])", r"\1-\2", text)).lower()


def string_to_snake_case(text: str) -> str:
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", text)
    s2 = re.sub("([a-z])([A-Z])", r"\1_\2", s1).lower()
    s3 = re.sub("([0-9])([A-Z])", r"\1\2", s2)
    return str(re.sub(r"\W+", "_", s3))


def string_append_missing_lines(lines: list[str], content: str) -> str:
    # Split the current content into lines
    current_lines = content.splitlines()

    # Determine the lines that need to be added
    lines_to_add = [line for line in lines if line not in current_lines]

    if lines_to_add:
        # Ensure the content ends with a newline before appending new lines
        content = string_ensure_end_with_new_line(content)
        # Add the missing lines
        content += "\n".join(lines_to_add) + "\n"

    return content


def string_ensure_end_with_new_line(text: str) -> str:
    return text if text.endswith("\n") else text + "\n"


def string_remove_prefix(string: str, prefix: str) -> str:
    """
    Remove a prefix from a string if it exists at the beginning.
    Uses regex to match the exact prefix at the start of the string.

    :param string: The string to process
    :param prefix: The prefix to remove
    :return: String with prefix removed if found at start
    """
    return re.sub(f"^{re.escape(prefix)}", "", string)


def string_replace_params(text: str, params: dict) -> str:
    """
    Replace parameters in a text string with values from a dictionary.
    Each parameter in the text should be in the format %param_name%.
    Example:
        text = "Hello %name%, you are %age% years old"
        params = {"name": "John", "age": "30"}
        result = "Hello John, you are 30 years old"
    """
    result = text
    for key, value in params.items():
        result = result.replace(f"%{key}%", str(value))
    return result


def string_truncate(text: str, limit: int) -> str:
    if len(text) > limit:
        return text[: limit - 3] + "..."
    return text


def string_render_boolean(boolean: bool) -> str:
    return "True" if boolean else "False"


def string_generate_lorem_ipsum(length: int = 100) -> str:
    if length <= 0:
        return ""

    base = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
        "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
        "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. "
        "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. "
        "Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
    )

    text = (base + " ") * ((length // (len(base) + 1)) + 1)

    cut = text[:length].rstrip()

    if (
        len(cut) == length
        and length < len(text)
        and not cut.endswith((" ", ".", ",", "!", "?", ";", ":"))
    ):
        last_space = cut.rfind(" ")
        if last_space > 0:
            cut = cut[:last_space]

    return cut.strip()
