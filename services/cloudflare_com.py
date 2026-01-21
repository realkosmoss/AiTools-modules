from curl_cffi import requests
import time
import json
import random
import secrets

class Cloudflare:
    class Random:
        @staticmethod
        def gR():
            e = int(time.time() * 1000)
            t = int(time.perf_counter() * 1_000_000)

            result = []
            template = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx"

            for char in template:
                if char in {'x', 'y'}:
                    r = random.random() * 16

                    if e > 0:
                        r = int((e + r) % 16)
                        e //= 16
                    else:
                        r = int((t + r) % 16)
                        t //= 16

                    if char == 'x':
                        val = r
                    else:
                        val = (r & 3) | 8

                    result.append(f"{val:x}")
                else:
                    result.append(char)

            return "".join(result)
        
        @staticmethod
        def Dv(e=21):
            AR = "useandom-26T198340PX75pxJACKVERYMINDBUSHWOLF_GQZbfghjklqvwyzrict";
            t = ""
            e |= 0
            n = [secrets.randbits(8) for _ in range(e)]
            while e:
                e -= 1
                t += AR[n[e] & 63]

            return t
        
    class _Messages:
        @staticmethod
        def _is_continuation(old, new, max_new=2):
            if not old:
                return True

            def normalize(msgs):
                return [
                    (m["role"], m["content"])
                    for m in msgs
                ]

            old_n = normalize(old)
            new_n = normalize(new)

            if len(new_n) < len(old_n):
                return False

            if new_n[:len(old_n)] != old_n:
                return False

            if len(new_n) - len(old_n) > max_new:
                return False

            return True
        
        @staticmethod
        def _convert_messages(messages: list) -> list:
            _cf_msgs = []
            for m in messages:
                _cf_msgs.append({
                    "id": Cloudflare.Random.Dv(16),
                    "role": m["role"],
                    "parts": [
                        {
                            "type": "text",
                            "text": m["content"]
                        }
                    ]
                })

            return _cf_msgs
        
    class Models:
        # DeepSeek
        DEEPSEEK_MATH_7B = "@cf/deepseek-ai/deepseek-math-7b-instruct"
        DEEPSEEK_R1_32B = "@cf/deepseek-ai/deepseek-r1-distill-qwen-32b"

        # Google
        GEMMA_2B_IT_LORA = "@cf/google/gemma-2b-it-lora"
        GEMMA_3_12B = "@cf/google/gemma-3-12b-it"
        GEMMA_7B_LORA = "@cf/google/gemma-7b-it-lora"

        # Meta
        LLAMA2_7B_CHAT_FP16 = "@cf/meta/llama-2-7b-chat-fp16"
        LLAMA2_7B_CHAT_INT8 = "@cf/meta/llama-2-7b-chat-int8"

        LLAMA3_1_8B_INSTRUCT_FP8 = "@cf/meta/llama-3.1-8b-instruct-fp8"
        LLAMA3_2_1B_INSTRUCT = "@cf/meta/llama-3.2-1b-instruct"
        LLAMA3_2_3B_INSTRUCT = "@cf/meta/llama-3.2-3b-instruct"
        LLAMA3_2_11B_VISION_INSTRUCT = "@cf/meta/llama-3.2-11b-vision-instruct"
        LLAMA3_3_70B_INSTRUCT_FP8_FAST = "@cf/meta/llama-3.3-70b-instruct-fp8-fast"
        LLAMA3_8B_INSTRUCT = "@cf/meta/llama-3-8b-instruct"

        LLAMA4_SCOUT_17B_16E_INSTRUCT = "@cf/meta/llama-4-scout-17b-16e-instruct"

        # Mistral
        MISTRAL_7B_INSTRUCT_V0_1 = "@cf/mistral/mistral-7b-instruct-v0.1"
        MISTRAL_7B_INSTRUCT_V0_2_LORA = "@cf/mistral/mistral-7b-instruct-v0.2-lora"
        MISTRAL_SMALL_24B_INSTRUCT = "@cf/mistralai/mistral-small-3.1-24b-instruct"

        # OpenAI
        GPT_OSS_20B = "@cf/openai/gpt-oss-20b"
        GPT_OSS_120B = "@cf/openai/gpt-oss-120b"

        # Qwen
        QWEN1_5_14B_CHAT_AWQ = "@cf/qwen/qwen1.5-14b-chat-awq"
        QWEN2_5_CODER_32B_INSTRUCT = "@cf/qwen/qwen2.5-coder-32b-instruct"
        QWEN3_30B_FP8 = "@cf/qwen/qwen3-30b-a3b-fp8"
        QWQ_32B = "@cf/qwen/qwq-32b"
        
    def __init__(self, session: requests.Session):
        self.session = session
        self.ws: requests.WebSocket

        self.last_model: str = None
        self.last_messages: list = None
        
        # chat variables
        self._pk: str = None
        self._room_id: str = None

        self.base_url: str = None
        self.room_name: str = None
        self.ws_url: str = None

        self._emulate_page_load()

    def _emulate_page_load(self):
        self.session.get("https://playground.ai.cloudflare.com/")
        self._new_room()

    def _new_room(self):
        # chat variables
        self._pk = self.Random.gR()
        self._room_id = self.Random.Dv()
        # url construction
        self.base_url = "playground.ai.cloudflare.com/agents/playground"
        self.room_name = f"Cloudflare-AI-Playground-{self._room_id}"
        self.ws_url = f"wss://{self.base_url}/{self.room_name}?_pk={self._pk}"

        _temp_headers = {
            "referer": "https://playground.ai.cloudflare.com/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin"
        }
        _temp_headers = {**self.session.headers, **_temp_headers}
        self.session.get(f"https://{self.base_url}/{self.room_name}/get-messages", headers=_temp_headers)

        self.ws = self.session.ws_connect(
            self.ws_url,
            headers={
                "Origin": "https://playground.ai.cloudflare.com",
                "User-Agent": self.session.headers.get("user-agent"),
                "Sec-GPC": "1",
                "sec-websocket-extensions": "permessage-deflate; client_max_window_bits",
                "Pragma": "no-cache",
            }
        )
        self.ws.send_json({"args":[],"id":f"{self.Random.Dv(8)}","method":"getModels","type":"rpc"})

    def _change_model(self, model, system = "You are a helpful assistant."):
        # send it and pray
        self.ws.send_json({
            "type": "cf_agent_state",
            "state": {
                "model": model,
                "temperature": 1,
                "stream": True,
                "system": system
            }
        })

    def _parse_stream(self):
        def _iter_json_objects(s: str):
            decoder = json.JSONDecoder()
            idx = 0
            length = len(s)

            while idx < length:
                while idx < length and s[idx].isspace():
                    idx += 1
                if idx >= length:
                    break

                try:
                    obj, idx = decoder.raw_decode(s, idx)
                except json.JSONDecodeError:
                    break
                yield obj
        reasoning = []
        text = []

        while True:
            frame, opcode = self.ws.recv()

            if opcode != 1:
                continue

            msg = json.loads(frame)

            if msg.get("type") != "cf_agent_use_chat_response":
                continue

            if msg.get("done"):
                break

            body = msg.get("body")
            if not body:
                continue

            for inner in _iter_json_objects(body):
                t = inner.get("type")

                if t == "reasoning-delta":
                    reasoning.append(inner.get("delta", ""))

                elif t == "text-delta":
                    text.append(inner.get("delta", ""))

        return {
            "reasoning": "".join(reasoning).strip(),
            "text": "".join(text).strip(),
        }

    def generate(self, messages: list, model: str, *, system=None):
        new_chat = False

        if self.last_model != model:
            self._change_model(model, system)
            self.last_model = model
            new_chat = True

        if not self._Messages._is_continuation(self.last_messages, messages):
            new_chat = True

        if new_chat:
            if not self.ws.closed:
                self.ws.close()
            self._new_room()
            self._emulate_page_load()
            self.last_messages = []


        self.last_messages = messages.copy()

        _request_id = self.Random.Dv(8)
        _messages = self._Messages._convert_messages(messages)

        _base = {
            "id": _request_id,
            "type": "cf_agent_use_chat_request",
            "url": f"https://playground.ai.cloudflare.com/agents/playground/{self.room_name}",
            "init": {
                "method": "POST",
                "headers": {
                    "content-type": "application/json",
                    "user-agent": "ai-sdk/5.0.116 runtime/browser"
                },
                "body": json.dumps({
                    "id": self.Random.gR(),
                    "messages": _messages,
                    "trigger": "submit-message"
                })
            }
        }
        if self.ws.closed:
            self._new_room()
        self.ws.send_json(_base)

        _out = self._parse_stream()
        return _out["text"]
