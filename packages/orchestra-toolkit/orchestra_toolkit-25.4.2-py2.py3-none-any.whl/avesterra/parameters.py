"""Copyright 2024-2025 LEDR Technologies Inc.
This file is part of the Orchestra library, which helps developer use our Orchestra technology which is based on AvesTerra, owned and developped by Georgetown University, under license agreement with LEDR Technologies Inc.
The Orchestra library is a free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.
The Orchestra library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more details.
You should have received a copy of the GNU Lesser General Public License along with the Orchestra library. If not, see <https://www.gnu.org/licenses/>.
If you have any questions, feedback or issues about the Orchestra library, you can contact us at support@ledr.io.
"""

# --  Creation Date:    2025-07-11 18:54:00                  --
# --  AvesTerra version: V8.5                                 --

from enum import IntEnum


class Parameter(IntEnum):
    FALSE = 0
    TRUE = 1
    AVESTERRA = 1
    ABOUT = 2
    PING = 3
    DEFERRAL = 4
    REBOOT = 5
    PROCESS = 6
    LAUNCH = 7
    TERMINATE = 8
    KILL = 9
    CONFIGURE = 10
    NETWORK = 11
    HOST = 12
    PHYSICAL = 13
    LOGICAL = 14
    VIRTUAL = 15
    REDIRECT = 16
    COUNT = 17
    ENTITIES = 18
    REFERENCES = 19
    DENSITY = 20
    REGISTER = 21
    DEREGISTER = 22
    INSTATE = 23
    DESTATE = 24
    FILTER = 25
    UNFILTER = 26
    LOG = 27
    SIZE = 28
    WIPE = 29
    TEST = 30
    PLATFORM = 31
    PORTAL = 32
    UNPORTAL = 33
    MAP = 34
    UNMAP = 35
    COUPLE = 36
    DECOUPLE = 37
    PAIR = 38
    UNPAIR = 39
    CREATE = 40
    DELETE = 41
    UPDATE = 42
    ETHERNET = 43
    INTERNET = 44
    ALLOW = 45
    DENY = 46
    VOID = 47
    SCRUB = 48
    SERIAL = 49
    CLOCK = 50
