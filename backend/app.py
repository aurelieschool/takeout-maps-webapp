import pandas as pd
import json
import googlemaps
import requests
from flask import Flask, request, jsonify

## Returns geolocation data 
app = Flask(__name__)
api_key = 'process.env.KEY'

# is this bad practice to just have a loose variable like this
loc_cache = {}

# get a list of all the latitudes and longitudes in the file
# as well as the number of times they were visited
@app.route('/locations', methods=['GET']) 
def get_locations():

    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    data = json.load(file)

    # normalizing the data into a json file, cleaning it so that the NaN files disappear
    df = pd.json_normalize(data, 'locations', errors='ignore')
    df_clean = df.loc[:, df.columns!='activity'] # removing activity (temporarily) because it's a pain
    df_clean = df.dropna(axis=1)

    lat = df['latitudeE7']
    long = df['longitudeE7']

    latlong_list = {}

    for x, y in zip(lat, long):
        if (x, y) in latlong_list:
            latlong_list[(x, y)] += 1
        else:
            latlong_list[(x, y)] = 1

    return jsonify(latlong_list)


## send an api request to google to get address & info 
## if the location is already in the location cache, set the address to be equal to that cache value
## return the address (either from cache or from fetching)
@app.route('/info', methods=['GET'])
def get_info():
    multiplier = 10000000

    args = request.args
    x = (args.get('x'))/multiplier
    y = (args.get('y'))/multiplier

    if None in (x, y):
        print("error: somehow no latitude and longitude inputted")
    
    url = ''
    
    if (x, y in loc_cache):
        addr = loc_cache[x, y]
    else:
        url = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={x},{y}&key={api_key}'
        try: 
            response = requests.get(url)
            data = response.json()
            first_result = data['results'][0]
            
            addr = first_result['formatted_address']
            loc_cache[x, y] = addr
        except:
            print("error: couldn't get data for location")
    
    return addr

if __name__ == '__main__':
    app.run(debug=True)