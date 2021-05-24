import c4d
import sys
import os

from byplay.helpers import join

PLUGIN_ID = 1057320

if sys.version_info[0] == 2:
    sys.path.append(join("{{BYPLAY_PLUGIN_PATH}}", "python2"))
else:
    sys.path.append(join("{{BYPLAY_PLUGIN_PATH}}", "python3"))

os.environ["BYPLAY_SYSTEM_DATA_PATH"] = "{{BYPLAY_DATA_PATH}}"
os.environ["BYPLAY_PLUGIN_LOG_PATH"] = "{{BYPLAY_LOG_PATH}}"

from byplay import dialog
from importlib import reload
print("HELLO")

reload(dialog)


class ByplayDialogCommand(c4d.plugins.CommandData):
    dialog = None

    def Execute(self, doc):
        if self.dialog is None:
            self.dialog = dialog.ByplayDialog(doc)
        self.doc = doc

        return self.dialog.Open(dlgtype=c4d.DLG_TYPE_ASYNC, pluginid=PLUGIN_ID, defaultw=400, defaulth=300)

    def RestoreLayout(self, sec_ref):
        if self.dialog is None:
            self.dialog = dialog.ByplayDialog(self.doc)

        # Restores the layout
        return self.dialog.Restore(pluginid=PLUGIN_ID, secret=sec_ref)


if __name__ == "__main__":
    c4d.plugins.RegisterCommandPlugin(id=PLUGIN_ID,
                                      str="Import Byplay recording",
                                      info=0,
                                      help="Display a basic GUI",
                                      dat=ByplayDialogCommand(),
                                      icon=None)
