from mxcubecore import HardwareRepository as HWR

from mxcubeweb.core.adapter.beamline_adapter import BeamlineAdapter
from mxcubeweb.core.components.component_base import ComponentBase


class Beamline(ComponentBase):
    def __init__(self, app, config):
        super().__init__(app, config)

    def init_signals(self):
        from mxcubeweb.routes import signals

        if HWR.beamline.xrf_spectrum:
            HWR.beamline.xrf_spectrum.connect(
                HWR.beamline.xrf_spectrum,
                "xrf_task_progress",
                signals.xrf_task_progress,
            )

    def get_aperture(self):
        """
        Returns list of apertures and the one currently used.

        :return: Tuple, (list of apertures, current aperture)
        :rtype: tuple
        """
        beam = HWR.beamline.beam

        aperture_list = beam.get_available_size()["values"]
        current_aperture = beam.get_value()[-1]

        return aperture_list, current_aperture

    def get_viewport_info(self):
        """
        Get information about current "view port" video dimension, beam position,
        pixels per mm, returns a dictionary with the format:

            data = {"pixelsPerMm": pixelsPerMm,
                    "imageWidth": width,
                    "imageHeight": height,
                    "format": fmt,
                    "sourceIsScalable": source_is_scalable,
                    "scale": scale,
                    "videoSizes": video_sizes,
                    "position": position,
                    "shape": shape,
                    "size_x": sx, "size_y": sy}

        :returns: Dictionary with view port data, with format described above
        :rtype: dict
        """
        fmt, source_is_scalable = "MJPEG", False

        if self.app.CONFIG.app.VIDEO_FORMAT == "MPEG1":
            fmt, source_is_scalable = "MPEG1", True
            video_sizes = HWR.beamline.sample_view.camera.get_available_stream_sizes()
            (width, height, scale) = HWR.beamline.sample_view.camera.get_stream_size()
        else:
            scale = 1
            width = HWR.beamline.sample_view.camera.get_width()
            height = HWR.beamline.sample_view.camera.get_height()
            video_sizes = [(width, height)]

        pixelsPerMm = HWR.beamline.diffractometer.get_pixels_per_mm()

        return {
            "pixelsPerMm": pixelsPerMm,
            "imageWidth": width,
            "imageHeight": height,
            "format": fmt,
            "sourceIsScalable": source_is_scalable,
            "scale": scale,
            "videoSizes": video_sizes,
            "videoHash": HWR.beamline.sample_view.camera.stream_hash,
            "videoURL": self.app.CONFIG.app.VIDEO_STREAM_URL,
        }

    def beamline_get_all_attributes(self):
        ho = BeamlineAdapter(HWR.beamline)
        data = ho.dict()
        actions = []

        data.update(
            {
                "path": HWR.beamline.session.get_base_image_directory(),
                "actionsList": actions,
            }
        )

        data.update(
            {"energyScanElements": ho.get_available_elements().get("elements", [])}
        )

        return data

    def prepare_beamline_for_sample(self):
        if hasattr(HWR.beamline.collect, "prepare_for_new_sample"):
            HWR.beamline.collect.prepare_for_new_sample()
