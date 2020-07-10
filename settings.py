"""
Docks https://sentinelhub-py.readthedocs.io/
"""
import os


SENTINEL_HUB_SECRET_KEY = os.environ.get("SENTINEL_HUB_SECRET_KEY")
SENTINEL_HUB_CLIENT_ID = os.environ.get("SENTINEL_HUB_CLIENT_ID")
SENTINEL_HUB_INSTANCE_ID = os.environ.get("SENTINEL_HUB_INSTANCE_ID")

CLI = True
LOG_LEVEL = "INFO"

BAND_TYPES = {
    "NDVI-CM": {
        "desc": """
        NDVI (Normalized Difference Vegetation Index) - COLOR_MAP
        """,
        "exec_script": """
        //VERSION=3

        let viz = ColorMapVisualizer.createDefaultColorMap();
        
        function evaluatePixel(samples) {
            let val = index(samples.B08, samples.B04);
            val = viz.process(val);
            val.push(samples.dataMask);
            return val;
        }
        
        function setup() {
          return {
            input: [{
              bands: [
                "B04",
                "B08",
                "dataMask"
              ]
            }],
            output: {
              bands: 4
            }
          }
        }
        """
    },
    "NDVIGV": {
        "desc": """NDVI (Normalized Difference Vegetation Index) - Grayscale visualization.""",
        "exec_script": """
        //VERSION=3

        let viz = new HighlightCompressVisualizerSingle();
        
        function evaluatePixel(samples) {
            let val = index(samples.B08, samples.B04);
            val = viz.process(val);
            val.push(samples.dataMask);
            return val;
        }
        
        function setup() {
          return {
            input: [{
              bands: [
                "B04",
                "B08",
                "dataMask"
              ]
            }],
            output: {
              bands: 2
            }
          }
        }

        """
    },
    "NDVIRainbow": {
     "desc": """NDVI (Normalized Difference Vegetation Index) - Rainbow, 
     from blue to red, through green and yellow.""",
     "exec_script": """
     //VERSION=3
        let viz = ColorGradientVisualizer.createBlueRed();
        
        function evaluatePixel(samples) {
            let val = index(samples.B08, samples.B04);
            val = viz.process(val);
            val.push(samples.dataMask);
            return val;
        }
        
        function setup() {
          return {
            input: [{
              bands: [
                "B04",
                "B08",
                "dataMask"
              ]
            }],
            output: {
              bands: 4
            }
          }
        }
     """
    },
    "NDVIGTW": {
     "desc": """NDVI (Normalized Difference Vegetation Index) - 
     Green to white linear scale.""",
     "exec_script": """
     //VERSION=3
        let viz = ColorGradientVisualizer.createWhiteGreen();
        
        function evaluatePixel(samples) {
            let val = index(samples.B08, samples.B04);
            val = viz.process(val);
            val.push(samples.dataMask);
            return val;
        }
        
        function setup() {
          return {
            input: [{
              bands: [
                "B04",
                "B08",
                "dataMask"
              ]
            }],
            output: {
              bands: 4
            }
          }
        }
     """
    },
    "NDVIRTWL": {
     "desc": """NDVI (Normalized Difference Vegetation Index) - 
     Red to white linear scale, representing the black-body color depending on the temperature.""",
     "exec_script": """
     //VERSION=3

        let viz = ColorGradientVisualizer.createRedTemperature();
        
        function evaluatePixel(samples) {
            let val = index(samples.B08, samples.B04);
            val = viz.process(val);
            val.push(samples.dataMask);
            return val;
        }
        
        function setup() {
          return {
            input: [{
              bands: [
                "B04",
                "B08",
                "dataMask"
              ]
            }],
            output: {
              bands: 4
            }
          }
        }
     """
    },
    "NDVIINDEX": {
     "desc": """DVI (Normalized Difference Vegetation Index) - INDEX""",
     "exec_script": """
     //VERSION=3

    function evaluatePixel(samples) {
        let val = index(samples.B08, samples.B04);
        return [val, samples.dataMask];
    }
    
    function setup() {
      return {
        input: [{
          bands: [
            "B04",
            "B08",
            "dataMask"
          ]
        }],
        output: {
          bands: 2
        }
      }
    }
     """
    },
    "TRUE-COLORHC": {
     "desc": """True color image by mapping the red, green and blue input bands. 
     Value = B04,B03,B02 - RGB visualization.""",
     "exec_script": """
     //VERSION=3

        let minVal = 0.0;
        let maxVal = 0.4;
        
        let viz = new HighlightCompressVisualizer(minVal, maxVal);
        
        function evaluatePixel(samples) {
            let val = [samples.B04, samples.B03, samples.B02];
            val = viz.processList(val);
            val.push(samples.dataMask);
            return val;
        }
        
        function setup() {
          return {
            input: [{
              bands: [
                "B02",
                "B03",
                "B04",
                "dataMask"
              ]
            }],
            output: {
              bands: 4
            }
          }
        }
     """
    },
    # Note work !
    # "TRUE-COLORDV": {
    #  "desc": """True color image by mapping the red, green and blue input bands.
    #  Value = B04,B03,B02 - Output components normalized for visualization""",
    #  "exec_script": """
    #  //VERSION=3
    #
    #     let minVal = 0.0;
    #     let maxVal = 0.4;
    #
    #     let viz = new DefaultVisualizer(minVal, maxVal);
    #
    #     function evaluatePixel(samples) {
    #         let val = [samples.B04, samples.B03, samples.B02];
    #         val = viz.processList(val);
    #         val.push(samples.dataMask);
    #         return val;
    #     }
    #
    #     function setup() {
    #       return {
    #         input: [{
    #           bands: [
    #             "B02",
    #             "B03",
    #             "B04",
    #             "dataMask"
    #           ]
    #         }],
    #         output: {
    #           bands: 4
    #         }
    #       }
    #     }
    #
    #     }
    #  """
    # },
    # "TRUE-COLOR-REFLECTANCE": {
    #  "desc": """True color image by mapping the red, green and blue input bands.
    #   Value = B04,B03,B02 - REFLECTANCE""",
    #  "exec_script": """
    #  //VERSION=3
    #
    #     function evaluatePixel(samples) {
    #         let val = [samples.B04, samples.B03, samples.B02, samples.dataMask];
    #         return val;
    #     }
    #
    #     function setup() {
    #       return {
    #         input: [{
    #           bands: [
    #             "B02",
    #             "B03",
    #             "B04",
    #             "dataMask"
    #           ]
    #         }],
    #         output: {
    #           bands: 4
    #         }
    #       }
    #     }
    #  """
    # },
    # "": {
    #  "desc": """""",
    #  "exec_script": """"""
    # },
}


