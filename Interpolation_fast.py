import arcpy
from datetime import datetime

path = r"E:\GEO427\Project\scratch.gdb"

print('checking out tools')
arcpy.CheckOutExtension("Spatial")
print('setting up workspace')
arcpy.env.workspace = path
arcpy.env.overwriteOutput = True


#input and output files

csv = r"E:\GEO427\Project\Portland_Air\filter_first_week_clean.csv"
fc = r"E:\GEO427\Project\Neighborhoods_Regions\Neighborhoods_Regions.shp"
#out
raster_out =r"E:\GEO427\Project\full_map_first week"


#input column names
time = "Time"
name ="Sensor"
lat ="Latitude"
lon ="Longitude"
value ="PM2_5_ATMA"
clip = False


start_date_time = "2019-02-04 00:00:00"
end_date_time= "2019-02-08 11:59:00"
start_time ="08:00:00"
end_time="17:00:00"
time_format="yyyy-MM-dd HH:mm:ss"
py_time_format = '%Y-%m-%d %H:%M:%S'


# internal names
clipping ="clipping.shp"
init_air = "init_air"
air = "air"
air_table = "air_table"

#columns
time_of_day = "time_of_day"
day = "2018-01-01"
start_time =day+' '+start_time
end_time=day+' '+end_time
date_column="datetime2"
time2 = "time2"
temp_time = "temp_time"

#define the sql queries for time
day_query = date_column+""" >= TIMESTAMP """ +"'"+start_date_time +"'" \
    +" AND " +date_column +" <= TIMESTAMP  " +"'"+end_date_time+"'"

chunk_query = time2+""" >= TIMESTAMP """ +"'"+start_time +"'" \
    +" AND "+time2 +" <= TIMESTAMP  " +"'"+end_time+"'"

sd_time=datetime.strptime(start_date_time,py_time_format)
ed_time=datetime.strptime(end_date_time,py_time_format)
sd_time_chunk=datetime.strptime(start_time,py_time_format)
ed_time_chunk=datetime.strptime(end_time,py_time_format)

all_stamps = set()
###############################################################################
#clearing out the scratch workspace
print("clearing scratch workspace")
arcpy.Delete_management(air)

print("reading in csv")
#arcpy.CreateFeatureclass_management(path,air,"POINT")
arcpy.MakeTableView_management(csv,air)
arcpy.CopyRows_management(air,"thing")
arcpy.MakeTableView_management("thing",init_air)

print("creating feature table")
#add fields to air
arcpy.AddField_management(init_air,date_column, "DATE")
arcpy.AddField_management(init_air,time2, "DATE")
arcpy.AddField_management(init_air,temp_time, "STRING")


print("rearranging")
#This chunk of code is slow. May be worth writing a map function
#include the time conversions (those are even slower)
def handle_time(row):
    row[0]=row[0][:19]
    row[1]= day+str(row[0])[10:]
    row[2]= datetime.strptime(row[0],py_time_format)
    row[3]= datetime.strptime(row[1],py_time_format)
    return row

update = arcpy.da.UpdateCursor(init_air,[time,temp_time,date_column, time2])
for row in update:
    try:
        row = handle_time(row)
        if((row[2]>=sd_time) & (row[2]<= ed_time)&(row[3]>=sd_time_chunk)& (row[3]<= ed_time_chunk)):
            update.updateRow(row)
            all_stamps.add(row[2])
        else:
            update.deleteRow()
    except Exception as e:
        print(e)

del update, row


#arcpy.MakeTableView_management(init_air, air_table)
#create set of times
#print("generating list")
#all_stamps = set(row[0] for row in arcpy.da.SearchCursor(init_air, date_column))
ntimes = len(all_stamps)
print(str(ntimes)+ " time values met the criteria")

print("looping over times")

def create_layer (table,time, time_column, value_column):
    """ Takes a feature layer, a datetime value, and a column name
    queries for time
    runs a spline iinterpolation with column as the z value
    returns raster"""
    try:
        sql = str(time_column) + " = TIMESTAMP "+"'"+str(time)+"'"
        arcpy.SelectLayerByAttribute_management(table,"NEW_SELECTION", sql)
        arcpy.CopyRows_management(table, "temp_table")
        arcpy.MakeXYEventLayer_management("temp_table",lon, lat, "temp_file")
        out = arcpy.sa.Spline("temp_file",value_column)
        out.save()
        return out
    except ExcecuteError as e:
        print("Something went wrong with layer "+str(time))
        raise e
    except RuntimeError as e:
        print(e)
        raise(e)


try:
    sum = create_layer(init_air,all_stamps.pop(),date_column, value)
    total = 1
except Exception as e:


#loop over unique time values, create a layer for each one
#keep  cumulative sum raster, and a count of processed
# so average can be taken at end
while len(all_stamps) > 0  :
    try:
        c= all_stamps.pop()
        temp = create_layer(init_air,c,date_column, value)
        sum = sum+temp
        total = total+1
        if total%20 == 0:
            print(total + " out of "+ntimes+" calculated")
    except RuntimeError as e:
        print(e)
        break
    except Exception as e:
        print(e)

try:
    final = sum/total
    arcpy.CopyRaster_management(final,raster_out)
except Exception as e:
    print("Unable to create final raster")
    print(e)


print(arcpy.GetMessages(1))
