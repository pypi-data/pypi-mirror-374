# call.py
from requests import request
import random, os
from itertools import cycle

def proxy_request(
    method,
    url,
    proxies=None,
    data=None,
    json=None,
    headers=None,
    params=None,
    max_retries=5,
    rotate='random',
    timeout=10,
    **kwargs
):
    """
    Send an HTTP request via proxies, rotating through them on failure.

    Args:
      method (str): 'GET', 'POST', etc.
      url (str): Target URL.
      proxies (list): List of proxy address strings or dicts.
      data, json, headers, params: Passed to requests.
      max_retries (int): How many times to retry per request.
      rotate (str): 'random' or 'cycle' (round robin).
      timeout (int): Timeout per request.
      **kwargs: Any additional requests arguments.

    Returns:
      requests.Response object if successful.
      Raises last exception if all retries failed.
    """
    print(f"Calling {method} {url} with proxies: {proxies}")
    if(proxies):
        proxy_source = (
            cycle(proxies) if rotate == 'cycle' else None
        )

        for attempt in range(max_retries):
            proxy = (
                next(proxy_source)
                if proxy_source
                else random.choice(proxies)
            )
            if isinstance(proxy, dict):
                proxy_dict = proxy
            else:
                proxy_dict = {'http': proxy, 'https': proxy}
            try:
                response = request(
                    method=method,
                    url=url,
                    proxies=proxy_dict,
                    data=data,
                    json=json,
                    headers=headers,
                    params=params,
                    timeout=timeout,
                    **kwargs
                )
                response.raise_for_status()
                return response
            except Exception as ex:
                last_exception = ex
        raise last_exception
    
    else:
        response = request(
            method=method,
            url=url,
            data=data,
            json=json,
            headers=headers,
            params=params,
            timeout=timeout,
            **kwargs
        )
        response.raise_for_status()
        return response

def substitute(obj, variables):
    """
    Recursively substitute placeholders in strings, dicts, and lists.

    Supports:
      - <key> and [key] from the variables dict
      - {ENV_VAR} from environment variables
    """
    if isinstance(obj, str):
        replaced = obj
        # Replace from variables
        for k, v in variables.items():
            print(f"Substituting in string: {replaced}, key: {k}, value: {v}")
            replaced = replaced.replace(f"<{k}>", str(v))
            replaced = replaced.replace(f"[{k}]", str(v))

        # Replace from environment
        for k, v in os.environ.items():
            if f"{{{k}}}" in replaced:
                replaced = replaced.replace(f"{{{k}}}", v)

        return replaced

    elif isinstance(obj, dict):
        return {k: substitute(v, variables) for k, v in obj.items()}

    elif isinstance(obj, list):
        return [substitute(i, variables) for i in obj]

    else:
        return obj


def call_api(config, variables, proxies=None, max_retries=5, timeout=10, rotate='random'):
    #print(f"Calling API with config: {config} and variables: {variables}")
    method = config.get("method", "GET").upper()
    url = substitute(config.get("url"), variables)
    #print(f"Prepared URL: {url}")
    headers = substitute(config.get("headers", {}).copy(), variables)
    params = substitute(config.get("params", {}), variables)
    data = substitute(config.get("data", None), variables)
    json_data = substitute(config.get("json", None), variables)
    timeout = config.get("timeout", timeout)

    if "bearer_token" in config:
        headers["Authorization"] = f"Bearer {substitute(config['bearer_token'], variables)}"

    resp = proxy_request(
        method=method,
        url=url,
        headers=headers,
        params=params,
        data=data,
        json=json_data,
        proxies=proxies,
        timeout=timeout,
        max_retries=max_retries,
        rotate=rotate,
    )
    return resp

