"""Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

import avesterra.aspects as aspects
from avesterra.avial import *
from avesterra.taxonomy import AvAttribute, AvAspect


def insert_attribution(
    entity: AvEntity,
    attributions: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    value: AvValue = NULL_VALUE,
    instance: AvInstance = NULL_INSTANCE,
    deferred: bool = False,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    aspects.insert(
        aspect=AvAspect.ATTRIBUTION,
        entity=entity,
        attribute=attributions,
        name=name,
        value=value,
        instance=instance,
        deferred=deferred,
        authorization=authorization,
    )


def remove_attribution(
    entity: AvEntity,
    instance: AvInstance = NULL_INSTANCE,
    deferred: bool = False,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    aspects.remove(
        aspect=AvAspect.ATTRIBUTION,
        entity=entity,
        instance=instance,
        deferred=deferred,
        authorization=authorization,
    )


def replace_attribution(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    value: AvValue = NULL_VALUE,
    instance: AvInstance = NULL_INSTANCE,
    deferred: bool = False,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    aspects.replace(
        aspect=AvAspect.ATTRIBUTION,
        entity=entity,
        attribute=attribute,
        value=value,
        instance=instance,
        deferred=deferred,
        authorization=authorization,
    )


def find_attribution(
    entity: AvEntity,
    name: AvName = NULL_NAME,
    value: AvValue = NULL_VALUE,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvInstance:
    return aspects.find(
        aspect=AvAspect.ATTRIBUTION,
        entity=entity,
        name=name,
        value=value,
        instance=instance,
        authorization=authorization,
    )


def include_attribution(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    deferred: bool = False,
    value: AvValue = NULL_VALUE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    return aspects.include(
        aspect=AvAspect.ATTRIBUTION,
        entity=entity,
        attribute=attribute,
        value=value,
        deferred=deferred,
        authorization=authorization,
    )


def exclude_attribution(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    deferred: bool = False,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    return aspects.exclude(
        aspect=AvAspect.ATTRIBUTION,
        entity=entity,
        attribute=attribute,
        deferred=deferred,
        authorization=authorization,
    )


def set_attribution(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    name: AvName = NULL_NAME,
    value: AvValue = NULL_VALUE,
    deferred: bool = False,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    return aspects.set(
        aspect=AvAspect.ATTRIBUTION,
        entity=entity,
        attribute=attribute,
        name=name,
        value=value,
        deferred=deferred,
        authorization=authorization,
    )


def get_attribution(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvValue:
    return aspects.get(
        aspect=AvAspect.ATTRIBUTION,
        entity=entity,
        attribute=attribute,
        authorization=authorization,
    )


def clear_attribution(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    deferred: bool = False,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    aspects.clear(
        aspect=AvAspect.ATTRIBUTION,
        entity=entity,
        attribute=attribute,
        deferred=deferred,
        authorization=authorization,
    )


def attribution_count(
    entity: AvEntity,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvCount:
    return aspects.count(
        aspect=AvAspect.ATTRIBUTION,
        entity=entity,
        authorization=authorization,
    )


def attribution_member(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> bool:
    return aspects.member(
        aspect=AvAspect.ATTRIBUTION,
        entity=entity,
        attribute=attribute,
        authorization=authorization,
    )


def attribution_name(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvName:
    return aspects.name(
        aspect=AvAspect.ATTRIBUTION,
        entity=entity,
        attribute=attribute,
        instance=instance,
        authorization=authorization,
    )


def attribution_key(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvKey:
    return aspects.key(
        aspect=AvAspect.ATTRIBUTION,
        entity=entity,
        attribute=attribute,
        instance=instance,
        authorization=authorization,
    )


def attribution_value(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvValue:
    return aspects.value(
        aspect=AvAspect.ATTRIBUTION,
        entity=entity,
        attribute=attribute,
        instance=instance,
        authorization=authorization,
    )


def attribution_index(
    entity: AvEntity,
    attribute: AvAttribute = NULL_ATTRIBUTE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvInstance:
    return aspects.index(
        aspect=AvAspect.ATTRIBUTION,
        entity=entity,
        attribute=attribute,
        authorization=authorization,
    )


def attribution_attribute(
    entity: AvEntity,
    instance: AvInstance = NULL_INSTANCE,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvAttribute:
    return aspects.attribute(
        aspect=AvAspect.ATTRIBUTION,
        entity=entity,
        instance=instance,
        authorization=authorization,
    )


def sort_attributions(
    entity: AvEntity,
    deferred: bool = False,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    aspects.sort(
        aspect=AvAspect.ATTRIBUTION,
        entity=entity,
        deferred=deferred,
        authorization=authorization,
    )


def erase_attribution(
    entity: AvEntity,
    deferred: bool = False,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> None:
    aspects.erase(
        aspect=AvAspect.ATTRIBUTION,
        entity=entity,
        deferred=deferred,
        authorization=authorization,
    )


def retrieve_attributions(
    entity: AvEntity,
    authorization: AvAuthorization = NULL_AUTHORIZATION,
) -> AvInterchange:
    return aspects.retrieve(
        aspect=AvAspect.ATTRIBUTION,
        entity=entity,
        authorization=authorization,
    )
