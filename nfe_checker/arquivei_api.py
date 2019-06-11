import base64
import json
import xml.etree.ElementTree as ET
from typing import List, Tuple, Dict
from urllib.parse import urlparse, parse_qs

import requests
from tenacity import retry, stop_after_attempt, wait_random

from nfe_checker.shared import logger

API_BASE = "https://apiuat.arquivei.com.br"
_API_ENDPOINT = API_BASE + "/v1/nfe/received?cursor={cursor}&limit={limit}"
_ = [".", "NFe", "infNFe", "total", "ICMSTot", "vNF"]
_NFE_VALUE_XPATH = "/{http://www.portalfiscal.inf.br/nfe}".join(_)


def parse_nfe_xml(xml_str: str) -> dict:
    root = ET.fromstring(xml_str)
    result = {"value": float(root.find(_NFE_VALUE_XPATH).text)}
    return result


def _parse_nfe_xml(item: dict) -> Dict:
    """
    Parse the XML of each NFE item from the API's JSON response
    Args:
        item: a single NFE dict, with the 'xml' and 'access_key' keys

    Returns:

    """
    decoded = base64.b64decode(item["xml"])
    parsed_xml = parse_nfe_xml(decoded)
    return {"access_key": item["access_key"], "value": parsed_xml["value"]}


def _get_cursor_from_url(url: str):
    """
    Parse the URL params and returns the cursor
    >>> _get_cursor_from_url("https://apiuat.arquivei.com.br/v1/nfe/received?cursor=30439&limit=50")
    30439
    """

    query = urlparse(url).query
    return int(parse_qs(query)["cursor"][0])


class ArquiveiAPI:
    def __init__(self, client: requests.Session, credentials: dict):
        """
        Args:
            client: requests Session client
        """
        self.credentials = credentials
        self.client = client

    @retry(reraise=True, stop=stop_after_attempt(2), wait=wait_random(1, 2))
    def query_nfes(self, cursor: int = 0, limit: int = 50) -> dict:
        """
        Just a basic query using the API. The 'retry' decorator gives us more
        reliability,  preventing transients faults.
        """
        limit = min(50, limit)
        url_query = _API_ENDPOINT.format(cursor=cursor, limit=limit)

        logger.debug(f"Requesting '{url_query}'")

        response = self.client.get(url_query, headers=self.credentials)
        try:
            _ = response.json()
        except json.JSONDecodeError as e:
            logger.exception(f"Problem to decode the response: '{response.text}'", e)
            raise e

        if response.status_code != 200:
            logger.error(f"Response for '{url_query}' was {response.status_code}")
            logger.error(_)
        logger.debug(f"{_['count']} NFEs found. Next: {_['page']['next']}")
        return _

    def get_last_nfes(self, cursor: int = 0, limit: int = 50) -> Tuple[List[Dict], int]:
        """
        Using recursion we iterate over the API in order to get the NFE's (
        all the availables or just the new ones)

        Args:
           cursor: initial cursor position
           limit: max results by query (max 50)

        Returns: List of NFE's objects and next page cursor
        """
        all_nfes = []
        response = self.query_nfes(cursor=cursor)

        next_page_cursor = _get_cursor_from_url(response["page"]["next"])

        if response["count"] == limit:
            next_nfes, next_page_cursor = self.get_last_nfes(next_page_cursor)
            all_nfes += next_nfes

        for item in response["data"]:
            all_nfes.append(_parse_nfe_xml(item))

        return all_nfes, next_page_cursor
