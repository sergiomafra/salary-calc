# Calc weekdays of the month
# Grab last dolar cotation
# Import yaml data
# Calculate for given period
# Print final result
from datetime import datetime, date, timedelta

import calendar
import numpy as np
import pandas as pd
import requests
import yaml


# Grab last dolar cotation
now = datetime.now()
day = date.today()
if day.weekday() > 4 or (day.weekday() == 0 and now.time().hour < 9):
    if day.weekday() == 0:
        diff = 3
    else:
        diff = day.weekday() - 4
    day = day - timedelta(diff)
elif now.time().hour < 9:
    day = date.today() - timedelta(1)
formatted_date = day.strftime('%m-%d-%Y')
query_url = ("https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/"
             "CotacaoDolarDia(dataCotacao=@dataCotacao)?@dataCotacao='"
             f"{formatted_date}'&$top=100&$format=json")

r = requests.get(query_url)
currency_data = r.json()
dolar = currency_data['value'][0]['cotacaoVenda']

# Import yaml data
with open('data.yaml', 'r') as yaml_file:
    data = yaml.safe_load(yaml_file)


# Calculate for a given period
def year_month_to_tuple(year_month):
    return tuple([int(x) for x in year_month.split('-')])


start_period = year_month_to_tuple(data['GIVEN_PERIOD_START'])
end_period = year_month_to_tuple(data['GIVEN_PERIOD_END'])
months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
          'August', 'September', 'October', 'November', 'December']
years = [x for x in range(start_period[0], end_period[0]+1)]


def calc_weekdays(year, month):
    month_cal = calendar.Calendar().monthdayscalendar(year, month)
    cal = pd.DataFrame(month_cal).drop(columns=[5, 6])
    weekdays = cal[cal > 0].count().agg('sum')
    return weekdays


final_list = []
for year in years:
    start_value = 1
    end_value = 12
    months_weekdays = np.zeros(12, dtype=int)
    if year == start_period[0]:
        start_value = start_period[1]
    if year == end_period[0]:
        end_value = end_period[1]
    for i in range(start_value, end_value+1):
        months_weekdays[i-1] = calc_weekdays(year, i)
    final_list.append(months_weekdays)

# Final result
day = day.strftime("%Y-%m-%d")
df = pd.DataFrame(final_list, index=years, columns=months)
print(f'Dolar (USD) price in Reais (BRL) on {day}: {dolar}\n')
print(f'WEEKDAYS:\n{df}\n')
df = df * data['INCOME_HOURLY_RATE'] * 8
print(f'EXPECTED USD SALARY:\n{df}\n')
df = df * dolar
print(f'EXPECTED BRL SALARY:\n{df}')
