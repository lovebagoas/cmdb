# coding:utf8
import json
import re

from functools import partial
from django.core.serializers import serialize

serialize = partial(serialize, 'json')


def id_to_dict(obj_dict, value):
    obj_dict.update(id=value)
    return obj_dict


def serialize_queryset(obj):
    obj_list = [id_to_dict(partial_item.get('fields'), partial_item.get('pk'))
                for partial_item in json.loads(serialize(obj))]
    return obj_list


def serialize_instance(obj):
    if obj:
        return serialize_queryset([obj])[0]
    else:
        return None


def cut_str(str, len):
    cut_len = r'.{%s}' % len
    str_list = re.findall(cut_len, str)
    new_str = '\n'.join(str_list)
    return new_str
