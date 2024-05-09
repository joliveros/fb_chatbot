#!/usr/bin/env python
import os

from prisma import Prisma

from fb_chatbot.facebook_thread import FacebookThreadInstance

NAME = "fb_chatbot"

import alog
import click
import json
from fb_chatbot import settings
from fbchat import Client


class FacebookChatBot(Client):
    threads = dict()

    def __init__(self, save_session=False, **kwargs):
        self.session_file = './session.json'

        session_cookies = None

        if os.path.exists(self.session_file):
            with open(self.session_file) as f:
                session_cookies = json.load(f)

        super().__init__(session_cookies=session_cookies,
                         **kwargs)

        if save_session:
            with open('session.json', 'w') as session_file:
                json.dump(self.getSession(), session_file)

        self.db = Prisma()
        self.db.connect()

    def onMessage(self, thread_id, **kwargs):
        thread = None
        if thread_id in self.threads:
            thread = self.threads[thread_id]
        else:
            other_user = self.fetchUserInfo(thread_id)[thread_id]

            thread = self.threads[thread_id] = \
                FacebookThreadInstance(thread_id=thread_id,
                                       other_user=other_user,
                                       db=self.db,
                                       client=self)

        thread.onMessage(thread_id=thread_id, **kwargs)



@click.command()
# @click.option("--headless", "-H", is_flag=True)
# @click.option("--dry-run", "-d", is_flag=True)
@click.option("--save-session", "-S", is_flag=True)
def main(**kwargs):
    client = FacebookChatBot(email=settings.FACEBOOK_EMAIL,
                             password=settings.FACEBOOK_PASS,
                             **kwargs)

    client.listen()

if __name__ == "__main__":
    main()
