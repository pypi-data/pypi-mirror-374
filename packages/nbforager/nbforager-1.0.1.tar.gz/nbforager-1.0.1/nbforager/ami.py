"""app/model/id helper functions."""

import urllib
from typing import Any
from urllib.parse import ParseResult

from vhelpers import vlist, vint

from nbforager.exceptions import NbApiError
from nbforager.types_ import LStr, LDAny
from nbforager.types_ import T2Str, T3Str, T3StrInt


def am_to_object_type(app: str, model: str) -> str:
    """Convert application and model to object_type.

    :param app: Application value.
    :param model: Model value.
    :return: Object type.

    :example:
        am_to_object_type("ipam", "ip-address") -> "ipam.ipaddress"
    """
    singular = model_singular(model)
    if app == "virtualization":
        if singular == "interface":
            singular = f"vm{singular}"
    return f"{app}.{singular}"


def attr_name(obj: Any) -> str:
    """Transform the class name to the attribute name, lowercase without postfix.

    :param obj: The object or name to transform.

    :return: Attribute name.

    :example:
        attr_name("TenantGroupsJ") -> "tenant_groups"
    """
    name = obj.__class__.__name__
    if isinstance(obj, str):
        name = obj
    name = replace_upper(name)
    if name[:-1].endswith("_"):
        name = name[:-2]
        if name[:-1].endswith("_"):
            name = name[:-2]
    return name


def attr_names(obj: Any) -> LStr:
    """Transform the class names to the attribute names, lowercase without postfix.

    :param obj: The object or name to transform.

    :return: Attribute names.

    :example:
        attr_names(NbForager.tenancy) -> ["tenant_groups", "tenants"]
    """
    attrs = [s for s in dir(obj) if s[0].isupper()]
    methods = [replace_upper(s)[:-2] for s in attrs]
    return methods


def attr_to_model(attr: str) -> str:
    """Convert attribute name to model name.

    :param attr: The attribute name to be converted.

    :return: The converted model name.

    :example:
        attr_to_model("ip_addresses") -> "ip-addresses"
    """
    return attr.replace("_", "-")


def model_to_attr(model: str) -> str:
    """Convert model name to attribute name.

    :param model: The model name to be converted.

    :return: The converted attribute name.

    :example:
        model_to_attr("ip-addresses") -> "ip_addresses"
    """
    return model.replace("-", "_")


def nested_urls(nb_objects: LDAny) -> LStr:
    """Get a list of URLs from a Netbox nested objects.

    :param nb_objects: A list of Netbox objects.

    :return: URLs of nested objects.
    """
    urls: LStr = []
    for nb_object in nb_objects:
        if not isinstance(nb_object, dict):
            continue
        for key, value in nb_object.items():
            if key == "url" and isinstance(value, str):
                urls.append(value)
            elif isinstance(value, list):
                urls_ = nested_urls(value)
                urls.extend(urls_)
            elif isinstance(value, dict):
                if url := value.get("url"):
                    if isinstance(url, str):
                        urls.append(url)
    urls = vlist.no_dupl(urls)
    return sorted(urls)


def path_to_attrs(path: str) -> T2Str:
    """Convert path of app/model to attribute names.

    :param path: Path of app/model.

    :return: Application and model attribute names.

    :example:
        path_to_attrs("ipam/ip-addresses") -> "ipam", "ip_addresses"
    """
    app, model = path.strip("/").split("/")
    model = model_to_attr(model)
    return app, model


def model_singular(plural: str) -> str:
    """Convert a plural model name to a singular model name.

    :param plural: A plural model name.
    :return: A singular model name.
    """
    singular = plural.replace("_", "").replace("-", "")
    if singular.endswith("ies"):
        singular = singular[:-3] + "y"  # entries -> entry
    elif singular.endswith("ses"):
        singular = singular[:-2]  # ipaddresses -> ipaddress
    elif singular.endswith("xes"):
        singular = singular[:-2]  # prefixes -> prefix
    elif singular.endswith("sis"):
        pass  # chassis -> chassis
    elif singular.endswith("s"):
        singular = singular[:-1]  # types -> type
    return singular


def replace_upper(word: str) -> str:
    """Replace upper character with underscore and lower.

    :param word: The word to be modified.

    :return: The modified word.

    :example: replace_upper("IpAddresses") -> "ip_addresses"
    """
    if not word:
        return ""
    word = word[0].lower() + word[1:]
    new_word = ""
    for char in word:
        if char.isupper():
            new_word += "_" + char.lower()
        else:
            new_word += char
    return new_word


