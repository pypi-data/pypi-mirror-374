![apipie logo](https://raw.githubusercontent.com/kokoslabs/apipie/main/media/apipielogo.svg)

ever wished that apis where easy to use, ever wished that private apis could be used publicly, and not lose security, well this is (somewhat) the perfect thing for you. Documentation available [here](https://kokoslabs.github.io/apipie)

*installing apipie*

Install it by running
```bash
pip install apipie
```

if you would prefer not to use a venv run 

```bash
python3 -m pip install apipie
```

or, on windows

```bash
py -m pip install apipie
```

to use you can run

```bash
apipie config.json False
```

The first argument is the filename, or the json iteself, if you would rather just input it right into there, make the second value true, that tells the code you want to use a string not a file path

you can also run it inside a .py file.

example.py
```python
from apipie import Apipie

apipie=Apipie('config.json', False)

#or

apipie=Apipie('{"some":{"json":"here"}}',True)

if __name__ == "__main__":
    apipie.run(debug=True, port=8080, host = "127.0.0.1")
```