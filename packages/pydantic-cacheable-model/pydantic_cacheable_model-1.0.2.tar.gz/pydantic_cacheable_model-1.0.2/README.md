# pydantic-cacheable-model

Small helpers to make your **Pydantic v2** models trivially cacheable to disk.

---

## Installation

```bash
pip install pydantic-cacheable-model
```

Supports Python **3.10+**

---

## Usage

```py
from __future__ import annotations
from datetime import datetime
from pydantic_cacheable_model import CacheableModel, CacheId

class UserModel(CacheableModel):
    email: CacheId[str]  # <- used as the cache identifier
    joined: datetime

# Create and cache to disk
u = UserModel(email="alice@example.com", joined=datetime.now())
u.cache()

# Load a single item by identifier
u2 = UserModel.load(cache_id="alice@example.com")
assert u2 == u

# Optionally handle missing caches or validation mismatches
maybe_user = UserModel.load(cache_id="missing@example.com", not_found_ok=True)

# List everything cached
all_users = UserModel.load_all_cached()
```

---

## Configuration

Below are the configuration knobs you can use. This single block shows all options; pick the ones you need.

```py
from __future__ import annotations
from datetime import datetime
from pydantic_cacheable_model import CacheableModel, CacheId

# 1) Customize cache root and directory name
class UserModel(CacheableModel):
    # Change root directory (default: ".cache")
    CACHE_ROOT = ".data-cache"

    # Force a specific subdirectory name (otherwise derived from class name)
    CACHE_DIRNAME = "users"

    email: CacheId[str]
    joined: datetime


# 2) Customize filename mapping (avoid if ids contain unsafe characters)
class FriendlyFilenames(CacheableModel):
    slug: CacheId[str]

    @classmethod
    def cache_id_to_filename(cls, *, cache_id: str) -> str:
        # Default uses a SHA-256 hash; this stores plain ids instead
        return f"{cache_id}.json"


# 3) Custom identifier logic without using CacheId
class Document(CacheableModel):
    kind: str
    slug: str

    @property
    def cache_id(self) -> str:
        return f"{self.kind}/{self.slug}"
```

---

## How It Works

- Cache location: `./.cache/<model-dir>/` by default. `<model-dir>` is derived from the class name, removing a trailing `Model` and converting CamelCase to kebab-case (e.g., `UserModel` → `user`, `LongNameModel` → `long-name`).
- File naming: `sha256(cache_id).json` for safe, stable filenames.
- Data format: pretty-printed JSON. `Enum` values and `datetime` objects serialize automatically.
- Choosing the identifier: mark one field with `CacheId[T]`. If you need custom logic, override the `cache_id` property instead.

---

## API

- `CACHE_ROOT: str` — class var; default `".cache"`.
- `CACHE_DIRNAME: str | None` — class var; override to force subdirectory name. If `None`, derived from the class name.
- `cache_dir_path() -> str` — directory path where this model caches files.
- `cache_id_to_filename(*, cache_id: str) -> str` — classmethod; maps an id to a filename (default: SHA-256 hex + `.json`).
- `get_cache_path(*, cache_id: str) -> str` — full path to the cache file for a given id.
- `load(*, cache_id: str, not_found_ok: bool = False, warn_mismatch: bool = True) -> Self | None` — load and validate. If `not_found_ok=True`, returns `None` on missing or, when validation fails, returns `None` and optionally warns.
- `load_all_cached() -> list[Self]` — load all cached instances for the model.
- `cache() -> None` — write the instance to disk.
- `cache_path: str` — the path where this instance is cached.

---

## License

MIT — free to use and modify.
