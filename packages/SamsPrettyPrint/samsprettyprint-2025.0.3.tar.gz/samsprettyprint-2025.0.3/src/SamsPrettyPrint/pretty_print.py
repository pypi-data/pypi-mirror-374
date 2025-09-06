import math
from typing import List, Any, Type
import numpy as np
from typing import Sequence

import pyperclip

"""
Many useful functions to format prints neatly
"""

# Enable if IDE can use ASCII colour codes such as \033[91m
ASCII_COLOUR_CODES_ENABLED = True


def functions():
    return {
        "align": align,
        "cast_to_list": cast_to_fixed_length_list,
        "disable_ascii_colour_codes": disable_ascii_colour_codes,
        "enable_ascii_colour_codes": enable_ascii_colour_codes,
        "isnumeric": isnumeric,
        "itemised_dictionary": itemised_dictionary,
        "print_dict": print_dict,
        "print_table": print_table,
        "print_title": print_title,
        "table": table,
        "title1": title1,
        "title3": title3,
        "title5": title5,
    }


# //==================================================\\
# ||                      align                       ||
# \\==================================================//
def align(
        text,
        width: int,
        fill: str = ' ',
        alignment: str = '<',
        strip_whitespace: bool = True,
) -> str:
    """
    Returns a '^' centered, '<' left or '>' right aligned string of length width.
    """
    text = str(text).strip()[:width] if strip_whitespace else str(text)[:width]
    padding = width - len(remove_ascii_colour_tags(text))
    match alignment:
        case '<':
            return text + (fill*padding)[:padding]
        case '^':
            return fill*math.floor(padding/2) + text + fill*math.ceil(padding/2)
        case '>':
            return (fill*padding)[:padding] + text
        case _:
            raise ValueError("Parameter alignment must be one of ('<', '^', '>')")


# //==================================================\\
# ||            cast_to_fixed_length_list             ||
# \\==================================================//
def cast_to_fixed_length_list(
        x: Any,
        length: int,
        item_type: Type,
        default_value: Any,
        msg: str
):
    """
    For example with parameterization length=5, item_type=int, default_value=* the function performs as follows

        x=None              ---return--->   [*,*,*,*,*]
        x=0                 ---return--->   [0,0,0,0,0]
        x=[0,1,2]           ---return--->   [0,1,2,*,*]
        x=[0,1,2,3,4,5,6]   ---return--->   [0,1,2,3,4]
    """
    if x is None:
        return [default_value]*length
    elif isinstance(x, item_type):
        return [x]*length
    elif isinstance(x, Sequence) and all(isinstance(item, item_type) for item in x):
        return list(x)[:length] + [default_value]*max(0, length - len(x))
    else:
        raise ValueError(msg)


# //==================================================\\
# ||            disable_ascii_color_codes             ||
# \\==================================================//
def disable_ascii_colour_codes():
    global ASCII_COLOUR_CODES_ENABLED
    ASCII_COLOUR_CODES_ENABLED = False


# //==================================================\\
# ||             enable_ascii_color_codes             ||
# \\==================================================//
def enable_ascii_colour_codes():
    global ASCII_COLOUR_CODES_ENABLED
    ASCII_COLOUR_CODES_ENABLED = True


# //==================================================\\
# ||                    isnumeric                     ||
# \\==================================================//
def isnumeric(value: Any) -> bool:
    """
    Checks if a value is numeric
    """
    # Integers, floats and complex numbers are numeric
    # NumPy int8, int16, int32, float16, float32, float64 are also numeric
    if isinstance(value, (int, float, complex, np.integer, np.floating)):
        return True

    # In fact anything that can be cast to a float should also be considered numeric
    try:
        float(value)
        return True
    except (ValueError, TypeError, OverflowError) as e:
        return False


