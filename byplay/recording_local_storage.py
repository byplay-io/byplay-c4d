import os
import logging
import json
from byplay.config import Config
from byplay.helpers import join


class RecordingLocalStorage:
    def list_recording_ids(self):
        Config.read()
        recs = os.listdir(Config.recordings_dir())
        logging.info("List of files: {} -> {}".format(Config.recordings_dir(), recs))
        extracted = [rec_id for rec_id in recs if self.is_extracted(rec_id)]
        return list(sorted(extracted))

    def c4d_fbpx_path(self, recording_id):
        return join(self.full_path(recording_id), "c4d_scene_ar_v1.fbx")

    def thumbnail_path(self, recording_id):
        return join(self.full_path(recording_id), "thumbnail.jpg")

    def first_frame_path(self, recording_id):
        return join(self.full_path(recording_id), "frames/ar_00001.png")

    def read_manifest(self, recording_id):
        with open(join(self.full_path(recording_id), "recording_manifest.json")) as f:
            return json.load(f)

    def list_env_exr_paths(self, recording_id):
        assets_path = join(Config.recordings_dir(), recording_id, 'assets')
        if not os.path.exists(assets_path):
            return []
        paths = [join(assets_path, p) for p in os.listdir(assets_path) if p.endswith(".exr")]
        return paths

    def full_path(self, recording_id: str) -> str:
        return join(Config.recordings_dir(), recording_id)

    def is_extracted(self, recording_id: str):
        path = join(self.full_path(recording_id), ".extracted")
        exists = os.path.exists(path)
        logging.info("rec: {} / {}".format(path, exists))
        return exists

    def is_motion_only(self, recording_id: str):
        return recording_id.endswith("_MO")
