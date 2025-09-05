# Standard Libraries
from typing import Optional


def get_options_errors(
    passed_option, valid_options: list, option_name: Optional[str] = None
):
    """
    Get an error string that lists the valid options for an argument.
    """
    if option_name is None:
        option_name = "option"

    opts_string = "".join([f"-{i}\n" for i in valid_options])
    err_string = (
        f'"{passed_option}" is an invalid {option_name}.'
        f"\nValid options are: \n{opts_string}"
    )

    return err_string
