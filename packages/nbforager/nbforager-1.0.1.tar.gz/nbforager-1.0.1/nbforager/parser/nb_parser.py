"""NbParser."""

import logging
from functools import wraps
from typing import Any, Type, Dict, List, Tuple

from netports import SwVersion
from vhelpers import vstr, vlist

from nbforager.exceptions import NbParserError, NbVersionError
from nbforager.types_ import DAny, Int, Str, LDAny, TLists, SeqUIntStr, ODAny, LT3Str, LStr

VERSION_NB = "4.2"
"""Minimum supported Netbox version."""

DEPRECATED_MODELS: LT3Str = [
    ("circuits/circuit-terminations", "site", "scope"),
    ("dcim/devices", "device_role", "role"),
    ("dcim/platforms", "napalm_args", ""),  # key deleted
    ("dcim/platforms", "napalm_driver", ""),  # key deleted
    ("dcim/racks", "type", "form_factor"),
    ("extras/custom-fields", "choices", "choice_set"),
    ("extras/custom-fields", "content_types", "object_types"),
    ("extras/custom-fields", "object_type", "related_object_type"),
    ("extras/custom-fields", "ui_visibility", "ui_visible"),
    ("extras/custom-links", "content_types", "object_types"),
    ("extras/export-templates", "content_types", "object_types"),
    ("extras/image-attachments", "content_type", "object_type"),
    ("extras/object-changes", "", "core/object-changes"),  # model moved
    ("extras/saved-filters", "content_types", "object_types"),
    ("ipam/prefixes", "site", "scope"),
    ("ipam/services", "device", "parent"),
    ("ipam/services", "virtual_machine", "parent"),
    ("ipam/vlan-groups", "max_vid", "vid_ranges"),
    ("ipam/vlan-groups", "min_vid", "vid_ranges"),
    ("tenancy/contact-assignments", "content_type", "object_type"),
    ("tenancy/contacts", "group", "groups"),
    ("virtualization/clusters", "site", "scope"),
]
"""Models deprecated in Netbox v4.2."""

DEPRECATED_TYPES: List[Tuple[str, LStr, Type]] = [
    ("dcim/inventory-items", ["component", "cable"], dict),
    ("dcim/power-outlets", ["power_port", "cable"], dict),
    ("dcim/cable-terminations", ["termination", "cable"], dict),
    ("dcim/devices", ["primary_ip", "family"], dict),
    ("dcim/devices", ["primary_ip4", "family"], dict),
    ("ipam/ip-addresses", ["assigned_object", "cable"], dict),
]
"""Types deprecated in Netbox v4.2."""


def check_strict(method):
    """Wrap method to check value.

    :param method: The method to be decorated.

    :return: The decorated function.
    """

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrap."""
        result = method(self, *args, **kwargs)
        if self.strict and not result:
            keys = "/".join(args)
            raise NbParserError(f"{keys=} expected in {self._source()}.")
        return result

    return wrapper


def check_in_strict_manner(method):
    """Wrap method to check value in strict manner, returned value is mandatory.

    :param method: The method to be decorated.

    :return: The decorated function.
    """

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrap."""
        strict_actual = self.strict
        self.strict = True

        result = method(self, *args, **kwargs)

        self.strict = strict_actual
        if not result:
            keys = "/".join(args)
            raise NbParserError(f"{keys=} expected in {self._source()}.")

        return result

    return wrapper


