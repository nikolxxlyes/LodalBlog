import json
from datetime import datetime
import os

def get_city(loc):
    from geopy.geocoders import Nominatim
    coord = json.loads(loc)
    query = coord.values()
    # query = [52.2297 ,21.0122]
    geolocator = Nominatim(user_agent="LodalBlog")
    location = geolocator.reverse(query,language='en')
    city = location.raw['address']['city'].lower()
    country_code = location.raw['address']['country_code']

    return city,country_code

def geo_import(city='kyiv',county_code='ua'):
    import requests
    from blog import app
    try:
        url = "https://api.openweathermap.org/data/2.5/forecast?q={},{}&APPID={}&units=metric".format(
                city,county_code,app.config['OPEN_WEATHER_APPID'])
        r = requests.get(url)
        # print(r.status_code)
        if r.status_code == 200:
            w = r.json()
        write_weather(w)
    except ConnectionError:
        print("connection error")

def write_weather(weather):
    from blog import db
    from blog.models import WeatherPoint

    for w in weather['list']:
        rain = w['rain']['3h'] if w.get('rain') else 0
        snow = w['snow']['3h'] if w.get('snow') else 0

        point = WeatherPoint(city=weather['city']['name'].lower(),
                            country = weather['city']['country'].lower(),
                            timestamp = datetime.strptime(w['dt_txt'],'%Y-%m-%d %H:%M:%S'),
                            temp = w['main']['temp'],
                            feels_like = w['main']['feels_like'],
                            wind_spd = w['wind']['speed'],
                            description = w['weather'][0]['description'],
                            icon = w['weather'][0]['icon'],
                            precipitation = rain if rain else snow
                        )
        db.session.add(point)

    db.session.commit()
    print("Complete downloads")


file_name = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'current_weather.json')

if __name__  == "__main__":
    geo_import()