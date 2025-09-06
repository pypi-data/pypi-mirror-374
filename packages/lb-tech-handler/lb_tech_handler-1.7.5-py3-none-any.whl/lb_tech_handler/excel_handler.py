import pandas as pd
import openpyxl
import os

def read_excel_file(file_path:str,sheet_name:str="Sheet1"):
    """
    Read an Excel file and return a pandas DataFrame.

    Args:
        file_path (str): The path to the Excel file.
        sheet_name (str): The name of the sheet to read. Defaults to "Sheet1".

    Returns:
        pd.DataFrame: A pandas DataFrame containing the data from the Excel file.
    """
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    if not file_path.endswith(".xlsx"):
        raise ValueError("The file must be an Excel file.")
    
    if not os.path.isfile(file_path):
        raise ValueError("The file must be a valid file.")
    
    df = pd.read_excel(file_path,sheet_name=sheet_name)
    
    return df


