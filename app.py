#testing for server reply with llm

import chainlit as cl
from llm import stream_answer

SYSTEM_PROMPT = ( #anti halusanation this needs to be written well 
    "You are a helpful assistant. Answer clearly and concisely. "
    "Explain things in plain language a non-expert can follow."
)
# start me kiya hoga yha jayega
@cl.on_chat_start
async def on_chat_start():
    """Runs once per browser session."""
    cl.user_session.set(
        "history",
        [{"role": "system", "content": SYSTEM_PROMPT}],
    )
    await cl.Message(
        content="Phase 0 online. No documents loaded yet — ask me anything to test the connection."
    ).send()


# on user message
@cl.on_message
async def on_message(message: cl.Message):
    """Runs every time the user sends a message."""
    history = cl.user_session.get("history")  #for that history thing
    history.append({"role": "user", "content": message.content})

    reply = cl.Message(content="")
    await reply.send()

    collected = ""
    try:
        async for piece in stream_answer(history):
            collected += piece
            await reply.stream_token(piece)
    except Exception as e:
        await reply.stream_token(f"\n\n**Error:** {type(e).__name__}: {e}")
        history.pop()  # don't keep a turn that failed
        await reply.update()
        return

    await reply.update()
    history.append({"role": "assistant", "content": collected})
    cl.user_session.set("history", history)