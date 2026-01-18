import json

product_array = []
with open("files/output/filtered_product_data.json", "r") as file:
    product_array = json.load(file)
