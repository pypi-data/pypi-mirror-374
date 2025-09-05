from typing import Any, Dict, List, Optional, Tuple


class ModelTransformer:
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
        self.defs = schema.get("$defs", {})

    def transform(self) -> Optional[Dict[str, Any]]:
        model = None
        if "properties" in self.schema:
            model = self._process_model(self.schema, self.schema.get("title", "Main"))
        return model

    def _process_model(
        self, model_schema: Dict[str, Any], model_name: str
    ) -> Dict[str, Any]:
        if model_name in self.defs:
            model_schema = self.defs.get(model_name, model_schema)

        properties = model_schema.get("properties", {})
        required_fields = set(model_schema.get("required", []))

        fields = []
        for field_name, prop in properties.items():
            field_type, relation, options, title = self._map_type(prop, field_name)
            field_config = {
                "name": field_name,
                "type": field_type,
                "displayName": prop.get("title", title),
            }
            if field_name in required_fields:
                field_config["required"] = True
            if options:
                field_config["options"] = options
            if relation:
                field_config["relation"] = relation
            else:  # add format only if not relation
                if "format" in prop:
                    field_config["format"] = prop["format"]
            fields.append(field_config)

        return {
            "name": model_name.lower(),
            "displayName": model_name,
            "primaryKey": "id",
            "fields": fields,
        }

    @classmethod
    def _extract_ref_and_type(
        cls, prop: Dict[str, Any]
    ) -> Tuple[Optional[str], Optional[str]]:
        if "$ref" in prop:
            ref_name = prop["$ref"].split("/")[-1]
            return ref_name, "ref"

        for key in ("anyOf", "oneOf"):
            if key in prop:
                for option in prop[key]:
                    ref, t = cls._extract_ref_and_type(option)
                    if ref:
                        return ref, t
                    if "type" in option and option["type"] != "null":
                        return None, option["type"]

        if "type" in prop:
            return None, prop["type"]

        return None, None

    def _map_type(
        self, prop: Dict[str, Any], field_name: Optional[str]
    ) -> Tuple[str, Optional[str], Optional[List[str]], Optional[str]]:
        ref_name, prop_type = self._extract_ref_and_type(prop)

        if ref_name:
            ref_schema = self.defs.get(ref_name, {})
            if "enum" in ref_schema:
                return "enum", None, ref_schema["enum"], ref_schema.get("title", None)
            return "select", ref_name.lower(), None, ref_schema.get("title", None)

        if prop_type == "array":
            items = prop.get("items", {})
            ref_name, _ = self._extract_ref_and_type(items)
            if ref_name:
                return "multiselect", ref_name.lower(), None, ref_name
            return "array", None, None, None

        if prop_type == "object":
            if "properties" in prop:
                relation_name = prop.get("title", None) or field_name
                if relation_name:
                    return (
                        "file" if prop.get("title") == relation_name else "select",
                        relation_name.lower(),
                        None,
                        relation_name,
                    )
            return "json", None, None, None

        if prop_type == "string" and "enum" in prop:
            return "radio", None, prop["enum"], None

        if prop_type == "boolean":
            return "boolean", None, None, None

        if prop_type in ("integer", "number"):
            return "number", None, None, None

        if prop_type == "string":
            if prop.get("format") in ("date-time", "date", "duration", "time"):
                return "date", None, None, None
            if prop.get("format") == "uuid":
                return "uuid", None, None, None
            return "string", None, None, None

        return "json", None, None, None


if __name__ == "__main__":
    import json

    example_schema = {
        "$defs": {
            "Status": {
                "enum": ["Active", "Disabled"],
                "title": "Status",
                "type": "string",
            }
        },
        "additionalProperties": False,
        "properties": {
            "is_active": {"default": True, "title": "Is Active", "type": "boolean"},
            "first_name": {
                "anyOf": [{"maxLength": 50, "type": "string"}, {"type": "null"}],
                "default": None,
                "title": "First Name",
            },
            "email": {
                "format": "email",
                "maxLength": 255,
                "title": "Email",
                "type": "string",
            },
            "status": {"$ref": "#/$defs/Status"},
            "id": {"default": None, "title": "Id", "type": "string", "format": "uuid"},
        },
        "required": ["email", "status"],
        "title": "User",
        "type": "object",
    }

    transformer = ModelTransformer(example_schema)
    models = transformer.transform()
    print(json.dumps(models, indent=2))
