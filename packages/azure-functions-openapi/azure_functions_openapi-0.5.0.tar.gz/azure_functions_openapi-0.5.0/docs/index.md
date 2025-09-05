# Azure Functions OpenAPI

Welcome to **azure-functions-openapi** — a library that provides seamless integration of **OpenAPI (Swagger)** documentation for Python-based Azure Functions.

## Features

- `@openapi` decorator with:
  - `summary`, `description`, `tags`
  - `operation_id`, `route`, `method`
  - `request_model`, `response_model`
- Automatic generation of:
  - `/openapi.json`
  - `/openapi.yaml`
  - `/docs` (Swagger UI)
- Pydantic v1 and v2 support
- Type-safe schema generation
- Zero-configuration integration
- Compatible with Python 3.9+

## Getting Started

### 1. Create a Function App and Register Routes

To expose your Azure Functions with OpenAPI documentation, decorate your function with `@openapi`
and register the documentation endpoints manually.

```python
# function_app.py

import json
import logging
import azure.functions as func
from azure_functions_openapi.decorator import openapi
from azure_functions_openapi.openapi import get_openapi_json, get_openapi_yaml
from azure_functions_openapi.swagger_ui import render_swagger_ui

app = func.FunctionApp()


@app.route(route="http_trigger", auth_level=func.AuthLevel.ANONYMOUS)
@openapi(
    route="/api/http_trigger",
    summary="HTTP Trigger with name parameter",
    description="""
Returns a greeting using the **name** from query or body.

You can pass the name:
- via query string: `?name=Azure`
- via JSON body: `{ "name": "Azure" }`
""",
    operation_id="greetUser",
    tags=["Example"],
    parameters=[
        {
            "name": "name",
            "in": "query",
            "required": True,
            "schema": {"type": "string"},
            "description": "Name to greet",
        }
    ],
    response={
        200: {
            "description": "Successful response with greeting",
            "content": {
                "application/json": {
                    "examples": {
                        "sample": {
                            "summary": "Example greeting",
                            "value": {"message": "Hello, Azure!"},
                        }
                    }
                }
            },
        },
        400: {"description": "Invalid request"},
    },
)
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    name = req.params.get("name")
    if not name:
        try:
            body = req.get_json()
            name = body.get("name") if isinstance(body, dict) else None
        except ValueError:
            pass

    if not name:
        return func.HttpResponse("Invalid request – `name` is required", status_code=400)

    return func.HttpResponse(
        json.dumps({"message": f"Hello, {name}!"}),
        mimetype="application/json",
        status_code=200,
    )


# OpenAPI documentation routes
@app.route(route="openapi.json", auth_level=func.AuthLevel.ANONYMOUS)
def openapi_spec(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(get_openapi_json(), mimetype="application/json")


@app.route(route="openapi.yaml", auth_level=func.AuthLevel.ANONYMOUS)
def openapi_yaml_spec(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(get_openapi_yaml(), mimetype="application/x-yaml")


@app.route(route="docs", auth_level=func.AuthLevel.ANONYMOUS)
@app.function_name(name="swagger_ui")
def swagger_ui(req: func.HttpRequest) -> func.HttpResponse:
    return render_swagger_ui()
```

---

### 2. Run the App

Use the Azure Functions Core Tools:

```bash
func start
```

---

### 3. View the Swagger API

Once the app is running, open your browser:

- OpenAPI JSON: [http://localhost:7071/openapi.json](http://localhost:7071/openapi.json)
- OpenAPI YAML: [http://localhost:7071/openapi.yaml](http://localhost:7071/openapi.yaml)
- Swagger UI: [http://localhost:7071/docs](http://localhost:7071/docs)

---

## Documentation

- [Quickstart](./usage.md)
- [Installation Guide](./installation.md)
- [API Reference](./api.md)
- [Examples](./examples/hello_openapi.md)
- [Contribution Guide](./contributing.md)
- [Development Guide](./development.md)

---

## About

- Repository: [GitHub](https://github.com/yeongseon/azure-functions-openapi)
- License: MIT
