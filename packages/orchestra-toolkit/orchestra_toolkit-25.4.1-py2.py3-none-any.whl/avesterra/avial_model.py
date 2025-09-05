"""Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

from abc import abstractmethod
from threading import Lock
import json
from typing import Dict, Generic, Iterable, List, TypeVar
from typing_extensions import deprecated
import avesterra.avial as av
from avesterra.taxonomy import AvAttribute
from tabulate import tabulate


class AvialModel:
    """
    Thread-safe data structure to hold an Avial model.
    more info on the Avial model can be found in the wiki:
    https://docs.ledr.io/en/the-orchestra-platfrom/avial-model

    You can either build a model from scratch or load it from a JSON dictionary,
    which you can get by retrieving an existing entity and parsing the JSON string.
    You can turn the model back into a JSON dictionary to store it back in the
    entity.

    Do note that retrieve + modify + store paradigm is not thread safe and can
    lead to data loss if multiple threads (perhaps multiple clients) concurrently
    modify the same entity.
    When doing a lot of editing or when multiple clients are involved, one has
    to be careful to not overwrite changes made by other clients.

    Every aspect of the avial model can either be accessed through it's unique
    key or by index.
    Unique key are:
    - Properties: the key
    - Attributions: the attribute
    - Trait: the key
    - Facts: the attribute
    - Facets: the name
    - Factors: the key
    - Features: the key
    - Fields: the name
    - Frames: the key

    If you try to access the NULL key, the first occurence of the NULL key will
    be returned.
    If you try to access a key that does not exist, a new object will be created

    This model makes it possible to create multiple objects with the same unique
    key by using the `append` method recklessly, which is not legal in Avial.
    You are responsible for ensuring it does not happen.
    Though it is possible to have multiple objects with the NULL key, the
    avial STORE operation does NOT support it. Therefore, this data structure
    only helps you to parse such models, not to create them.
    If you need to create such a model with multiple objects with the NULL key,
    you will need to use the specific avial methods insert/remove which support
    such operations by index.

    Note that index are 0-based, unlike the usual 1-based indexing in Avial.

    Example:
    ```
    auth = AvAuthorization("c08d118a-0ebf-4889-b5de-bbabbf841403")
    entity = av.AvEntity(0, 0, 177185)

    # Step 1 - Retrieve the entity
    val = av.retrieve_entity(entity, auth)

    # Step 2 - Parse the JSON string into an avial model
    model = AvialModel.from_interchange(val)

    # Step 3 - Read and modify it
    my_value = model.facts[AvAttribute.NAME].facets["first"].value = AvValue.encode_text("New first name")
    my_value = model.facts[AvAttribute.NAME].facets["first"].factors[0].value = AvValue.encode_text("I'm the first factor")
    my_value = model.facts[AvAttribute.NAME].facets["first"].factors["another"].value = AvValue.encode_text("I'm another factor")

    # Step 4 - Store the updated model back to the entity
    obj.store_entity(
        entity,
        AvMode.REPLACE,
        model.to_interchange(),
        auth,
    )
    ```
    """

    def __init__(self):
        self.name: str = ""
        self.key: str = ""
        self.data: int = 0
        self.attributions = AttributionList()
        self.collections = CollectionList()
        self.facts = FactList()
        self.properties = PropertyList()
        self.tables = TableList()

    def __eq__(self, other):
        if not isinstance(other, AvialModel):
            return False
        return (
            self.name == other.name
            and self.key == other.key
            and self.data == other.data
            and self.attributions == other.attributions
            and self.collections == other.collections
            and self.facts == other.facts
            and self.properties == other.properties
            and self.tables == other.tables
        )

    def pretty_str(self, indent: int = 0):
        indent_str = " " * indent
        name_str = f"{indent_str}Name: {self.name}\n"
        key_str = f"{indent_str}Key: {self.key}\n"
        if self.data:
            data_str = f"{indent_str}Data: {self.data}\n"
        else:
            data_str = ""
        if self.attributions:
            attributions_str = f"{indent_str}Attributions ({len(self.attributions)}):\n{self.attributions.pretty_str(indent+4)}\n"
        else:
            attributions_str = ""
        if self.collections:
            collections_str = f"{indent_str}Collections ({len(self.collections)}):\n{self.collections.pretty_str(indent+4)}\n"
        else:
            collections_str = ""
        if self.facts:
            facts_str = f"{indent_str}Facts ({len(self.facts)}):\n{self.facts.pretty_str(indent+4)}\n"
        else:
            facts_str = ""
        if self.properties:
            properties_str = f"{indent_str}Properties ({len(self.properties)}):\n{self.properties.pretty_str(indent+4)}\n"
        else:
            properties_str = ""
        if self.tables:
            tables_str = f"{indent_str}Tables ({len(self.tables)}):\n{self.tables.pretty_str(indent+4)}\n"
        else:
            tables_str = ""

        return f"{name_str}{key_str}{data_str}{attributions_str}{collections_str}{facts_str}{properties_str}{tables_str}"

    @staticmethod
    def from_interchange(value: av.AvValue):
        """
        Convenience method
        """
        s = value.decode_interchange()
        return AvialModel.from_json_dict(json.loads(s))

    @staticmethod
    def retrieve(entity: av.AvEntity, timeout: av.AvTimeout, auth: av.AvAuthorization):
        """
        Convenience method to retrieve an entity and get the result as an AvialModel
        """
        return AvialModel.from_interchange(av.retrieve_entity(entity, timeout, auth))

    def to_interchange(self) -> av.AvValue:
        return av.AvValue.encode_interchange(json.dumps(self.to_json_dict()))

    @staticmethod
    def from_json_dict(d: Dict):
        model = AvialModel()

        model.name = d.get("Name", "")
        model.key = d.get("Key", "")
        model.data = d.get("Data", 0)

        model.attributions = AttributionList.from_json_list(d.get("Attributions", []))
        model.collections = CollectionList.from_json_list(d.get("Collections", []))
        model.facts = FactList.from_json_list(d.get("Facts", []))
        model.properties = PropertyList.from_json_list(d.get("Properties", []))
        model.tables = TableList.from_json_list(d.get("Tables", []))

        return model

    def to_json_dict(self):
        d = {}

        d["Model"] = "Avial"
        d["Version"] = "V6.0"
        d["Format"] = 2
        if self.name:
            d["Name"] = self.name
        if self.key:
            d["Key"] = self.key
        if self.data:
            d["Data"] = self.data
        if self.attributions:
            d["Attributions"] = self.attributions.to_json_list()
        if self.collections:
            d["Collections"] = self.collections.to_json_list()
        if self.facts:
            d["Facts"] = self.facts.to_json_list()
        if self.properties:
            d["Properties"] = self.properties.to_json_list()
        if self.tables:
            d["Tables"] = self.tables.to_json_list()
        return d


Tv = TypeVar("Tv")
Tk = TypeVar("Tk")


class AspectList(Generic[Tv, Tk]):
    """
    Dictionnary-like data structure where there can be multiple items with NULL key.
    Items with non-null key have unique key, and can be accessed by their key.
    Any item, including those with NULL key, can be accessed by index.
    """

    items: List[Tv]
    mutex: Lock

    def __init__(self, items: Iterable[Tv] | None = None):
        if items is not None:
            self.items = list(items)
        else:
            self.items = []
        self.mutex = Lock()

    @abstractmethod
    def pretty_str(self, indent: int = 0) -> str:
        pass

    @abstractmethod
    def _keyof(self, item: Tv) -> Tk:
        pass

    @abstractmethod
    def _default_item(self, key: Tk) -> Tv:
        pass

    @abstractmethod
    def _keytype(self) -> type[Tk]:
        """This is needed because python generics aren't very smart."""
        pass

    def __bool__(self):
        return bool(self.items)

    def __len__(self):
        return len(self.items)

    def __eq__(self, other):
        return self.items == other.items

    def __str__(self):
        return "[" + ", ".join(str(p) for p in self.items) + "]"

    def __iter__(self):
        return iter(self.items)

    def __getitem__(self, handle: int | Tk) -> Tv:
        with self.mutex:
            res = self._get_opt(handle)
            if res is None:
                if not isinstance(handle, self._keytype()):
                    raise IndexError()
                res = self._default_item(handle)
                self.items.append(res)
            return res

    def __setitem__(self, handle: int | Tk, value: Tv):
        if isinstance(handle, self._keytype()):
            expected = self._keyof(value)
            if handle != expected:
                raise ValueError(f"Key mismatch: {handle} != {expected}")
        with self.mutex:
            idx = self._get_idx(handle)
            if idx is None:
                self.items.append(value)
            else:
                self.items[idx] = value

    def get_opt(self, handle: int | Tk) -> Tv | None:
        with self.mutex:
            return self._get_opt(handle)

    def _get_opt(self, handle: int | Tk) -> Tv | None:
        """
        Returns None if the item does not exist
        """
        idx = self._get_idx(handle)
        if idx is None:
            return None
        return self.items[idx]

    def _get_idx(self, item: int | Tk) -> int | None:
        """If return an int, it's guaranteed to be a valid index."""
        if isinstance(item, self._keytype()):
            for idx, p in enumerate(self.items):
                if self._keyof(p) == item:
                    return idx
            return None
        elif isinstance(item, int):
            if 0 <= item < len(self.items):
                return item
            return None
        else:
            raise TypeError(f"Invalid type for item: {type(item)}")

    def append(self, value: Tv):
        with self.mutex:
            self.items.append(value)

    def __contains__(self, item: int | Tk) -> bool:
        with self.mutex:
            return self._get_idx(item) is not None

    @deprecated("Use `in` instead")
    def has(self, item: int | Tk) -> bool:
        return item in self

    def pop(self, item: int | Tk) -> Tv | None:
        with self.mutex:
            idx = self._get_idx(item)
            if idx is None:
                return None
            res = self.items[idx]
            del self.items[idx]
            return res

    def remove(self, handle: int | Tk):
        self.pop(handle)


