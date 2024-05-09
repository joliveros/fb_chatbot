#!/usr/bin/env python

import alog
import dataclasses
import argparse
import click
from hugchat import hugchat
from hugchat.login import Login

from fb_chatbot import settings


@click.command()
@click.option("--headless", "-H", is_flag=True)
@click.option("--dry-run", "-d", is_flag=True)
def main(**kwargs):
    # Log in to huggingface and grant authorization to huggingchat
    EMAIL = settings.HF_EMAIL
    PASS = settings.HF_PASS
    cookie_path_dir = "./cookies/"  # NOTE: trailing slash (/) is required to avoid errors
    sign = Login(EMAIL, PASS)
    cookies = sign.login(cookie_dir_path=cookie_path_dir, save_cookies=True)

    # Create your ChatBot
    chatbot = hugchat.ChatBot(cookies=cookies.get_dict())  # or cookie_path="usercookies/<email>.json"

    # Non stream response
    query_result = chatbot.chat("Hi! can you speak spanish?")

    print(query_result)  # or query_result.text or query_result["text"]

if __name__ == "__main__":
    main()
