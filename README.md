#### Docks https://sentinelhub-py.readthedocs.io/

#### How to use 
install virtual env with python 3.8

```python
pip install -r requirements.txt
```

```python
python fields_photo_downloader.py -c 35.424557,32.521052,35.560513,32.650360 -t 2020-05-01,2020-05-30 -b NDVIGV
```
-c coordinates
-t time range can be 2020-11-01 or 2020-05-01,2020-05-30
-b band type(you can finde band type in settings.BAND_TYPES)

For one day
```python
python fields_photo_downloader.py -c 35.424557,32.521052,35.560513,32.650360 -t 2020-05-01 -b NDVIGV
```



Hint:
bbox finder - http://bboxfinder.com/
sentinel hub - https://apps.sentinel-hub.com/
sentinel WMS request - 
https://www.sentinel-hub.com/develop/api/ogc/standard-parameters/wms/