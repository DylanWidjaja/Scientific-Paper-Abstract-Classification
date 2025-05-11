import json 
import re

with open('astronomy.json', 'r') as file:
    data = json.load(file)
    for article in data:
        print(article)
        print("_"*200)