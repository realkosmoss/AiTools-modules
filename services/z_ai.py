from curl_cffi import requests
from datetime import datetime, timezone
from urllib.parse import urlencode
import uuid, time, re, json
import hmac, hashlib, base64
from typing import Union

class _ShittyFuckingQueryBuilder:
    def __init__(
        self,
        user_id,
        token,
        chat_id,
        user_agent,
        title,
        language="en-US",
        tz_name="Europe/Warsaw",
        platform="web",
        version="0.0.1",
        browser_name="Chrome",
        os_name="Windows",
        screen_width=1680,
        screen_height=1050,
        viewport_width=801,
        viewport_height=925,
        color_depth=24,
        pixel_ratio=1,
    ):
        now_ms = int(time.time() * 1000)
        now_utc = datetime.now(timezone.utc)
        self.data = {
            "timestamp": now_ms,
            "requestId": str(uuid.uuid4()),
            "user_id": user_id,
            "version": version,
            "platform": platform,
            "token": token,
            "user_agent": user_agent,
            "language": language,
            "languages": language,
            "timezone": tz_name,
            "cookie_enabled": True,
            "screen_width": screen_width,
            "screen_height": screen_height,
            "screen_resolution": f"{screen_width}x{screen_height}",
            "viewport_width": viewport_width,
            "viewport_height": viewport_height,
            "viewport_size": f"{viewport_width}x{viewport_height}",
            "color_depth": color_depth,
            "pixel_ratio": pixel_ratio,
            "current_url": f"https://chat.z.ai/c/{chat_id}",
            "pathname": f"/c/{chat_id}",
            "search": "",
            "hash": "",
            "host": "chat.z.ai",
            "hostname": "chat.z.ai",
            "protocol": "https:",
            "referrer": "",
            "title": title,
            "timezone_offset": -60,
            "local_time": now_utc.isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            "utc_time": now_utc.strftime("%a, %d %b %Y %H:%M:%S GMT"),
            "is_mobile": "false",
            "is_touch": "false",
            "max_touch_points": 0,
            "browser_name": browser_name,
            "os_name": os_name,
            "signature_timestamp": now_ms,
        }

    def string_for_signature(self):
        data = dict(self.data)
        data.pop("signature_timestamp", None)
        return urlencode(data)

    def string(self):
        return urlencode(self.data)

class _ShittyFuckingMessageHandler:
    _NS = uuid.UUID("00000000-0000-0000-0000-000000000001")

    def __init__(self, chat_id: str):
        self.chat_id = chat_id

    def build(self, messages):
        internal = []
        parent_id = None

        for m in messages:
            role = str(m["role"])
            content = str(m["content"])

            msg_id = str(
                uuid.uuid5(
                    self._NS,
                    f"{role}:{content}:{parent_id}"
                )
            )

            internal.append({
                "id": msg_id,
                "parent_id": parent_id,
                "role": role,
                "content": content,
            })

            parent_id = msg_id

        return internal

    def current(self, internal_messages):
        return internal_messages[-1]

class _ShittyFuckingContextHandler:
    def __init__(self):
        self.user_name = f"Guest-{int(time.time() * 1000)}"
        self.user_location = "Unknown"
        self.timezone = "Europe/Warsaw"

    def variables(self):
        now = datetime.now()
        return {
            "{{USER_NAME}}": self.user_name,
            "{{USER_LOCATION}}": self.user_location,
            "{{CURRENT_DATETIME}}": now.strftime("%Y-%m-%d %H:%M:%S"),
            "{{CURRENT_DATE}}": now.strftime("%Y-%m-%d"),
            "{{CURRENT_TIME}}": now.strftime("%H:%M:%S"),
            "{{CURRENT_WEEKDAY}}": now.strftime("%A"),
            "{{CURRENT_TIMEZONE}}": self.timezone,
            "{{USER_LANGUAGE}}": "en-US",
        }