class Annotation:
    def __init__(
        self,
        attribute: AvAttribute = AvAttribute.NULL,
        name: av.AvName = av.NULL_NAME,
        value: av.AvValue = av.NULL_VALUE,
    ):
        self.attribute: AvAttribute = attribute
        self.name: av.AvName = name
        self.value: av.AvValue = value

    def __eq__(self, other):
        if not isinstance(other, Annotation):
            return False
        return (
            self.attribute == other.attribute
            and self.name == other.name
            and self.value == other.value
        )

    def pretty_str(self, indent: int = 0):
        indent_str = " " * indent
        return indent_str + str(self)

    def __str__(self):
        return f"{self.attribute.name}_ATTRIBUTE\t{self.name}: {self.value}"

    @staticmethod
    def from_json_list(li: List):
        a = Annotation()

        attribute_name = li[0].removesuffix("_ATTRIBUTE")
        a.attribute = AvAttribute[attribute_name]
        a.name = li[1]
        a.value = av.AvValue.from_json(li[2])

        return a

    def to_json_list(self):
        li = []
        li.append(self.attribute.name + "_ATTRIBUTE")
        li.append(self.name)
        li.append(self.value.obj())
        return li


class AnnotationList(AspectList[Annotation, AvAttribute]):
    def pretty_str(self, indent: int = 0) -> str:
        return "\n".join([p.pretty_str(indent) for p in self])

    def _keyof(self, item: Annotation) -> AvAttribute:
        return item.attribute

    def _default_item(self, key: AvAttribute) -> Annotation:
        return Annotation(attribute=key)

    def _keytype(self) -> type[AvAttribute]:
        return AvAttribute

    @staticmethod
    def from_json_list(li: list):
        return AnnotationList(Annotation.from_json_list(p) for p in li)

    def to_json_list(self):
        return [p.to_json_list() for p in self]


