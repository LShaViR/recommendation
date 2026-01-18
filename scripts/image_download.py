import json
import requests
import mimetypes

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
}

product_array = []
with open("files/output/products_data.json", "r") as file:
    product_array = json.load(file)


def is_url_image(url, file_name):
    try:
        r = requests.get(url, timeout=5, headers=headers, stream=True)
        if r.status_code != 200:
            return False
        content_type = r.headers.get("content-type")
        extension = mimetypes.guess_extension(content_type)
        if not extension:
            extension = ".jpg"  # Default fallback

        full_filename = f"files/images/{file_name}{extension}"

        with open(full_filename, "wb") as file:
            file.write(r.content)

        return r.status_code == 200
    except Exception as e:
        return False


image_not_working = []
for product in product_array:
    if not is_url_image(product["featured_image"], product["sku_id"]):
        image_not_working.append(product)


# put this image_not_working in a file
with open("files/output/image_not_working.json", "w") as f:
    json.dump(image_not_working, f, indent=4)
