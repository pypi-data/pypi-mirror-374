# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Original Copyright 2025 Stanford Center for Research on Foundation Models.
# For the original license and copyright information, see the LICENSE file in this repository.

from abc import abstractmethod
import contextlib
import json
from typing import Dict, Generator, Iterable, Mapping, Optional, Tuple

from diskcache import Cache


def request_to_key(request: Mapping) -> str:
    """Normalize a `request` into a `key` so that we can hash using it."""
    return json.dumps(request, sort_keys=True)


class KeyValueStore(contextlib.AbstractContextManager):
    """Key value store that persists writes."""

    @abstractmethod
    def contains(self, key: Mapping) -> bool:
        pass

    @abstractmethod
    def get(self, key: Mapping) -> Optional[Dict]:
        pass

    @abstractmethod
    def get_all(self) -> Generator[Tuple[Dict, Dict], None, None]:
        pass

    @abstractmethod
    def put(self, key: Mapping, value: Dict) -> None:
        pass

    @abstractmethod
    def multi_put(self, pairs: Iterable[Tuple[Dict, Dict]]) -> None:
        pass

    @abstractmethod
    def remove(self, key: Mapping) -> None:
        pass


class SqliteKeyValueStore(KeyValueStore):
    """Key value store backed by a SQLite file."""

    def __init__(self, path: str):
        self._cache = Cache(path)
        super().__init__()

    def __enter__(self) -> "SqliteKeyValueStore":
        self._cache.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._cache.__exit__(exc_type, exc_value, traceback)

    def contains(self, key: Mapping) -> bool:
        return request_to_key(key) in self._cache

    def get(self, key: Mapping) -> Optional[Dict]:
        key_string = request_to_key(key)
        result = self._cache.get(key_string)
        if result is not None:
            assert isinstance(result, dict)
            return result
        return None

    def get_all(self) -> Generator[Tuple[Dict, Dict], None, None]:
        for key, value in self._cache.items():
            yield (key, value)

    def put(self, key: Mapping, value: Dict) -> None:
        key_string = request_to_key(key)
        self._cache[key_string] = value

    def multi_put(self, pairs: Iterable[Tuple[Dict, Dict]]) -> None:
        for key, value in pairs:
            self.put(key, value)

    def remove(self, key: Mapping) -> None:
        del self._cache[key]


class BlackHoleKeyValueStore(KeyValueStore):
    """Key value store that discards all data."""

    def __enter__(self) -> "BlackHoleKeyValueStore":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        pass

    def contains(self, key: Mapping) -> bool:
        return False

    def get(self, key: Mapping) -> Optional[Dict]:
        return None

    def get_all(self) -> Generator[Tuple[Dict, Dict], None, None]:
        # Return an empty generator.
        # See: https://stackoverflow.com/a/13243870
        return
        yield

    def put(self, key: Mapping, value: Dict) -> None:
        return None

    def multi_put(self, pairs: Iterable[Tuple[Dict, Dict]]) -> None:
        return None

    def remove(self, key: Mapping) -> None:
        return None
