import requests
import json
import pendulum
from dynaconf import settings
from retrying import retry
import os

BASE_URI = "http://api.weatherapi.com/v1/forecast.json"


def get_indonesia_kabupaten_kota():
    """[summary]
    Returns:
        [type]: [description]
    """
    f = open(settings.LOCATION_JSON)
    locations = json.load(f)
    f.close()
    return locations
   
def dump_to_file(filename, data ):
    """[summary]

        Save in UTC format
    Args:
        filename ([type]): [description]
        json ([type]): [description]

    Returns:
        [type]: [description]
    """
    _api_date = pendulum.from_timestamp(data.get('location').get('localtime_epoch')) 
    _save_dir = os.path.join('./data', filename, 'dt='+_api_date.format('YYYY-MM-DD'), 'hr='+_api_date.format('HH'))
    if not os.path.exists(_save_dir):
        print(_save_dir)
        os.makedirs(_save_dir)
    print (data) 
    with open(_save_dir + "/" +filename+ "_" + _api_date.format('YYYYMMDDHHmmss') + '.json', 'w',  encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return 0


@retry(stop_max_attempt_number=3,wait_fixed=2000 ) #if error, wait 2 seconds, then retry up to 3 times 
def call_api(base_uri, params):
    """[summary]
        Call API
    Args:
        params ([type]): [description]

    Returns:
        [type]: [description]
    """
    _response = requests.get(base_uri, params=params).json()
    return _response

# main
if __name__ == "__main__":
    kabupaten_kota_id = get_indonesia_kabupaten_kota()

    for kabkot in kabupaten_kota_id:
        params={
        'key':settings.API_KEY,
        'days':1,
        'aqi':'no',
        'alerts':'no',
        'q':','.join([str(kabkot.get('lat')),str(kabkot.get('long'))])
        }
        response = call_api(base_uri= BASE_URI, params=params )
        kab_kot=kabkot.get('kabko').replace('.', '').replace(' ', '_').lower()

        response['kabupaten_kota']=kabkot.get('kabko')
        dump_to_file(kab_kot, response)