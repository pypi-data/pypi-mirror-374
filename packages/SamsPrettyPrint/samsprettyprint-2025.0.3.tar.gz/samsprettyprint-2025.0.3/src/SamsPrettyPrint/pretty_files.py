import logging
import os
import re


def search_for_file(
        list_of_paths: list,
        file_name: str,
        log_errors: bool = True,
) -> (str | None, float):
    """
    Given a list of paths, for example ['folderAAA', 'folderBBB']
    And the name of the file where '{}' is the version number, for example, 'data_version_{}.txt'
    Will search for the file in the given directories and return the most recent version

    Consider the following example:
    |-folderAAA
    |	|-other.jpg
    |   |-data_version_1.txt
    |-folderBBB
    |	|-data_version_2.16.txt
    |   |-data_version_2.17.txt
    Calling         search_for_data(['folderAAA', 'folderBBB'], 'data_version_{}.txt')
    Will return     'folderBBB/data_version_2.17.txt', 2.17
    """
    full_path = None
    latest_version = -1

    for path in list_of_paths:

        # If the path does not exist, skip it
        if not os.path.exists(path):
            continue

        # Create a string of all the files in the path
        listdir = '|'.join(os.listdir(path))

        # If the file is not versioned, you may input file_name which does not contain '{}'
        # In this case return the path straight away if it contains the file
        if '{}' not in file_name:
            if file_name in listdir and latest_version < 0:
                full_path = os.path.join(path, file_name)
                latest_version = 0

        # Otherwise, search for files where '{}' is replaced with a number
        else:
            # The file_name may contain '{}' but may be saved with a blank version ''
            # If we find such a file assume it is version zero
            if file_name.format('') in listdir and latest_version < 0:
                full_path = os.path.join(path, file_name.format(''))
                latest_version = 0

            # Get a list of version numbers
            versions = re.findall(pattern=file_name.format(r'(\d+\.?\d*)'), string=listdir)

            # Iterate over the version numbers
            # If any are greater than our current latest_version we will select that path
            for v in versions:
                if float(v) > latest_version:
                    full_path = os.path.join(path, file_name.format(v))
                    latest_version = float(v)

    # If the file was not found, we will log an error ad return None
    if log_errors and (latest_version == -1):
        logging.error(
            f"No file called {file_name} could be found in the given paths:\n   |> " + '\n   |> '.join(list_of_paths, )
        )

    return full_path, latest_version
