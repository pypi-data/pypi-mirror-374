from shapefile2db import StateShapeFileToDB, ShapeFileToDB
from printpop import print_lime

print_lime("Test")
shapeFilePath = "C:\\Users\\ryan\\Visual Code Projects\\shapefileholder\\tl_2020_us_zcta520.shp"
print_lime(f"ShapeFile Path: {shapeFilePath}")
# shapeFile2db_obj = ShapeFileToDB(shape_file_name=shapeFilePath, point_max = 100, digit_max=4)
shapeFile2db_obj = StateShapeFileToDB(shape_file_name=shapeFilePath, point_max=100, digit_max=4, state='CA')
shapeFile2db_obj.export()