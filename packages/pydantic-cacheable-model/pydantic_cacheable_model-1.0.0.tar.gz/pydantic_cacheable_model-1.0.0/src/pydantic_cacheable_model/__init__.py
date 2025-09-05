from __future__ import annotations

import hashlib
import json
import os
import re
import warnings
from datetime import datetime
from enum import Enum
from glob import glob
from typing import Annotated, Any, ClassVar, Literal, Self, TypeVar, overload

from pydantic import BaseModel, ValidationError

T = TypeVar("T")


class _CacheIdMarker:
    pass


CacheId = Annotated[T, _CacheIdMarker()]

__all__ = ["CacheableModel", "CacheId"]


def _json_default(o: Any):
    if isinstance(o, Enum):
        return o.value
    if isinstance(o, datetime):
        return o.isoformat()
    raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")


class CacheableModel(BaseModel):
    CACHE_ROOT: ClassVar[str] = ".cache"
    CACHE_DIRNAME: ClassVar[str | None] = None

    @property
    def cache_id(self) -> str:
        cache_id_fields: list[str] = []
        for name, field in type(self).model_fields.items():
            try:
                metadata = getattr(field, "metadata", ())
            except Exception:
                metadata = ()
            if any(isinstance(m, _CacheIdMarker) for m in metadata):
                cache_id_fields.append(name)

        if not cache_id_fields:
            raise NotImplementedError
        if len(cache_id_fields) > 1:
            raise ValueError(
                f"Multiple CacheId fields defined: {', '.join(cache_id_fields)}"
            )

        value = getattr(self, cache_id_fields[0])
        if value is None:
            raise ValueError(f"CacheId field '{cache_id_fields[0]}' is None")
        return value if isinstance(value, str) else str(value)

    @classmethod
    def cache_dir_path(cls) -> str:
        model_dir = (
            cls.CACHE_DIRNAME
            or re.sub(
                r"(?<!^)(?=[A-Z])", "-", cls.__name__.replace("Model", "")
            ).lower()
        )
        return os.path.join(cls.CACHE_ROOT, model_dir)

    @classmethod
    def cache_id_to_filename(cls, *, cache_id: str) -> str:
        digest = hashlib.sha256(cache_id.encode("utf-8")).hexdigest()
        return f"{digest}.json"

    @classmethod
    def get_cache_path(cls, *, cache_id: str) -> str:
        return os.path.join(
            cls.cache_dir_path(), cls.cache_id_to_filename(cache_id=cache_id)
        )

    @overload
    @classmethod
    def load(
        cls,
        *,
        cache_id: str,
        not_found_ok: Literal[False] = ...,
        warn_mismatch: bool = ...,
    ) -> Self: ...

    @overload
    @classmethod
    def load(
        cls,
        *,
        cache_id: str,
        not_found_ok: Literal[True],
        warn_mismatch: bool = ...,
    ) -> Self | None: ...

    @classmethod
    def load(
        cls,
        *,
        cache_id: str,
        not_found_ok: bool = False,
        warn_mismatch: bool = True,
    ) -> Self | None:
        path = cls.get_cache_path(cache_id=cache_id)
        if not os.path.exists(path):
            if not_found_ok:
                return None
            raise FileNotFoundError(
                f"Cache not found for {cls.__name__}({cache_id}) at {path}"
            )

        with open(path, "r") as fp:
            data = json.load(fp)
        try:
            return cls(**data)
        except ValidationError as e:
            if not_found_ok:
                if warn_mismatch:
                    warnings.warn(
                        f"Could not load cached {cls.__name__}({cache_id}) at {path}: {e}",
                        category=UserWarning,
                        stacklevel=2,
                    )
                return None
            raise

    @classmethod
    def load_all_cached(cls) -> list[Self]:
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
        return self.get_cache_path(cache_id=self.cache_id)

    def cache(self) -> None:
        os.makedirs(self.cache_dir_path(), exist_ok=True)
        with open(self.cache_path, "w") as fp:
            json.dump(
                obj=self.model_dump(mode="json"),
                fp=fp,
                indent=2,
                default=_json_default,
            )
