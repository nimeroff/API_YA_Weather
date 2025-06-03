import requests
import pandas as pd
import matplotlib.pyplot as plt

def get_data(lat, lon, api_key):
    #Функция для получения данных о погоде от API Яндекс.Погоды.
    url = f"https://api.weather.yandex.ru/v2/forecast?lat={lat}&lon={lon}&limit=7&hours=false"
    headers = {'X-Yandex-API-Key': api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка при получении данных: {response.status_code} - {response.text}")
        return None

def parse_data(data, cityname):
    dt_forecasts = data['forecasts']
    parsedata = []
    for dt in dt_forecasts:
        date = dt['date']
        temp_min = dt['parts']['day']['temp_min']
        temp_max = dt['parts']['day']['temp_max']
        temp_avg = dt['parts']['day']['temp_avg']
        feels_like = dt['parts']['day']['feels_like']
        condition = dt['parts']['day']['condition']
        wind_speed = dt['parts']['day']['wind_speed']
        pressure_mm = dt['parts']['day']['pressure_mm']
        humidity = dt['parts']['day']['humidity']

        parsedata.append({
            'city':cityname,
            'date':date,
            'temp_min': temp_min,
            'temp_max': temp_max,
            'temp_avg': temp_avg,
            'feels_like': feels_like,
            'condition': condition,
            'wind_speed': wind_speed,
            'pressure_mm': pressure_mm,
            'humidity': humidity
        })

    df = pd.DataFrame(parsedata)
    return df

def analyze_data(analyze_frame):
    # print(analyze_frame)
    pd.set_option('display.max_columns', None)
    #группировка данных по городам за все дни
    df_group = analyze_frame.groupby('city').agg(
        minavg_temp=('temp_avg', 'min'), #определим самую низкую температуру
        maxavg_temp=('temp_avg', 'max'), #определим самую высокую температуру
        avg_feels_temp=('feels_like','mean'), #средняя ощущаемая температура
        max_wind_speed=('wind_speed', 'max'), #максимальная скорость ветра
        max_pressure_mm =('pressure_mm','max'), #максимальне давление в мм
        mean_humidity = ('humidity','mean') #средняя влажность за все прогнозные дни
    )
    df_group = df_group.rename(columns={'city':'Город','minavg_temp':'Мин сред темп','maxavg_temp':'Макс сред темп',
                                        'avg_feels_temp':'Сред ощущ темп','max_wind_speed':'Макс скор. ветра',
                                        'max_pressure_mm':'Макс давление','mean_humidity':'Сред влажность'})
    print("\nГруппированные данные по городам:")
    print(df_group)

    # Город с самым теплым днем в прогнозе
    hot_day = analyze_frame.loc[analyze_frame['temp_avg'].idxmax()]
    if not hot_day.empty:
        print('\n Город с самым теплым днем в прогнозе:')
        print(hot_day[['city','date','temp_avg']])

    # Город с самым холодным днем в прогнозе
    cold_day = analyze_frame.loc[analyze_frame['temp_avg'].idxmin()]
    if not cold_day.empty:
        print('\n Город с самым холодным днем в прогнозе:')
        print(cold_day[['city', 'date', 'temp_avg']])

    # Поиск дней с дождем
    df_rain = analyze_frame[analyze_frame['condition'].str.contains("rain")]
    if not df_rain.empty:
        df_rain = df_rain.rename(columns={'city': 'Город', 'date': 'День'})
        print("\nДни с дождем:")
        print(df_rain[['Город','День']])
    # Поиск дней с грозой
    df_storm = analyze_frame[analyze_frame['condition'].str.contains('thunderstorm')]
    if not df_storm.empty:
        df_storm = df_storm.rename(columns={'city': 'Город', 'date': 'День'})
        print("\nДни с грозой:")
        print(df_storm[['Город','День']])
    # Поиск дней со снегом
    df_snow = analyze_frame[analyze_frame['condition'].str.contains('snow')]
    if not df_snow.empty:
        df_snow = df_snow.rename(columns={'city': 'Город', 'date': 'День'})
        print("\nДни со снегом:")
        print(df_snow[['Город','День']])

    return df_group, hot_day, cold_day, df_rain, df_storm, df_snow

# Построение графика
def Diag(dict_df):
    plt.figure(figsize=(15, 7))
    for city, df_city in dict_df.items():
        plt.plot(df_city['date'],df_city['temp_min'],label = city, marker='.')
        for ind, cat in df_city['temp_min'].items():
            plt.text(df_city['date'][[ind]],cat, str(cat), fontsize=10, ha='center')
    plt.legend()
    plt.tight_layout()
    plt.title('Минимальная температура по городам')
    plt.xlabel('Дата')
    plt.ylabel('Температура')
    plt.xticks(rotation=0, horizontalalignment='right', fontsize=10)
    plt.show()

def main():
    api_key = '9ce5f2f9-e13a-4de2-a5ac-9cc1e9e8cf50'  #API-ключ
    cities = {
        'Владивосток': (43.115542, 131.885494),
        'Сочи': (43.585472, 39.723098),
        'Санкт-Петербург': (59.938784, 30.314997),
        'Уфа': (54.735152, 55.958736),
        'Калининград': (54.710162, 20.510137),
        'Новосибирск': (55.030204, 82.920430)
    }

    df_weather = pd.DataFrame()
    for city_name, (lat, lon) in cities.items():
        data = get_data(lat, lon, api_key)
        if data:
            df_city = parse_data(data, city_name)
            df_weather = pd.concat([df_weather, df_city], ignore_index=True)

    # Обработка данных
    if not df_weather.empty:
        df_group, hot_day, cold_day, df_rain, df_storm, df_snow = analyze_data(df_weather)
        Diag({city: df_weather[df_weather['city'] == city] for city in cities.keys()})
    else:
        print('Нет данных для обработки')


if __name__ == "__main__":
    main()