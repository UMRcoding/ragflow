import logging
import discord
import requests
import base64
import asyncio

URL = '{YOUR_IP_ADDRESS:PORT}/v1/api/completion_aibotk' # Default: https://demo.ragflow.io/v1/api/completion_aibotk

JSON_DATA = {
    "conversation_id": "xxxxxxxxxxxxxxxxxxxxxxxxxxx", # Get conversation id from /api/new_conversation
    "Authorization": "ragflow-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx", # RAGFlow Assistant Chat Bot API Key
    "word": "" # User question, don't need to initialize
}

DISCORD_BOT_KEY = "xxxxxxxxxxxxxxxxxxxxxxxxxx" #Get DISCORD_BOT_KEY from Discord Application


intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)


@client.event
async def on_ready():
    logging.info(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if client.user.mentioned_in(message):

        if len(message.content.split('> ')) == 1:
            await message.channel.send("Hi~ How can I help you? ")
        else:
            JSON_DATA['word']=message.content.split('> ')[1]
            response = requests.post(URL, json=JSON_DATA)
            response_data = response.json().get('data', [])
            image_bool = False

            for i in response_data:
                if i['type'] == 1:
                    res = i['content']
                if i['type'] == 3:
                    image_bool = True
                    image_data = base64.b64decode(i['url'])
                    with open('tmp_image.png','wb') as file:
                        file.write(image_data)
                    image= discord.File('tmp_image.png')

            await message.channel.send(f"{message.author.mention}{res}")

            if image_bool:
                await message.channel.send(file=image)


loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(client.start(DISCORD_BOT_KEY))
except KeyboardInterrupt:
    loop.run_until_complete(client.close())
finally:
    loop.close()
