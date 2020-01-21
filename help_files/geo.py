
def get_geo(city):
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
        'tem': w['temp'],
        'wind_spd': w['wind_spd'],
        'description': w['weather']['description'],
        'icon_code': w['weather']['icon'],
    }
    return weather

def get_icon(icon):
    from PIL import Image
    img = Image.open(r'icons/{}.png'.format(icon))

    return img
#
# weather = get_geo('kiev')
# print(weather)
# get_icon(weather['icon_code'])