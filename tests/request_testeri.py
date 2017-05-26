import requests, json

#url = 'http://date.jsontest.com/'

def get_all(url):
    response = requests.get(url)
    json_data = json.loads(response.text)
    return json_data

def get_index(url, index):
    response = requests.get(url)
    json_data = json.loads(response.text)
    return json_data[index]
