import requests
import time 
import sys
import json
from bs4 import BeautifulSoup as bs
import random

# CrossRef API endpoint
url = "https://api.crossref.org/works"
  
# Parameters for the query
params = {
    'query': '',          # Search term
    'filter': 'type:journal-article,has-abstract:true',  # Restrict to journal articles that has an abstract
    'rows': 1,                     # Number of results
    'sort': 'references-count',   # Sort by most referenced paper
    'order': 'desc',
    'offset' : 0                   # Ignores first n (offset number) results
}

# List of scientific fields
field = ['astronomy', 'psychology', 'sociology']

for i in range(3):

    # Setting the field 
    params['query'] = field[i]

    # Opening JSON file to store abstracts
    with open(f"{field[i]}.json", "w") as file:
        file.write("[\n") # Start the JSON array
        offset_list=[] # List to hold article offset that has been collected
        j = 0
        while(j < 400):
            
            while(True):
                # Selects journals at random
                offset = random.randint(0,1000)
                if offset in offset_list: # If journal has been selected before, select another journal
                    continue
                else:
                    params['offset'] = offset # Set offset parameter to offset number
                    offset_list.append(offset) # Append the generated offset number to the list of used offset numbers
                    break

            # Make the request to the CrossRef API
            response = requests.get(url, params=params)

            # Check if the request was unsuccesful
            if response.status_code != 200:
                print(f"Error: Unable to fetch data (Status Code: {response.status_code})")
                #Exit program if else condition is true
                sys.exit()
            

            print(f"Extracting {params['query']} articles, currently at {j} articles, offset = {offset}") #Check progress
            data = response.json() #Putting the json response into a python dictionary

            for item in data['message']['items']:
                # Extract metadata
                abstract = item.get('abstract', 'No Abstract Available')

                # Creating BeautifulSoup object to extract abstract from xml tags
                try:
                    soup = bs(abstract, "lxml")
                    # Returns all strings within the xml tags <jats:p> | There can be multiple <jats:p> tags
                    abstract_text_list = soup.find_all('jats:p')
                    temp = [] # Temporary array to store text within xml tags
                    for k in abstract_text_list:
                        temp.append(k.text)
                    # Joining all strings into one whole string 
                    abstract_text = "".join(temp)              #The strings are joined without whitespace or punctionation marks but this should 
                                                               #not be a problem as the data will be preprocessed and that removes punctionation marks anyway
                        
                    if j > 0:
                        file.write(",\n")  # Add a comma before each new abstract after the first
                    json.dump(abstract_text, file, indent=4) # Writing the abstract into the json file
                    j += 1
                except Exception as e: #The abstract format varies occasionally, so this is just for error catching so the program keeps running
                    print("Error: " + str(e))
                    continue
            time.sleep(4) # Adding sleep to not overwhelm the API
        file.write("\n]") # Ending the JSON file 