# //==================================================\\
# ||               itemised_dictionary                ||
# \\==================================================//
def itemised_dictionary(
        dictionary: dict,
        indentation=' * ',
        separator='   ',
        key_title: str = None,
        value_title: str = None,
        min_key_width: int | None = None,
        max_key_width: int | None = None,
        number_format="{:.2f}",
        newline: str = '\n',
):
    """
    Prints each key-value pair on a newline such that they keys and values line up in a column.
    :param dictionary: {key: value} where both keys and values can be cast to string.
    :param indentation: The indentation will be printed before each line.
    :param separator: The separator will be printed between the key and value.
    :param key_title: If provided will be printed above the column of keys with a --- underline.
    :param value_title: If provided will be printed above the column of keys with a --- underline.
    :param min_key_width: The column with of the keys will be at least min_key_width.
    :param max_key_width: The column with of the keys will be at most max_key_width.
    :param number_format: Convert a value to a “formatted” representation, as controlled by #formatspec.
    :param newline: Control character for end of line.
    :return:
    """

    # Find the maximum character width of the keys and values
    key_width = max([len(str(key)) for key in dictionary.keys()] + [len(key_title) if key_title else 0])
    value_width = max([len(str(value)) for value in dictionary.values()] + [len(value_title) if value_title else 0])

    # min_key_width <= key_width <= max_key_width
    if min_key_width:
        key_width = max(min_key_width, key_width)
    if max_key_width:
        key_width = min(max_key_width, key_width)

    text = ""

    # If titles are provided print them with a dashed line underneath
    if key_title or value_title:
        text += f"{' '*len(indentation)}{align(key_title, key_width)}{separator}{str(value_title)}{newline}"
        text += f"{' '*len(indentation)}{'-'*key_width}{separator}{'-'*value_width}{newline}"

    # Print out the keys and values line by line
    for key, value in dictionary.items():

        # Embedded dictionaries will be listed in a single line
        if type(value) is dict:
            value = ", ".join([
                f"[{str(k).replace('(', '').replace(')', '').replace(' ', '')}] "
                f"{number_format.format(float(v)) if isnumeric(v) else str(v)}"
                for k, v in value.items()
            ])

        # Numbers will be formatted according to numberFormat
        elif isnumeric(value):
            value = number_format.format(float(value))

        # Print the final formulation
        text += f"{indentation}{align(key, key_width)}{separator}{align(value, value_width)}{newline}"

    return text


#  //==================================================\\
#  ||                      _print                      ||
#  \\==================================================//
def _print(text: str, copy_to_clipboard: bool = False):
    print(text)
    if copy_to_clipboard:
        pyperclip.copy(text)


# //==================================================\\
# ||                    print_dict                    ||
# \\==================================================//
def print_dict(
        dictionary: dict,
        indentation=' * ',
        separator='   ',
        key_title: str = None,
        value_title: str = None,
        min_key_width: int | None = None,
        max_key_width: int | None = None,
        number_format="{:.2f}",
        newline: str = '\n',
):
    _print(itemised_dictionary(dictionary, indentation, separator, key_title,
                              value_title, min_key_width, max_key_width, number_format, newline))


# //==================================================\\
# ||                   print_table                    ||
# \\==================================================//
def print_table(
        rows: Sequence[Sequence[Any]],
        column_headers: Sequence[Any] | None = None,
        column_max_widths: Sequence[int] | int | None = None,
        column_min_widths: Sequence[int] | int | None = None,
        column_alignment: Sequence[str] | str | None = '<',
        column_separator: str = '   ',
        header_underline: str | None = '---',
        newline: str = '\n',
        number_format: str = "{:.2g}",
        format_numeric_str: bool = False,
        strip_whitespace: bool = True,
        copy_to_clipboard: bool = False,
):
    _print(table(rows, column_headers, column_max_widths, column_min_widths, column_alignment, column_separator,
                 header_underline, newline, number_format, format_numeric_str, strip_whitespace), copy_to_clipboard)


# //==================================================\\
# ||                   print_title                    ||
# \\==================================================//
def print_title(text: str, width=None, prefix='', bold=False, level: int = 3, copy_to_clipboard: bool = False):
    """
    Prints the text as a large eye-catching
    """
    # Note \033[1m is the ANSI escape sequence for bold
    text = ascii_colour_bold(text) if bold else text
    match level:
        case 1:
            _print(title1(text, *([] if width is None else [width]), prefix=prefix), copy_to_clipboard)
        case 3:
            _print(title3(text, *([] if width is None else [width]), prefix=prefix), copy_to_clipboard)
        case 5:
            _print(title5(text, *([] if width is None else [width]), prefix=prefix), copy_to_clipboard)
        case _:
            raise ValueError("Parameter 'lines' must be 1, 3 or 5.")


