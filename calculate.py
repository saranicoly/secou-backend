import googlemaps
import re
import requests
import os
from datetime import datetime, date
from collections import OrderedDict
from elevationAPI import elevation

OPEN_WEATHER_KEY = os.environ['OPEN_WEATHER_KEY']
GCP_KEY = os.environ['GCP_KEY']

gmaps = googlemaps.Client(key=GCP_KEY)

dados = { 
            "200": 10,
            "201": 20,
            "202": 60,
            "311": 5,
            "312": 10,
            "313": 10,
            "314": 10,
            "500": 10,
            "501": 20,
            "502": 50,
            "503": 60,
            "504": 60,
            "511": 50,
            "520": 50,
            "521": 50,
            "522": 60,
            "531": 50
        }


def extract_street_names(directions_result):
    street_names = []
    street_location = OrderedDict()
    padrao = r'<b>(.*?)</b>'
    for step in directions_result[0]['legs'][0]['steps']:
        instructions = step.get('html_instructions', '')
        if instructions:
            #parts = instructions.split(' on ')
            names = re.findall(padrao, instructions)
            coords = ['north', 'south', 'east', 'west', 'right', 'left']
            
            for name in names:
                flag = True
                for coord in coords:
                    if coord in name:
                        flag = False
                if flag:
                    street_names.append(name)
                    street_location[name] = step.get('end_location', {'lat': -8.1,'lng': -34.9})
            
            '''if len(parts) > 1:
                names = re.findall(padrao, parts[1]) # Remove any HTML tags after the street name
                for name in names:
                    street_names.append(name)
            else:
                parts = instructions.split(' toward ')
                names = re.findall(padrao, parts[0]) # Get the last part before the HTML tag
                street_names.append(names[-1])'''

    return street_names, street_location

def get_geolocation(address):
    geocode_result = gmaps.geocode(address)

    lat = geocode_result[0]['geometry']['location']['lat']
    lng = geocode_result[0]['geometry']['location']['lng']

    # lat=-8.0514
    # lng=-34.9459

    return {'lat': lat, 'lng': lng}

def get_weather(time, lat=-8.0514, lng=-34.9459):

    #Obtem a hora atual
    current_hour = int(str(datetime.now()).split(' ')[1].split(':')[0])

    #Verifica se a hora que deseja prever esta num intervalo muito proximo da hora atual (a previsao só faz sentido se for para pelo menos 3 horas depois da atual, devido a restricoes da api)
    if int(time) in range(current_hour-2, current_hour+2, 1):
        #obtem o clima atual utilizando a api de clima atual
        url = f'https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lng}&exclude=alerts&appid={OPEN_WEATHER_KEY}'
        requestReturn = requests.get(url).json()
        weather_id = str(requestReturn['current']['weather'][0]['id'])
        if weather_id in dados:
            return dados[weather_id]
        return 0

    #obtem a previsao do clima utilizando a api de previsao
    url = f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lng}&appid={OPEN_WEATHER_KEY}'

    requestReturn = requests.get(url).json()

    #A api retorna dados para 5 dias a partir do dia atual, aqui é realizada uma filtragem para se obter os dados somente do dia atual
    current_day_data = []
    for data in requestReturn['list']:
        if data['dt_txt'].split(' ')[0] == str(date.today()):
            current_day_data.append(data)

    #A api retorna a previsao para horas especificas do dia (contando de 3 em 3 horas), essa variavel armazena as horas que tiveram a previsao do tempo obtida
    forecasted_hours = [data['dt_txt'].split(' ')[1].split(':')[0] for data in current_day_data]

    #A previsao do tempo escolhida sera a da hora que estiver mais proxima da hora que se deseja prever (se eu quero prever o clima das 16hrs mas so tenho o clima das 15h e 18h disponivel, o clima das 15h sera escolhido)
    #para isso a distancia (intervalo) entre o tempo que se deseja prever e as horas que tem a previsao disponivel eh analisada
    time_distance = [abs(int(time)-int(hour)) for hour in forecasted_hours]

    #O index do menor intervalo de tempo eh utilizado para obter a previsao mais proxima da desejada
    index_min_time_distance = time_distance.index(min(time_distance))

    #O id do clima é obtido a partir dos dados do dia atual utilizando o index da hora prevista que tem o menor intervalo com a hora desejada
    weather_id = str(current_day_data[index_min_time_distance]['weather'][0]['id'])
    if weather_id in dados:
        return dados[weather_id]
    return 0

def get_elevation(lat=-8.0514, lng=-34.9459):
    loc = (lat, lng)
    results = elevation(gmaps, loc)
    return results[0]['elevation']

def calculate_probability(weather, elevation):
    if elevation>100:
        probability_elevation = 0.1
    elif elevation<1:
        probability_elevation = 100
    else:
        probability_elevation = 100-elevation
    
    probability = weather*0.7 + probability_elevation*0.3

    return probability

def calculate_route(origin, destination, time):
    if not time:
        time = datetime.now().hour

    current_hour = int(str(datetime.now()).split(' ')[1].split(':')[0])

    if int(time) in range(current_hour-2, current_hour+2, 1):
        departure_time = datetime.now()
    else:
        departure_time = datetime.fromisoformat(f'{str(date.today())} {time}:00:00.000')
        
    directions_result_raw = gmaps.directions(origin, destination, mode="walking", departure_time=departure_time)
    streets, street_location = extract_street_names(directions_result_raw)
    # Remove duplicates from the streets list, keeping the order
    directions_result = list(dict.fromkeys(streets).keys())
    weather_streets = OrderedDict()
    streets_geolocation = OrderedDict()
    for street in directions_result:
        lat, lng = get_geolocation(f'{street}, recife').values()
        weather = get_weather(time, lat, lng)
        elevation = get_elevation(lat, lng)
        streets_geolocation[street] = street_location[street]
        probability = calculate_probability(weather, elevation)

        if probability>50:
            weather_streets[street] = True
        else:
            weather_streets[street] = False

    return (weather_streets, directions_result_raw, streets_geolocation)
