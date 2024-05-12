#!/usr/bin/env python

from fb_chatbot import settings
from fb_chatbot.facebook_thread import FacebookThreadInstance
from fb_chatbot.hf_chatbot_wrapper import HFChatBotWrapper
from fbchat import Client
from prisma import Prisma
from redis import Redis
from redis_collections import List

import alog
import click
import json
import pickle
import time


class FacebookChatResponder(Client):
    threads = dict()

    def __init__(
        self,
        dry_run,
        hf_clear_conv,
        save_session=False,
        **kwargs
    ):
        self.redis_client = Redis(host=settings.REDIS_HOST)
        self.dry_run = dry_run
        self.db = Prisma()
        self.db.connect()
        session_cookies = None

        if not save_session:
            session_cookies = (self.db.session
                               .find_unique(where=dict(id=settings.FACEBOOK_EMAIL)))

            if session_cookies:
                session_cookies = session_cookies.value

        super().__init__(session_cookies=session_cookies,
                         **kwargs)

        session_cookies = (self.db.session
                           .find_unique(where=dict(id=settings.FACEBOOK_EMAIL)))

        if save_session or not session_cookies:
            data = dict(id=settings.FACEBOOK_EMAIL,
                        value=json.dumps(self.getSession()))
            session_cookies = self.db.session.upsert(where=dict(id=settings.FACEBOOK_EMAIL),
                                                     data=dict(
                                                         update=data,
                                                         create=data
                                                     )
                                                     ).value

        self.hf_chatbot = HFChatBotWrapper(
            save_session=save_session,
            db=self.db,
            hf_clear_conv=hf_clear_conv)

        self.messages = List(redis=self.redis_client, key='fbchat')

        while True:
            if len(self.messages) == 0:
                time.sleep(1)
            else:
                msg = self.messages.pop(0)
                msg = pickle.loads(msg)

                self.onMessage(**msg)

    def onMessage(self, thread_id, **kwargs):
        thread = None
        if thread_id in self.threads:
            thread = self.threads[thread_id]
        else:
            other_user = self.fetchUserInfo(thread_id)[thread_id]

            thread = self.threads[thread_id] = \
                FacebookThreadInstance(
                    dry_run=self.dry_run,
                    hf_chatbot=self.hf_chatbot,
                    user_id=self.uid,
                    thread_id=thread_id,
                    other_user=other_user,
                    db=self.db,
                    client=self
                )

        thread.onMessage(thread_id=thread_id, **kwargs)



@click.command()
@click.option("--save-session", "-S", is_flag=True)
@click.option("--hf-clear-conv", "-C", is_flag=True)
@click.option("--dry-run", "-D", is_flag=True)
def main(**kwargs):
    client = FacebookChatResponder(email=settings.FACEBOOK_EMAIL,
                                  password=settings.FACEBOOK_PASS,
                                  **kwargs)

    client.listen()

if __name__ == "__main__":
    main()
