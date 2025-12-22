from curl_cffi import requests
import random, json, math

class PerchanceContext:
    def __init__(
        self,
        LoreData: str,
        Username: str,
        UserDescription: str,
        BotName: str,
        BotDescription: str,
    ):
        self.loreData = LoreData
        self.Username = Username
        self.UserDescription = UserDescription
        self.BotName = BotName
        self.BotDescription = BotDescription

class _MessageHandler:
    @staticmethod
    def token_count(text: str) -> int:
        APPROX_CHARS_PER_TOKEN = 3.9
        return int(math.floor((len(text) / APPROX_CHARS_PER_TOKEN) + 0.5))

    @staticmethod
    def _build_message_block(messages, Username, BotName):
        parts = ["<MESSAGES>"]

        for m in messages:
            if m["role"] == "user":
                parts.append(f"{Username}: {m['content']}")
                parts.append("")
            elif m["role"] == "assistant":
                parts.append(f"{BotName}: {m['content']}")

        parts.append("</MESSAGES>")
        return "\n".join(parts)
    
    @staticmethod
    def convert_messages(messages, Context: PerchanceContext):
        _last_user_message = next(
            m for m in reversed(messages)
            if m["role"] == "user"
        )
        _messages_str = _MessageHandler._build_message_block(messages, Context.Username, Context.BotName)
        _loreData = json.dumps(Context.loreData)

        instruction = f"Please write the next 10 messages for the following chat/RP. Most messages should be a medium-length paragraph, including thoughts, actions, and dialogue. Create an engaging, captivating, and genuinely fascinating story. So good that you can't stop reading. Use a natural, unpretentious writing style.\n\n# Reminders:\n- Some of {Context.Username}'s messages are written by the user. Consider where the user is trying to lead the roleplay, and deeply intuit the story arc that the user is hinting toward with their actions. You should aim to write exactly the sort of story that they want to read.\n- You can use *asterisks* to start and end actions and/or thoughts in typical roleplay style. Most messages should be detailed and descriptive, including dialogue, actions, and thoughts. Utilize all five senses for character experiences.\n- This story never ends. You must keep the story going forever. Drive the story forward, introducing new arcs and events when narratively appropriate.\n- Aim for superb narrative pacing, and deep worldbuilding. Reveal the world/characters/plot gradually through character interactions and experiences. Allow the reader to discover its intricacies organically (instead of using exposition dumps).\n- Each message should be contained within a single paragraph. Add a blank line between each message. Balance moments of tension and relaxation to maintain reader engagement. Vary sentence and paragraph length to control the rhythm of the roleplay, switching from shorter, punchier sentences to longer, more descriptive ones as appropriate to create interesting variation in pace and structure.\n- Avoid unnecessary and unoriginal repetition of previous messages.\n- Bring characters to life by portraying their unique traits, thoughts, emotions, appearances, and speech patterns realistically. Consider the situation, motivations, and potential consequences. Ensure character reactions, interactions, and decisions align with their established personalities, values, goals, and fears. Use subtle gestures, distinctive quirks, and colloquialisms to create enriched, lifelike scenes. Allow characters' motivations and personalities to evolve authentically throughout the story, creating genuine character arcs.\n- The overall goal is to create a genuinely fascinating and engaging roleplay/story. So good that you can't stop reading. Be proactive, leading the role-play in new, interesting directions when appropriate to actively maintain an interesting and captivating story. Don't try to pull the user back to things that they don't want.\n- Develop the story in a manner that a skilled author and engaging storyteller would. Craft conversations that reveal character, advance the plot, and feel natural. Use subtext and unique speech patterns to differentiate characters and convey information indirectly.\n- Narrator messages should be longer than normal messages.\n\n# Here's {Context.BotName}'s description/personality:\n---\n{Context.BotDescription}\n---\n\n# Here's {Context.Username}'s description/personality:\n---\n{Context.UserDescription}\n---\n\n# Here's the initial scenario and world info:\n---\n{_loreData}\n---\n\n# Here's what has happened so far in this roleplay/chat/story:\n{_messages_str}\n---\n\nYour task is to write the next 10 messages in this chat/roleplay between {Context.Username} and {Context.BotName}. There should be a blank new line between messages.\n\nWrite the next 10 messages. Most messages should be a medium-length paragraph, including thoughts, actions, and dialogue."
        startWith = f"{Context.Username}: {_last_user_message}\n\n{Context.BotName}:"
        baseData = {
            "instruction": instruction,
            "startWith": startWith,
            "stopSequences": [
                "\n\n",
                f"\n{Context.Username}:",
                f"\n{Context.BotName}:"
            ],
            "generatorName": "ai-chat",
            "startWithTokenCount": _MessageHandler.token_count(startWith),
            "instructionTokenCount": _MessageHandler.token_count(instruction)
        }
        return baseData

