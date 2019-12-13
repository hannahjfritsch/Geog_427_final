import arcpy

import arcpy

path = r"E:\GEO427\Project\scratch.gdb"
raster_folder = "rasters"


arcpy.env.workspace = path
arcpy.env.overwriteOutput = False
arcpy.CheckOutExtension("Spatial")

in_raster = arcpy.sa.Raster("Spline_tem100")

out_raster = arcpy.sa.GreaterThanEqual(in_raster,0 * in_raster)


arcpy.CopyRaster_management(out_raster,"floored1")