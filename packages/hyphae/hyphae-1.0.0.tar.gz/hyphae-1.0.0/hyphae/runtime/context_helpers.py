from truffle.hyphae.context_pb2 import Context
from truffle.infer.convo.conversation_pb2 import Conversation, Message
from typing import Any, Dict, List, Optional, Union

from hyphae.hooks import get_initial_context as user_get_initial_context

def get_user_block_from_initial_context(initial: Context) -> Optional[Context.ContextBlock]:
    """
    Extracts the initial user message from the provided context.
    If no initial user message is found, returns None.
    """
    for block in initial.blocks:
        if block.block_id == "default-user" or block.role == Message.ROLE_USER:
                return block
    return None
def get_initial_context( initial : Context) -> Context:
    if user_get_initial_context:
        return user_get_initial_context(initial)
    print("Using default get_initial_context implementation.")
    ctx = Context()
    system_blk  = Context.ContextBlock(block_id="system", role=Message.ROLE_SYSTEM)
    system_blk.entries.add(text=(
        "You are an expert in composing functions."
        "You are given a question, task, or goal, and a set of possible functions to use to "
        "accomplish it."
        "Based on the question, you will need to make a series of function/tool calls to achieve "
        "the purpose."
        "If the given question lacks what is needed to accomplish the task, you can ask for more "
        "information with RespondToUser.\n"
        "You may receive files, which will be passed to you as file paths, usually in "
        "/root/. Try to put any files you send back to the user in the same directory as "
        "well. Ensure paths are correct when referencing them to send back to the user.\n"
        "You are inside your own secure, ephemeral personal Alpine Linux container, where you have "
        "full root "
        "access and can do whatever you need. It is okay to break system packages, etc, the "
        "container is all yours, enjoy it, call it home."
        "It is fully isolated from the rest of the system and will be destroyed after the task is "
        "completed, no worries!"
        "Please only speak in function calls. Use response tools to contact the user sparingly, "
        "they want you to primarily work independently."
        "Please respond in the given JSON format:\n {\"tool\": {\"tool_name\": \"<tool_name>\", "
        "\"args\": {<tool specific args, given by the schemas below>} }\n"
    ), source=Context.ContextEntry.SOURCE_APP)
    system_blk.entries.add(placeholder=Context.ContextPlaceholder(type=Context.ContextPlaceholder.PLACEHOLDER_AVAILABLE_TOOLS))
    system_blk.entries.add(text=(
        "\n Ensure you follow the proper format for the above tools, \n"
        "you have your own Linux container, so you should be able to do anything you want, be creative.\n "
        "Below are any files the user has uploaded, and their path in the container:\n"
    ), source=Context.ContextEntry.SOURCE_APP)
    system_blk.entries.add(placeholder=Context.ContextPlaceholder(type=Context.ContextPlaceholder.PLACEHOLDER_FILE_LIST))
    system_blk.entries.add(text=(
        "Please remember to strive for excellence, you have your own computer, versitile "
        "tools, and the genius required to succeed. \n"
        "Any action history given was done by you previously, learn from mistakes and "
        "chain actions towards a goal.\n"
    ), source=Context.ContextEntry.SOURCE_APP)
    ctx.blocks.append(system_blk)

    usr_blk = get_user_block_from_initial_context(initial)
    if not usr_blk:
        usr_blk = Context.ContextBlock(block_id="default-user", role=Message.ROLE_USER)
        usr_blk.entries.add(text="No initial user prompt provided.", source=Context.ContextEntry.SOURCE_APP)
        print("No initial user prompt provided, using default.")
    else:
        print("Using initial user prompt from context.")
        ctx.blocks.append(usr_blk)
    return ctx
