from flask import Flask, request, render_template
from flask_caching import Cache
import requests
import olakeys as olakeys
from geopy.distance import great_circle

app = Flask(__name__)

api_key = olakeys.api_key
request_id = olakeys.request_id

def get_coordinates(address):
    print(address)
    url = f"https://api.olamaps.io/places/v1/geocode?address={address}&api_key={api_key}"
    response = requests.get(url,headers={"X-Request-Id":request_id})
    if response.status_code == 200:
        data = response.json()
        if 'geocodingResults' in data and len(data['geocodingResults'])>0:
            first_result = data['geocodingResults'][0]
            geometry = first_result.get('geometry',{})
            location = geometry.get('location', {})
            lat = location.get('lat')
            lng = location.get('lng')
            print("Lat - ",lat)
            print("Lng - ",lng)
            return lat,lng
        return None, None
    

@app.route('/',methods=['GET','POST'])

def index():
    distance = None
    source_coords = None
    destination_coords = None
    if request.method == 'POST':
        source_address = request.form['source']
        destination_address = request.form['destination']
        source_lat, source_lng = get_coordinates(source_address)
        destination_lat, destination_lng = get_coordinates(destination_address)

        if source_lat is not None and destination_lat is not None:
            source_coords = (source_lat, source_lng)
            destination_coords = (destination_lat, destination_lng)
            distance = great_circle(source_coords, destination_coords).kilometers
            print("Distance:",distance)
        else:
            print(source_coords)
            print("GOT NONE IN COORDINATES")
    
    return render_template('index.html',distance=distance, source_coords=source_coords, destination_coords=destination_coords)

if __name__ == '__main__':
    app.run(debug=True)
