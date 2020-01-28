def get_geo_icon(icon,size):
    from PIL import Image
    import os
    file_path = os.path.join('blog', 'static', 'icons', '{}.png'.format(icon))
    # img = Image.open(file_path)
    # re_img = img.resize(size)
    return file_path

def get_geo(city,size=(48,48)):
    import requests
    url = "http://api.weatherbit.io/v2.0/current?key=ce98563a888c4c99bd95e6df31181c52&city={}".format(city)
    r = requests.get(url)
    # print(r.status_code)

    if r.status_code == 200:
        w = r.json()
        # print(w)
        # print(w['count'])
        w = w['data'][0]
    else:
        return None

    weather = {
        'timezone': w['timezone'],
        'sunrise': w['sunrise'],
        'sunset': w['sunset'],
        'ob_time': w['ob_time'],
        'city_name': w['city_name'],
        'temp': w['temp'],
        'wind_spd': w['wind_spd'],
        'description': w['weather']['description'],
        'icon': get_geo_icon(w['weather']['icon'],size)
    }
    if weather['temp']>= 0:
        weather['temp'] = '+ ' + str(weather['temp'])

    return weather

# weather = get_geo('kiev')
# print(weather)