class Perchance:
    def __init__(self, session: requests.Session):
        self.session = session
        self._emulate_page_load()

        self.userKey = ""
        self.verified = False # we dont really use this, damn

    @staticmethod
    def gen_cache_bust():
        return random.uniform(0.3, 1)
    @staticmethod
    def gen_random_int():
        return random.randint(0, 10**18 - 1)

    def _check_key_valid(self): # helper function to check if the key is still valid
        _temp_headers = {
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
        }
        _temp_headers = {**self.session.headers, **_temp_headers}
        _resp = self.session.get(f"https://text-generation.perchance.org/api/checkUserVerificationStatus?userKey={self.userKey}&__cacheBust={self.gen_cache_bust()}", headers=_temp_headers)
        _data = _resp.json()
        return _data["status"] == "verified"

    def _emulate_page_load(self): # everything the browser does at the start, not the generation part
        self.session.get("https://perchance.org/ai-chat")

        _temp_headers = {
            "referer": "https://perchance.org/",
            "sec-fetch-dest": "iframe",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-site",
        }
        _temp_headers = {**self.session.headers, **_temp_headers}

        self.session.get("https://3ed577a8ef2db1575c94395be05e8192.perchance.org/ai-chat?__generatorLastEditTime=1764050829011", headers=_temp_headers) # pretty fucking sure they dont check that
        
        _temp_headers["referer"] = "https://perchance.org/ai-chat"
        
        self.session.get(f"https://perchance.org/api/clearCacheIfGeneratorOrImportsHaveBeenUpdated?generatorName=ai-chat&importedGeneratorNames=ai-text-plugin,bug-report-plugin,comments-plugin,fullscreen-button-plugin,huge-emoji-list,literal-plugin,tabbed-comments-plugin-v1,text-editor-plugin-v1,upload-plugin,dynamic-import-plugin&clientHtmlServerRenderTime=1765915139961&transferSize=300&queryParamString=&__cacheBust={self.gen_cache_bust()}", headers=_temp_headers)

        _temp_headers = {
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
        }
        _temp_headers = {**self.session.headers, **_temp_headers}
        _resp = self.session.get(f"https://text-generation.perchance.org/api/verifyUser?thread=0&__cacheBust={self.gen_cache_bust()}", headers=_temp_headers)
        _data = _resp.json()
        if _data["status"] == "already_verified" or _data["status"] == "success":
            self.userKey = _data["userKey"]
        else:
            # if this fails go to https://perchance.org/ai-chat and generate 1 message, this skips cloudflare solving, only needed once (per ip probably)
            raise Exception("[Perchance.org] Failed to verify. Verify once in browser or someshit, rerun ig. Response:", _data)
        
        # infinite loop possible here but idgaf
        if self._check_key_valid():
            self.verified = True
        else:
            self._emulate_page_load() # ig?!

    def generate(self, _messages, PContext: PerchanceContext):
        if not self._check_key_valid():
            self._emulate_page_load()
        
        messagesData = _MessageHandler.convert_messages(_messages, PContext)
        
        _temp_headers = {
            "accept-encoding": "gzip, deflate, br, zstd",
            "origin": "https://text-generation.perchance.org",
            "referer": "https://text-generation.perchance.org/embed",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
        }
        _temp_headers = {**self.session.headers, **_temp_headers}
        for _ in range(3):
            _generation_url = f"https://text-generation.perchance.org/api/generate?userKey={self.userKey}&thread=1&requestId=aiTextCompletion{self.gen_random_int()}&__cacheBust={self.gen_cache_bust()}"
            _resp = self.session.post(_generation_url, json=messagesData, headers=_temp_headers)
            _resp_text = _resp.text
            if "invalid_key" in _resp_text:
                if not self._check_key_valid():
                    self._emulate_page_load()
            
        _final_message = ""
        for _line in _resp_text.splitlines():
            line = _line.strip()
            if not line:
                continue
            if line.startswith("t:"):
                _token = line.replace('t:"', '')[:-1]
                if not _token.strip():
                    continue
                _final_message += _token
            if line.startswith("data:"):
                _data = json.loads(line.replace("data:", ""))
                if _data["final"]:
                    _final_message += _data["text"]
                    break
        return _final_message.strip()
