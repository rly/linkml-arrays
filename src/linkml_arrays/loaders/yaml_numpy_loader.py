from decimal import Decimal

from typing import Type, Union

import numpy as np
from pydantic import BaseModel
import yaml

from linkml_runtime.loaders.loader_root import Loader
from linkml_runtime.utils.yamlutils import YAMLRoot
from linkml_runtime import SchemaView
from linkml_runtime.linkml_model import ClassDefinition


def iterate_element(input_dict: dict, element_type: ClassDefinition, schemaview: SchemaView) -> dict:
    ret_dict = dict()
    for k, v in input_dict.items():
        found_slot = schemaview.induced_slot(k, element_type.name)
        if "linkml:elements" in found_slot.implements:
            array_file_path = v.replace("saved in ", "")
            v = np.load(array_file_path)
        elif isinstance(v, dict):
            found_slot_range = schemaview.get_class(found_slot.range)
            v = iterate_element(v, found_slot_range, schemaview)
        # else: do not transform v
        ret_dict[k] = v

    return ret_dict


class YAMLNumpyLoader(Loader):

    def load_any(self, source: str, **kwargs):
        """ Return element formatted as a YAML string with paths to numpy files containing the ndarrays"""
        return self.load(source, **kwargs)

    def loads(self, source: str, **kwargs):
        """ Return element formatted as a YAML string with paths to numpy files containing the ndarrays"""
        return self.load(source, **kwargs)

    def load(self, source: str, target_class: Type[Union[YAMLRoot, BaseModel]], schemaview: SchemaView, **kwargs):
        """ Return element formatted as a YAML string with paths to numpy files containing the ndarrays"""
        input_dict = yaml.safe_load(source)

        element_type = schemaview.get_class(target_class.__name__)
        element = iterate_element(input_dict, element_type, schemaview)
        obj = target_class(**element)

        return obj


