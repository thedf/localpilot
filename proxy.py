import config
import httpx
import os
import subprocess
import logging
from starlette import applications, responses, exceptions
from starlette.requests import Request
import config
import json
import uvicorn

app = applications.Starlette()
state = config.models[config.models["default"]]
local_server_process = None
logging.basicConfig(level=logging.DEBUG)


def start_local_server(model_filename):
    global local_server_process
    if local_server_process:
        local_server_process.terminate()
        local_server_process.wait()
    cmd = [
        "python3",
        "-m",
        "llama_cpp.server",
        "--model",
        model_filename,
        "--n_gpu_layers",
        "1",
        "--n_ctx",
        "4096",
    ]  # TODO: set this more correctly
    logging.debug("Running: %s" % " ".join(cmd))
    local_server_process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )


@app.route("/set_target", methods=["POST"])
async def set_target(request: Request):
    global state
    response = await request.json()
    target = response["target"]
    if target not in config.models:
        raise exceptions.HTTPException(
            status_code=400, detail=f"Invalid target: {target}"
        )

    state = config.models[target]
    if config.models[target].get("type") == "local":
        start_local_server(
            os.path.join(config.model_folder, config.models[target]["filename"])
        )

    message = f"Target set to {state}"
    return responses.JSONResponse({"message": message}, status_code=200)

@app.route('/telemetry{path:path}', methods=["GET", "POST", "PUT", "DELETE"])
async def telemetry(request: Request):
    if request.url.path == '/telemetry/vscode/ab' :
        data  = {
            "Features": [
                "vsliv368cf",
                "vsreu685",
                "python383cf",
                "vspor879",
                "vspor708",
                "vspor363",
                "binariesv615",
                "bridge0708",
                "bridge0723",
                "vsaa593",
                "copilotaa-treat",
                "c4g48928",
                "asynctok",
                "aa_t_chat"
            ],
            "Flights": {
                "1j36": "vsliv368cf",
                "1j6r": "vsreu685",
                "1o3k": "python383cf",
                "1wr3": "vspor879",
                "1wr7": "vspor708",
                "1wra": "vspor363",
                "2po2": "binariesv615",
                "2spg": "bridge0708",
                "2v3u": "bridge0723",
                "30jm": "vsaa593",
                "3sde": "copilotaa-treat",
                "3w27": "c4g48928",
                "57ej": "asynctok",
                "5lyy": "aa_t_chat"
            },
            "Configs": [
                {
                    "Id": "vscode",
                    "Parameters": {
                        "aa_t_chat": True,
                        "account-aa": True,
                        "config.editor.experimental.asyncTokenization": True,
                        "copilotaa": True,
                        "livesharecontinuousaa": False,
                        "mindaroBinariesVersion": "1.0.20210615.1",
                        "mindaroBinariesVersion-1.0.20210702": "1.0.20210708.15",
                        "mindaroBinariesVersion-1.0.20210723": "1.0.20210723.6",
                        "portForwardingServiceEnabled-development": True,
                        "portForwardingServiceEnabled-production": True,
                        "portForwardingServiceEnabled-staging": True,
                        "RemoveKernelToolbarInInteractiveWindow": False,
                        "reusableLinks": True,
                        "shouldUseGrpcService": True
                    }
                }
            ],
            "ParameterGroups": None,
            "FlightingVersion": 5446,
            "ImpressionId": "139A620C2CC74DBF822AFF55CA99E6E8",
            "AssignmentContext": "vsliv368cf:30146710;vsreu685:30147344;python383cf:30185419;vspor879:30202332;vspor708:30202333;vspor363:30204092;binariesv615:30325510;bridge0708:30335490;bridge0723:30353136;vsaa593:30376534;copilotaa-treat:30487095;c4g48928:30535728;asynctok:30898717;aa_t_chat:30882232;"
        }
    else :
        data = {"success" : True}
    return responses.JSONResponse(data, status_code=200)

# Used to support copilot
@app.route("/copilot_internal/v2/token", methods=["GET"])
async def get_copilot_token(request: Request):
    content = {
        "expires_at": 2600000000,
        "annotations_enabled": True,
        "chat_enabled": True,
        "chat_jetbrains_enabled": False,
        "code_quote_enabled": True,
        "copilot_ide_agent_chat_gpt4_small_prompt": False,
        "copilotignore_enabled": False,
        "intellij_editor_fetcher": False,
        "prompt_8k": True,
        "public_suggestions": "disabled",
        "refresh_in": 1500,
        "sku": "free_educational",
        "snippy_load_test_enabled": False,
        "telemetry": "disabled",
        "token": "tid=4738e6bf83be7560d2b35387822b1ffa2;exp=2600000000;sku=free_educational;st=dotcom;chat=1;8kp=1:3a8f77a59e67d477a0f7e1e9aad5734760d03290a5ae2fc4b029bfca8d5bd2762",
        "tracking_id": "4738e6bf83be7560d2b35387822b1ffa2",
        "vsc_panel_v2": False,
    }
    return responses.JSONResponse(status_code=200, content=content)


@app.route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(request: Request):
    global state
    path = request.url.path
    # TODO: make converters based on the known api formats
    # Check and modify the path based on the given conditions
    if path.startswith("/v1/engines/") and path.endswith("/completions"):
        path = "/v1/completions"
    elif path == "/completions":
        path = "/v1/chat/completions"

    logging.debug(f"Current state: {state}")

    headersToAdd = {}
    if state["type"] == "remote":
        url = f"{state['domain']}{path}"
        if "api_key" in state and state["api_key"]:
            headersToAdd = {"Authorization": f"Bearer {state['api_key']}"}
    elif state["type"] == "local":
        url = f"http://localhost:8000{path}"

    # Decode the byte string into a regular string
    data_bytes = await request.body()
    data_str = data_bytes.decode("utf-8")

    # Parse the string into a dictionary
    # Make sure to handle exceptions in case the string is not a valid JSON
    try:
        data = json.loads(data_str)
    except json.JSONDecodeError:
        # Handle the error case, possibly by returning an error response
        return responses.Response("Invalid request data", status_code=400)

    headers = dict(request.headers) | headersToAdd

    # TODO: adjust the inputs and outputs based on api format
    # Clean headers and adjust data
    headers.pop("authorization", None)
    headers.pop("content-length", None)
    data["model"] = state["model"]
    data = json.dumps(data)
    r = None
    async with httpx.AsyncClient() as client:
        try:
            if request.method == "GET":
                r = await client.get(url, params=request.query_params, headers=headers)
            elif request.method == "POST":
                r = await client.post(url, data=data, headers=headers, timeout=30)
            elif request.method == "PUT":
                r = await client.put(url, data=data, headers=headers)
            elif request.method == "DELETE":
                r = await client.delete(url, headers=headers)
        except httpx.RemoteProtocolError as exc:
            logging.debug(f"Connection closed prematurely: {exc}")
    content = r.content if r else ""
    status_code = r.status_code if r else 204
    headers = dict(r.headers) if r else dict()
    return responses.Response(content=content, status_code=status_code, headers=headers)


@app.exception_handler(404)
async def not_found(request, exc):
    return responses.JSONResponse({"error": "Not found"}, status_code=404)


@app.exception_handler(500)
async def server_error(request, exc):
    return responses.JSONResponse({"error": "Server error"}, status_code=500)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5001)