class Property:
    def __init__(
        self,
        name: str = "",
        key: str = "",
        value: av.AvValue = av.NULL_VALUE,
        annotations: Iterable[Annotation] | None = None,
    ):
        self.name: av.AvName = name
        self.key: av.AvKey = key
        self.value: av.AvValue = value
        self.annotations = AnnotationList(annotations or [])

    def __eq__(self, other):
        if not isinstance(other, Property):
            return False
        return (
            self.name == other.name
            and self.key == other.key
            and self.value == other.value
            and self.annotations == other.annotations
        )

    def pretty_str(self, indent: int = 0):
        if self.annotations:
            ann = "\n" + self.annotations.pretty_str(indent + 4)
        else:
            ann = ""
        indent_str = " " * indent
        return indent_str + f"{self.name}\t[{self.key}]: {self.value}" + ann

    @staticmethod
    def from_json_list(li: List):
        p = Property()

        p.name = li[0]
        p.key = li[1]
        p.value = av.AvValue.from_json(li[2])
        if len(li) > 3:
            p.annotations = AnnotationList.from_json_list(li[3])
        else:
            p.annotations = AnnotationList()

        return p

    def to_json_list(self):
        li = []
        li.append(self.name)
        li.append(self.key)
        li.append(self.value.obj())
        if self.annotations:
            li.append(self.annotations.to_json_list())
        return li


class PropertyList(AspectList[Property, str]):
    def pretty_str(self, indent: int = 0) -> str:
        return "\n".join([p.pretty_str(indent) for p in self])

    def _keyof(self, item: Property) -> str:
        return item.key

    def _default_item(self, key: str) -> Property:
        return Property(key=key)

    def _keytype(self) -> type[str]:
        return str

    @staticmethod
    def from_json_list(li: list):
        return PropertyList(Property.from_json_list(p) for p in li)

    def to_json_list(self):
        return [p.to_json_list() for p in self]


