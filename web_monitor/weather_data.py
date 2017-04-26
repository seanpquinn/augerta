# Script to get (potentially) useful weather data for Utah
# Relies on openweathermap.org for data
import urllib2
import json

api_key = "42e100842cf5ed49"

# API call gives us the weather data in JSON format
api_call = "http://api.wunderground.com/api/%s/conditions/q/UT/Hinckley.json" %api_key
raw_data = urllib2.urlopen(api_call).read()
raw_data = raw_data.replace('\n','')
raw_data = raw_data.replace('\t','')
data_json = json.loads(raw_data)
disp_loc = data_json['current_observation']['display_location']
city = str(disp_loc['full'])
lat = float(disp_loc['latitude'])
lon = float(disp_loc['longitude'])

curr_obs = data_json['current_observation']
temp = str(curr_obs['temperature_string'])
p = curr_obs['pressure_mb']
hum = str(curr_obs['relative_humidity'])
wind = str(curr_obs['wind_string'])
desc = str(curr_obs['weather'])
dew = str(curr_obs['dewpoint_string'])

out_str = "<html>\n<head>\n<style>\np {\n\tfont-size: 80%;\n}\n</style>\n</head>"
out_str += "\n<body>\n"
out_str += "<p>%s<br>" %city
out_str += "Lat: %.2f Lon: %.2f<br>" %(lat,lon)
out_str += "%s<br>" %desc
out_str += "Dewpoint: %s<br>" %dew
out_str += "Temp: %s<br>" %temp
out_str += "Pct humidity: %s<br>" %hum
out_str += "Wind %s<br>\n</p>" %wind
out_str += "\n</body>\n</html>"

with open('/var/www/html/monitor/weather.html','w') as f:
	f.write(out_str)
