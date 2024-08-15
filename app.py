from flask import Flask, request, render_template
from flask_caching import Cache
import requests
import olakeys as olakeys
import urllib.parse
from geopy.distance import great_circle

app = Flask(__name__)

api_key = olakeys.api_key
request_id = olakeys.request_id

def get_coordinates(address):
    print(address)
    url = f"https://api.olamaps.io/places/v1/geocode?address={address}&api_key={api_key}"
    headers = {"X-Request-Id": request_id, "Accept": "application/json"}
    response = requests.get(url, headers=headers)
   
    #response = requests.get(url,headers={"X-Request-Id":request_id})
    
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
    else:
        print("Error: Request failed with status code", response.status_code)
        return None
    return None, None

def get_oladistance(source_lat, source_lng, destination_lat, destination_lng):
    origin = f"{source_lat},{source_lng}"
    destination = f"{destination_lat},{destination_lng}"

    origin_encoded = urllib.parse.quote(origin)
    destination_encoded = urllib.parse.quote(destination)

    #url = f"https://api.olamaps.io/routing/v1/directions?origin=22.529923,88.346142&destination=19.115354,72.873658&mode=driving&alternatives=false&steps=false&overview=full&language=en&traffic_metadata=false&api_key=wko8RH3XmUxdfV5cbCHMJdbYTIh7c59dn34xh7kH"
    
    #url = f"https://api.olamaps.io/routing/v1/directions?origin={origin_encoded}&destination={destination_encoded}&mode=driving&alternatives=false&steps=false&overview=full&language=en&traffic_metadata=false&api_key={api_key}"
    
    url = f"https://api.olamaps.io/routing/v1/distanceMatrix?origins={origin_encoded}&destinations={destination_encoded}&api_key={api_key}"
    headers = {"Accept": "application/json"}
    response = requests.get(url,headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data is not None and 'rows' in data and len(data['rows']) > 0:
            distance = data['rows'][0]['elements'][0]['distance']
            return distance
        else:
            print("Error: Invalid response data")
            print(response.json())
            return None
    else:
        print(response.json)
        print("Error: Request failed with status code", response.status_code)
        return None
   



@app.route('/',methods=['GET','POST'])

def index():
    distance = None
    ola_distance = None
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
            ola_distance = get_oladistance(source_lat, source_lng, destination_lat, destination_lng)/1000
            print("Ola Distance:",ola_distance)
        else:
            print(source_coords)
            print("GOT NONE IN COORDINATES")         
    
    return render_template('index.html',distance=distance, ola_distance=ola_distance)

if __name__ == '__main__':
    app.run(debug=True)
