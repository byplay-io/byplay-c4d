import c4d

import byplay.c4d_scene_loader
from byplay.recording_local_storage import RecordingLocalStorage



def thumbnail_button_settings():
    settings = c4d.BaseContainer()
    settings[c4d.BITMAPBUTTON_BUTTON] = False
    settings[c4d.BITMAPBUTTON_BORDER] = False
    settings[c4d.BITMAPBUTTON_TOGGLE] = False
    return settings


def get_image_size(path):
    bitmap = c4d.bitmaps.BaseBitmap()
    bitmap.InitWith(path)
    return bitmap.GetSize()


def load_recording_bitmap(path, max_size=100):
    bitmap = c4d.bitmaps.BaseBitmap()
    bitmap.InitWith(path)

    width, height = bitmap.GetSize()
    target_width = max_size
    target_height = max_size
    if width > height:
        target_height = int(max_size * height / width)
    else:
        target_width = int(max_size * width / height)
    dst_bitmap = c4d.bitmaps.BaseBitmap()
    dst_bitmap.Init(target_width, target_height, 24)

    bitmap.ScaleIt(dst_bitmap, 256, False, False)

    return dst_bitmap


def make_empty_bitmap(size=100):
    bitmap = c4d.bitmaps.BaseBitmap()
    bitmap.Init(size, size, 24)
    return bitmap

class GroupWrapper:
    def __init__(self, dialog, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.dialog = dialog

    def __enter__(self):
        self.dialog.GroupBegin(*self.args, **self.kwargs)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dialog.GroupEnd()


class ByplayDialog(c4d.gui.GeDialog):
    THUMBNAIL_SIZE = 150

    def __init__(self, doc):
        super().__init__()
        self.doc = doc
        self.recording_storage = RecordingLocalStorage()
        self.recording_ids = list(reversed(self.recording_storage.list_recording_ids()))
        self._value = 0
        self._ids_by_names = {}
        self._last_id = 100000
        self.recording_thumbnail_image = None
        self.recording_manifest = None
        self.resolution = None

    def AllocateId(self, name=None):
        if name is not None and name in self._ids_by_names:
            return self._ids_by_names[name]
        new_id = self._last_id + 1
        self._last_id += 1
        if name is None:
            name = "noname_{}".format(new_id)
        self._ids_by_names[name] = new_id
        return new_id

    def FetchId(self, name):
        return self._ids_by_names[name]

    def StartGroup(self, cols=1, rows=1, flags=0, init_width=10, init_height=10):
        return GroupWrapper(
            self,
            id=self.AllocateId(),
            flags=flags,
            cols=cols,
            rows=rows,
            initw=init_width,
            inith=init_height
        )

    def FillRecordingIds(self):
        self.AddChild(self.FetchId("recording_ids"), 0, "[ select ]")
        for i, v in enumerate(self.recording_ids):
            self.AddChild(self.FetchId("recording_ids"), i + 1, v)

    def CreateLayout(self):
        with self.StartGroup(cols=2):
            self.GroupBorderSpace(4, 4, 4, 4)
            with self.StartGroup(rows=2, flags=c4d.BFH_SCALEFIT | c4d.BFV_TOP):
                self.AddStaticText(id=self.AllocateId(), flags=0, name="Select recording id:")
                self.AddComboBox(self.AllocateId("recording_ids"), c4d.BFH_SCALEFIT | c4d.BFV_TOP, 200, 20, False)
                self.FillRecordingIds()

            with self.StartGroup(rows=2, init_width=150, init_height=200):
                self.AddStaticText(
                    id=self.AllocateId("recording_info"),
                    flags=c4d.BFH_SCALEFIT | c4d.BFV_TOP,
                    name="---------"
                )
                self.recording_thumbnail_image = self.AddCustomGui(
                    self.AllocateId(),
                    c4d.CUSTOMGUI_BITMAPBUTTON, "",
                    c4d.BFH_RIGHT | c4d.BFV_TOP, 0, 0,
                    thumbnail_button_settings()
                )
        self.recording_thumbnail_image.SetImage(make_empty_bitmap(self.THUMBNAIL_SIZE))
        self.AddDlgGroup(c4d.DLG_OK | c4d.DLG_CANCEL)
        return True

    def Command(self, id, msg):
        if id == c4d.DLG_CANCEL:
            self.Close()
            return True

        # print currently selected "child""
        if id == self.FetchId("recording_ids"):
            rec_id_number = self.GetInt32(self.FetchId("recording_ids")) - 1
            if rec_id_number < 0:
                return True
            self.recording_id = self.recording_ids[rec_id_number]

            bitmap = load_recording_bitmap(
                self.recording_storage.thumbnail_path(self.recording_id),
                self.THUMBNAIL_SIZE
            )
            self.resolution = get_image_size(self.recording_storage.first_frame_path(self.recording_id))
            self.recording_thumbnail_image.SetImage(bitmap)

            data = self.recording_storage.read_manifest(self.recording_id)
            fps = int(data['fps'])
            frames_count = int(data['framesCount'])
            duration = int(frames_count / fps)
            self.SetString(
                self.FetchId("recording_info"),
                "{} fps; {} frames; {}s".format(fps, frames_count, duration)
            )

        if id == c4d.DLG_OK:
            if self.recording_id is None:
                c4d.gui.MessageDialog("Please select a recording first")
                return True

            data = self.recording_storage.read_manifest(self.recording_id)
            fps = int(data['fps'])
            frames_count = int(data['framesCount'])

            loader = byplay.c4d_scene_loader.ByplayC4DSceneLoader(
                doc=self.doc,
                recording_id=self.recording_id,
                recording_storage=self.recording_storage,
                frame_count=frames_count,
                fps=fps,
                resolution=self.resolution,
                settings={}
            )
            loader.load()

            self.Close()
            return True

        return c4d.gui.GeDialog.Command(self, id, msg)
