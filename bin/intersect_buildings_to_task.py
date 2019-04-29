import geopandas as gpd
import numpy as np
import os
from gbdx_data_handler_class import GBDXDataHandler

# initialize data handler using gbdx/docker input and output directories
# handler = GBDXDataHandler(input_dir='/Users/elizabethgolden/Documents/intersect_test/small_inputs',
#                           output_dir='/Users/elizabethgolden/Downloads/flooded_buildings')
handler = GBDXDataHandler()

# get building footprints and convert to geopandas dataframe
footprints_filepath = handler.get_vector_filepath(input_port='footprints_shp')
footprint_gdf = gpd.read_file(footprints_filepath[0])

# reproject to geographic crs
footprint_gdf = footprint_gdf.to_crs({'init': 'epsg:4326'})

# give each row (or building) an index
footprint_gdf['id'] = range(1, len(footprint_gdf) + 1)

# get flood extent vectors and convert to geopandas dataframe
flood_filepath = handler.get_vector_filepath(input_port='flood_shp')
flood_gdf = gpd.read_file(flood_filepath[0])

# reproject to geographic crs
flood_gdf = flood_gdf.to_crs({'init': 'epsg:4326'})

# give each row (or flood vector) an index
flood_gdf['id'] = range(1, len(flood_gdf) + 1)

# perform a spatial join to mark which building footprints intersect flood extent polys
flooded_join = gpd.sjoin(footprint_gdf, flood_gdf, how="left", op='intersects')
# replace NaN with 0 in flood_cat (flood category) columns
values = {'flood_cat': 0}
flooded = flooded_join.fillna(value=values)

# find duplicate building rows by grouping by building id (id_left)
grouped = flooded.groupby('id_left')

# return one entry for each duplicate by selecting the flood category (flood_cat) max
floodcat_max = grouped['flood_cat'].agg(np.max)

# convert pandas series to dateframe
floodcat_df = floodcat_max.to_frame()

# give it an index so the building ids become a column again
floodcat_df = floodcat_df.reset_index()

# rename building id column name (id_left) to id so can merge back using original id column
floodcat_df = floodcat_df.rename(columns={'id_left': 'id'})

# merge datframe containing building footprint id and max flood category back to original building footprints gdf
final_footprints = footprint_gdf.merge(floodcat_df, on='id')

# create output directory
out_path = os.path.join(handler.output_dir, 'footprints_flood_results')
if os.path.exists(out_path) is False:
    os.makedirs(out_path)
os.chdir(out_path)

# save footprints to shapefile
final_footprints.to_file(os.path.join('footprints_flood_results.shp'))