def url_to_ami_items(url: str) -> T3Str:
    """Split the URL into the application, model, and ID items.

    :param url: The URL to be parsed.

    :return: A tuple containing the application, model, and port (if available).
             If the URL is invalid or does not contain the necessary items, returns empty strings.

    :example:
        split_url("https://domain.com/api/ipam/vrfs?id=1") -> ("ipam", "vrfs", "1")
    """
    url_o: ParseResult = urllib.parse.urlparse(url)
    if not url_o.path:
        return "", "", ""

    path = url_o.path.strip("/")
    items = path.split("/")
    if len(items) < 2:
        return "", "", ""
    if items[0] == "api":
        items = items[1:]
    if len(items) < 2 or len(items) > 3:
        return "", "", ""

    app = str(items[0])
    model = str(items[1])
    id_ = ""
    if len(items) == 3:
        id_ = str(items[2])
    return app, model, id_


def url_to_ami(url: str, path: bool = False) -> T3StrInt:
    """Convert URL of app/model/id to attribute names.

    :param url: URL of app/model/id.
    :param path: If True, return model as item of path, else return madel as attribute.
    :return: Tuple of application attribute name, model attribute name and object ID.

    :example:
        url_to_attrs("https://domain.com/api/ipam/ip-addresses/1") -> "ipam", "ip_addresses", 1
    """
    app, model, idx = url_to_ami_items(url)
    expected = "expected app/modem/id format"

    if not app or app.isdigit():
        raise NbApiError(f"Invalid {app=} in {url=}, {expected}.")
    if not model or model.isdigit():
        raise NbApiError(f"Invalid {model=} in {url=}, {expected}.")
    if idx and not idx.isdigit():
        raise NbApiError(f"Invalid {idx=} in {url=}, {expected}.")

    if not path:
        model = model_to_attr(model)

    return app, model, vint.to_int(idx)


def url_to_am_path(url: str) -> str:
    """Convert URL to path app/model.

    :param url: A string representing the Netbox API URL.
    :return: A string representing the app/mode/ path.

    :example:
        url_to_am_path("https://domain.com/api/ipam/vrf/1") -> "ipam/vrf/"
    """
    app, model, _ = url_to_ami_items(url)
    if not (app and model):
        raise ValueError(f"{app=} {model=} required.")
    return f"{app}/{model}/"


def url_to_ami_path(url: str) -> str:
    """Convert URL to path app/model/id.

    :param url: A string representing the Netbox API URL.
    :return: A string representing the app/mode/id path.

    :example:
        url_to_am_path("https://domain.com/api/ipam/vrf/1") -> "ipam/vrf/1/"
    """
    app, model, id_ = url_to_ami_items(url)
    if not (app and model and id_):
        raise ValueError(f"{app=} {model=} {id_=} required.")
    return f"{app}/{model}/{id_}/"


def url_to_ami_url(url: str) -> str:
    """Convert URL to short URL with /api/app/model/id.

    :param url: A string representing the Netbox API URL.
    :return: A string representing the short URL.

    :example:
        url_to_ami_url("https://domain.com/api/ipam/vrf/1/") -> "/api/ipam/vrf/1/"
    """
    app, model, id_ = url_to_ami(url=url, path=True)
    ami_url = f"/api/{app}/{model}/"
    if id_:
        ami_url += f"{id_}/"
    return ami_url


def url_to_api_url(url: str) -> str:
    """Convert Netbox UI URl to API URL.

    :param url: A string representing the Netbox UI URL.
    :return: A string representing the Netbox API URL.

    :example:
        url_to_ui_url("https://domain.com/ipam/vrf/1/") -> "https://domain.com/api/ipam/vrf/1/"
    """
    url_o: ParseResult = urllib.parse.urlparse(url)
    app, model, id_ = url_to_ami(url=url, path=True)
    ui_url = f"{url_o.scheme}://{url_o.netloc}/api/{app}/{model}/"
    if id_:
        ui_url += f"{id_}/"
    return ui_url


def url_to_object_type(url: str) -> str:
    """Convert url to object_type.

    :param url: URL to Netbox object.
    :return: Object type.

    :example:
        url_to_object_type("/api/ipam/ip-addresses/1/") -> "ipam.ipaddress"
    """
    app, model, _ = url_to_ami(url)
    object_type = am_to_object_type(app, model)
    return object_type


def url_to_ui_url(url: str) -> str:
    """Convert Netbox API URl to UI URL.

    :param url: A string representing the Netbox API URL.
    :return: A string representing the Netbox UI URL.

    :example:
        url_to_ui_url("https://domain.com/api/ipam/vrf/1/") -> "https://domain.com/ipam/vrf/1/"
    """
    url_o: ParseResult = urllib.parse.urlparse(url)
    app, model, id_ = url_to_ami(url=url, path=True)
    ui_url = f"{url_o.scheme}://{url_o.netloc}/{app}/{model}/"
    if id_:
        ui_url += f"{id_}/"
    return ui_url
