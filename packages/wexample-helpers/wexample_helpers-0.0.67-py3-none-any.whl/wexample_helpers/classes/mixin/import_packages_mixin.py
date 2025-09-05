from __future__ import annotations

import importlib
import pkgutil
import sys
from typing import ClassVar

from pydantic import BaseModel


class ImportPackagesMixin:
    """Mixin that accumulates `import_packages` and provides a bootstrap loader.

    - Classes may declare `import_packages` as an iterable of package names.
    - __init_subclass__ merges declarations across the hierarchy (L→R, then self).
    - load_imports() imports modules, builds a parent namespace, and rebuilds Pydantic models.
    """

    import_packages: ClassVar[tuple[str, ...]] = ()
    _imports_loaded: ClassVar[bool] = False

    def __init_subclass__(cls, **kwargs) -> None:  # type: ignore[override]
        super().__init_subclass__(**kwargs)
        merged: list[str] = []
        for base in cls.__bases__:
            merged += list(getattr(base, "import_packages", ()))
        merged += list(getattr(cls, "import_packages", ()))
        # Deduplicate while preserving order
        cls.import_packages = tuple(dict.fromkeys(merged))

    @classmethod
    def load_imports(cls) -> None:
        """Import packages from `cls.import_packages` and rebuild Pydantic models.

        This mitigates Pydantic v2 'class-not-fully-defined' errors by ensuring all
        referenced modules are imported before model_rebuild is invoked.
        """
        # Per-class guard: idempotent within a process
        if getattr(cls, "_imports_loaded", False):
            return
        loaded_packages = getattr(cls, "import_packages", ())

        # 1) Import foundational packages first (merged from the class hierarchy)
        for pkg_name in loaded_packages:
            try:
                pkg = importlib.import_module(pkg_name)
            except Exception:
                continue
            if hasattr(pkg, "__path__"):
                for mod in pkgutil.walk_packages(pkg.__path__, pkg.__name__ + "."):
                    try:
                        importlib.import_module(mod.name)
                    except Exception:
                        # Best effort: some optional modules may fail to import
                        pass

        # 2) Build a parent namespace with symbols from the loaded packages to resolve bare names
        parent_ns: dict[str, object] = {}
        for name, module in list(sys.modules.items()):
            if not module:
                continue
            if any(
                name == pkg or name.startswith(pkg + ".") for pkg in loaded_packages
            ):
                try:
                    parent_ns.update(vars(module))
                except Exception:
                    pass

        # 3) Rebuild all Pydantic models (two passes for forward refs)
        seen: set[type] = set()
        stack = list(BaseModel.__subclasses__())
        while stack:
            m = stack.pop()
            if m in seen:
                continue
            seen.add(m)
            # Provide a broad namespace for forward ref resolution
            try:
                setattr(m, "__pydantic_parent_namespace__", parent_ns)
            except Exception:
                pass
            try:
                m.model_rebuild()
            except Exception:
                # Ignore, next pass may resolve
                pass
            stack.extend(m.__subclasses__())

        for m in list(seen):
            try:
                setattr(m, "__pydantic_parent_namespace__", parent_ns)
                m.model_rebuild()
            except Exception:
                pass

        try:
            cls._imports_loaded = True
        except Exception:
            pass
