def clean_value(value):
    if value is None:
        return None

    value = str(value).strip()

    if value == "":
        return None

    return value


def clean_items(board_data):
    cleaned = []

    for item in board_data["items_page"]["items"]:
        record = {
            "id": item["id"],
            "name": clean_value(item["name"])
        }

        for column in item["column_values"]:
            record[column["id"]] = clean_value(column["text"])

        cleaned.append(record)

    return cleaned