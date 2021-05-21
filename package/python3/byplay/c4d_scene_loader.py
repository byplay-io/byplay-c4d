import c4d
from typing import Union, Tuple
from byplay.recording_local_storage import RecordingLocalStorage


def remove_backgrounds(doc):
    bgs = [o for o in doc.GetObjects() if o.GetType() == c4d.Obackground]
    [bg.Remove() for bg in bgs]


def remove_all(doc):
    os = doc.GetObjects()
    [o.Remove() for o in os]


def set_texture_backgroud(mat, first_frame_path, start_frame=0, end_frame=0, fps=30):
    color = c4d.BaseList2D(c4d.Xbitmap)
    flg = c4d.DESCFLAGS_SET_NONE
    color.SetParameter(c4d.BITMAPSHADER_FILENAME, first_frame_path, flg)
    color.SetParameter(c4d.BITMAPSHADER_TIMING_FROM, start_frame, flg)
    color.SetParameter(c4d.BITMAPSHADER_TIMING_TO, end_frame, flg)
    color.SetParameter(c4d.BITMAPSHADER_TIMING_FPS, fps, flg)
    color.SetParameter(
            c4d.BITMAPSHADER_TIMING_TIMING,
            c4d.BITMAPSHADER_TIMING_TIMING_FRAME,
            flg
            )
    mat[c4d.MATERIAL_COLOR_SHADER] = color
    mat.InsertShader(color)


def assign_material(doc, obj, mat, projection):
    doc.InsertMaterial(mat)
    texture_tag = obj.GetTag(c4d.Ttexture)
    if not texture_tag:
        texture_tag = obj.MakeTag(c4d.Ttexture)
    texture_tag[c4d.TEXTURETAG_MATERIAL] = mat
    texture_tag[c4d.TEXTURETAG_PROJECTION] = projection

    mat[c4d.MATERIAL_ANIMATEPREVIEW] = True
    mat[c4d.MATERIAL_PREVIEWSIZE] = c4d.MATERIAL_PREVIEWSIZE_NO_SCALE

    mat.SetName(obj.GetName())
    c4d.EventAdd()


def assign_material_frontal(doc, obj, mat):
    assign_material(doc, obj, mat, c4d.TEXTURETAG_PROJECTION_FRONTAL)


def assign_material_spherical(doc, obj, mat):
    assign_material(doc, obj, mat, c4d.TEXTURETAG_PROJECTION_SPHERICAL)


def create_object(doc, name, type):
    o = c4d.BaseObject(type)
    o.SetName(name)
    doc.InsertObject(o, None, None)
    c4d.EventAdd()
    return o


class ByplayC4DSceneLoader:
    def __init__(
            self,
            doc,
            recording_id: str,
            frame_count, fps,
            recording_storage: RecordingLocalStorage,
            resolution: Union[Tuple[int, int], None],
            settings):
        self.doc = doc
        self.recording_id = recording_id
        self.settings = settings
        self.frame_count = frame_count
        self.fps = fps
        self.recording_storage = recording_storage
        self.resolution = resolution

    def load(self):
        target_null = create_object(self.doc, "Byplay {}".format(self.recording_id), c4d.Onull)

        self.set_timing()

        existing_objects_ids = [o.GetGUID() for o in self.doc.GetObjects()]
        c4d.documents.MergeDocument(
            self.doc,
            self.recording_storage.c4d_fbpx_path(self.recording_id),
            c4d.SCENEFILTER_OBJECTS,
            None
        )
        self._create_bg()
        self._create_sky(self.recording_storage.list_env_exr_paths(self.recording_id)[0])
        new_objects = self.doc.GetObjects()
        for o in new_objects:
            if o.GetGUID() not in existing_objects_ids:
                o.InsertUnder(target_null)
        self.set_render_settings()

    def set_timing(self):
        self.doc.SetFps(self.fps)
        target_time = c4d.BaseTime(self.frame_count, self.fps)
        if target_time > self.doc.GetMaxTime():
            self.doc.SetMaxTime(target_time)

    def set_render_settings(self):
        if self.resolution is None:
            print("Resolution is none :(")
            return
        rdata = self.doc.GetActiveRenderData()
        w, h = self.resolution
        rdata[c4d.RDATA_XRES] = w
        rdata[c4d.RDATA_YRES] = h
        rdata[c4d.RDATA_FILMASPECT] = w / h
        c4d.EventAdd()

    def _create_bg(self):
        bg_obj = create_object(self.doc, "Background {}".format(self.recording_id), c4d.Obackground)
        bg_mat = c4d.BaseMaterial(c4d.Mmaterial)
        set_texture_backgroud(
            bg_mat,
            self.recording_storage.first_frame_path(self.recording_id),
            1,
            self.frame_count,
            self.fps
        )
        assign_material_frontal(self.doc, bg_obj, bg_mat)

    def _create_sky(self, path):
        sky_obj = create_object(self.doc, "Sky {}".format(self.recording_id), c4d.Osky)
        sky_mat = c4d.BaseMaterial(c4d.Mmaterial)
        set_texture_backgroud(sky_mat, path)
        assign_material_spherical(self.doc, sky_obj, sky_mat)
        sky_obj[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = c4d.OBJECT_OFF
        return sky_obj