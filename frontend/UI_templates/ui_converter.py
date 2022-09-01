import traceback
import os
from pathlib import Path

#Convert all .ui to relevant .py files at start.
def ui_converter():
    for file in Path('./UI_templates').glob('*.ui'):
        ui_convert_cmd = "pyuic5 -x {1}/{0} -o {1}/{2}.py".format(file.name, file.parent, file.stem)
        os.system(ui_convert_cmd)

    if not Path('icons_rc.py').exists():
        try:
            qrc_convert_cmd = f"pyrcc5  UI_templates/icons.qrc -o icons_rc.py"
            os.system(qrc_convert_cmd)
        except:
            traceback.print_exc()

    else:
        return
