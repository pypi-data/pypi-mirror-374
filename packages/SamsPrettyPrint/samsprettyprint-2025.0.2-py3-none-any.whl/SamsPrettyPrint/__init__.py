__name__ = "SamsPrettyPrint"
__version__ = "2025.0.2"
__author__ = "Samuel Ward"


from .pretty_print import (
    align,
    cast_to_fixed_length_list,
    disable_ascii_colour_codes,
    enable_ascii_colour_codes,
    isnumeric,
    itemised_dictionary,
    print_dict,
    print_table,
    print_title,
    table,
    title1,
    title3,
    title5,
)
from .pretty_examples import (
    ex_array,
    ex_df,
    ex_dict,
    ex_list,
    ex_str,
)

__all__ = [
    'align',
    'cast_to_fixed_length_list',
    'disable_ascii_colour_codes',
    'enable_ascii_colour_codes',
    'ex_array',
    'ex_df',
    'ex_dict',
    'ex_list',
    'ex_str',
    'isnumeric',
    'itemised_dictionary',
    'print_dict',
    'print_table',
    'print_title',
    'table',
    'title1',
    'title3',
    'title5',
]