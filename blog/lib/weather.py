import json
import pprint
import os

def geo_import(city):
    global file_name
    import requests
    url = "https://api.openweathermap.org/data/2.5/forecast?q={}&APPID={}&units=metric".format(
            city,'59f15f0d844c57412ffd602800d16379')
    r = requests.get(url)
    # print(r.status_code)

    if r.status_code == 200:
        w = r.json()

    with open(file_name,'w') as fo:
        json.dump(w,fo)

def get_geo():
    global file_name
    with open(file_name,'r') as fo:
        weather = json.load(fo)
    info_weather = []
    for w in weather['list']:
        des = {
            'city_name': weather['city']['name'],
            'time': w['dt_txt'],
            'feels_like': w['main']['feels_like'],
            'temp': w['main']['temp'],
            'wind_spd': w['wind']['speed'],
            'description': w['weather'][0]['description'].capitalize(),
            'icon_url': "http://openweathermap.org/img/wn/{}@2x.png".format(w['weather'][0]['icon']),
            'rain': w['rain']['3h'] if w.get('rain') else 0,
            'snow': w['snow']['3h'] if w.get('snow') else 0
        }
        if des['temp'] >= 0:
            des['temp'] = '+ ' + str(des['temp'])
        if des['feels_like']>= 0:
            des['feels_like'] = '+ ' + str(des['feels_like'])
        info_weather.append(des)
    return info_weather

file_name = os.path.join('blog','static','current_weather.json')
# geo_import('kiev',file_name)
# pprint.pprint(get_geo(file_name))