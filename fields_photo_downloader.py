import concurrent
import datetime
import logging
import os
import argparse
from sentinelhub import (
    SHConfig, MimeType, CRS,
    BBox, SentinelHubRequest,
    DataSource, bbox_to_dimensions, WmsRequest
)
import settings
from utils import init_mp_pool, init_logger, init_thread_pool_executor, timeit

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
        self.band_type = None

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

    def bbox_size(self):
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
        tr = time_range.strip().split(',')
        log.info("TIME RANGE {0}".format(tr))
        if len(tr) == 2 and tr[-1] != '':
            return tuple(tr)
        else:
            return tr

    def check_band_type(self, band_type):
        if band_type in settings.BAND_TYPES:
            return band_type
        else:
            raise ValueError("Band type incorrect check settings.BAND_TYPES.")

    def eval_scr_by_band(self, band_name):
        eval_src = settings.BAND_TYPES.get(band_name)
        return eval_src.get("exec_script")

    def dates_range(self, dates):
        if len(dates) > 1:
            start = datetime.datetime.strptime(dates[0], "%Y-%m-%d")
            end = datetime.datetime.strptime(dates[1], "%Y-%m-%d")
            date_generated = [
                (start + datetime.timedelta(days=x)).strftime('%Y-%m-%d')
                for x in range(0, (end - start).days + 1)
            ]
            return date_generated
        else:
            return dates

    def multi_proc_requests(self, dates):
        with init_mp_pool() as pool:
            try:
                for i in pool.imap_unordered(self.sentinel_mp_requests, dates):
                    pass
            except Exception as pool_exc:
                log.error("Error is raised: {0}".format(pool_exc))

    def get_satellite_data(self, dates):
        for date in dates:
            self.sentinel_mp_requests(date)

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

    def sentinel_mp_requests(self, date):
        c = self._bbox
        t = (date, date)
        b = self.band_type
        res = self.sentinel_cli_hub_request(c, t, b)
        res.get_data(save_data=True)

    def sentinel_cli_hub_request(self, coords, time_range, band_type):
        """
        In next title you can find acceptable layer(band-type)
        https://www.sentinel-hub.com/develop/api/ogc/standard-parameters/wms/
        :param cords: Coordinates in BBOX format
        :param time_range: str representation of time
        :param band_type: settings BAND_TYPES
        :return:
        """

        hr = SentinelHubRequest(
            data_folder=self.data_dir,
            evalscript=self.eval_scr_by_band(self.check_band_type(band_type)),
            input_data=[
                SentinelHubRequest.input_data(
                    data_source=DataSource.SENTINEL2_L2A,
                    time_interval=time_range,
                )
            ],
            responses=[
                SentinelHubRequest.output_response('default', MimeType.PNG)
            ],
            bbox=coords,
            size=self._size,
            config=self.config
        )

        return hr

    @timeit
    def main_cli(self, arguments):
        c = self.prepare_coordinates(arguments.coordinates)
        t = self.prepare_time(arguments.time_range)
        b = self.check_band_type(arguments.band_type)
        self._bbox = BBox(bbox=c, crs=CRS.WGS84)
        self._size = bbox_to_dimensions(self._bbox, resolution=6)  # need add argument resolution
        self.band_type = b
        if t and len(t) > 1:
            dates = self.dates_range(t)
            log.info("DATES: {0}".format(dates))
            self.multi_proc_requests(dates)
        elif t and len(t) == 1:
            t = tuple([t[0], t[0]])
            req = self.sentinel_cli_hub_request(self._bbox, t, b)
            req.get_data(save_data=True)
            log.debug(f"Files Saved in {req.data_folder}")
        else:
            log.error("Dates set is empty or incorrect!")

    @timeit
    def main_cli_sync(self, arguments):
        c = self.prepare_coordinates(arguments.coordinates)
        t = self.prepare_time(arguments.time_range)
        b = self.check_band_type(arguments.band_type)
        if len(t) > 1:
            self._bbox = BBox(bbox=c, crs=CRS.WGS84)
            self._size = bbox_to_dimensions(self._bbox,
                                            resolution=6)  # need add argument resolution
            self.band_type = b
            dates = self.dates_range(t)
            log.info("DATES: {0}".format(dates))
            self.get_satellite_data(dates)
        else:
            req = self.sentinel_cli_hub_request(c, t, b)
            req.get_data(save_data=True)
            log.debug(f"Files Saved in {req.data_folder}")

    def main(self):
        req = self.sentinel_hub_request()
        req.get_data(save_data=True)
        log.debug(f"Files Saved in {req.data_folder}")


if __name__ == '__main__':
    init_logger(log)
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
        inst.main_cli(args)# main_cli 23043.75 ms
        # inst.main_cli_sync(args) # main_cli_sync 299120.74 ms

    else:
        inst = GISImageDownloader("test")
        inst.main()
