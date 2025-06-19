import chainlit as cl
from agents import Agent, RunConfig, AsyncOpenAI, OpenAIChatCompletionsModel, Runner
from dotenv import load_dotenv, find_dotenv
from openai.types.responses import ResponseTextDeltaEvent
import os
import asyncio

# Load environment variables
load_dotenv(find_dotenv())
gemini_api_key = os.getenv("GOOGLE_API_KEY")

# Initialize Google Gemini API client (disguised under AsyncOpenAI wrapper)
client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# Define the runtime configuration
run_config = RunConfig(
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
    model_provider=client,
    tracing_disabled=True
)

# Define the agent (notice: no need to re-specify the model here)
agent1 = Agent(
    name="Assistant",
    instructions="You are a helpful assistant and you can answer questions about various topics.",
    model=OpenAIChatCompletionsModel(model="gemini-2.0-flash", openai_client=client),
)

# # ✅ Run the agent using the run_config
# result = Runner.run_sync(agent1, "Capital of Pakistan?", run_config=run_config)

# # Print the result
# print(result.final_output)
@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("history",[])
    await cl.Message(content="Welcome to the Gemini-powered chatbot! How can I assist you today?").send()

@cl.on_message
async def handle_message(message:cl.Message):
    history=cl.user_session.get("history")
    msg=cl.Message(content="")
    await msg.send()
    history.append({"role":"user","content":message.content})
    result = Runner.run_streamed(agent1, input=history, run_config=run_config)
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data,ResponseTextDeltaEvent):
            await msg.stream_token(event.data.delta)
    history.append({"role":"assistant","content":result.final_output})
    cl.user_session.set("history",history)
    await cl.Message(content=result.final_output).send()
