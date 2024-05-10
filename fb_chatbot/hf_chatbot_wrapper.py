import json
import os
from dataclasses import dataclass

import alog
from hugchat import hugchat
from hugchat.hugchat import ChatBot, Message
from hugchat.login import Login
from prisma import Prisma

from fb_chatbot import settings


@dataclass(unsafe_hash=True)
class HFChatBotWrapper:
    save_session: bool
    db: Prisma
    cookies: dict = None
    chatbot: ChatBot = None
    cookie_name: str = 'hf_session'

    def __post_init__(self):
        self.cookies = self.db.session.find_unique(where=dict(id=self.cookie_name))

        if not self.cookies or self.save_session:
            EMAIL = settings.HF_EMAIL
            PASS = settings.HF_PASS
            cookie_path_dir = "./cookies/"  # NOTE: trailing slash (/) is required to avoid errors
            sign = Login(EMAIL, PASS)
            cookies = sign.login(cookie_dir_path=cookie_path_dir, save_cookies=True)
            self.db.session.create(dict(id=self.cookie_name,
                                        value=json.dumps(cookies.get_dict())))

        self.cookies = self.db.session.find_unique(where=dict(id=self.cookie_name))

        self.chatbot = hugchat.ChatBot(cookies=self.cookies.value)

        models = [model.name for model in self.chatbot.get_available_llm_models()]

        llm_ix = models.index('meta-llama/Meta-Llama-3-70B-Instruct')

        self.chatbot.switch_llm(llm_ix)

        # self.chatbot.chat('''
        # Estas son tus instrucciones:
        # 1)
        # ''')

        def chat(self, **kwargs) -> Message:
            return self.chatbot.chat(**kwargs)
