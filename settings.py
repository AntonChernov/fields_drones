"""
Docks https://sentinelhub-py.readthedocs.io/
"""
import os



# SENTINEL_HUB_SECRET_KEY = os.environ.get("SENT_SECRET_KEY",
#                                          ";gK@$:y>ib)5u4[rQ5}<<:leo<?*.o1yoh_0fqE0")

SENTINEL_HUB_SECRET_KEY = os.environ.get("SENT_SECRET_KEY",
                                         "1Pvjh-r(C%[CLOjheY>HmsYU8d&}A>cCr&E!]_S^")
# SENTINEL_HUB_CLIENT_ID = os.environ.get("SENTINEL_HUB_CLIENT_ID",
#                                         "4278197c-61d9-4994-8938-7861751f542e")
SENTINEL_HUB_CLIENT_ID = os.environ.get("SENTINEL_HUB_CLIENT_ID",
                                        "67ab20e8-f17a-4eb8-aa74-9957cb339765")

SENTINEL_HUB_INSTANCE_ID = os.environ.get("SENTINEL_HUB_INSTANCE_ID",
                                          "dc0d8642-27d6-4172-be8d-9df83c0d8c63")

CLI = False

BAND_TYPES = (
    "NDVI",
    "NDVI-S2-L2C",
    "NDVI-S2-L2A",
    "TRUE-COLOR-S2-L1C",
    "TRUE_COLOR",
    "TRUE-COLOR-S2-L2C"
)

FIELDS = {
        "test": {
            "maxcc": 0.3,
            "width": 512,
            "height": 856,
            "dir": "/tmp/test_dir",
            "resolution": 60,# meters
            "coordinates": [35.424557,32.521052, 35.560513,32.650360],
            # "coordinates": [34.878856,32.120528, 34.885315,32.129178],
            "time_range": {
                # "start_date": "2020-05-01",
                "start_date": "2020-01-01",
                # "end_date": "2020-05-30",
                "end_date": "2020-01-30",
                },
            # Без облаков нафото
            #Docks https://sentinelhub-py.readthedocs.io/en/latest/examples/processing_api_request.html#Example-1:-True-color-(PNG)-on-a-specific-date
            # https://apps.sentinel-hub.com/dashboard/#/configurations <-- exec script can be generate here
            "exec_script": """
                //VERSION=3
                function setup() {
                  return {
                    input: ["B02", "B03", "B04", "CLM"],
                    output: { bands: 3 }
                  }
                }
                
                function evaluatePixel(sample) {
                  if (sample.CLM == 1) {
                    return [0.75 + sample.B04, sample.B03, sample.B02]
                  }
                  return [3.5*sample.B04, 3.5*sample.B03, 3.5*sample.B02];
                }
                """
            }
        }


