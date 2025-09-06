#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : chat
# @Time         : 2025/9/3 14:41
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :  todo


from openai import AsyncOpenAI

from meutils.pipe import *
from meutils.decorators.retry import retrying
from meutils.io.files_utils import to_bytes, guess_mime_type
from meutils.caches import rcache

from meutils.llm.openai_utils import to_openai_params

from meutils.config_utils.lark_utils import get_next_token_for_polling
from meutils.schemas.openai_types import chat_completion, chat_completion_chunk, CompletionRequest, CompletionUsage, \
    ChatCompletion

base_url = "https://longcat.chat/api/v1/chat-completion"
base_url = "https://longcat.chat/api/v1/chat-completion-oversea"
base_url = "https://longcat.chat/api/v1"


class Completions(object):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    async def create(self, request: CompletionRequest, **kwargs):
        payload = self.requset2payload(request)
        payload['conversationId'] = await self.create_chat()

        logger.debug(payload)

        headers = {
            'Cookie': self.api_key
        }

        async with httpx.AsyncClient(base_url=base_url, headers=headers, timeout=100) as client:
            async with client.stream("POST", "/chat-completion", json=payload) as response:
                logger.debug(response.status_code)
                response.raise_for_status()

                async for chunk in response.aiter_lines():
                    logger.debug(chunk)

    def requset2payload(self, request: CompletionRequest):
        payload = {
            "content": request.last_user_content,  # todo: 多轮
            "messages": [
                # {
                #     "role": "user",
                #     "content": "hi",
                #     "chatStatus": "FINISHED",
                #     "messageId": 11263291,
                #     "idType": "custom"
                # },
                # {
                #     "role": "assistant",
                #     "content": "",
                #     "chatStatus": "LOADING",
                #     "messageId": 92193819,
                #     "idType": "custom"
                # }
            ],
            "reasonEnabled": 0,
            "searchEnabled": 0,
            "regenerate": 0
        }

        return payload

    async def create_chat(self):
        headers = {
            'Cookie': self.api_key
        }
        payload = {
            "model": "",
            "agentId": ""
        }
        async with httpx.AsyncClient(base_url=base_url, headers=headers, timeout=100) as client:
            response = await client.post("/session-create", json=payload)
            response.raise_for_status()
            # {'code': 0,
            #  'data': {'agent': '1',
            #           'conversationId': 'c1731258-230a-4b2e-b7ef-ea5e83c38e0e',
            #           'createAt': 1756883097539,
            #           'currentMessageId': 0,
            #           'label': '今天',
            #           'model': 'LongCat',
            #           'title': '新对话',
            #           'titleType': 'SYSTEM',
            #           'updateAt': 1756883097539},
            #  'message': 'success'}
            return response.json()['data']['conversationId']


if __name__ == '__main__':
    cookie = "_lxsdk_cuid=1990e1e8790c8-0b2a66e23040a48-16525636-1fa400-1990e1e8790c8; passport_token_key=AgEGIygg22VuoMYTPonur9FA_-EVg9UXLu3LYOzJ4kIHSjQZeSNhwpytTU_cZFP6V1Juhk0CHMrAgwAAAABYLAAA9vXtnciaZBu2V99EMRJYRHTDSraV_OPLemUuVpi2WLsaa6RqC0PAKAOm6W_hIpbV"
    request = CompletionRequest(
        messages=[{'role': 'user', 'content': '你好'}]
    )
    arun(Completions(api_key=cookie).create(request))
    # arun(Completions(api_key=cookie).create_chat())
