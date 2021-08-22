import requests
import json
res = requests.get('https://cat-fact.herokuapp.com')

data = res.content


