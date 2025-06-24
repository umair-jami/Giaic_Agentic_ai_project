import os
import asyncio
import requests
from dotenv import load_dotenv
from agents import Agent,Runner,function_tool,AsyncOpenAI,OpenAIChatCompletionsModel
from agents.run import RunConfig

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPEN_WEATHER_API = os.getenv("OPEN_WEATHER_API")

if not GEMINI_API_KEY or not OPEN_WEATHER_API:
    raise ValueError("Please set GEMINI_API_KEY and OPEN_WEATHER_API in your environment variables.")

client= AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
model=OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=client
)

config=RunConfig(
    model=model,
    model_provider=client,
    tracing_disabled=True
)
@function_tool
def get_weather(city: str) -> str:
    """
    Retrieves the current weather information for a specified city.

    Args:
        city (str): The name of the city to fetch the weather for.

    Returns:
        str: A formatted string describing the current weather conditions, such as temperature, humidity, and weather description.
    """
    url=f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPEN_WEATHER_API}&units=metric"
    response=requests.get(url)
    if response.status_code !=200:
        return f"Error: Unable to fetch weather data for {city}. Please check the city name or try again later."
    data=response.json()
    temp=data["main"]["temp"]
    desc=data["weather"][0]["description"]
    humidity=data["main"]["humidity"]
    return f"The current temperature in {city} is {temp}°C with {desc}. The humidity level is {humidity}%."

async def run_weather_bot(city: str) -> str:
    """Runs the weather bot to fetch current weather information for a specified city."""
    agent=Agent(
        name="WeatherBot",
        instructions="You are a helpful assistant that provides current weather information for any city.",
        model=model,
        tools=[get_weather]
    )
    result=await Runner.run(agent,f"What's the weather in {city}?",run_config=config)
    return result.final_output