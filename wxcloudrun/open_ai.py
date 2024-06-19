import base64
import uuid
import io
from typing_extensions import override
import logging

from openai import OpenAI
from openai import AssistantEventHandler
# from openai.types.beta.threads.image_url_content_block_param import ImageURLContentBlockParam
from openai.types.beta.threads.image_file_content_block_param import ImageFileContentBlockParam
from openai.types.beta.threads.text_content_block import TextContentBlock
from openai.types.beta.threads.image_file_content_block import ImageFileContentBlock
# from openai.types.beta.threads.image_url_param import ImageURLParam
from openai.types.beta.threads.image_file_param import ImageFileParam

logger = logging.getLogger('open_ai')

class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        pass

    @override
    def on_text_delta(self, delta, snapshot):
        pass

    def on_tool_call_created(self, tool_call):
        pass

    def on_tool_call_delta(self, delta, snapshot):
        pass

    @override
    def on_message_done(self, message) -> None:
        pass


class OpenAIClient():
    greeting = """
    Hi, this is IC, Let's start. Please tell me your current teeth status.
    """

    def __init__(self) -> None:
        self.__client = OpenAI()
        self.__assistant = self.__client.beta.assistants.retrieve(
            # assistant_id="asst_Tsf0p4fN1eJWJdFd70ewK6TZ" # hardcoded for demo
            assistant_id="asst_v44LfzODIBaA6yMjOq3L7T7q"
        )

    def get_thread(self, thread_id):
        if thread_id:
            thread = self.__client.beta.threads.retrieve(thread_id=thread_id)
        else:
            thread = self.__client.beta.threads.create()
            self.__client.beta.threads.messages.create(
                thread_id=thread.id,
                role="assistant",
                content=self.greeting,
            )
        return thread

    def get_last_msg(self, thread):
        messages = self.__client.beta.threads.messages.list(thread_id=thread.id, order='asc')
        logger.info(messages)
        return messages.data[-1].content[0].text.value

    def append_text_msg(self, thread, msg):
        self.__client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=msg,
        )

    @staticmethod
    def encode_image(image_content):
        return base64.b64encode(image_content).decode('utf-8')

    def append_image_msg(self, thread, image_content, image_type):
        message_file = self.__client.files.create(
            file=(str(uuid.uuid4()) + '.' + image_type, io.BytesIO(image_content)), purpose="vision"
        )
        # url = f"data:image/png;base64,{OpenAIClient.encode_image(image_content)}"
        self.__client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=[
                ImageFileContentBlockParam(
                    image_file=ImageFileParam(
                        file_id=message_file.id
                    ),
                    type='image_file'
                )
            ]
        )

    def truncate_thread(self, thread):
        messages = self.__client.beta.threads.messages.list(thread_id=thread.id, order='asc')
        for i in range(4, len(messages.data)): #  hardcode for demo
            self.__client.beta.threads.messages.delete(messages.data[i].id)

    def dup_thread(self, thread):
        messages = self.__client.beta.threads.messages.list(thread_id=thread.id, order='asc')
        thread = self.__client.beta.threads.create()
        for message in messages.data:
            content_obj = message.content[0]
            if isinstance(content_obj, TextContentBlock):
                content = content_obj.text.value
            elif isinstance(content_obj, ImageFileContentBlock):
                content = [ImageFileContentBlockParam(
                    image_file=content_obj.image_file,
                    type='image_file',
                )]
            else:
                content = ''
            self.__client.beta.threads.messages.create(
                thread_id=thread.id,
                role=message.role,
                content=content,
            )
        return thread

    def run_thread(self, thread):
        logger.info("start running thread...")
        with self.__client.beta.threads.runs.stream(
            thread_id=thread.id,
            assistant_id=self.__assistant.id,
            instructions="Please address the user as Dr. Tong. The user has a premium account.",
            event_handler=EventHandler(),
        ) as stream:
            stream.until_done()


        logger.info("running done. getting results...")
        return self.get_last_msg(thread)