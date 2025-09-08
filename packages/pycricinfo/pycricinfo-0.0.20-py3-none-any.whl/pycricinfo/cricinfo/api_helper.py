import json
import logging
import re
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Optional, Type, TypeVar
from urllib.parse import urljoin, urlparse

import requests
from pydantic import BaseModel, ValidationError

from pycricinfo.config import BaseRoute, get_settings
from pycricinfo.exceptions import CricinfoAPIException
from pycricinfo.utils import replace_empty_objects_with_null

logger = logging.getLogger("cricinfo")
T = TypeVar("T", bound=BaseModel)


def get_and_parse(
    route: str,
    type_to_parse: Type[T],
    params: dict = None,
    null_out_empty_dicts: bool = False,
    base_route: BaseRoute = BaseRoute.core,
) -> T:
    """
    Make a GET request to the API and parse the response to the supplied type

    Parameters
    ----------
    route : str
        The route template to call
    type_to_parse : Type[T]
        The source model type to attempt to parse the response into
    params : dict, optional
        Any parameters to fill in into the route, in a dictionary of key-value pairs, by default None
    null_out_empty_dicts : bool, optional
        Whether to replace any dictionaries that contain only None values with None, by default False
    base_route: BaseRoute, optional
        The base route to use for the API call, by default BaseRoute.core
    Returns
    -------
    T
        The response data parsed into the supplied model
    """
    api_response = get_request(route, params, base_route)

    if null_out_empty_dicts:
        api_response = replace_empty_objects_with_null(api_response)

    try:
        return type_to_parse.model_validate(api_response)
    except ValidationError as ex:
        logger.error(ex)
        raise


def get_request(
    route: str,
    params: Optional[dict[str, str]] = None,
    base_route: BaseRoute = BaseRoute.core,
    response_output_sub_folder: str = None,
) -> dict | str:
    """
    Make a GET request to the Football Stats API

    Parameters
    ----------
    route : str
        The route template to call
    params : dict[str, str], optional
        Any parameters to fill in into the route, in a dictionary of key-value pairs, by default None
    base_route: BaseRoute, optional
        The base route to use for the API call, by default BaseRoute.core
    Returns
    -------
    dict
        The JSON content of the API response
    """
    request_id = str(uuid.uuid4())
    response_logging_extras = {
        "cricket_stats.request_id": request_id,
        "cricket_stats.request_route_template": route,
    }

    if params:
        route = format_route(route, params)

    if base_route == BaseRoute.core:
        base = get_settings().core_base_route_v2
    elif base_route == BaseRoute.site:
        base = get_settings().site_base_route_v2
    else:
        base = get_settings().pages_base_route
    full_route = f"{base}{route}"

    session = requests.Session()
    session.headers["User-Agent"] = get_settings().page_headers.user_agent
    session.headers["Referer"] = urljoin(route, urlparse(route).path)
    session.headers["Accept"] = get_settings().page_headers.accept

    logger.debug(f"Querying: {full_route}", extra={"cricket_stats.request_id": request_id})
    response = session.get(full_route)

    response_logging_extras["cricket_stats.response_code"] = response.status_code
    if base_route == BaseRoute.page:
        result: bytes = response.content
        logger.debug(json.dumps(f"Page fetched from: {full_route}"), extra=response_logging_extras)
        output = str(result)
        output_for_file = re.sub(r"^b\'|\'$", "", output)
        response_output_file_extension = "html"
    else:
        output = result = response.json()
        logger.debug(json.dumps(result, indent=4), extra=response_logging_extras)
        output_for_file = json.dumps(result, indent=4)
        response_output_file_extension = "json"

    _output_response_to_file(output_for_file, route, response_output_sub_folder, response_output_file_extension)

    if response.status_code != 200:
        logger.error(
            f"Status Code '{response.status_code}' returned for '{full_route}'",
            extra=response_logging_extras,
        )
        raise CricinfoAPIException(status_code=response.status_code, route=full_route, content=output)

    return output


def format_route(route: str, params: dict[str, str] = {}) -> str:
    """
    Format the route with the provided parameters

    Parameters
    ----------
    route : str
        The route template to format
    params : dict[str, str]
        The parameters to fill in into the route

    Returns
    -------
    str
        The formatted route
    """
    for key, value in params.items():
        if not key.startswith("{"):
            key = "{" + key
        if not key.endswith("}"):
            key = key + "}"
        route = route.replace(key, str(value))
    return route


def _output_response_to_file(response: str, route: str, sub_folder: str, file_extension: str) -> None:
    """
    Output the content of the response to a file

    Parameters
    ----------
    response : str
        The API/page response
    route : str
        The route that was called
    """
    folder = Path(get_settings().api_response_output_folder)
    today = datetime.today().strftime("%Y%m%d")
    file_name = f"{datetime.now(UTC).time().strftime('%H%M%S')}_{route.replace('/', '_')}.{file_extension}"

    if sub_folder:
        folder = folder / sub_folder
    folder = folder / today
    folder.mkdir(parents=True, exist_ok=True)

    file_path = (folder / file_name).resolve()
    with open(file_path, "w") as file:
        file.write(response)