class NbParser:
    """Dictionary parser for extracting values from a Netbox object using a chain of keys.

    Netbox object may have None instead of a dictionary when a related object is absent,
    requiring constant data type checks. NbParser ensures the desired value is returned
    with the correct data type, even if the data is missing.

    Raises NbParserError if strict=True and some keys are missing.
    """

    def __init__(self, data: DAny, strict: bool = False, **kwargs):  # pylint: disable=E0601
        """Init NbParser.

        :param data: Netbox object.
        :type data: dict

        :param strict: True - if data is invalid raise NbParserError,
            False - if data is invalid return empty data with proper type.
        :type strict: bool

        :param version: Netbox version.
            Designed for compatibility with different versions.
        :type version: str
        """
        self.data = _init_data(data)
        self.strict = strict
        self.version = str(kwargs.get("version") or "")

    def __repr__(self):
        """__repr__."""
        data = None
        if isinstance(self.data, dict):
            for key in ["name", "prefix", "address", "cid", "object_type", "id"]:
                if value := self.data.get(key):
                    data = vstr.repr_params(**{key: str(value)})
                    break

        name = self.__class__.__name__
        return f"<{name}: {data}>"

    # ====================== universal get methods =======================

    def any(self, *keys) -> Any:
        """Get any value by keys.

        :param keys: Chaining dictionary keys to retrieve the desired value.

        :return: Value or None if the value is absent.
        :rtype: Any
        """
        try:
            return self._get_keys(type_=type(None), keys=keys)
        except NbParserError:
            return None

    def bool(self, *keys) -> bool:
        """Get bool value by keys.

        :param keys: Chaining dictionary keys to retrieve the desired value.

        :return: Boolean value or False if the value is absent.
        :rtype: bool
        """
        first_key = keys[0]
        self._raise_deprecated_key(first_key)
        return self._get_keys(type_=bool, keys=keys)

    def dict(self, *keys) -> Dict:
        """Get dictionary value by keys.

        :param keys: Chaining dictionary keys to retrieve the desired value.

        :return: Dictionary value or an empty dictionary if the value is absent.
        :rtype: dict

        :raise NbParserError: If strict=True and the value is not a dictionary or key is absent.
        """
        first_key = keys[0]
        self._raise_deprecated_key(first_key)
        return self._get_keys(type_=dict, keys=keys)

    def int(self, *keys) -> int:
        """Get integer value by keys.

        :param keys: Chaining dictionary keys to retrieve the desired value.

        :return: Integer value or 0 if the value is absent.
        :rtype: int

        :raise NbParserError: If strict=True and the value is not a digit or key is absent.
        """
        first_key = keys[0]
        self._raise_deprecated_key(first_key)
        self._raise_deprecated_type(first_key)

        data = self.data
        try:
            for key in keys:
                data = data[key]
        except (KeyError, TypeError) as ex:
            if self.strict:
                type_ = type(ex).__name__
                raise NbParserError(f"{type_}: {ex}, {keys=} in {self._source()}") from ex
            return 0

        if isinstance(data, int):
            return data

        if isinstance(data, str) and data.isdigit():
            return int(data)

        if self.strict:
            raise NbParserError(f"{keys=} {int} expected in {self._source()}.")
        return 0

    def list(self, *keys) -> List:
        """Get list value by keys.

        :param keys: Chaining dictionary keys to retrieve the desired value.

        :return: List value or an empty list if the value is absent.
        :rtype: list

        :raise NbParserError: If strict=True and the value is not a list or key is absent.
        """
        first_key = keys[0]
        self._raise_deprecated_key(first_key)
        return self._get_keys(type_=list, keys=keys)

    def str(self, *keys) -> str:
        """Get string value by keys.

        :param keys: Chaining dictionary keys to retrieve the desired value.

        :return: String value or an empty string if the value is absent.
        :rtype: str

        :raise NbParserError: If strict=True and the value is not a string or key is absent.
        """
        first_key = keys[0]
        self._raise_deprecated_key(first_key)
        return self._get_keys(type_=str, keys=keys)

    def _raise_deprecated_key(self, key: Str) -> None:
        """Log and rasie error if the key is deprecated for specific app/model.

        :param key: First key in the chain of keys.
        :return: None. Log error and raise NbVersionError.
        :raise NbVersionError: If the key is deprecated for specific app/model.
        """
        # skip old version
        sw_version_act = SwVersion(self.version)
        sw_version_req = SwVersion(VERSION_NB)
        if self.version and sw_version_act < sw_version_req:
            return None

        # log deprecated key if version
        url = self.data.get("url", "")
        for model, key_old, key_new in DEPRECATED_MODELS:
            if f"/api/{model}/" not in url:
                continue

            # model moved
            if not key_old:
                msg = f"Deprecated model {model!r} in {url}, please use {key_new!r}."
                logging.error(msg)
                raise NbVersionError(msg)

            # model changed
            if key == key_old:
                class_ = self.__class__.__name__
                model_old = f"{model}.{key_old}"
                # changed key
                if key_new:
                    model_new = f"{model}.{key_new}"
                    msg = (
                        f"Deprecated model {model_old!r} in {url}, "
                        f"please use {model_new!r} for Netbox>={VERSION_NB} or "
                        f"specify low Netbox version in {class_}(version=3)."
                    )
                    logging.error(msg)
                    raise NbVersionError(msg)
                # removed key
                if key_old in self.data:
                    msg = (
                        f"Deprecated model {model_old!r} in {url}, please remove it or "
                        f"specify low Netbox version in {class_}(version=3)."
                    )
                    logging.error(msg)
                    raise NbVersionError(msg)

    def _raise_deprecated_type(self, keys: LStr) -> None:
        """Log and rasie error if the type is deprecated for specific app/model.

        :param keys: Keys chain to get interested value.
        :return: None. Log error and raise NbVersionError.
        :raise NbVersionError: If the type is deprecated for specific app/model.
        """
        # skip old version
        if self.version and SwVersion(self.version) < SwVersion("4.2"):
            return

        # log deprecated key if version
        url = self.data.get("url", "")
        for model, keys_old, type_new in DEPRECATED_TYPES:
            keys_new = keys[: len(keys_old)]
            value = self.any(*keys_new)
            if f"/api/{model}/" not in url:
                continue
            if keys_new != keys_old:
                continue
            if isinstance(value, type_new):
                continue

            type_old = type(value)
            model_old = ".".join([model, *keys_old])
            msg = f"Deprecated type {model_old} {type_old!r} in {url}, please use {type_new!r}."
            logging.error(msg)
            raise NbVersionError(msg)

    # ======================== strict get methods ========================

    @check_in_strict_manner
    def strict_dict(self, *keys) -> Dict:
        """Get dictionary value by keys in strict manner, value is mandatory.

        Useful when strict=False, but you need to obtain a value in a strict manner.
        :param keys: Chaining dictionary keys to retrieve the desired value.

        :return: Dictionary value.
        :rtype: dict

        :raise NbParserError: If the value is not a dictionary or key is absent or value is empty.
        """
        return self.dict(*keys)

    @check_in_strict_manner
    def strict_int(self, *keys) -> Int:
        """Get integer value by keys in strict manner, value is mandatory.

        Useful when strict=False, but you need to obtain a value in a strict manner.
        :param keys: Chaining dictionary keys to retrieve the desired value.

        :return: Integer value.
        :rtype: int

        :raise NbParserError: If the value is not int or key is absent or value is 0.
        """
        return self.int(*keys)

    @check_in_strict_manner
    def strict_list(self, *keys) -> List:
        """Get string value by keys in strict manner, value is mandatory.

        Useful when strict=False, but you need to obtain a value in a strict manner.
        :param keys: Chaining dictionary keys to retrieve the desired value.

        :return: List value.
        :rtype: list

        :raise NbParserError: If the value is not a list or key is absent or value is empty.
        """
        return self.list(*keys)

    @check_in_strict_manner
    def strict_str(self, *keys) -> Str:
        """Get string value by keys in strict manner, value is mandatory.

        :param keys: Chaining dictionary keys to retrieve the desired value.

        :return: String value.
        :rtype: str

        :raise NbParserError: If the value is not a string or key is absent or value is absent.
        """
        return self.str(*keys)

    # ============================= helpers ==============================

    def _get_keys(self, type_: Type, keys: SeqUIntStr, data: ODAny = None) -> Any:
        """Retrieve values from data using keys and check their data types.

        :param type_: Data type.
        :param keys: Chaining dictionary keys to retrieve the desired value.
        :param data: Dictionary.

        :return: Value with proper data type.

        :raise NbParserError: If strict=True and key absent or type not match.
        """
        if data is None:
            data = self.data
        try:
            for key in keys:
                data = data[key]  # type: ignore
        except (KeyError, IndexError, TypeError) as ex:
            if self.strict:
                ex_type = type(ex).__name__
                raise NbParserError(f"{ex_type}: {ex}, {keys=} in {self._source()}.") from ex
            return type_()

        if type_ is type(None):
            return data
        if not isinstance(data, type_):
            if self.strict:
                ex_type = "TypeError"
                raise NbParserError(f"{ex_type}: {keys=} {type_} expected in {self._source()}.")
            return type_()

        return data

    def _source(self) -> Str:
        """Return URL or dictionary of source object."""
        if isinstance(self.data, dict):
            if url := self.data.get("url"):
                return str(url)
        return str(self.data)


