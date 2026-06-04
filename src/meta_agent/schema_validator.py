def validate_schema(data, schema, path="$"):
    errors = []
    _validate(data, schema, path, errors)
    return errors


def _validate(data, schema, path, errors):
    if not isinstance(schema, dict):
        return

    if "enum" in schema and data not in schema["enum"]:
        errors.append(f"{path}: expected one of {schema['enum']!r}, got {data!r}")
        return

    expected_type = schema.get("type")
    if expected_type is not None and not _matches_type(data, expected_type):
        errors.append(f"{path}: expected type {expected_type!r}, got {_type_name(data)}")
        return

    if isinstance(data, dict):
        required = schema.get("required", [])
        for field_name in required:
            if field_name not in data:
                errors.append(f"{path}: missing required field {field_name!r}")

        properties = schema.get("properties", {})
        for field_name, field_schema in properties.items():
            if field_name in data:
                _validate(data[field_name], field_schema, f"{path}.{field_name}", errors)

    if isinstance(data, list):
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(data):
                _validate(item, item_schema, f"{path}[{index}]", errors)

    if isinstance(data, (int, float)) and not isinstance(data, bool):
        minimum = schema.get("minimum")
        if minimum is not None and data < minimum:
            errors.append(f"{path}: expected >= {minimum}, got {data}")
        maximum = schema.get("maximum")
        if maximum is not None and data > maximum:
            errors.append(f"{path}: expected <= {maximum}, got {data}")


def _matches_type(data, expected_type):
    if isinstance(expected_type, list):
        return any(_matches_type(data, single_type) for single_type in expected_type)
    if expected_type == "null":
        return data is None
    if expected_type == "object":
        return isinstance(data, dict)
    if expected_type == "array":
        return isinstance(data, list)
    if expected_type == "string":
        return isinstance(data, str)
    if expected_type == "integer":
        return isinstance(data, int) and not isinstance(data, bool)
    if expected_type == "number":
        return isinstance(data, (int, float)) and not isinstance(data, bool)
    if expected_type == "boolean":
        return isinstance(data, bool)
    return True


def _type_name(data):
    if data is None:
        return "null"
    if isinstance(data, bool):
        return "boolean"
    if isinstance(data, dict):
        return "object"
    if isinstance(data, list):
        return "array"
    if isinstance(data, str):
        return "string"
    if isinstance(data, int):
        return "integer"
    if isinstance(data, float):
        return "number"
    return type(data).__name__
