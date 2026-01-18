import pandas as pd
import json
from typing import List, Dict, Any

fallback = {
    "sku_id": None,
    "title": "no title",
    "sector": "",
    "lowest_price": 0,
    "brand_name": "other",
    "sub_category": "",
    "product_type": "",
    "gender": "unisex",
    "description": "no description",
    "tags": [],
    "featured_image": None,
}


def csv_to_json(
    csv_filepath: str, json_filepath: str, fallback: Dict[str, Any]
) -> None:
    """
    Reads a CSV file and converts it to a JSON array of objects.
    """
    # Load the CSV data
    df = pd.read_csv(csv_filepath)

    # Convert to a list of dictionaries
    json_data: List[Dict[str, Any]] = df.to_dict(orient="records")

    # Replace NaN values with Fallback for each column
    for row in json_data:
        for key, value in row.items():
            if pd.isna(value) or value == "":
                row[key] = fallback[key]

    # Save as a JSON file
    with open(json_filepath, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=4)

    print(f"Successfully converted {csv_filepath} to {json_filepath}")


# Usage
csv_to_json(
    "D:/job/culture-circle/files/exported_products_by_popularity.csv",
    "files/output/products_data.json",
    fallback,
)
