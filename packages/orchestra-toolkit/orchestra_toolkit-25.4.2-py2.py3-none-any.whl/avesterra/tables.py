"""Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

import avesterra.aspects as aspects
from avesterra.avial import *
from avesterra.taxonomy import AvAspect


def insert_table(
    entity: AvEntity,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    instance: AvInstance = NULL_INSTANCE,
    deferred: bool = False,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    aspects.insert(
        aspect=AvAspect.TABLE,
        entity=entity,
        name=name,
        key=key,
        instance=instance,
        deferred=deferred,
        authorization=authorization,
    )


def remove_table(
    entity: AvEntity,
    instance: AvInstance = NULL_INSTANCE,
    deferred: bool = False,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    aspects.remove(
        aspect=AvAspect.TABLE,
        entity=entity,
        instance=instance,
        deferred=deferred,
        authorization=authorization,
    )


def replace_table(
    entity: AvEntity,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    instance: AvInstance = NULL_INSTANCE,
    deferred: bool = False,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    aspects.replace(
        aspect=AvAspect.TABLE,
        entity=entity,
        name=name,
        key=key,
        instance=instance,
        deferred=deferred,
        authorization=authorization,
    )


def find_table(
    entity: AvEntity,
    name: AvName = NULL_NAME,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvInstance:
    return aspects.find(
        aspect=AvAspect.TABLE,
        entity=entity,
        name=name,
        instance=instance,
        authorization=authorization,
    )


def include_table(
    entity: AvEntity,
    name: AvName = NULL_NAME,
    key: AvKey = NULL_KEY,
    deferred: bool = False,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    return aspects.include(
        aspect=AvAspect.TABLE,
        entity=entity,
        name=name,
        key=key,
        deferred=deferred,
        authorization=authorization,
    )


def exclude_table(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    deferred: bool = False,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    return aspects.exclude(
        aspect=AvAspect.TABLE,
        entity=entity,
        key=key,
        deferred=deferred,
        authorization=authorization,
    )


def set_table(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    value: AvValue = NULL_VALUE,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    offset: AvOffset = NULL_OFFSET,
    deferred: bool = False,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    return aspects.set(
        aspect=AvAspect.TABLE,
        entity=entity,
        key=key,
        value=value,
        index=index,
        instance=instance,
        offset=offset,
        deferred=deferred,
        authorization=authorization,
    )


def get_table(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    offset: AvOffset = NULL_OFFSET,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvValue:
    return aspects.get(
        aspect=AvAspect.TABLE,
        entity=entity,
        key=key,
        index=index,
        instance=instance,
        offset=offset,
        authorization=authorization,
    )


def clear_table(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    index: AvIndex = NULL_INDEX,
    instance: AvInstance = NULL_INSTANCE,
    offset: AvOffset = NULL_OFFSET,
    deferred: bool = False,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    aspects.clear(
        aspect=AvAspect.TABLE,
        entity=entity,
        key=key,
        index=index,
        instance=instance,
        offset=offset,
        deferred=deferred,
        authorization=authorization,
    )


def table_count(
    entity: AvEntity,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvCount:
    return aspects.count(
        aspect=AvAspect.TABLE,
        entity=entity,
        authorization=authorization,
    )


def table_member(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> bool:
    return aspects.member(
        aspect=AvAspect.TABLE,
        entity=entity,
        key=key,
        authorization=authorization,
    )


def table_name(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvName:
    return aspects.name(
        aspect=AvAspect.TABLE,
        entity=entity,
        key=key,
        instance=instance,
        authorization=authorization,
    )


def table_key(
    entity: AvEntity,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvKey:
    return aspects.key(
        aspect=AvAspect.TABLE,
        entity=entity,
        instance=instance,
        authorization=authorization,
    )


def table_value(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvValue:
    return aspects.value(
        aspect=AvAspect.TABLE,
        entity=entity,
        key=key,
        instance=instance,
        authorization=authorization,
    )


def table_index(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvInstance:
    return aspects.index(
        aspect=AvAspect.TABLE,
        entity=entity,
        key=key,
        authorization=authorization,
    )


def table_attribute(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvInstance:
    return aspects.attribute(
        aspect=AvAspect.TABLE,
        entity=entity,
        key=key,
        instance=instance,
        authorization=authorization,
    )


def sort_tables(
    entity: AvEntity,
    deferred: bool = False,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    aspects.sort(
        aspect=AvAspect.TABLE,
        entity=entity,
        deferred=deferred,
        authorization=authorization,
    )


def erase_table(
    entity: AvEntity,
    deferred: bool = False,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    aspects.erase(
        aspect=AvAspect.TABLE,
        entity=entity,
        deferred=deferred,
        authorization=authorization,
    )


def retrieve_tables(
    entity: AvEntity,
    key: AvKey = NULL_KEY,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvInterchange:
    return aspects.retrieve(
        aspect=AvAspect.TABLE,
        entity=entity,
        key=key,
        instance=instance,
        authorization=authorization,
    )
