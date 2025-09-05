__all__ = ["UniDict"]
from lt_utils.common import *
from lt_utils.misc_utils import updateDict


class UniDict(OrderedDict):
    def __init__(
        self,
        *args,
        _frozen_state: bool = True,
        **kwargs,
    ):
        """
        Args:
            _frozen_state (bool, optional): If frozen, no values can be set after the initialization. Defaults to True.
        """
        super().__init__(*args, **kwargs)

        self._frozen_state = _frozen_state
        self._redefine_attrs()

    def _check(self, fn_inst: str):
        if hasattr(self, "_frozen_state"):
            if self._frozen_state:
                raise RuntimeError(
                    f"You cannot use ``{fn_inst}`` on a {self.__class__.__name__} instance while '_frozen_state' is set to True."
                )

    def __delitem__(self, key: str):
        self._check("__delitem__")
        super().__delitem__(key)

    def __setitem__(self, name, value):
        self._check("__setitem__")
        super().__setitem__(name, value)

    def __setattr__(self, name, value):
        if name != "_frozen_state":
            self._check("__setattr__")
        super().__setattr__(name, value)

    def _redefine_attrs(self):
        data = self.copy()
        if hasattr(self, "_frozen_state"):
            _frozen = data.pop("_frozen_state", True)
            self._frozen_state = False

        updateDict(self, data)

        if hasattr(self, "_frozen_state"):
            self._frozen_state = _frozen

    def setdefault(self, key: Any, default: None = None):
        self._check("setdefault")
        super().setdefault(key, default)

    def unfreeze_dict(self):
        self._frozen_state = False

    def freeze_dict(self):
        self._frozen_state = True

    def pop(self, key: Any, default: Optional[Any] = None):
        self._check("pop")
        super().pop(key, default)

    def force_set(self, name, value):
        """Ignores the frozen state"""
        super().__setitem__(name, value)

    def update(self, **kwargs):
        super().update(**kwargs)

    def force_update(self, **kwargs):
        old_state = self._frozen_state
        self._frozen_state = False
        for k, v in kwargs.items():
            if k != "_frozen_state":
                self.__setitem__(k, v)
            else:
                old_state = v
        self._frozen_state = old_state

    def copy(self):
        return dict(self).copy()

    def find(self, item: object, total: int = -1, *, verbose_exceptions: bool = False):
        """
        Find objects by value, accepting also values
        with the same type if the cannot be compared
        """
        matching = []

        for k, v in self.items():
            try:
                if v == item:
                    current = {"key": k, "value": v}
                    if total > 0:
                        if total == 1:
                            return current
                        matching.append(current)
                        if len(matching) >= total:
                            return matching[:total]
                    else:
                        matching.append(current)
            except Exception as e:
                if verbose_exceptions:
                    print(e)
                pass

        if not matching:
            return None
        if total > 0:
            return matching[:total]
        return matching

    def _update(self, **kwargs):
        """Same as the original update, but this version
        returns the class itself. Very circumstantial use-cases"""
        self.update(**kwargs)
        return self

    def save_state(self, location: Union[str, Path], *args, **kwargs):
        path = Path(location)
        assert "." in path.name, "Cannot process without any specific extension"
        if path.name.endswith((".npy", ".pkl")):
            from lt_utils.file_ops import save_pickle

            save_pickle(path, self.copy(), *args, **kwargs)
        elif path.name.endswith(".json"):
            from lt_utils.file_ops import save_json

            save_json(path, self.copy(), *args, **kwargs)
        elif path.name.endswith((".yaml", ".yml")):
            from lt_utils.file_ops import save_yaml

            save_yaml(path, self.copy(), *args, **kwargs)
        else:
            raise ValueError(
                f"No valid extension has been provided to '{path.name}'. It must be either 'npy', 'pkl', 'json', 'yaml' or 'yml'."
            )

    def load_state(self, location: Union[str, Path], *args, **kwargs):
        path = Path(location)
        assert "." in path.name, "Cannot process without any specific extension"
        if path.name.endswith((".npy", ".pkl")):
            from lt_utils.file_ops import load_pickle
            from numpy import ndarray

            previous_state = load_pickle(str(path), *args, **kwargs)
            if isinstance(previous_state, ndarray):
                previous_state = previous_state.tolist()
        elif path.name.endswith(".json"):
            from lt_utils.file_ops import load_json

            previous_state = load_json(str(path), *args, **kwargs)
        elif path.name.endswith((".yml", ".yaml")):
            from lt_utils.file_ops import load_yaml

            previous_state = load_yaml(str(path), *args, **kwargs)
        else:
            raise ValueError(
                f"No valid extension has been provided to '{path.name}'. It must be either 'npy', 'pkl', 'json', 'yaml' or 'yml'."
            )
        assert isinstance(
            previous_state, (UniDict, dict)
        ), f"The state loaded from '{str(path)}' are not a valid dictionary."
        self.force_update(**previous_state)
        self._redefine_attrs()

    @classmethod
    def load_from_file(cls, location: Union[str, Path], *args, **kwargs):
        path = Path(location)
        assert "." in path.name, "Cannot process without any specific extension"
        if path.name.endswith((".npy", ".pkl")):
            from lt_utils.file_ops import load_pickle
            from numpy import ndarray

            previous_state = load_pickle(str(path), *args, **kwargs)
            if isinstance(previous_state, ndarray):
                previous_state = previous_state.tolist()
        elif path.name.endswith(".json"):
            from lt_utils.file_ops import load_json

            previous_state = load_json(str(path), *args, **kwargs)
        elif path.name.endswith((".yml", ".yaml")):
            from lt_utils.file_ops import load_yaml

            previous_state = load_yaml(str(path), *args, **kwargs)
        else:
            raise ValueError(
                f"No valid extension has been provided to '{path.name}'. It must be either 'npy', 'pkl', 'json', 'yaml' or 'yml'."
            )
        assert isinstance(
            previous_state, (UniDict, dict)
        ), f"The state loaded from '{str(path)}' are not a valid dictionary."
        return cls(**previous_state)
