import json
import logging
import os
from typing import Type, Union, Dict, Any, List

import pandas as pd


def write_to_file(file_path: str, file_text: str) -> bool:
    """
    Purpose:
        Write text from a file
    Args/Requests:
         file_path: file path
         file_text: Text of file
    Return:
        Status: True if appened, False if failed
    """

    try:
        with open(file_path, "w") as myfile:
            myfile.write(file_text)
            return True

    except Exception as error:
        logging.error(error)
        return False


def append_to_file(file_path: str, file_text: str) -> bool:
    """
    Purpose:
        Append text to a file
    Args/Requests:
         file_path: file path
         file_text: Text of file
    Return:
        Status: True if appended, False if failed
    """

    try:
        with open(file_path, "a") as myfile:
            myfile.write(file_text)
            return True

    except Exception as error:
        logging.error(error)
        return False


def read_from_file(file_path: str) -> str:
    """
    Purpose:
        Read data from a file
    Args/Requests:
         file_path: file path
    Return:
        read_data: Text from file
    """
    try:
        with open(file_path) as f:
            read_data = f.read()

    except Exception as error:
        logging.error(error)
        return None

    return read_data


def make_df_from_dict(dict_obj: Dict[str, List[Any]]) -> pd.DataFrame:
    """
    Purpose:
        turns a dictonary to a pandas dataframe
    Args/Requests:
         dict_obj = dictonary object
    Return:
        df: Dataframe of the dictonary
    """

    df_map = {}
    keys = dict_obj.keys()

    for key in keys:
        df_map[key] = []

        for val in dict_obj[key]:
            df_map[key].append(val)

    df = pd.DataFrame.from_dict(df_map)
    return df


def get_cmd_output(cmd: str) -> str:
    """
    Purpose:
        Run a shell command and get the output
    Args:
        cmd: The command to run
    Returns:
        result_stirng: the result of the command
    """

    result_stirng = os.popen(cmd).read()
    return result_stirng


def load_json(path_to_json: str) -> Dict[str, Any]:
    """
    Purpose:
        Load json files
    Args:
        path_to_json (String): Path to  json file
    Returns:
        Conf: JSON file if loaded, else None
    """
    try:
        with open(path_to_json, "r") as config_file:
            conf = json.load(config_file)
            return conf

    except Exception as error:
        logging.error(error)
        raise TypeError("Invalid JSON file")


def save_json(json_path: str, json_data: Any) -> None:
    """
    Purpose:
        Save json files
    Args:
        path_to_json (String): Path to  json file
        json_data: Data to save
    Returns:
        N/A
    """
    try:
        with open(json_path, "w") as outfile:
            json.dump(json_data, outfile)
    except Exception as error:
        raise OSError(error)
