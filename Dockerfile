FROM jonduckworthdg/geopandas-base:2.7

RUN pip install rasterio

RUN mkdir /my_scripts
ADD ./bin /my_scripts
CMD python /my_scripts/intersect_buildings_to_task.py