if __name__ == "__main__":
    from .main import Apipie
    import sys
    apipie=Apipie(
        config_path=sys.argv[1] if len(sys.argv) > 1 else 'api_config.json',
        is_string=(sys.argv[2].lower() == 'true') if len(sys.argv) > 2 else False
    )
    apipie.run(debug=(sys.argv[3].lower() == 'true') if len(sys.argv) > 3 else False, port=int(sys.argv[4]) if len(sys.argv) > 4 else 8080, host=sys.argv[5] if len(sys.argv) > 5 else "127.0.0.1")