class Fact:
    def __init__(
        self,
        attribute: AvAttribute,
        value: av.AvValue = av.NULL_VALUE,
    ):
        self.attribute = attribute
        self.name = ""
        self.value = value
        self.facets = FacetList()
        self.features = FeatureList()
        self.fields = FieldList()
        self.frames = FrameList(self.fields)

    def __eq__(self, other):
        if not isinstance(other, Fact):
            return False
        return (
            self.attribute == other.attribute
            and self.name == other.name
            and self.value == other.value
            and self.facets == other.facets
            and self.features == other.features
            and self.fields == other.fields
            and self.frames == other.frames
        )

    def pretty_str(self, indent: int = 0):
        indent_str = " " * indent
        header_str = f"{indent_str}Fact: {self.attribute.name:<15} {self.name}\n"
        value_str = (
            f"{indent_str}Value: {self.value.tag().name}: {self.value.decode()}\n"
        )
        if self.facets:
            facet_str = f"{indent_str}Facets ({len(self.facets)}):\n{self.facets.pretty_str(indent+4)}\n"
        else:
            facet_str = ""
        if self.features:
            feature_str = f"{indent_str}Features ({len(self.features)}):\n{self.features.pretty_str(indent+4)}\n"
        else:
            feature_str = ""
        if self.fields:
            field_str = f"{indent_str}Fields ({len(self.fields)}):\n{self.fields.pretty_str(indent+4)}\n"
        else:
            field_str = ""
        if self.frames:
            frame_str = f"{indent_str}Frames ({len(self.frames)}):\n{self.frames.pretty_str(indent+4)}\n"
        else:
            frame_str = ""
        return f"{header_str}{value_str}{facet_str}{feature_str}{field_str}{frame_str}"

    @staticmethod
    def from_json_list(li: List):
        f = Fact(AvAttribute.NULL)

        attribute_name = li[0].removesuffix("_ATTRIBUTE")
        f.attribute = AvAttribute[attribute_name]
        f.name = li[1]
        f.value = av.AvValue.from_json(li[2])
        f.facets = FacetList.from_json_list(li[3])
        f.features = FeatureList.from_json_list(li[4])
        f.fields = FieldList.from_json_list(li[5])
        f.frames = FrameList.from_json_list(li[6], f.fields)
        f.frames.fields = f.fields

        return f

    def to_json_list(self):
        li = []
        li.append(self.attribute.name + "_ATTRIBUTE")
        li.append(self.name)
        li.append(self.value.obj())
        li.append(self.facets.to_json_list())
        li.append(self.features.to_json_list())
        li.append(self.fields.to_json_list())
        li.append(self.frames.to_json_list())
        return li


class FactList(AspectList[Fact, AvAttribute]):
    def pretty_str(self, indent: int = 0):
        return "".join([f.pretty_str(indent) for f in self])

    def _keyof(self, item: Fact) -> AvAttribute:
        return item.attribute

    def _default_item(self, key: AvAttribute) -> Fact:
        return Fact(key)

    def _keytype(self) -> type[AvAttribute]:
        return AvAttribute

    @staticmethod
    def from_json_list(li: list):
        return FactList(Fact.from_json_list(p) for p in li)

    def to_json_list(self):
        return [p.to_json_list() for p in self]


class Facet:
    def __init__(self, name: str, value: av.AvValue = av.NULL_VALUE):
        self.name = name
        self.value = value
        self.factors = FactorList()

    def __eq__(self, other):
        if not isinstance(other, Facet):
            return False
        return (
            self.name == other.name
            and self.value == other.value
            and self.factors == other.factors
        )

    def pretty_str(self, indent: int = 0):
        indent_str = " " * indent
        if self.factors:
            factor_str = f"{indent_str}Factors ({len(self.factors)}):\n{self.factors.pretty_str(indent+4)}\n"
        else:
            factor_str = ""
        return f"{indent_str}Name: {self.name}\n{indent_str}Value: {self.value}\n{factor_str}"

    @staticmethod
    def from_json_list(li: List):
        f = Facet("")

        f.name = li[0]
        f.value = av.AvValue.from_json(li[1])
        f.factors = FactorList.from_json_list(li[2])

        return f

    def to_json_list(self):
        li = []
        li.append(self.name)
        li.append(self.value.obj())
        li.append(FactorList.to_json_list(self.factors))
        return li


class FacetList(AspectList[Facet, str]):
    def pretty_str(self, indent: int = 0):
        return "\n".join([f.pretty_str(indent) for f in self])

    def _keyof(self, item: Facet) -> str:
        return item.name

    def _default_item(self, key: str) -> Facet:
        return Facet(name=key)

    def _keytype(self) -> type[str]:
        return str

    @staticmethod
    def from_json_list(li: List):
        return FacetList([Facet.from_json_list(f) for f in li])

    def to_json_list(self):
        return [f.to_json_list() for f in self]


class Factor:
    def __init__(self, key: str, value: av.AvValue = av.NULL_VALUE):
        self.key = key
        self.value = value

    def __eq__(self, other):
        if not isinstance(other, Factor):
            return False
        return self.key == other.key and self.value == other.value

    def pretty_str(self, indent: int = 0):
        indent_str = " " * indent
        return f"{indent_str}{self.key}: {self.value}"

    @staticmethod
    def from_json_list(li: List):
        f = Factor("")

        f.key = li[0]
        f.value = av.AvValue.from_json(li[1])

        return f

    def to_json_list(self):
        li = []
        li.append(self.key)
        li.append(self.value.obj())
        return li