def _init_data(data: DAny) -> DAny:
    """Init data."""
    if data is None:
        return {}
    if isinstance(data, dict):
        return data
    raise TypeError(f"{data=} {dict} expected.")


# ============================ functions =============================


def find_objects(objects: LDAny, **kwargs) -> LDAny:
    """Find Netbox objects in tree by extended finding parameters.

    :param objects: Netbox objects where searching is required using kwargs.
    :param kwargs: Extended filtering parameters.
    :return: Filtered Netbox objects.
    """
    if not kwargs:
        return objects
    (key, values), *key_values = list(kwargs.items())
    if not isinstance(values, TLists):
        values = [values]

    objects_: LDAny = []
    for data in objects:
        if not isinstance(key, str):
            raise TypeError(f"Key {str} expected.")
        keys = key.split("__")
        if len(keys) <= 1:
            keys = [key]
        if keys[0] == "tags":
            if len(keys) != 2:
                raise ValueError(f"{keys=} {len(keys)=} expected 2.")
            values_ = [d[keys[1]] for d in data["tags"]]
            if vlist.is_in(values_, values):
                objects_.append(data)
        else:
            value_ = NbParser(data).any(*keys)
            if value_ in values:
                objects_.append(data)

    if key_values:
        objects_ = find_objects(objects=objects_, **dict(key_values))
    return objects_
