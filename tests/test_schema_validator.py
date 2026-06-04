import unittest

from meta_agent.schema_validator import validate_schema


class SchemaValidatorTest(unittest.TestCase):
    def test_required_field(self):
        schema = {"type": "object", "required": ["name"], "properties": {"name": {"type": "string"}}}
        errors = validate_schema({}, schema)
        self.assertTrue(any("missing required field 'name'" in error for error in errors))

    def test_type_validation(self):
        schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        errors = validate_schema({"name": 123}, schema)
        self.assertTrue(any("expected type 'string'" in error for error in errors))

    def test_nullable_type_validation(self):
        schema = {"type": ["string", "null"]}
        self.assertEqual(validate_schema(None, schema), [])
        self.assertEqual(validate_schema("ok", schema), [])
        self.assertTrue(validate_schema(3, schema))

    def test_enum_validation(self):
        schema = {"enum": ["read_only", "blocked"]}
        errors = validate_schema("unsafe", schema)
        self.assertTrue(any("expected one of" in error for error in errors))

    def test_array_items_validation(self):
        schema = {"type": "array", "items": {"type": "object", "required": ["name"]}}
        errors = validate_schema([{}], schema)
        self.assertTrue(any("$[0]: missing required field 'name'" in error for error in errors))

    def test_integer_range_validation(self):
        schema = {"type": "integer", "minimum": 1, "maximum": 5}
        self.assertEqual(validate_schema(3, schema), [])
        self.assertTrue(validate_schema(0, schema))
        self.assertTrue(validate_schema(6, schema))

    def test_valid_nested_object(self):
        schema = {
            "type": "object",
            "required": ["items"],
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["name", "status"],
                        "properties": {
                            "name": {"type": "string"},
                            "status": {"enum": ["active", "paused"]},
                        },
                    },
                }
            },
        }
        self.assertEqual(validate_schema({"items": [{"name": "agent", "status": "active"}]}, schema), [])


if __name__ == "__main__":
    unittest.main()
