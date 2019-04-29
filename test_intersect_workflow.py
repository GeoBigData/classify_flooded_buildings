from gbdxtools import Interface
gbdx = Interface()

s3_flood_extents = 's3://egolden/floodwatch/intersect_inputs/flood_shp_one/'
s3_footprints = 's3://egolden/floodwatch/intersect_inputs/footprints_shp/'

intersect_task = gbdx.Task('classify_flooded_footprints',
                           footprints_shp=s3_footprints,
                           flood_shp=s3_flood_extents)

workflow = gbdx.Workflow([intersect_task])
workflow.savedata(intersect_task.outputs.footprints_flood_results, location='egolden/intersect_results')
workflow.execute()
print(workflow.id)

