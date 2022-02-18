import json


def get_field_from_json(json_str: str = None,
                        json_file: str = None,
                        path_to_field: list = None):
    """
    Simple navigation through json object (json_str or json_file is required)
    :param json_str: (Optional) json object via string
    :param json_file: (Optional) path to a file with json object
    :param path_to_field: (Optional) list with path to a field
        (if not specified, interactive mode used)
    :return: value in the field
    >>> get_field_from_json(json_str='{"a": 42, "b":[{"c": true},{"d":null}]}',\
    path_to_field=['a'])
    42
    >>> get_field_from_json(json_str='{"a": 42, "b":[{"c": true},{"d":null}]}',\
    path_to_field=['b', 0, 'c'])
    True
    >>> get_field_from_json(json_str='{"a": 42, "b":[{"c": true},{"d":null}]}',\
    path_to_field=['b', 1, 'd']) is None
    True
    """
    if json_file is None and json_str is None:
        raise ValueError('At least one json_str or json_file '
                         'must be specified')
    elif json_str is not None:
        json_object = json.loads(json_str)
    else:
        json_object = json.load(open(json_file, 'r'))
    if path_to_field is not None:
        for index in path_to_field:
            json_object = json_object[index]
        return json_object
    else:
        while isinstance(json_object, dict) or isinstance(json_object, list):
            if isinstance(json_object, dict):
                while True:
                    print('JSON object fields:', ', '.join(json_object))
                    field = input('Type in one of the field or leave blank '
                                  'to see the whole object: ')
                    if field == '':
                        print(json.dumps(json_object,
                                         ensure_ascii=False,
                                         indent=4))
                        return
                    elif field in json_object:
                        json_object = json_object[field]
                        break
                    else:
                        print('Wrong field, there is no such one\n'
                              'Try again')
            elif isinstance(json_object, list):
                while True:
                    length = len(json_object)
                    print(f'List has {length} objects in it')
                    field = input(f'Type in a number from 0 to {length - 1} '
                                  'or leave blank to see the whole list: ')
                    if field == '':
                        print(json.dumps(json_object,
                                         ensure_ascii=False,
                                         indent=4))
                        return
                    elif field.isnumeric():
                        field = int(field)
                        if 0 <= field < length:
                            json_object = json_object[int(field)]
                            break
                        else:
                            print('Wrong number, out of range\n'
                                  'Try again')
                    else:
                        print('Wrong type, please type in a number\n'
                              'Try again')
        print(json_object)


if __name__ == '__main__':
    get_field_from_json(json_file=input())
