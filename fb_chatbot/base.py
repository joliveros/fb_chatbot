#!/usr/bin/env python
import os

from prisma import Prisma

from fb_chatbot.facebook_thread import FacebookThreadInstance
from fb_chatbot.hf_chatbot_wrapper import HFChatBotWrapper

NAME = "fb_chatbot"

import alog
import click
import json
from fb_chatbot import settings
from fbchat import Client


class FacebookChatBot(Client):
    threads = dict()

    def __init__(self, save_session=False, **kwargs):
        self.db = Prisma()
        self.db.connect()

        session_cookies = (self.db.session
                           .find_unique(where=dict(id=settings.FACEBOOK_EMAIL)))

        if session_cookies:
            session_cookies = session_cookies.value


        super().__init__(session_cookies=session_cookies,
                         **kwargs)

        if save_session or not session_cookies:
            data = dict(id=settings.FACEBOOK_EMAIL,
                        value=json.dumps(self.getSession()))
            session_cookies=self.db.session.upsert(where=dict(id=settings.FACEBOOK_EMAIL),
                                                   data=dict(
                                                       update=data,
                                                       create=data
                                                   )
                                                   ).value

        self.update_user_info()

        self.hf_chatbot = HFChatBotWrapper(save_session=save_session, db=self.db)

        # check all threads
        # self.respond_to_open_threads()

    def respond_to_open_threads(self):
        threads = self.db.facebookthread.find_many(include=dict(
            FacebookMessage=dict(
                orderBy=dict(timestamp='asc'),
                take=1
            )
        ))
        for thread in threads:
            if len(thread.FacebookMessage) > 0:
                authorId = thread.FacebookMessage[-1].authorId
                thread_id = thread.id

                if self.uid is not authorId:
                    # alog.info(f'## should respond {thread.id}##')
                    other_user = self.fetchUserInfo(thread_id)[thread_id]
                    thread = self.threads[thread_id] = \
                        FacebookThreadInstance(
                            hf_chatbot=self.hf_chatbot,
                            user_id=self.uid,
                            thread_id=thread.id,
                            other_user=other_user,
                            db=self.db,
                            client=self
                        )

                    thread.respond_to_conversation()

    def update_user_info(self):
        user = self.fetchUserInfo(self.uid)[self.uid]
        data = dict(
            photo=user.photo,
            gender=user.gender,
            first_name=user.first_name,
            last_name=user.last_name,
            name=user.name,
            url=user.url
        )

        user = self.db.facebookuser.upsert(
            where=dict(id=self.uid),
            data=dict(
                create=dict(id=self.uid, **data),
                update=data
            )
        )

    def onMessage(self, thread_id, **kwargs):
        thread = None
        if thread_id in self.threads:
            thread = self.threads[thread_id]
        else:
            other_user = self.fetchUserInfo(thread_id)[thread_id]

            thread = self.threads[thread_id] = \
                FacebookThreadInstance(
                    hf_chatbot=self.hf_chatbot,
                    user_id=self.uid,
                    thread_id=thread_id,
                    other_user=other_user,
                    db=self.db,
                    client=self
                )

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
