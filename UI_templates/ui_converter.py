import os
from pathlib import Path

#Convert all .ui to relevant .py files at start.
def ui_converter():
    for file in Path('./UI_templates').glob('*.ui'):
        file_convert_cmd = "pyuic5 -x {1}/{0} -o {1}/{2}.py".format(file.name, file.parent, file.stem)
        os.system(file_convert_cmd)

