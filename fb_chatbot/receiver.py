#!/usr/bin/env python

from fb_chatbot import settings
from fbchat import Client
from prisma import Prisma
from redis import Redis
from redis_collections import List
import alog
import click
import json
import pickle

class FacebookChatReceiver(Client):
    threads = dict()

    def __init__(
        self,
        save_session=False,
        **kwargs
    ):
        self.redis_client = Redis(host=settings.REDIS_HOST)
        self.db = Prisma()
        self.db.connect()
        session_cookies=None

        if not save_session:
            session_cookies = (self.db.session
                               .find_unique(where=dict(id=settings.FACEBOOK_EMAIL)))

            if session_cookies:
                session_cookies = session_cookies.value


        super().__init__(session_cookies=session_cookies,
                         **kwargs)

        if save_session or not session_cookies:
            data = dict(id=settings.FACEBOOK_EMAIL,
                        value=json.dumps(self.getSession()))
            session_cookies=self.db.session.upsert(
                where=dict(id=settings.FACEBOOK_EMAIL),
                   data=dict(
                       update=data,
                       create=data
                   )
               ).value

        self.update_user_info()

        self.messages = List(redis=self.redis_client, key='fbchat')

    def onMessage(self, **kwargs):
        msg = pickle.dumps(kwargs, protocol=pickle.HIGHEST_PROTOCOL)
        self.messages.append(msg)

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



@click.command()
@click.option("--save-session", "-S", is_flag=True)
def main(**kwargs):
    client = FacebookChatReceiver(email=settings.FACEBOOK_EMAIL,
                                  password=settings.FACEBOOK_PASS,
                                  **kwargs)

    client.listen()

if __name__ == "__main__":
    main()
