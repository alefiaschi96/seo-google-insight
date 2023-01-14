import json
import pandas as pd
import requests
import sys
import os
import csv

def create_csv_string(filtered_json):
    csv_string = ""
    for item in filtered_json:
        csv_string = csv_string + item["label"].upper() + "\n"
        for head in item["headings"]:
            csv_string = csv_string + head.upper() + ";"
        csv_string = csv_string[:-1] + "\n"
        for sub_item in item["items"]:
            for x in sub_item:
                csv_string = csv_string + x + ";"
            csv_string = csv_string[:-1] + "\n"
        csv_string = csv_string + "\n"
    return csv_string

def check_keys_in_headings(keys, head):
    for key in keys:
        if key in head.keys():
            print("YES")
            return True
    return False


def create_headings(headings, keys, included_keys = None):
    headings_list = []
    url_key = None
    print(headings)
    for head in headings:
        if not included_keys or check_keys_in_headings(included_keys, head):
            print("\t\tHead: " + "\t\tHead: ".join(head))
            for key in keys:
                if head.get(key):
                    if head.get(key) in ["url", "URL"]:
                        url_key = head.get(key)
                    else:
                        headings_list.append(head.get(key))
    if url_key:
        headings_list = [url_key] + headings_list
    return headings_list


def create_old_headings():
    for head in headings:
        if head.get("key"):
            old_headings.append(head["key"])

        if "url" in old_headings:
            url_key = old_headings.pop(old_headings.index("url"))
            old_headings.insert(0, url_key)
        elif "URL" in old_headings:
            url_key = old_headings.pop(old_headings.index("URL"))
            old_headings.insert(0, url_key)


def create_new_headings():
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
    # Creiamo un dizionario chiamato headings_dict in cui la chiave è la "key" dell'elemento
    # in headings e il valore è il "valueType" dell'elemento
    headings_dict = {head["key"]: head["valueType"] for head in headings}

    # Iteriamo attraverso la lista items
    for item in items:
        new_sub_items = []

        keys = list(sorted(item.keys()))
        if "url" in keys:
            url_key = keys.pop(keys.index("url"))
            keys.insert(0, url_key)
        if "URL" in keys:
            url_key = keys.pop(keys.index("URL"))
            keys.insert(0, url_key)

        # Iteriamo attraverso la lista key_headings
        for new_key in key_headings:

            # Se l'item corrente ha la chiave new_key, assegniamo il valore associato a text
            text = str(item.get(new_key)) if item.get(new_key) else ""

            # Recuperiamo il valore "valueType" dalla chiave new_key nel dizionario headings_dict
            value_type = headings_dict.get(new_key, "")

            # Se il valore "valueType" non è "url", aggiungiamo il valore alla fine di "text"
            if value_type.lower() != 'url':
                text += " " + value_type

            # Aggiungiamo "text" alla lista new_sub_items
            new_sub_items.append(text)
            
        # Alla fine dell'iterazione su key_headings, aggiungiamo new_sub_items alla lista new_item
        new_item.append(new_sub_items)

def escape_semicolon(obj):
    if isinstance(obj, str):
        return obj.replace(";", "\\;")
    elif isinstance(obj, dict):
        return {k: escape_semicolon(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [escape_semicolon(elem) for elem in obj]
    else:
        return obj


api_key = 'AIzaSyA2qULRLicOP4mfMtEGreX47DLlcGON1aQ'
filtered_json = []

print("1- Inserire url\n2- Analisi result.json")
first_input = input("");

if first_input == "1":
    print("\n\nInserire un url e premere invio.\n")
    print("Dopo l'ultimo url, digitare 'd' e premere invio\n\n")
    new_url = ""
    url_list = []

    while new_url != "d":
        new_url = input("Inserire url: ")
        if new_url != "d":
            url_list.append(new_url)

    for url in url_list:
        response = requests.get(f'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&key={api_key}')
        if response.status_code == 200:
            data = response.json()
            data = data["lighthouseResult"]["audits"]
            json_data = json.dumps(data, indent=4)
            with open('results.json', 'w') as f:
                # scrivi la stringa json nel file
                f.write(json_data.replace("itemType", "valueType"))

            with open("results.json", "r") as f:
                data = json.load(f)
                for key, audit in data.items():
                    headings = audit.get("details", {}).get("headings", [])
                    items = audit.get("details", {}).get("items", [])

                    if headings != [] and items != []:

                        filtered_item = {}
                        filtered_item["label"] = audit["title"]

                        new_headings = []
                        old_headings = []

                        headings = [
                            d
                            for d in headings
                            if (
                                d.get("key") is not None
                                and d.get("label") is not None 
                                and d.get("valueType") is not None
                            )
                        ]
                        headings.sort(key=lambda x: x.get("key", ""))
                        old_headings = create_headings(headings, "key")

                        new_headings = create_headings(headings, ["label", "text"])

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
else:
    with open("results.json", "r") as f:
        number = 0
        data = json.load(f)
        data = escape_semicolon(data)
        for key, audit in data.items():
            headings = audit.get("details", {}).get("headings", [])
            items = audit.get("details", {}).get("items", [])

            if headings != [] and items != []:
                number = number + 1

                filtered_item = {}
                filtered_item["label"] = audit["title"]

                label_headings = []
                key_headings = []

                headings = [
                    d
                    for d in headings
                    if (
                        d.get("key") is not None
                        # and d.get("label") is not None 
                        and d.get("valueType") is not None
                    )
                ]
                print("\n\n" + key + ": \n\tHeadings: " + str(len(headings)))
                headings.sort(key=lambda x: x.get("key", ""))
                
                key_headings = create_headings(headings, ["key"], ["label", "text"])
                print("\n\tKeys: ")
                print("\t" + "\t".join(key_headings))

                label_headings = create_headings(headings, ["label", "text"])
                print("\n\tLabels: ")
                print("\t" + "\t".join(label_headings))

                filtered_item["headings"] = label_headings

                if len(filtered_item["headings"]) > 0:
                    new_item = []

                    create_json()

                    filtered_item["items"] = new_item

                    filtered_json.append(filtered_item)

        print(number)

        json_data = json.dumps(filtered_json, indent=4)
        with open("new_results.json", "w") as f:
            f.write(json_data.replace("\n", ""))

        csv_string = create_csv_string(filtered_json)
        

        with open(("test.csv").replace("/", "-"), "w") as f:
            f.write(csv_string)
            print(os.path.abspath(("test.csv").replace("/", "-")))
            
        print("Generazione csv comnpletata")