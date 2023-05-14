import json

import quart
import quart_cors
from quart import request
import subprocess
import os
import tempfile

app = quart_cors.cors(quart.Quart(__name__), allow_origin="https://chat.openai.com")


def execute_python_file(file_path):
    result = subprocess.run(["python", file_path], capture_output=True, text=True)
    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
    }


@app.post("/execute")
async def execute_code():
    data = await request.get_json()
    code = data.get("code")
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as temp:
        temp.write(code)
    response = execute_python_file(temp.name)
    os.remove(temp.name)
    return quart.Response(response=json.dumps(response), status=200)


@app.get("/logo.png")
async def plugin_logo():
    filename = "logo.png"
    return await quart.send_file(filename, mimetype="image/png")


@app.get("/.well-known/ai-plugin.json")
async def plugin_manifest():
    host = request.headers["Host"]
    with open("./.well-known/ai-plugin.json") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/json")


@app.get("/openapi.yaml")
async def openapi_spec():
    host = request.headers["Host"]
    with open("openapi.yaml") as f:
        text = f.read()
        return quart.Response(text, mimetype="text/yaml")


def main():
    app.run(debug=True, host="0.0.0.0", port=5003)


if __name__ == "__main__":
    main()
