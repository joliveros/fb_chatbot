from dataclasses import dataclass
import alog
from fbchat import User
from prisma import Prisma



@dataclass(unsafe_hash=True)
class FacebookThreadInstance:
    thread_id: str
    other_user: User
    db: Prisma
    client: any

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

        user = self.db.facebookuser.upsert(
            where=dict(id=self.thread_id),
            data=dict(
                create=dict(id=self.thread_id, **data),
                update=data
            )
        )

    def onMessage(self, thread_id, author_id, message_object, **kwargs):
        alog.info(alog.pformat(message_object))

        alog.info([thread_id, author_id])

        alog.info(alog.pformat(kwargs))

        self.client.markAsDelivered(thread_id, message_object.uid)
        self.client.markAsRead(thread_id)
