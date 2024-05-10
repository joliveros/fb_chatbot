from dataclasses import dataclass
from datetime import datetime
from fbchat import User
from prisma import Prisma
from fbchat import Message

import alog
import json

from fb_chatbot.hf_chatbot_wrapper import HFChatBotWrapper


@dataclass(unsafe_hash=True)
class FacebookThreadInstance:
    hf_chatbot: HFChatBotWrapper
    thread_id: str
    other_user: User
    db: Prisma
    client: any
    user_id: str
    user: User = None
    messages = []

    def __post_init__(self):
        ouser = self.other_user
        data = dict(
            photo=ouser.photo,
            gender=ouser.gender,
            first_name=ouser.first_name,
            last_name=ouser.last_name,
            name=ouser.name,
            url=ouser.url
        )

        ouser = self.db.facebookuser.upsert(
            where=dict(id=self.thread_id),
            data=dict(
                create=dict(id=self.thread_id, **data),
                update=data
            )
        )

        self.user = self.db.facebookuser.find_unique(where=dict(id=self.user_id))

        data = dict(
            id=self.thread_id,
            user=dict(connect=dict(id=self.user_id)),
            otherUser=dict(connect=dict(id=self.thread_id))
        )

        thread = self.db.facebookthread.upsert(
            where=dict(id=self.thread_id),
            data=dict(
                create=data,
                update=data
            ))

        self.thread_data = thread

        self.messages = self.db.facebookmessage.\
                find_many(where=dict(threadId=self.thread_id))

    def onMessage(self, mid, thread_id, author_id, message, ts, message_object, metadata, **kwargs):
        self.client.markAsDelivered(thread_id, message_object.uid)
        self.client.markAsRead(thread_id)

        data = dict(
            id=mid,
            folder=json.dumps(metadata['folderId']),
            message=message,
            timestamp=datetime.fromtimestamp(int(ts)/1000),
            author=dict(connect=dict(id=author_id)),
            thread=dict(connect=dict(id=self.thread_id))
        )

        message = self.db.facebookmessage.create(data=data)

        self.messages.append(message)

        if author_id == thread_id:
            prompt = f'''
            Por favor responde a esta conversacion en la quien tu eres "self":
            {self.conversation}
            '''

            alog.info(prompt)

            res = self.hf_chatbot.chat(prompt)

            alog.info(Message(text=str(res)))

            self.client.send(Message(text=str(res)), thread_id=self.thread_id)

    @property
    def conversation(self):
        conversation = [['self' if msg.authorId == self.user_id else self.other_user.first_name, msg.message] for msg in self.messages[-1:]]

        conversation = [': '.join(msg) for msg in conversation]

        return '\n'.join(conversation)
