"""Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

from avesterra.avial import *
from avesterra.taxonomy import AvAttribute, AvAspect
import avesterra.aspects as aspects


def insert_item(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    deferred: bool = False,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    aspects.insert(
        aspect=AvAspect.ITEM,
        entity=entity,
        attribute=attribute,
        name=name,
        key=key,
        value=value,
        index=index,
        instance=instance,
        deferred=deferred,
        authorization=authorization,
    )


def remove_item(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    deferred: bool = False,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    aspects.remove(
        aspect=AvAspect.ITEM,
        entity=entity,
        key=key,
        index=index,
        instance=instance,
        deferred=deferred,
        authorization=authorization,
    )


def replace_item(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    deferred: bool = False,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    aspects.replace(
        aspect=AvAspect.ITEM,
        entity=entity,
        attribute=attribute,
        name=name,
        key=key,
        value=value,
        index=index,
        instance=instance,
        deferred=deferred,
        authorization=authorization,
    )


def find_item(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvIndex:
    return aspects.find(
        aspect=AvAspect.ITEM,
        entity=entity,
        attribute=attribute,
        name=name,
        key=key,
        index=index,
        instance=instance,
        authorization=authorization,
    )


def include_item(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    deferred: bool = False,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    return aspects.include(
        aspect=AvAspect.ITEM,
        entity=entity,
        attribute=attribute,
        name=name,
        key=key,
        value=value,
        deferred=deferred,
        authorization=authorization,
    )


def exclude_item(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    deferred: bool = False,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    return aspects.exclude(
        aspect=AvAspect.ITEM,
        entity=entity,
        key=key,
        value=value,
        deferred=deferred,
        authorization=authorization,
    )


def set_item(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    deferred: bool = False,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    return aspects.set(
        aspect=AvAspect.ITEM,
        entity=entity,
        attribute=attribute,
        name=name,
        key=key,
        value=value,
        deferred=deferred,
        authorization=authorization,
    )


def get_item(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvValue:
    return aspects.get(
        aspect=AvAspect.ITEM,
        entity=entity,
        key=key,
        value=value,
        authorization=authorization,
    )


def clear_item(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    deferred: bool = False,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    aspects.clear(
        aspect=AvAspect.ITEM,
        entity=entity,
        key=key,
        value=value,
        deferred=deferred,
        authorization=authorization,
    )


def item_count(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvCount:
    return aspects.count(
        entity=entity,
        aspect=AvAspect.ITEM,
        key=key,
        instance=instance,
        authorization=authorization,
    )


def item_member(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> bool:
    return aspects.member(
        aspect=AvAspect.ITEM,
        entity=entity,
        key=key,
        value=value,
        instance=instance,
        authorization=authorization,
    )


def item_name(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvName:
    return aspects.name(
        aspect=AvAspect.ITEM,
        entity=entity,
        key=key,
        value=value,
        index=index,
        instance=instance,
        authorization=authorization,
    )


def item_key(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvKey:
    return aspects.key(
        aspect=AvAspect.ITEM,
        entity=entity,
        key=key,
        index=index,
        instance=instance,
        authorization=authorization,
    )


def item_value(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvValue:
    return aspects.value(
        aspect=AvAspect.ITEM,
        entity=entity,
        key=key,
        index=index,
        instance=instance,
        authorization=authorization,
    )


def item_index(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvIndex:
    return aspects.index(
        aspect=AvAspect.ITEM,
        entity=entity,
        key=key,
        value=value,
        instance=instance,
        authorization=authorization,
    )


def item_attribute(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvAttribute:
    return aspects.attribute(
        aspect=AvAspect.ITEM,
        entity=entity,
        key=key,
        value=value,
        index=index,
        instance=instance,
        authorization=authorization,
    )


def sort_items(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    instance: AvInstance = NULL_INSTANCE,
    deferred: bool = False,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    aspects.sort(
        aspect=AvAspect.ITEM,
        entity=entity,
        key=key,
        instance=instance,
        deferred=deferred,
        authorization=authorization,
    )


def erase_items(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    instance: AvInstance = NULL_INSTANCE,
    deferred: bool = False,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    aspects.erase(
        aspect=AvAspect.ITEM,
        entity=entity,
        key=key,
        instance=instance,
        deferred=deferred,
        authorization=authorization,
    )


def retrieve_items(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvInterchange:
    return aspects.retrieve(
        aspect=AvAspect.ITEM,
        entity=entity,
        key=key,
        instance=instance,
        authorization=authorization,
    )
