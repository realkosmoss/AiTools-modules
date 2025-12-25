# pip install fastapi uvicorn
# uvicorn api:app --host 127.0.0.1 --port 11434
from fastapi import FastAPI
from datetime import datetime, timezone
from fastapi import Request

# from services.perchance_org import Perchance, PerchanceContext # not adding this, cant be bothered really
from services.z_ai import Z_AI
from services.cloudflare_com import Cloudflare

from fingerprints import make_galaxy_s23

session = make_galaxy_s23()

# fucking services, 100% not the best way to do it but who the fuck cares
# hmm, probably mutating the session, both z.ai and cloudflare, fuck
zai = Z_AI(session)
cf = Cloudflare(session)

MODEL_MAP = {
    key: {
        "provider": provider,
        "model": value,
    }
    for provider, cls in {
        "zai": Z_AI.Models,
        "cloudflare": Cloudflare.Models,
    }.items()
    for name, value in vars(cls).items()
    if not name.startswith("_")
    for key in (
        (name, f"{name}_thinking") if provider == "zai" else (name,)
    )
}

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

@app.api_route("/", methods=["GET", "HEAD"])
def root():
    return "very good very nice very good very niceeee"

@app.api_route("/version", methods=["GET", "HEAD", "POST"])
@app.api_route("/api/version", methods=["GET", "HEAD", "POST"])
def version():
    return {"version":"0.13.5"}

@app.api_route("/api/tags", methods=["GET", "HEAD"])
def ls():
    base_format = {
        "models": []
    }
    for _model_name in MODEL_MAP:
        _model = {
                "name": _model_name,
                "model": _model_name,
                "modified_at": "2069-01-01T00:00:00.0000000+00:00",
                "size": 1000000000,
                "digest": "1111111111111111111111111111111111111111111111111111111111111111",
                "details": {
                    "parent_model": "",
                    "format": "gguf",
                    "family": _model_name,
                    "families": [
                        _model_name
                    ],
                    "parameter_size": "699.99M",
                    "quantization_level": "Q8_0"
                }
            }
        base_format["models"].append(_model)
    return base_format

# add /api/ps

@app.post("/api/show")
def show(body: dict):
    _model_name = body.get("name") or body.get("model")
    if not _model_name:
        return "nice"
    _base = {
        "license": "Shitty license",
        "details": {
            "parent_model": "",
            "format": "gguf",
            "family": _model_name,
            "families": [_model_name],
            "parameter_size": "699.99M",
            "quantization_level": "Q8_0"
        },
        "model_info": {
            "general.architecture": _model_name,
            "general.parameter_count": 1000000000,
            "general.quantization_version": 2,
            f"{_model_name}.context_length": 32768
        },
        "capabilities": ["completion"],
        "modified_at": "2025-12-22T20:27:58.3889148+01:00"
    }
    return _base

@app.post("/api/generate")
async def generate(req: Request):
    body = await req.json()

    model = body.get("model", "unknown")
    messages = body.get("messages", [])

    content = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            content = m.get("content", "")
            break

    return {
        "model": model,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "message": {
            "role": "assistant",
            "content": f"echo: {content}",
        },
        "done": True,
    }

@app.post("/api/chat")
async def chat(req: Request):
    body = await req.json()

    model = body.get("model", "unknown")
    messages = body.get("messages", [])

    entry = MODEL_MAP.get(model)
    if not entry:
        return "not actual model fuck face", 400

    provider = entry["provider"]
    _model = entry["model"]

    if provider == "zai":
        thinking = False
        if "_thinking" in _model:
            _model = _model.replace("_thinking", "")
            thinking = True
        response = zai.generate(messages, _model, thinking=thinking)
    elif provider == "cloudflare":
        response = cf.generate(messages, _model)
    else:
        raise RuntimeError(f"Unsupported provider: {provider}")

    return {
        "model": model,
        "created_at": "2069-01-01T00:00:00.000000Z",
        "message": {
            "role": "assistant",
            "content": response
        },
        "done": True,
        "total_duration": 699999999,
        "load_duration": 699999,
        "prompt_eval_count": 69,
        "prompt_eval_duration": 6999999,
        "eval_count": 699,
        "eval_duration": 699999999
    }

@app.post("/api/me")
async def me():
    return {
        "id": "69999999-6999-6999-6999-699996999999",
        "email": "user@example.com",
        "name": "Jane Doe",
        "bio": "example",
        "avatarurl": "https://example.com/avatar.png",
        "firstname": "Jane",
        "lastname": "Doe",
        "plan": "free"
    }