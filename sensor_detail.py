""" Where the hardcoding regarding the sensors goes
The sensor specific classes and the dictionary to access them go here

dicttionary of object is function_dictionary - at bottom

"""
import sensor_structure
from sensor_structure import SensorFormat
from sensor_structure import ExpectedColumns
import pandas as pd
#############################################################################################################
##Constants #################################################################################################
DESTINATION_TIME_ZONE = 'Asia/Kathmandu'

#############################################################################################################
##Helper Functions ##########################################################################################
##Should include unit transforms, date reformats, etc #######################################################
##Whatever applies directly to the data #####################################################################

def toCelcius (x):
	"""
	x = Temperature in Fahrenheit
	returns c, temperature in Celcius
	Converts temperatures from Farenheit to Celcius
	## a way to tell the unit of the original temperature is important"""

	c = x-32
	c = 5*c/9
	return c

def dateConvert (series,initial_zone, *dayfirst):
	_dayfirst = False
	if dayfirst:
		_dayfirst = dayfirst[0]
	series = pd.to_datetime(series,dayfirst = _dayfirst)
	#need to check if datetime is already localized
	# ask the data first, then
	series= pd.DatetimeIndex(pd.to_datetime(series,unit='ms'))
	if series.tzinfo == None or series[1].utcoffset == None:
	   series = series.tz_localize(initial_zone)
	series = series.tz_convert(DESTINATION_TIME_ZONE)
	return series

##############################################################################################################
##Specific Sensor Classess ###################################################################################


class LaserEggFormat(SensorFormat):
	raw_colummns = ExpectedColumns({'Time Point', 'PM2.5 (µg/m³)'})
	formatted_columns = ExpectedColumns({'Time','PM2.5'})
	column_map = {'Time Point':'Time', 'PM2.5 (µg/m³)':'PM2.5'}
	time_zone = 'Asia/Manila'
	sensor_key = "laser egg"

	@classmethod
	def data_transform(cls,df):
		df['Time'] = dateConvert(df['Time'],cls.time_zone,True)
		return df

class PurpleAirFormat(SensorFormat):
	raw_colummns = ExpectedColumns({'created_at', 'entry_id', 'PM1.0_CF_ATM_ug/m3', \
		'PM2.5_CF_ATM_ug/m3','PM10.0_CF_ATM_ug/m3', 'UptimeMinutes', 'ADC', \
		'Temperature_F','Humidity_%', 'PM2.5_CF_1_ug/m3'})
	formatted_columns = ExpectedColumns({'Time', 'entry_id', 'PM1.0', 'PM2.5', 'PM10.0', \
		'Uptime', 'ADC','Temperature', 'Humidity', 'PM2.5B'})
	column_map = {'created_at':'Time', \
				'Temperature_F':'Internal_Temperature', \
				'PM1.0_CF_ATM_ug/m3_x':'PM1_ATMA',\
				'PM2.5_CF_ATM_ug/m3_x':'PM2_5_ATMA',\
				'PM10.0_CF_ATM_ug/m3_x':'PM10_ATMA',\
				'PM1.0_CF_ATM_ug/m3_y':'PM1_ATMB',\
				'PM2.5_CF_ATM_ug/m3_y':'PM2_5_ATMB',\
				'PM10.0_CF_ATM_ug/m3_y':'PM10_ATMB',\
                'PM10.0_CF_ATM_ug/m3_y':'PM10_ATMB',\
				'Humidity_%':'Humidity',\
				'UptimeMinutes':'Uptime',\
				'PM2.5_CF1_ug/m3_x':'PM2_5_ATMA',\
                'PM2.5_CF1_ug/m3_y':'PM2_5_ATMB'}
	time_zone = 'UTC'
	sensor_key = "purple air"

	@classmethod
	def data_transform(cls,df):
		df['Time']=dateConvert(df['Time'],cls.time_zone)
		df['Internal_Temperature'] = toCelcius(df['Internal_Temperature'])
		return df



class WeatherFormat(SensorFormat):
	raw_colummns = ExpectedColumns({'Timestamp', 'Outdoor Temperature', 'Outdoor Humidity', 'Dew Point',\
       'Heat Index', 'Wind Chill', 'Barometric Pressure', 'Rain', 'Wind Speed', \
       'Wind Average', 'Peak Wind', 'Wind Direction', 'Indoor Temperature',\
       'Indoor Humidity'})
	formatted_columns = ExpectedColumns({})
	column_map = {'Timestamp':'Time', \
				'Outdoor Temperature':'Temperature', \
				'Outdoor Humidity': 'Humidity',\
				'Dew Point':'Dew_Point',\
				'Heat Index':'Heat_Index',\
				'Wind Chill':'Wind_Chill',\
				'Wind Speed':'Wind_Speed',\
				'Barometric Pressure':'Pressure',\
				'Wind Average':'Av_Wind',\
				'Peak Wind':'Peak_Wind',\
				'Wind Direction': 'Wind_Direction',\
				'Indoor Temperature':'Indoor_Temperature',\
				'Indoor Humidity': 'Indoor_Humidity'}
	time_zone = 'Asia/Kathmandu'
	sensor_key = "weather"
	@classmethod
	def data_transform(cls, df):
		df['Time']=dateConvert(df['Time'],cls.time_zone)
		return df


############################################################################################################
##Dictionary of sensor objects##############################################################################
function_dictionary= {
	'purple air':PurpleAirFormat(),
	'laser egg':LaserEggFormat(),
	'weather':WeatherFormat() }