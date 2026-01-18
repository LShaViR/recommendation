import json

test_product_array = []

with open("files/output/products_data.json", "r") as file:
    test_product_array = json.load(file)

image_not_working = []
with open("files/output/image_not_working.json", "r") as f:
    image_not_working = json.load(f)


test_product_array = [
    item
    for item in test_product_array
    if item["sku_id"] not in [bad["sku_id"] for bad in image_not_working]
]

with open("files/output/filtered_product_data.json", "w") as file:
    json.dump(test_product_array, file, indent=4)