class FactorList(AspectList[Factor, str]):
    def pretty_str(self, indent: int = 0):
        return "\n".join([f.pretty_str(indent) for f in self])

    def _keyof(self, item: Factor) -> str:
        return item.key

    def _default_item(self, key: str) -> Factor:
        return Factor(key)

    def _keytype(self) -> type[str]:
        return str

    @staticmethod
    def from_json_list(li: List):
        return FactorList(Factor.from_json_list(f) for f in li)

    def to_json_list(self):
        return [f.to_json_list() for f in self]


class Feature:
    def __init__(self, name: str, key: str, value: av.AvValue = av.NULL_VALUE):
        self.name = name
        self.key = key
        self.value = value

    def __eq__(self, other):
        if not isinstance(other, Feature):
            return False
        return (
            self.name == other.name
            and self.key == other.key
            and self.value == other.value
        )

    def pretty_str(self, indent: int = 0):
        indent_str = " " * indent
        return f"{indent_str}{self.name}\t[{self.key}]: {self.value}"

    @staticmethod
    def from_json_list(li: List):
        f = Feature("", "")

        f.name = li[0]
        f.key = li[1]
        f.value = av.AvValue.from_json(li[2])

        return f

    def to_json_list(self):
        li = []
        li.append(self.name)
        li.append(self.key)
        li.append(self.value.obj())
        return li


class FeatureList(AspectList[Feature, str]):
    def pretty_str(self, indent: int = 0):
        return "\n".join([f.pretty_str(indent) for f in self])

    def _keyof(self, item: Feature) -> str:
        return item.key

    def _default_item(self, key: str) -> Feature:
        return Feature(name="", key=key)

    def _keytype(self) -> type[str]:
        return str

    @staticmethod
    def from_json_list(li: List):
        return FeatureList(Feature.from_json_list(f) for f in li)

    def to_json_list(self):
        return [f.to_json_list() for f in self]


class Field:
    def __init__(self, name: str, value: av.AvValue = av.NULL_VALUE):
        self.name = name
        self.value = value

    def __eq__(self, other):
        if not isinstance(other, Field):
            return False
        return self.name == other.name and self.value == other.value

    def pretty_str(self, indent: int = 0):
        indent_str = " " * indent
        return f"{indent_str}{self.name}: {self.value}"

    @staticmethod
    def from_json_list(li: List):
        f = Field("")

        f.name = li[0]
        f.value = av.AvValue.from_json(li[1])

        return f

    def to_json_list(self):
        li = []
        li.append(self.name)
        li.append(self.value.obj())
        return li


class FieldList(AspectList[Field, str]):
    def pretty_str(self, indent: int = 0):
        return "\n".join([f.pretty_str(indent) for f in self])

    def _keyof(self, item: Field) -> str:
        return item.name

    def _default_item(self, key: str) -> Field:
        return Field(name=key)

    def _keytype(self) -> type[str]:
        return str

    def index_of(self, name: str):
        with self.mutex:
            for i, f in enumerate(self.items):
                if f.name == name:
                    return i
        return -1

    @staticmethod
    def from_json_list(li: list):
        return FieldList(Field.from_json_list(p) for p in li)

    def to_json_list(self):
        return [f.to_json_list() for f in self]


class Frame:
    def __init__(self, key: str, values: List[av.AvValue] | None = None):
        self.key = key
        self.values: List[av.AvValue] = values if values is not None else []
        self.fields: FieldList | None = None

    def __eq__(self, other):
        if not isinstance(other, Frame):
            return False
        return self.key == other.key and self.values == other.values

    def __len__(self):
        return len(self.values)

    def __getitem__(self, item: int | str):
        assert self.fields is not None
        if isinstance(item, int):
            return self.values[item]
        elif isinstance(item, str):
            idx = self.fields.index_of(item)
            if idx != -1:
                return self.values[idx]
            raise ValueError(f"Field '{item}' not found")
        else:
            raise TypeError(f"Invalid type for item: {type(item)}")

    def __setitem__(self, item: int | str, value: av.AvValue):
        assert self.fields is not None
        if isinstance(item, int):
            self.values[item] = value
        elif isinstance(item, str):
            idx = self.fields.index_of(item)
            if idx != -1:
                self.values[idx] = value
                return
            raise ValueError(
                f"Field '{item}' not found, available fields: {', '.join(f.name for f in self.fields)}"
            )
        else:
            raise TypeError(f"Invalid type for item: {type(item)}")

    @staticmethod
    def from_json_list(li: List):
        f = Frame("")

        f.key = li[0]
        f.values = [av.AvValue.from_json(f) for f in li[1]]

        return f

    def to_json_list(self):
        li = []
        li.append(self.key)
        li.append([f.obj() for f in self.values])
        return li


