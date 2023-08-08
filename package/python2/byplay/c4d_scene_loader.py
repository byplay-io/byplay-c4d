from __future__ import division
from __future__ import absolute_import
import logging

import c4d

from byplay.recording_local_storage import RecordingLocalStorage


def remove_backgrounds(doc):
    bgs = [o for o in doc.GetObjects() if o.GetType() == c4d.Obackground]
    [bg.Remove() for bg in bgs]


def remove_all(doc):
    os = doc.GetObjects()
    [o.Remove() for o in os]


def make_color_shader(first_frame_path, start_frame=0, end_frame=0, fps=30):
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
    return color


def assign_shader_color(mat, shader):
    mat[c4d.MATERIAL_COLOR_SHADER] = shader
    mat.InsertShader(shader)


def assign_shader_luminance(mat, shader):
    mat[c4d.MATERIAL_LUMINANCE_SHADER] = shader
    mat.InsertShader(shader)


def assign_material(doc, obj, mat, projection):
    doc.InsertMaterial(mat)
    texture_tag = obj.GetTag(c4d.Ttexture)
    if not texture_tag:
        texture_tag = obj.MakeTag(c4d.Ttexture)
    texture_tag[c4d.TEXTURETAG_MATERIAL] = mat
    texture_tag[c4d.TEXTURETAG_PROJECTION] = projection

    mat[c4d.MATERIAL_ANIMATEPREVIEW] = True
    mat[c4d.MATERIAL_PREVIEWSIZE] = c4d.MATERIAL_PREVIEWSIZE_NO_SCALE

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


class ByplayC4DSceneLoader(object):
    def __init__(
            self,
            doc,
            recording_id,
            frame_count, fps,
            recording_storage,
            resolution,
            motion_only,
            settings):
        self.doc = doc
        self.recording_id = recording_id
        self.motion_only = motion_only
        self.settings = settings
        self.frame_count = frame_count
        self.fps = fps
        self.recording_storage = recording_storage
        self.resolution = resolution

    def load(self):
        target_null = create_object(self.doc, u"Byplay {}".format(self.recording_id), c4d.Onull)

        self.set_timing()

        existing_objects_ids = [o.GetGUID() for o in self.doc.GetObjects()]
        c4d.documents.MergeDocument(
            self.doc,
            self.recording_storage.c4d_fbpx_path(self.recording_id),
            c4d.SCENEFILTER_OBJECTS,
            None
        )
        bg_mat = self._create_bg()
        exrs = self.recording_storage.list_env_exr_paths(self.recording_id)
        logging.info(u"Found exrs: {}".format(exrs))
        if len(exrs) > 0:
            self._create_sky(exrs[0])

        new_objects = self.doc.GetObjects()
        for o in new_objects:
            if o.GetGUID() not in existing_objects_ids:
                o.InsertUnder(target_null)
                if not self.motion_only and o.GetName().lower() == u"planes":
                    self._assign_planes(o, bg_mat)
        self.set_render_settings()

    def set_timing(self):
        self.doc.SetFps(self.fps)
        target_time = c4d.BaseTime(self.frame_count, self.fps)
        if target_time > self.doc.GetMaxTime():
            self.doc.SetMaxTime(target_time)

    def set_render_settings(self):
        if self.resolution is None:
            print u"Resolution is none :("
            return
        rdata = self.doc.GetActiveRenderData()
        w, h = self.resolution
        rdata[c4d.RDATA_XRES] = w
        rdata[c4d.RDATA_YRES] = h
        rdata[c4d.RDATA_FILMASPECT] = w / h
        rdata[c4d.RDATA_FRAMERATE] = self.fps
        c4d.EventAdd()

    def _create_bg(self):
        if self.motion_only:
            return None
        bg_obj = create_object(self.doc, u"Background {}".format(self.recording_id), c4d.Obackground)
        bg_mat = c4d.BaseMaterial(c4d.Mmaterial)
        assign_shader_color(
            bg_mat,
            make_color_shader(
                self.recording_storage.first_frame_path(self.recording_id),
                1,
                self.frame_count,
                self.fps
            )
        )
        assign_material_frontal(self.doc, bg_obj, bg_mat)
        bg_mat.SetName(bg_obj.GetName())
        return bg_mat

    def _add_compositing(self, obj):
        comp_tag = c4d.BaseTag(c4d.Tcompositing)
        obj.InsertTag(comp_tag)
        return comp_tag

    def _create_sky(self, path):
        sky_obj = create_object(self.doc, u"Sky {}".format(self.recording_id), c4d.Osky)
        sky_mat = c4d.BaseMaterial(c4d.Mmaterial)
        assign_shader_luminance(
            sky_mat,
            make_color_shader(path)
        )
        assign_material_spherical(self.doc, sky_obj, sky_mat)
        sky_mat.SetName(sky_obj.GetName())
        sky_mat.SetChannelState(c4d.CHANNEL_COLOR, False)
        sky_mat.SetChannelState(c4d.CHANNEL_LUMINANCE, True)
        sky_obj[c4d.ID_BASEOBJECT_VISIBILITY_EDITOR] = c4d.OBJECT_OFF
        comp_tag = self._add_compositing(sky_obj)
        comp_tag[c4d.COMPOSITINGTAG_SEENBYCAMERA] = False
        return sky_obj

    def _byplay_plane_material(self):
        name = u"Byplay Plane"
        for mat in self.doc.GetMaterials():
            if mat.GetName() == name:
                return mat

        mat = c4d.BaseMaterial(c4d.Mshadowcatcher)
        mat.SetName(name)
        self.doc.InsertMaterial(mat)
        return mat

    def _assign_planes(self, planes_container, bg_material):
        for plane in planes_container.GetChildren():
            assign_material_frontal(self.doc, plane, bg_material)
            comp_tag = self._add_compositing(plane)
            comp_tag[c4d.COMPOSITINGTAG_CASTSHADOW] = False
            comp_tag[c4d.COMPOSITINGTAG_BACKGROUND] = True
            comp_tag[c4d.COMPOSITINGTAG_BACKGROUND_GI] = True
            comp_tag[c4d.COMPOSITINGTAG_MATTEOBJECT] = True
