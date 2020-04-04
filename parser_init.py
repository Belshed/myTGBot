import requests
from covid import Covid
from bs4 import BeautifulSoup

target_url = 'https://стопкоронавирус.рф'

covid = Covid(source="worldometers")
response = requests.get(target_url)
covid_data = covid.get_data()