class _ShittyFuckingRequestBuilder:
    @staticmethod
    def build(model: str, internal_messages: list, message_handler: _ShittyFuckingMessageHandler, context_handler: _ShittyFuckingContextHandler, stream: bool = True):
        current = next(m for m in reversed(internal_messages) if m["role"] == "user")
        
        return {
            "stream": stream,
            "model": model,
            "messages": [
                {
                    "role": m["role"],
                    "content": m["content"]
                }
                for m in internal_messages
            ],
            "signature_prompt": current["content"],
            "params": {},
            "extra": {},

            "features": {
                "image_generation": False,
                "auto_web_search": False,
                "preview_mode": True,
                "flags": [],
                "enable_thinking": False,
                "web_search": False,
            },

            "variables": context_handler.variables(),
            "chat_id": message_handler.chat_id,
            "id": str(uuid.uuid4()),
            "current_user_message_id": current["id"],
            "current_user_message_parent_id": current["parent_id"],

            "background_tasks": {
                "title_generation": True,
                "tags_generation": True,
            },
        }

class Z_AI:
    class Models:
        GLM_4_7: str        = "glm-4.7"
        glm_4_6v: str       = "glm-4.6v"
        glm_4_6: str        = "GLM-4-6-API-V1"
        glm_4_5v: str       = "0727-360B-API"

    class HMAC_SHA256: # big pain in my ass
        _ROOT_SECRET = b"key-@@@@)))()((9))-xxxx&&&%%%%%"
        _BUCKET_WINDOW_MS = 300_000

        @staticmethod
        def _hmac_sha256_hex(key: bytes, message: str) -> str:
            return hmac.new(
                key,
                message.encode("utf-8"),
                hashlib.sha256
            ).hexdigest()

        @staticmethod
        def _derive_w(timestamp_ms: int) -> bytes:
            bucket = timestamp_ms // Z_AI.HMAC_SHA256._BUCKET_WINDOW_MS
            w_hex = Z_AI.HMAC_SHA256._hmac_sha256_hex(
                Z_AI.HMAC_SHA256._ROOT_SECRET,
                str(bucket)
            )
            return w_hex.encode("utf-8")

        @staticmethod
        def sign(
            *,
            request_id: str,
            user_id: str,
            payload: str, # the fucking user message, ffs
            timestamp_ms: Union[int, str],
        ) -> str:
            timestamp_ms = int(timestamp_ms)

            n = (
                f"requestId,{request_id},"
                f"timestamp,{timestamp_ms},"
                f"user_id,{user_id}"
            )

            payload_b64 = base64.b64encode(
                payload.encode("utf-8")
            ).decode("utf-8")

            d = f"{n}|{payload_b64}|{timestamp_ms}"

            W = Z_AI.HMAC_SHA256._derive_w(timestamp_ms)

            return hmac.new(
                W,
                d.encode("utf-8"),
                hashlib.sha256
            ).hexdigest()

    def __init__(self, session: requests.Session):
        self.session = session
        self._emulate_page_load()

        # Needed bullshit
        self.x_fe_version: str
        self.chat_id: str = None
        self.page_title: str
        self.id: str
        self.token: str

        # yes
        self.MessageHandler: _ShittyFuckingMessageHandler
        self.ContextManager = _ShittyFuckingContextHandler()

    def _emulate_page_load(self):
        _resp = self.session.get("https://chat.z.ai/")
        _page_title_match = re.search(r'<link[^>]*\btitle="([^"]+)"', _resp.text, re.IGNORECASE)
        self.page_title = _page_title_match.group(1)
        
        _x_fe_version_match = re.search(r"prod-fe-\d+(?:\.\d+)+", _resp.text)
        self.x_fe_version = _x_fe_version_match.group(0)

        # Temp headers
        _temp_headers = {
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
        }
        _temp_headers = {**self.session.headers, **_temp_headers}
        
        _resp = self.session.get("https://chat.z.ai/api/v1/auths/", headers=_temp_headers) # gets us the "token"
        _data = _resp.json()
        
        self.id    = _data["id"]
        self.token = _data["token"]
        
        _temp_headers.update({"authorization": f"Bearer {self.token}"})

        self.session.get("https://chat.z.ai/api/models", headers=_temp_headers)
        self.session.get("https://chat.z.ai/api/v1/users/user/settings", headers=_temp_headers)
    
    def _create_chat(self, messages: list, model: str):
        _temp_headers = {
            "origin": "https://chat.z.ai",
            "referer": "https://chat.z.ai/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
        }
        _temp_headers = {**self.session.headers, **_temp_headers}

        last_user = next(m for m in reversed(messages) if m["role"] == "user")

        msg_id = str(uuid.uuid4())
        now_ms = int(time.time() * 1000)

        payload = {
            "chat": {
                "id": "",
                "title": "New Chat",
                "models": [model],
                "params": {},
                "history": {
                    "messages": {
                        msg_id: {
                            "id": msg_id,
                            "parentId": None,
                            "childrenIds": [],
                            "role": "user",
                            "content": {
                                "type": "text",
                                "text": last_user["content"]
                            },
                            "timestamp": now_ms,
                            "models": [model],
                        }
                    },
                    "currentId": msg_id
                },
                "tags": [],
                "flags": [],
                "features": [
                    {"type": "mcp", "server": "vibe-coding", "status": "hidden"},
                    {"type": "mcp", "server": "ppt-maker", "status": "hidden"},
                    {"type": "mcp", "server": "image-search", "status": "hidden"},
                    {"type": "mcp", "server": "deep-research", "status": "hidden"},
                    {"type": "tool_selector", "server": "tool_selector", "status": "hidden"},
                    {"type": "mcp", "server": "advanced-search", "status": "hidden"},
                ],
                "mcp_servers": [],
                "enable_thinking": False,
                "auto_web_search": False,
                "timestamp": now_ms,
            }
        }

        resp = self.session.post(
            "https://chat.z.ai/api/v1/chats/new",
            json=payload,
            headers=_temp_headers,
        )

        data = resp.json()
        chat_id = data.get("id")
        
        self.chat_id = chat_id
        self.session.get(f"https://chat.z.ai/c/{self.chat_id}")

    def generate(self, _messages, model: str):
        if not self.token:
            self._emulate_page_load()
        if not self.chat_id:
            self._create_chat(_messages, model)
            self.MessageHandler = _ShittyFuckingMessageHandler(self.chat_id)

        _internal_messages = self.MessageHandler.build(_messages)
        _payload = _ShittyFuckingRequestBuilder.build(model, _internal_messages, self.MessageHandler, self.ContextManager)
        _query   = _ShittyFuckingQueryBuilder(
            self.id,
            self.token,
            self.MessageHandler.chat_id,
            self.session.headers.get("user-agent"),
            self.page_title)
        _signature = self.HMAC_SHA256.sign(
            request_id=_query.data["requestId"],
            user_id=_query.data["user_id"],
            payload=_payload["signature_prompt"],
            timestamp_ms=_query.data["timestamp"]
        )
        _temp_headers = {
            "accept-language": "en-US",
            "authorization": f"Bearer {self.token}",
            "content-type": "application/json",
            "origin": "https://chat.z.ai",
            "referer": f"https://chat.z.ai/c/{self.chat_id}",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-fe-version": self.x_fe_version,
            "x-signature": _signature
        }
        _temp_headers = {**self.session.headers, **_temp_headers}

        # returns: data: {"data":{"content":"","done":true,"error":{"code":"INTERNAL_ERROR","detail":"Oops, something went wrong. Please refresh the page or try again later."}},"type":"chat:completion"}
        # for some fucking reason, doesnt seem to effect the actual response tho
        _resp = self.session.post(f"https://chat.z.ai/api/v2/chat/completions?{_query.string()}", headers=_temp_headers, json=_payload, timeout=120)
        out = []
        got_delta = False

        for line in _resp.text.splitlines():
            if not line.startswith("data:"):
                continue

            payload = line[5:].strip()
            if not payload or payload == "[DONE]":
                break

            try:
                evt = json.loads(payload)
            except Exception:
                continue

            data = evt.get("data")
            if not isinstance(data, dict):
                continue

            delta = data.get("delta_content")
            if delta is not None:
                out.append(delta)
                got_delta = True
                continue

            edit_index = data.get("edit_index")
            edit_content = data.get("edit_content")
            if (
                got_delta
                and isinstance(edit_index, int)
                and isinstance(edit_content, str)
            ):
                current = "".join(out)
                out = [current[:edit_index] + edit_content]
                continue

            if data.get("done") is True:
                break

            error = data.get("error")
            if error and not got_delta:
                raise RuntimeError(
                    f"{error.get('code')}: {error.get('detail')}"
                )

        if not got_delta:
            raise RuntimeError("No model output received")

        return "".join(out)