class FrameList(AspectList[Frame, str]):
    def __init__(self, fields: FieldList):
        super().__init__()
        self.fields = fields

    def pretty_str(self, indent: int = 0):
        indent_str = " " * indent
        headers = [f.name for f in self.fields]
        rows = []
        for f in self:
            rows.append([f.key] + [f"{v.tag().name}: {v.decode()}" for v in f.values])

        res = tabulate(rows, headers=headers)
        res = indent_str + res.replace("\n", "\n" + indent_str)

        return res

    def _keyof(self, item: Frame) -> str:
        return item.key

    def _default_item(self, key: str) -> Frame:
        assert self.fields is not None
        res = Frame(key)
        res.fields = self.fields
        for f in self.fields:
            res.values.append(f.value)
        return res

    def _keytype(self) -> type[str]:
        return str

    @staticmethod
    def from_json_list(li: List, fields: FieldList):
        model = FrameList(fields)

        for f in li:
            frame = Frame.from_json_list(f)
            frame.fields = model.fields
            model.append(frame)

        return model

    def to_json_list(self):
        return [f.to_json_list() for f in self]


class Attribution:
    def __init__(
        self,
        attribute: AvAttribute,
        name: str = "",
        value: av.AvValue = av.NULL_VALUE,
    ):
        self.attribute = attribute
        self.name = name
        self.value = value
        self.traits = TraitList()

    def __eq__(self, other):
        if not isinstance(other, Attribution):
            return False
        return (
            self.attribute == other.attribute
            and self.name == other.name
            and self.value == other.value
            and self.traits == other.traits
        )

    def pretty_str(self, indent: int = 0):
        indent_str = " " * indent
        header_str = f"{indent_str}Attribution: {self.attribute.name:<15} {self.name}\n"
        value_str = (
            f"{indent_str}Value: {self.value.tag().name}: {self.value.decode()}\n"
        )
        if self.traits:
            trait_str = f"{indent_str}Traits ({len(self.traits)}):\n{self.traits.pretty_str(indent+4)}\n"
        else:
            trait_str = ""
        return f"{header_str}{value_str}{trait_str}"

    @staticmethod
    def from_json_list(li: List):
        f = Attribution(AvAttribute.NULL)

        print(li)

        attribute_name = li[0].removesuffix("_ATTRIBUTE")
        f.attribute = AvAttribute[attribute_name]
        f.name = li[1]
        f.value = av.AvValue.from_json(li[2])
        f.traits = TraitList.from_json_list(li[3])

        return f

    def to_json_list(self):
        li = []
        li.append(self.attribute.name + "_ATTRIBUTE")
        li.append(self.name)
        li.append(self.value.obj())
        li.append(self.traits.to_json_list())
        return li


class AttributionList(AspectList[Attribution, AvAttribute]):
    def pretty_str(self, indent: int = 0):
        return "".join([f.pretty_str(indent) for f in self])

    def _keyof(self, item: Attribution) -> AvAttribute:
        return item.attribute

    def _default_item(self, key: AvAttribute) -> Attribution:
        return Attribution(key)

    def _keytype(self) -> type[AvAttribute]:
        return AvAttribute

    @staticmethod
    def from_json_list(li: List):
        return AttributionList(Attribution.from_json_list(f) for f in li)

    def to_json_list(self):
        return [f.to_json_list() for f in self]


class Trait:
    def __init__(self, name: str, key: str, value: av.AvValue = av.NULL_VALUE):
        self.name = name
        self.key = key
        self.value = value

    def __eq__(self, other):
        if not isinstance(other, Trait):
            return False
        return (
            self.name == other.name
            and self.key == other.key
            and self.value == other.value
        )

    def pretty_str(self, indent: int = 0):
        indent_str = " " * indent
        return f"{indent_str}{self.name}\t[{self.key}]: {self.value}"

    @staticmethod
    def from_json_list(li: List):
        f = Trait("", "")

        f.name = li[0]
        f.key = li[1]
        f.value = av.AvValue.from_json(li[2])

        return f

    def to_json_list(self):
        li = []
        li.append(self.name)
        li.append(self.key)
        li.append(self.value.obj())
        return li


class TraitList(AspectList[Trait, str]):
    def pretty_str(self, indent: int = 0):
        return "\n".join([f.pretty_str(indent) for f in self])

    def _keyof(self, item: Trait) -> str:
        return item.key

    def _default_item(self, key: str) -> Trait:
        return Trait(name="", key=key)

    def _keytype(self) -> type[str]:
        return str

    @staticmethod
    def from_json_list(li: List):
        return TraitList(Trait.from_json_list(f) for f in li)

    def to_json_list(self):
        return [f.to_json_list() for f in self]


