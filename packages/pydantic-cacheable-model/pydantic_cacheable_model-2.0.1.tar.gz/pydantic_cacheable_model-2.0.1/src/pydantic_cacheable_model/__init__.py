"""Utilities to make Pydantic v2 models cacheable to disk.

Public API:
- `CacheableModel`: Base class providing disk-backed JSON cache helpers.
- `CacheKey[T]`: Marker for a single field to be used as the cache key.

See the project README for usage examples and configuration options.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import warnings
from datetime import datetime
from enum import Enum
from glob import glob
from typing import Annotated, Any, ClassVar, Literal, TypeVar, overload

if sys.version_info > (3, 11):
    from typing import Self
else:
    from typing_extensions import Self

from pydantic import BaseModel, ValidationError

T = TypeVar("T")


class CacheKeyComputationError(Exception):
    pass


class _CacheKeyMarker:
    pass


CacheKey = Annotated[T, _CacheKeyMarker()]


__all__ = ["CacheableModel", "CacheKey", "CacheKeyComputationError"]


def _json_default(o: Any):
    if isinstance(o, Enum):
        return o.value
    if isinstance(o, datetime):
        return o.isoformat()
    raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")


class CacheableModel(BaseModel):
    """Base model that can cache itself to disk as JSON.

    Configuration:
    - `CACHE_ROOT`: Root directory for all caches (default: `.cache`).
    - `CACHE_DIRNAME`: Optional subdirectory name for this model. If `None`, a
      name is derived from the class: the optional `Model` suffix is removed and
      CamelCase is converted to kebab-case (e.g., `UserModel` → `user`).
    """

    CACHE_ROOT: ClassVar[str] = ".cache"
    CACHE_DIRNAME: ClassVar[str | None] = None

    @property
    def cache_key(self) -> str:
        """Return the key string used to cache this instance.

        The default implementation discovers exactly one field annotated with
        `CacheKey[...]` and returns its value as a string. Subclasses may
        override this property to implement custom logic.

        Raises:
            CacheKeyComputationError:
                * If no `CacheKey` field is defined.
                * If multiple `CacheKey` fields exist
                * If CacheKey value is `None`.
        """
        cache_key_fields: list[str] = []
        for name, field in type(self).model_fields.items():
            try:
                metadata = getattr(field, "metadata", ())
            except Exception:
                metadata = ()
            if any(isinstance(m, _CacheKeyMarker) for m in metadata):
                cache_key_fields.append(name)

        if not cache_key_fields:
            raise CacheKeyComputationError(f"{type(self.__name__)}: Missing CacheKey")
        if len(cache_key_fields) > 1:
            raise CacheKeyComputationError(
                f"{type(self.__name__)}: Multiple CacheKey fields defined: {', '.join(cache_key_fields)}"
            )

        value = getattr(self, cache_key_fields[0])
        if value is None:
            raise CacheKeyComputationError(
                f"{type(self.__name__)}: CacheKey field '{cache_key_fields[0]}' is None"
            )
        return value if isinstance(value, str) else str(value)

    @classmethod
    def cache_dir_path(cls) -> str:
        """Return the directory path where this model stores its cache files."""
        model_dir = (
            cls.CACHE_DIRNAME
            or re.sub(
                r"(?<!^)(?=[A-Z])", "-", cls.__name__.replace("Model", "")
            ).lower()
        )
        return os.path.join(cls.CACHE_ROOT, model_dir)

    @classmethod
    def cache_key_to_filename(cls, *, cache_key: str) -> str:
        """Map a cache key to a filename.

        By default this returns `<sha256(cache_key)>.json` to ensure safe and
        stable filenames regardless of the content of `cache_key`.
        """
        digest = hashlib.sha256(cache_key.encode("utf-8")).hexdigest()
        return f"{digest}.json"

    @classmethod
    def get_cache_path(cls, *, cache_key: str) -> str:
        """Return the absolute path for the JSON cache file of `cache_key`."""
        return os.path.join(
            cls.cache_dir_path(), cls.cache_key_to_filename(cache_key=cache_key)
        )

    @overload
    @classmethod
    def load(
        cls,
        *,
        cache_key: str,
        not_found_ok: Literal[False] = ...,
        warn_mismatch: bool = ...,
    ) -> Self: ...

    @overload
    @classmethod
    def load(
        cls,
        *,
        cache_key: str,
        not_found_ok: Literal[True],
        warn_mismatch: bool = ...,
    ) -> Self | None: ...

    @classmethod
    def load(
        cls,
        *,
        cache_key: str,
        not_found_ok: bool = False,
        warn_mismatch: bool = True,
    ) -> Self | None:
        """Load an instance from cache.

        Args:
            cache_key: Key for the instance to load.
            not_found_ok: If True, return `None` when the cache file is missing
                (instead of raising ``FileNotFoundError``). When True, this also
                causes validation failures to return `None` (optionally with a
                warning).
            warn_mismatch: If True and `not_found_ok=True`, emit a warning when
                a cached payload fails validation against the current model.

        Returns:
            An instance of the model, or `None` when `not_found_ok=True` and the
            file is missing or fails validation.

        Raises:
            FileNotFoundError: If the cache file is missing and `not_found_ok` is False.
            ValidationError: If the cached data fails model validation and
                `not_found_ok` is False.
        """
        path = cls.get_cache_path(cache_key=cache_key)
        if not os.path.exists(path):
            if not_found_ok:
                return None
            raise FileNotFoundError(
                f"Cache not found for {cls.__name__}({cache_key}) at {path}"
            )

        with open(path, "r") as fp:
            data = json.load(fp)
        try:
            return cls(**data)
        except ValidationError as e:
            if not_found_ok:
                if warn_mismatch:
                    warnings.warn(
                        f"Could not load cached {cls.__name__}({cache_key}) at {path}: {e}",
                        category=UserWarning,
                        stacklevel=2,
                    )
                return None
            raise

    @classmethod
    def load_all_cached(cls) -> list[Self]:
        """Load all cached instances for this model.

        Returns:
            A list of model instances loaded from all `*.json` files in the
            model's cache directory.

        Raises:
            ValidationError: If any cached JSON payload fails validation.
        """
        dirname = cls.cache_dir_path()
        if not os.path.isdir(dirname):
            return []
        items: list[Self] = []
        for f in glob(os.path.join(dirname, "*.json")):
            with open(f, "r") as fp:
                items.append(cls(**json.load(fp)))
        return items

    @property
    def cache_path(self) -> str:
        """Return the absolute filesystem path where this instance is cached."""
        return self.get_cache_path(cache_key=self.cache_key)

    def cache(self) -> None:
        """Write this instance to its JSON cache file.

        Ensures the target directory exists, then writes the result of
        `self.model_dump(mode="json")` to disk with an additional JSON
        encoder that supports `Enum` and `datetime` values.
        """
        os.makedirs(self.cache_dir_path(), exist_ok=True)
        with open(self.cache_path, "w") as fp:
            json.dump(
                obj=self.model_dump(mode="json"),
                fp=fp,
                indent=2,
                default=_json_default,
            )
