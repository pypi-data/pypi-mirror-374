def extract_nested_annotated_field_types(direct_type_hint) -> list:
    """
    Reaches into a field inside a pydantic model and extracts the type hints inside a
    - `typing.Optional[Something]
    - 'typing.List[Something]'
    type hint
    :rtype: list
    :return:
    # todo need to handle cases like      exchanges: List[Union[Exchange| Location]] = Field(None)
    """
    result = [
        f_type
        for f_type in direct_type_hint.__dict__.get("__args__", [])
        if f_type not in [type(None)]
    ]
    result2 = []
    for f_type in result:
        if f_type.__name__ == "List" and f_type.__args__:
            result2.append(extract_nested_annotated_field_types(f_type)[0])
        else:
            result2.append(f_type)

    return result2


def safe_string(input_str: str, special_chars: list = []) -> str:
    return repr(input_str)