class Item:
    def __init__(
        self,
        attribute: AvAttribute = av.AvAttribute.NULL,
        name: str = "",
        value: av.AvValue = av.NULL_VALUE,
    ):
        self.attribute = attribute
        self.name = name
        self.value = value

    def __eq__(self, other):
        if not isinstance(other, Item):
            return False
        return (
            self.attribute == other.attribute
            and self.name == other.name
            and self.value == other.value
        )

    def pretty_str(self, indent: int = 0):
        indent_str = " " * indent
        return f"{indent_str}{self.attribute.name}\t[{self.name}]: {self.value}"

    @staticmethod
    def from_json_list(li: List):
        item = Item()

        attribute_name = li[0].removesuffix("_ATTRIBUTE")
        item.attribute = AvAttribute[attribute_name]

        item.name = li[1]
        item.value = av.AvValue.from_json(li[2])

        return item

    def to_json_list(self):
        li = []
        li.append(self.attribute.name + "_ATTRIBUTE")
        li.append(self.name)
        li.append(self.value.obj())
        return li


class ItemList(AspectList[Item, av.AvValue]):
    def pretty_str(self, indent: int = 0):
        return "\n".join([f.pretty_str(indent) for f in self])

    def _keyof(self, item: Item) -> av.AvValue:
        return item.value

    def _default_item(self, key: av.AvValue) -> Item:
        return Item(value=key)

    def _keytype(self) -> type[av.AvValue]:
        return av.AvValue

    @staticmethod
    def from_json_list(li: List):
        return ItemList(Item.from_json_list(f) for f in li)

    def to_json_list(self):
        return [f.to_json_list() for f in self]


class Collection:
    def __init__(self, name: str, key: str, value: av.AvValue = av.NULL_VALUE):
        self.name = name
        self.key = key
        self.value = value
        self.items = ItemList()

    def __eq__(self, other):
        if not isinstance(other, Collection):
            return False
        return (
            self.name == other.name
            and self.key == other.key
            and self.value == other.value
            and self.items == other.items
        )

    def pretty_str(self, indent: int = 0):
        indent_str = " " * indent
        header_str = (
            f"{indent_str}Collection: {self.name}\t[{self.key}]: {self.value}\n"
        )
        items_str = f"{indent_str}Items ({len(self.items)}):\n{self.items.pretty_str(indent+4)}\n"
        return f"{header_str}{items_str}"

    @staticmethod
    def from_json_list(li: List):
        f = Collection("", "")

        f.name = li[0]
        f.key = li[1]
        f.value = av.AvValue.from_json(li[2])
        f.items = ItemList.from_json_list(li[3])

        return f

    def to_json_list(self):
        li = []
        li.append(self.name)
        li.append(self.key)
        li.append(self.value.obj())
        li.append(self.items.to_json_list())
        return li


class CollectionList(AspectList[Collection, str]):
    def pretty_str(self, indent: int = 0):
        return "\n".join([f.pretty_str(indent) for f in self])

    def _keyof(self, item: Collection) -> str:
        return item.key

    def _default_item(self, key: str) -> Collection:
        return Collection(name="", key=key)

    def _keytype(self) -> type[str]:
        return str

    @staticmethod
    def from_json_list(li: List):
        return CollectionList(Collection.from_json_list(f) for f in li)

    def to_json_list(self):
        return [f.to_json_list() for f in self]


class Column:
    def __init__(self, name: str, value: av.AvValue = av.NULL_VALUE):
        self.name = name
        self.value = value

    def __eq__(self, other):
        if not isinstance(other, Column):
            return False
        return self.name == other.name and self.value == other.value

    def pretty_str(self, indent: int = 0):
        indent_str = " " * indent
        return f"{indent_str}{self.name}: {self.value}"

    @staticmethod
    def from_json_list(li: List):
        f = Column("")

        f.name = li[0]
        f.value = av.AvValue.from_json(li[1])

        return f

    def to_json_list(self):
        li = []
        li.append(self.name)
        li.append(self.value.obj())
        return li


class ColumnList(AspectList[Column, str]):
    def pretty_str(self, indent: int = 0):
        return "\n".join([f.pretty_str(indent) for f in self])

    def _keyof(self, item: Column) -> str:
        return item.name

    def _default_item(self, key: str) -> Column:
        return Column(name=key)

    def _keytype(self) -> type[str]:
        return str

    def index_of(self, name: str):
        with self.mutex:
            for i, f in enumerate(self.items):
                if f.name == name:
                    return i
        return -1

    @staticmethod
    def from_json_list(li: list):
        return ColumnList(Column.from_json_list(p) for p in li)

    def to_json_list(self):
        return [f.to_json_list() for f in self]


