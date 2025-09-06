from typing import Optional
import requests

from hestia_earth.converters.base.converter.helpers import is_url, is_uuid


def get_external_ecoinvent_process_data(glossary_enty: str) -> Optional[dict]:
    if is_url(glossary_enty) and "ecoinvent.org" in glossary_enty:
        api_url = glossary_enty
    elif is_uuid(glossary_enty):
        api_url = f'https://glossary.ecoinvent.org/ids/{glossary_enty}'
    else:
        raise Exception("")

    try:
        first_connection_attempt = requests.get(api_url, allow_redirects=False)

        headers = {
            "Referer": first_connection_attempt.next.url,
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Sec-GPC": "1",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Priority": "u=0, i",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache"
        }
        ecoinvent_process_json_result = requests.get(api_url, allow_redirects=True, headers=headers).json()
    except Exception as e:
        raise e

    return ecoinvent_process_json_result
