import json
import pandas as pd
import requests
import sys
import os

def create_csv_string(filtered_json):
    csv_string = ""
    for item in filtered_json:
        csv_string = csv_string + item["label"].upper() + "\n"
        for head in item["headings"]:
            csv_string = csv_string + head.upper() + ","
        csv_string = csv_string[:-1] + "\n"
        for sub_item in item["items"]:
            for x in sub_item:
                csv_string = csv_string + x + ","
            csv_string = csv_string[:-1] + "\n"
        csv_string = csv_string + "\n"
    return csv_string


def create_key_headings(headings):
    for head in headings:
        if head.get("key"):
            key_headings.append(head["key"])

        if "url" in key_headings:
            url_key = key_headings.pop(key_headings.index("url"))
            key_headings.insert(0, url_key)
        elif "URL" in key_headings:
            url_key = key_headings.pop(key_headings.index("URL"))
            key_headings.insert(0, url_key)
    return key_headings


def create_label_headings():
    for head in headings:
        if head.get("label"):
            new_headings.append(head["label"])
        elif head.get("text"):
            new_headings.append(head["text"])

    if "url" in new_headings:
        url_key = new_headings.pop(new_headings.index("url"))
        new_headings.insert(0, url_key)
    elif "URL" in new_headings:
        url_key = new_headings.pop(new_headings.index("URL"))
        new_headings.insert(0, url_key)


def create_json():
    for item in items:
        new_sub_items = []
        for new_key in key_headings:
            if item.get(new_key):
                text = str(item.get(new_key))
            if next((head for head in headings if head["key"] == new_key), None)[
                "valueType"
            ]:
                value_type = str(
                        next(
                            (head for head in headings if head["key"] == new_key),
                            None,
                        )["valueType"]
                )
                text = (
                    text
                )
                if value_type != 'url' and value_type != 'URL':
                    text = text + " " +  value_type
            new_sub_items.append(text)
        new_item.append(new_sub_items)



api_key = 'AIzaSyA2qULRLicOP4mfMtEGreX47DLlcGON1aQ'
google_api = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url'
print("\n\nInserire un url e premere invio.\n")
print("Dopo l'ultimo url, digitare 'd' e premere invio\n\n")
new_url = ""
url_list = []

while new_url != "d":
    new_url = input("Inserire url: ")
    if new_url != "d":
        url_list.append(new_url)

for url in url_list:
    response = requests.get(f'{google_api}={url}&key={api_key}')
    if response.status_code == 200:

        json_data = json.dumps(response.json()["lighthouseResult"]["audits"], indent=4)

        with open('results.json', 'w') as f:
            f.write(json_data)

        filtered_json = []

        with open("results.json", "r") as f:

            data = json.load(f)
            for key, audit in data.items():
                headings = audit.get("details", {}).get("headings", [])
                items = audit.get("details", {}).get("items", [])

                if headings != [] and items != []:

                    # Creating an empty dictionary to store filtered data
                    filtered_item = {}
                    # Create empty lists to store new and old headers
                    new_headings = []
                    key_headings = []

                    # Assigning the audit title value to the dictionary "label" key
                    filtered_item["label"] = audit["title"]                    

                    # Using a list comprehension to filter titles in "headings" which contain all the keys "key", "label" and "valueType" and are not null
                    headings = [d for d in headings if all(k in d for k in ("key", "label", "valueType"))]

                    # Sorting of the "headings" list according to the key "key"
                    headings.sort(key=lambda x: x.get("key", ""))

                    # Generation of key_headings list
                    key_headings = create_key_headings(headings)

                    create_new_headings()

                    filtered_item["headings"] = new_headings

                    if len(filtered_item["headings"]) > 0:
                        keys = list(sorted(items[0].keys()))
                        if "url" in keys:
                            url_key = keys.pop(keys.index("url"))
                            keys.insert(0, url_key)
                        if "URL" in keys:
                            url_key = keys.pop(keys.index("URL"))
                            keys.insert(0, url_key)

                        new_item = []

                        create_json()

                        filtered_item["items"] = new_item

                        filtered_json.append(filtered_item)

        json_data = json.dumps(filtered_json, indent=4)
        with open("new_results.json", "w") as f:
            f.write(json_data.replace("\n", ""))

        csv_string = create_csv_string(filtered_json)
        
        print(url)

        with open((url+".csv").replace("/", "-"), "w") as f:
            f.write(csv_string)
            print(os.path.abspath((url+".csv").replace("/", "-")))
            
        print("Generazione csv comnpletata")
    else:
        print(f'Errore {response.status_code}')
        sys.exit()
