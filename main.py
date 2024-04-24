# VARIABLES:
import google.generativeai as genai
import os
import requests
import PIL.Image
import discord
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from io import BytesIO

TOKEN = os.environ['TOKEN']
gemini_key = os.environ['gemini_key']

genai.configure(api_key=gemini_key)
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

# Functions
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
  print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
  if message.author == client.user:
    return
  try:
    if len(message.attachments) >= 1:
      model = genai.GenerativeModel("gemini-pro-vision")
      response = requests.get(message.attachments[0].url)
      img = PIL.Image.open(BytesIO(response.content))
      response = model.generate_content([message.content or "", img])
      await message.reply(response.text)
      return

    model = genai.GenerativeModel("gemini-pro")
    content = message.content
    '''
    
    if message.reference is not None:
      print(message.reference)
      if message.reference.resolved.author == client.user:
        content = message.reference.resolved.content
        return
      if message.reference.cached_message is None:
        channel = client.get_channel(message.reference.channel_id)
        content += await channel.fetch_message(message.reference.message_id
                                               ).content

      else:
        content += message.reference.cached_message.content'''
    response = chat.send_message(content,
                                 safety_settings={
                                     HarmCategory.HARM_CATEGORY_HATE_SPEECH:
                                     HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                                     HarmCategory.HARM_CATEGORY_HARASSMENT:
                                     HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                                 })

    max_length = 1700
    text = response.text
    chunks = [text[i:i + max_length] for i in range(0, len(text), max_length)]

    for chunk in chunks:
      await message.reply(chunk)

  except Exception as error:
    print(error)
    await message.reply(f'An error occured, {error}')


client.run(TOKEN)
