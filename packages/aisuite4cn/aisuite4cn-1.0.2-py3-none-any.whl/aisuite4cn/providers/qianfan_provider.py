import os
import time
from typing import Optional

import openai
from pydantic import BaseModel
from qianfan.resources.console.iam import IAM

from aisuite4cn.provider import Provider


class BearerToken(BaseModel):
    user_id: Optional[str] = None
    token: Optional[str] = None
    status: Optional[str] = None
    create_time: float = 0
    expire_time: float = 0


class QianfanProvider(Provider):
    """
    Baidu Qianfan Provider

    ref: https://cloud.baidu.com/doc/WENXINWORKSHOP/s/em4tsqo3v
    """

    access_key: Optional[str] = None
    secret_key: Optional[str] = None
    bearerToken: Optional[BearerToken] = None

    def __init__(self, **config):
        """
        Initialize the Qianfan provider with the given configuration.
        Pass the entire configuration dictionary to the Qianfan client constructor.
        """
        # Ensure access key and secret key is provided either in config or via environment variable

        self.config = dict(config)

        self.config.setdefault("api_key", os.getenv("QIANFAN_API_KEY"))
        if self.config['api_key']:
            self.config.pop("access_key")
            self.config.pop("secret_key")
            self.client = openai.OpenAI(
                base_url="https://qianfan.baidubce.com/v2",
                **self.config)
        else:
            self.access_key = self.config.pop("access_key", os.getenv("QIANFAN_ACCESS_KEY"))
            self.secret_key = self.config.pop("secret_key", os.getenv("QIANFAN_SECRET_KEY"))
            if not self.access_key:
                raise ValueError(
                    "Qainfan access key is missing. Please provide it in the config or set the QIANFAN_ACCESS_KEY environment variable."
                )
            if not self.secret_key:
                raise ValueError(
                    "Qianfan secret key is missing. Please provide it in the config or set the QIANFAN_SECRET_KEY environment variable."
                )
            # Pass the entire config to the Qianfan client constructor
            self.client = openai.OpenAI(
                api_key=self.get_bearer_token(),
                base_url="https://qianfan.baidubce.com/v2",
                **self.config)

            # Pass the entire config to the Qianfan client constructor
            self.async_client = openai.AsyncOpenAI(
                api_key=self.get_bearer_token(),
                base_url="https://qianfan.baidubce.com/v2",
                **self.config)

    def get_bearer_token(self):
        if self.bearerToken is None:
            self.bearerToken = BearerToken()
        if time.time() < self.bearerToken.expire_time:
            return self.bearerToken.token

        os.environ["QIANFAN_ACCESS_KEY"] = self.access_key
        os.environ["QIANFAN_SECRET_KEY"] = self.secret_key
        expire_in_seconds = 86400
        response = IAM.create_bearer_token(expire_in_seconds=expire_in_seconds)
        self.bearerToken.user_id = response.body.get('user_id')
        self.bearerToken.token = response.body.get('token')
        self.bearerToken.status = response.body.get('enable')
        self.bearerToken.create_time = time.time()
        self.bearerToken.expire_time = self.bearerToken.create_time + expire_in_seconds - 120
        return self.bearerToken.token

    def chat_completions_create(self, model, messages, **kwargs):
        if not self.config['api_key']:
            self.client.api_key = self.get_bearer_token()
        # Any exception raised by Qianfan will be returned to the caller.
        # Maybe we should catch them and raise a custom LLMError.
        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs  # Pass any additional arguments to the Moonshot API
        )

    async def async_chat_completions_create(self, model, messages, **kwargs):
        if not self.config['api_key']:
            self.client.api_key = self.get_bearer_token()
        return await self.async_client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs  # Pass any additional arguments to the Moonshot API
        )