# //==================================================\\
# ||                      table                       ||
# \\==================================================//
def table(
        rows: Sequence[Sequence[Any]],
        column_headers: Sequence[Any] | None = None,
        column_max_widths: Sequence[int] | int | None = None,
        column_min_widths: Sequence[int] | int | None = None,
        column_alignment: Sequence[str] | str | None = '<',
        column_separator: str = '   ',
        header_underline: str | None = '---',
        newline: str = '\n',
        number_format: str = "{:.2g}",
        format_numeric_str: bool = False,
        strip_whitespace: bool = True,
) -> str:
    """
    Create a table that looks, for example, like so:

    | column_headers[0] | column_headers[1] | column_headers[2] |
    |-------------------|-------------------|-------------------|
    | row[0][0]         | row[0][1]         | row[0][2]         |
    | row[1][0]         | row[1][1]         | row[1][2]         |

    :param rows: The object row[i][j] will be cast to a string and arranged in row i column j.
    :param column_headers: An optional extra sequence to be used as column headers.
    :param column_max_widths: Defines the maximum number of characters each column may take.
    :param column_min_widths: Defines the maximum number of characters each column may take.
    :param column_alignment: One of '<' left, '^' center or '>' right alignment.
    :param column_separator: This string is added as a separator between each column.
    :param header_underline: This string is repeated underneath each header. Set to None to remove this feature.
    :param newline: This string (e.g. '\n') will be appended to the end of each row.
    :param number_format: Numbers will be formated according to #formatspec
    :param format_numeric_str: If true, numeric strings (e.g. '1.2') will be formated according to number_format.
    :param strip_whitespace: Removes leading and trailing whitespace.
    :return: A nearly formated table.
    """

    # Number of rows and columns
    n: int = len(rows) + (1 if column_headers is not None else 0)
    m: int = max([len(row) for row in rows])

    # Cast rows to a List Lists of lengths n and m respectively
    # Fill missing elements with empty strings
    rows: List[Sequence[Any]] = [column_headers] + list(rows) if column_headers is not None else list(rows)
    rows: List[List[Any]] = [list(row)[:m] + ['']*max(0, m - len(row)) for row in rows]

    # Cast parameters 'column_max_widths' and 'column_min_widths' and 'column_separators' to lists
    column_max_widths: List[int] = cast_to_fixed_length_list(
        column_max_widths, m, int, default_value=np.inf,
        msg="Parameter 'column_max_widths' must be of type Sequence[int], int or None."
    )
    column_min_widths: List[int] = cast_to_fixed_length_list(
        column_min_widths, m, int, default_value=0,
        msg="Parameter 'column_min_widths' must be of type Sequence[int], int or None."
    )
    column_alignment: List[str] = cast_to_fixed_length_list(
        column_alignment, m, str, default_value='<',
        msg="Parameter 'column_alignment' must be a sequence of ('<', '^', '>')."
    )

    # Cast items to numbers and format them where appropriate
    for i, row in enumerate(rows):
        for j, item in enumerate(row):
            if isinstance(item, (int, float, complex, np.integer, np.floating)):
                try:
                    item = number_format.format(item)
                except (TypeError, ValueError):
                    pass
            elif isinstance(item, str) and format_numeric_str:
                try:
                    item = number_format.format(float(item))
                except (TypeError, ValueError):
                    pass
            rows[i][j] = str(item)

    # Calculate the width each column should be
    # min <= width <=max
    column_widths = [
        min((
            column_max_widths[j],
            max([len(remove_ascii_colour_tags(rows[i][j])) for i in range(n)] + [column_min_widths[j], ])
        ))
        for j in range(m)
    ]

    # Add padding to the items
    for i, row in enumerate(rows):
        for j, item in enumerate(row):
            rows[i][j] = align(
                item, column_widths[j], fill=' ', alignment=column_alignment[j], strip_whitespace=strip_whitespace
            )

    # Insert an underline after the first row
    if header_underline:
        underlines = [(header_underline*column_widths[j])[:column_widths[j]] for j in range(m)]
        rows.insert(1, underlines)

    # Join the text and return the tabel
    return newline.join(column_separator.join(row) for row in rows)


def title1(text: str, width=54, prefix=''):
    """Returns a single line string with '=' fill characters either side."""
    return '\n' + prefix + (' ' + text + ' ').center(width, '=')


def title3(text: str, width=54, prefix=''):
    """Returns a 3-line title string with the title in bold font and surrounded by bars."""
    return "\n" \
        + prefix + r'//' + '='*(width - 4) + r'\\' + '\n' \
        + prefix + r'||' + align(text, (width - 4), fill=' ', alignment='^') + r'||' + '\n' \
        + prefix + r'\\' + '='*(width - 4) + r'//'


def title5(text: str, width: int = 61, prefix: str = '', outer_patten: str = '%', inner_patten: str = '-=x='):
    """Returns a 5-line title string for maximum emphasis."""
    outer = prefix + outer_patten*(width//len(outer_patten)) + outer_patten[:width%len(outer_patten)]
    inner = prefix + inner_patten*(width//len(inner_patten)) + inner_patten[:width%len(inner_patten)]
    return f"\n{outer}\n{inner}\n{prefix}{align(text, width, fill=' ', alignment='^')}\n{inner}\n{outer}"


def ascii_colour_red(text: str) -> str:
    if ASCII_COLOUR_CODES_ENABLED:
        return "\033[91m" + text + "\033[0m"
    else:
        return "ERROR: " + text


def ascii_colour_orange(text: str) -> str:
    if ASCII_COLOUR_CODES_ENABLED:
        return "\033[93m" + text + "\033[0m"
    else:
        return "WARNING: " + text


def ascii_color_green(text: str) -> str:
    if ASCII_COLOUR_CODES_ENABLED:
        return "\033[92m" + text + "\033[0m"
    else:
        return "PASS: " + text


def ascii_colour_bold(text: str) -> str:
    if ASCII_COLOUR_CODES_ENABLED:
        return '\033[1m' + text + '\033[0m'
    else:
        return '*' + text + '*'


def remove_ascii_colour_tags(text: str) -> str:
    for tag in [
        "\033[91m",
        "\033[92m",
        "\033[93m",
        '\033[1m',
        "\033[0m"
    ]:
        text = text.replace(tag, '')
    return text
