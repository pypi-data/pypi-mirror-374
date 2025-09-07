from sanic import Sanic, response, Blueprint
from sanic.exceptions import Forbidden, SanicException
from sanic.response import html, text, json
from requests import request
from time import time
from .rate_limit import rate_limit
from .call import call_api, substitute
import json, hashlib, sys, os, inspect, random

request_data = None
debug = False
pathvars = {}
othervars = {}
var = {}

os.environ['SOMETHING'] = 'somevalue'

proxy_data = []
names = {}

class Apipie:
    def __init__(self, config_path: str, is_string: bool = False, proxies=None, max_retries=3, timeout=10, rotate=None):
        global proxy_data
        self.config_path = config_path
        self.is_string = is_string
        self.proxy_data = {
            'proxies': proxies,
            'max_retries': max_retries,
            'timeout': timeout,
            'rotate': rotate
        }
        
    def __getitem__(self, var_name):
        var = {**pathvars, **othervars}
        return var.get(var_name)
    
    def __setitem__(self, var_name, value):
        var = {**pathvars, **othervars}
        var[var_name] = value
        
    response = response

    def script(self, path):
        def decorator(func):
            names[path] = func
            return func
        return decorator

    def run(self, debug: bool = False, port: int = 8080, host: str = "127.0.0.1"):
        self.debug = debug
        self.port = port
        self.host = host
        try:
            main(
                config_path=os.path.dirname(os.path.abspath(sys.argv[0]))+'\\'+self.config_path,
                is_string=self.is_string,
                debug=self.debug,
                port=self.port,
                host=self.host
            )
        except FileNotFoundError:
            print(
                'Make sure path is correct based where and how the code is running, '
                f'because {self.config_path} was not found at '
                f'{os.path.dirname(os.path.abspath(sys.argv[0]))}\\{self.config_path}'
            )

class verification:    
    def hash_api_key(key: str) -> str:
        return hashlib.sha256(key.encode('utf-8')).hexdigest()

    def get_user_by_api_key(provided_key: str, users: dict) -> tuple:
        provided_key_hash = verification.hash_api_key(provided_key)
        for username, data in users.items():
            if debug:
                print("Checking user:", username)
                print("Stored hash:", data.get("api_key_hash"))
            if data.get("api_key_hash") == provided_key_hash:
                if debug: print("User verified:", username)
                return username, data
        return None, None


def main(config_path: str, is_string: bool = False, debug: bool = False, port: int = 8080, host: str = "127.0.0.1"):
    global othervars
    if debug: print('program started at: /a' + config_path)
    
    app = Sanic("API_Proxy")
    bp = Blueprint("proxy_routes")

    if is_string:
        config = config_path
    else:
        path = config_path.strip('\'"')
        with open(path) as f:
            config = f.read()
            
    if debug: print(config)

    foo = json.loads(config)
    keys = foo["keys"]
    replaced = substitute(config, keys)
    config = json.loads(replaced)
    users = config["users"]
    othervars = config.get("open-vars", {})
    routes = list(config["routes"].keys())
    route_to_api_key = config["routes"]
    apis = config["apis"]
    keys = config["keys"]

    def make_handler(api_name, api_config):
        cors_enabled = str(api_config.get("cors", "False")).lower() == "true"
        require_api_key = api_config.get("require_api_key", True)
        rate_limit_cfg = api_config.get("rate_limit", {"limit": 5, "window": 60})
        script = api_config.get("script", None)
        html_file = api_config.get("html_file", None)
        html_data = api_config.get("html", None)

        async def handler(request, **path_vars):
            global pathvars
            pathvars = path_vars
            if debug:
                print("path var for ", path_vars)
                print("othervars var for ", othervars)
            request_data = request

            # Check API Key
            api_key = request.headers.get("X-API-Key") or request.args.get("api_key")
            username, user_data = None, None
            if require_api_key:
                if not api_key:
                    if random.randint(1, 255) == 1:
                        raise SanicException("I'm a teapot ☕", status_code=418)
                    raise Forbidden("Missing API Key")
                username, user_data = verification.get_user_by_api_key(api_key, users)
                if not user_data:
                    if random.randint(1, 255) == 1:
                        raise SanicException("I'm a teapot ☕", status_code=418)
                    raise Forbidden("Invalid API Key")
                if api_name not in user_data.get("allowed_apis", []):
                    if random.randint(1, 255) == 1:
                        raise SanicException("I'm a teapot ☕", status_code=418)
                    raise Forbidden("API access denied for this key")
                
            if script:
                if request_data:
                    result = names[script](request_data)
                else:
                    result = names[script]()
                if result:
                    return result

            if html_file:
                with open(html_file, "r", encoding="utf-8") as f:
                    return html(substitute(f.read(), {**othervars, **path_vars}))

            if html_data:
                if isinstance(html_data, str):
                    return html(substitute(html_data, {**othervars, **path_vars}))
                elif isinstance(html_data, dict):
                    return html(substitute(json.dumps(html_data, indent=2), {**othervars, **path_vars}))
                else:
                    raise SanicException("Invalid HTML data format", status_code=500)

            merged_vars = {
                **othervars,
                **{k: v for k, v in request.args.items()},
                **{k: v[0] if isinstance(v, list) else v for k, v in request.form.items()},
                **path_vars
            }
            if debug: print("Merged vars:", merged_vars)
            result = call_api(api_config, merged_vars, *proxy_data)
            if debug: print("API call result:", result, type(result))
            resp = response.json(result.text)

            if cors_enabled:
                resp.headers["Access-Control-Allow-Origin"] = "*"
                resp.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, OPTIONS"
                resp.headers["Access-Control-Allow-Headers"] = "*"
            return resp

        # Rate limiting
        limit = int(rate_limit_cfg.get("limit", 5))
        window = int(rate_limit_cfg.get("window", 60))
        handler = rate_limit(limit, window, scope="ip")(handler)

        return handler

    for route in routes:
        api_key = route_to_api_key[route]
        config_entry = apis[api_key]
        method = config_entry.get("method", "GET").upper()
        handler = make_handler(api_key, config_entry)
        app.add_route(handler, f"/{route}", methods=[method, "OPTIONS"], name=f"handler_{route}")

    @bp.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
    async def proxy(request, path):
        api_key = request.args.get("api_key") or request.headers.get("X-API-Key")
        if not api_key or not is_valid_key(api_key):
            if random.randint(1, 255) == 1:
                return response.json({"error": "I'm a teapot ☕"}, status=418)
            return response.json({"error": "Invalid API Key"}, status=401)
    
    app.run(host=host, port=port, debug=debug, single_process=True)
    
if __name__ == "__main__":
    import sys
    main(
        config_path=sys.argv[1] if len(sys.argv) > 1 else 'api_config.json',
        is_string=(sys.argv[2].lower() == 'true') if len(sys.argv) > 2 else False
    )