FIELDS = {
        "test": {
            "maxcc": 0.3,
            "width": 512,
            "height": 856,
            "dir": "/tmp/test_dir",
            "resolution": 6,# meters for small area change resolution to 6 or some other from 1 to 2500
            "coordinates": [35.424557,32.521052, 35.560513,32.650360],
            # "coordinates": [34.878856,32.120528, 34.885315,32.129178],
            "time_range": {
                # "start_date": "2020-05-01",
                "start_date": "2020-05-01",
                # "end_date": "2020-05-30",
                "end_date": "2020-05-30",
                },
            # Без облаков нафото
            #Docks https://sentinelhub-py.readthedocs.io/en/latest/examples/processing_api_request.html#Example-1:-True-color-(PNG)-on-a-specific-date
            # https://apps.sentinel-hub.com/dashboard/#/configurations <-- exec script can be generate here
            # "exec_script": """
            #     //VERSION=3
            #     function setup() {
            #       return {
            #         input: ["B02", "B03", "B04", "CLM"],
            #         output: { bands: 3 }
            #       }
            #     }
            #
            #     function evaluatePixel(sample) {
            #       if (sample.CLM == 1) {
            #         return [0.75 + sample.B04, sample.B03, sample.B02]
            #       }
            #       return [3.5*sample.B04, 3.5*sample.B03, 3.5*sample.B02];
            #     }
            #     """,
            "exec_script": """
            //VERSION=3
                let viz = new HighlightCompressVisualizerSingle();
                
                function evaluatePixel(samples) {
                    let val = index(samples.B08, samples.B04);
                    val = viz.process(val);
                    val.push(samples.dataMask);
                    return val;
                }
                
                function setup() {
                  return {
                    input: [{
                      bands: [
                        "B04",
                        "B08",
                        "dataMask"
                      ]
                    }],
                    output: {
                      bands: 2
                    }
                  }
                }
            """
            }
        }


