import logging
import os
import argparse
from typing import Tuple, Any


from sentinelhub import (
    SHConfig, MimeType, CRS,
    BBox, SentinelHubRequest,
    DataSource, bbox_to_dimensions, WmsRequest
)

import settings

log = logging.getLogger(__name__)


class GISImageDownloader(object):
    def __init__(self, field_name):
        self.data = self.field_data(field_name)
        self._bbox, self._size = self.bbox_size()
        self.config = self.generate_conf()
        self.wms_config = self.generate_wms_conf()
        self.data_dir = self.check_data_dir_exist()
        self.start_date = self.data.get("time_range").get("start_date")
        self.end_date = self.data.get("time_range").get("end_date")
        self.end_date = self.data.get("time_range").get("end_date")

    def check_data_dir_exist(self):
        pth = self.data.get("dir")
        if not os.path.exists(pth):
            os.makedirs(pth)
        return pth

    def field_data(self, field_name):
        fd = settings.FIELDS.get(field_name)
        if not fd:
            raise ValueError("Name of field not set!")
        return fd

    def generate_conf(self):
        conf = SHConfig()
        conf.sh_client_id = settings.SENTINEL_HUB_CLIENT_ID
        conf.sh_client_secret = settings.SENTINEL_HUB_SECRET_KEY
        return conf

    def generate_wms_conf(self):
        conf = SHConfig()
        conf.instance_id = settings.SENTINEL_HUB_INSTANCE_ID
        return conf

    def bbox_size(self) -> Tuple[BBox, Any]:
        resolution = self.data.get("resolution")
        coords = self.data.get("coordinates")
        _bbox = BBox(bbox=coords, crs=CRS.WGS84)
        _size = bbox_to_dimensions(_bbox, resolution=resolution)
        return _bbox, _size

    def generate_evalscript(self):
        return self.data.get("exec_script")

    def prepare_coordinates(self, coords):
        return [float(item) for item in coords.split(',')]

    def prepare_time(self, time_range):
        t_r = time_range.strip()
        return tuple(t_r.split(','))

    def check_band_type(self, band_type):
        if band_type in settings.BAND_TYPES:
            return band_type
        else:
            raise ValueError("Band type incorrect check settings.BAND_TYPES.")

    def sentinel_hub_request(self):
        """
        According to next example
        https://sentinelhub-py.readthedocs.io/en/latest/examples/processing_api_request.html#Setting-area-of-interest
        :return: sentinel request
        """

        sent_req = SentinelHubRequest(
            data_folder=self.data_dir,
            evalscript=self.generate_evalscript(),
            input_data=[
                SentinelHubRequest.input_data(
                    data_source=DataSource.SENTINEL2_L1C,
                    time_interval=(self.start_date, self.end_date),
                )
            ],
            responses=[
                SentinelHubRequest.output_response('default', MimeType.PNG)
            ],
            bbox=self._bbox,
            size=self._size,
            config=self.config
        )

        return sent_req

    def sentinel_wms_request(self, coords, time_range, band_type):
        """
        In next title you can find acceptable layer(band-type)
        https://www.sentinel-hub.com/develop/api/ogc/standard-parameters/wms/
        :param cords: Coordinates
        :param time_range: str representation of time
        :param band_type:
        :return:
        """
        wms_request = WmsRequest(
            # data_source=DataSource.SENTINEL2_L1C,
            layer=band_type,
            data_folder=self.data_dir,
            bbox=BBox(bbox=coords, crs=CRS.WGS84),
            time=time_range,
            image_format=MimeType.TIFF_d32f,
            width=self.data.get("width"),
            height=self.data.get("height"),
            maxcc=self.data.get("maxcc"),
            config=self.wms_config
        )
        return wms_request

    def main_wms(self, arguments):
        c = self.prepare_coordinates(arguments.coordinates)
        t = self.prepare_time(arguments.time_range)
        b = self.check_band_type(arguments.band_type)
        req = self.sentinel_wms_request(c, t, b)
        req.get_data(save_data=True)
        log.debug(f"Files Saved in {req.data_folder}")

    def main(self):
        req = self.sentinel_hub_request()
        req.get_data(save_data=True)
        log.debug(f"Files Saved in {req.data_folder}")


if __name__ == '__main__':
    if settings.CLI:
        parser = argparse.ArgumentParser()
        parser.add_argument("-c", "--coordinates",  help="for coordinates "
                                                        "Example 46.16,-16.15;46.51,-15.58",
                            action="store")
        parser.add_argument("-t", "--time-range", help="time from,to "
                                                        "Example 2020-02-01,2020-03-01",
                            action="store")
        parser.add_argument("-b", "--band-type", help="",
                            action="store")
        args = parser.parse_args()
        inst = GISImageDownloader("test")
        inst.main_wms(args)

    else:
        inst = GISImageDownloader("test")
        inst.main()
