"""Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

from functools import cache
import avesterra as av
from orchestra import env
from orchestra.adapter_interface import Interface


class FromEnv:
    """Placeholder value to signify we'll get that value from environment"""


def mount_outlet(
    key: str,
    interface: Interface,
    authorization: av.AvAuthorization,
    mount_adapter: av.AvEntity | FromEnv = FromEnv(),
) -> av.AvEntity:
    if isinstance(mount_adapter, FromEnv):
        mount_adapter = _get_mount_outlet_from_env()

    res = av.invoke_entity_retry_bo(
        entity=mount_adapter,
        method=av.AvMethod.EXECUTE,
        name="MOUNT",
        key=key,
        value=interface.to_avialmodel().to_interchange(),
        presence=av.AvPresence.AVESTERRA,
        authorization=authorization,
    )
    return res.decode_entity()


def get_outlet(
    key: str,
    authorization: av.AvAuthorization,
    mount_adapter: av.AvEntity | FromEnv = FromEnv(),
):
    if isinstance(mount_adapter, FromEnv):
        mount_adapter = _get_mount_outlet_from_env()

    res = av.invoke_entity_retry_bo(
        entity=mount_adapter,
        method=av.AvMethod.EXECUTE,
        name="GET",
        key=key,
        presence=av.AvPresence.AVESTERRA,
        authorization=authorization,
    )
    return res.decode_entity()


@cache
def _get_mount_outlet_from_env() -> av.AvEntity:
    return env.get_or_raise(env.MOUNT_OUTLET, av.AvEntity.from_str)
