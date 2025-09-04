import json
from dataclasses import asdict, fields, is_dataclass
from typing import Any, Dict, Optional, Self, Union, get_args, get_origin


class SerializableMixin:
    def to_json(
        self,
        indent: Optional[int] = 4,
        ensure_ascii: bool = False,
        to_dict: bool = False,
    ) -> str | Dict[str, Any]:
        """Encode the dataclass into JSON string (or to dictionary)."""
        if not is_dataclass(self):
            raise TypeError(
                f"{self.__class__.__name__}.encode() should be called on dataclass instances"
            )

        data = asdict(self)
        return (
            data
            if to_dict
            else json.dumps(data, ensure_ascii=ensure_ascii, indent=indent)
        )

    @classmethod
    def from_json(cls, data: Dict | str) -> Self:
        """
        Decode a dict or JSON string into the dataclass.
        Automatically filters unknown fields and recursively decodes nested dataclasses.
        """
        if not is_dataclass(cls):
            raise TypeError(
                f"{cls.__name__}.decode() should be called on dataclass types"
            )

        if isinstance(data, str):
            dct: dict = json.loads(data)
        else:
            dct = data

        # Keeps only the fields that are defined in the dataclass
        field_names = {f.name: f for f in fields(cls) if f.init}
        filtered_data = {k: v for k, v in dct.items() if k in field_names}

        for key, value in filtered_data.items():
            field_info = field_names[key]
            field_type = field_info.type

            # Handle Optional types
            if get_origin(field_type) is Union:
                args = get_args(field_type)
                if type(None) in args:
                    non_none_types = [arg for arg in args if arg is not type(None)]
                    if len(non_none_types) == 1:
                        field_type = non_none_types[0]

            # Recursively decode nested dataclasses
            if is_dataclass(field_type) and isinstance(value, dict):
                filtered_data[key] = field_type.from_json(value)  # type: ignore

            elif get_origin(field_type) is list:
                item_type = get_args(field_type)[0]
                if is_dataclass(item_type) and isinstance(value, list):
                    filtered_data[key] = [
                        item_type.from_json(item) if isinstance(item, dict) else item  # type: ignore
                        for item in value
                    ]
            elif get_origin(field_type) is dict:
                key_type, val_type = get_args(field_type)
                if (
                    is_dataclass(val_type)
                    and isinstance(value, dict)
                    and key_type in (str, Any)
                ):
                    filtered_data[key] = {
                        k: val_type.from_json(v) if isinstance(v, dict) else v  # type: ignore
                        for k, v in value.items()
                    }

        return cls(**filtered_data)
