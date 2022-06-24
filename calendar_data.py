"""
Code for collecting & organizing news events collected from MT5 Platform
Expectations:
Collect from MT5 & Parse.
Update frequently, or based on next event time.
be causative to other aspects of the GUI,
ie. highlighting instruments with news coming up
"""
from pathlib import Path, PurePath

# class News:
#     """
    
#     """    
#     def __init__(self):
#         pass

def load_news_text_file(mt5):
    # Get terminal data
    terminal_info = mt5.terminal_info()._asdict()

    # Check if Calendar text file exists,
    # Otherwise return None
    if not PurePath.exists(terminal_info['data_path'] + 'MQL5\\Files\\test.txt'):
        return None
    file_path = Path(terminal_info['data_path'] + 'MQL5\\Files\\test.txt')
    
    with open(file_path,'r') as file:
        calendar_data = file.read()