class Row:
    def __init__(self, key: str, values: List[av.AvValue] | None = None):
        self.key = key
        self.value = av.NULL_VALUE
        self.values: List[av.AvValue] = values if values is not None else []
        self.columns: ColumnList | None = None

    def __eq__(self, other):
        if not isinstance(other, Row):
            return False
        return (
            self.key == other.key
            and self.values == other.values
            and self.value == other.value
        )

    def __len__(self):
        return len(self.values)

    def __getitem__(self, item: int | str):
        assert self.columns is not None
        if isinstance(item, int):
            return self.values[item]
        elif isinstance(item, str):
            idx = self.columns.index_of(item)
            if idx != -1:
                return self.values[idx]
            raise ValueError(f"Column '{item}' not found")
        else:
            raise TypeError(f"Invalid type for item: {type(item)}")

    def __setitem__(self, item: int | str, value: av.AvValue):
        assert self.columns is not None
        if isinstance(item, int):
            self.values[item] = value
        elif isinstance(item, str):
            idx = self.columns.index_of(item)
            if idx != -1:
                self.values[idx] = value
                return
            raise ValueError(
                f"Column '{item}' not found, available columns: {', '.join(f.name for f in self.columns)}"
            )
        else:
            raise TypeError(f"Invalid type for item: {type(item)}")

    @staticmethod
    def from_json_list(li: List):
        f = Row("")

        f.key = li[0]
        f.value = av.AvValue.from_json(li[1])
        f.values = [av.AvValue.from_json(f) for f in li[2]]

        return f

    def to_json_list(self):
        li = []
        li.append(self.key)
        li.append(self.value.obj())
        li.append([f.obj() for f in self.values])
        return li


class RowList(AspectList[Row, str]):
    def __init__(self, columns: ColumnList):
        super().__init__()
        self.columns = columns

    def pretty_str(self, indent: int = 0):
        indent_str = " " * indent
        tab_headers = []
        tab_headers.append("\n(row key)")
        tab_headers.append("\n(row default value)")
        for column in self.columns:
            tab_headers.append(
                f"{column.name}\n({column.value.tag().name}: {column.value.decode()})"
            )

        tab_rows = []
        for row in self:
            x = []
            x.append(row.key)
            x.append(f"({row.value.tag().name}: {row.value.decode()})")
            x.extend(f"{v.tag().name}: {v.decode()}" for v in row.values)
            tab_rows.append(x)

        res = tabulate(tab_rows, headers=tab_headers)
        res = indent_str + res.replace("\n", "\n" + indent_str)

        return res

    def _keyof(self, item: Row) -> str:
        return item.key

    def _default_item(self, key: str) -> Row:
        assert self.columns is not None
        res = Row(key)
        res.columns = self.columns
        for f in self.columns:
            res.values.append(f.value)
        return res

    def _keytype(self) -> type[str]:
        return str

    @staticmethod
    def from_json_list(li: List, columns: ColumnList):
        model = RowList(columns)

        for f in li:
            row = Row.from_json_list(f)
            row.columns = model.columns
            model.append(row)

        return model

    def to_json_list(self):
        return [f.to_json_list() for f in self]


class Table:
    def __init__(self, key: str):
        self.name = ""
        self.key = key
        self.columns = ColumnList()
        self.rows = RowList(self.columns)

    def __eq__(self, other):
        if not isinstance(other, Table):
            return False
        return (
            self.key == other.key
            and self.columns == other.columns
            and self.rows == other.rows
        )

    def pretty_str(self, indent: int = 0):
        indent_str = " " * indent
        header_str = f"{indent_str}Table: {self.name}\t[{self.key}]\t({len(self.rows)} rows, {len(self.columns)} columns)\n"
        table_str = self.rows.pretty_str(indent + 4)
        return f"{header_str}{table_str}"

    @staticmethod
    def from_json_list(li: List):
        f = Table("")

        f.name = li[0]
        f.key = li[1]
        f.columns = ColumnList.from_json_list(li[2])
        f.rows = RowList.from_json_list(li[3], f.columns)

        return f

    def to_json_list(self):
        li = []
        li.append(self.name)
        li.append(self.key)
        li.append(self.columns.to_json_list())
        li.append(self.rows.to_json_list())
        return li


class TableList(AspectList[Table, str]):
    def pretty_str(self, indent: int = 0):
        return "\n".join([f.pretty_str(indent) for f in self])

    def _keyof(self, item: Table) -> str:
        return item.key

    def _default_item(self, key: str) -> Table:
        return Table(key)

    def _keytype(self) -> type[str]:
        return str

    @staticmethod
    def from_json_list(li: List):
        return TableList(Table.from_json_list(f) for f in li)

    def to_json_list(self):
        return [f.to_json_list() for f in self]
