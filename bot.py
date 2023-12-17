import discord
from discord import app_commands
import requests
import datetime as d
import re
import credentials

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
separater = ",\n"
hypixelKey = credentials.hypixelKey
discordToken = credentials.discordToken

@client.event
async def on_ready():
    await tree.sync()
    print("Ready!")

@tree.command(name="cookies", description="Get cookies that a player has given this week!")
async def say_command(interaction: discord.Interaction, player: str):
    houses = []
    profile = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{player}").json()
    uuid = profile.get("id")
    if uuid == None:
        await interaction.response.send_message(f"{player} is an invalid username!")
        return
    player = profile.get("name")
    week = d.datetime.now().isocalendar()[0] * 52 + d.datetime.now().isocalendar()[1]
    hypixelData = requests.get(f"https://api.hypixel.net/player?key={hypixelKey}&uuid={uuid}").json()["player"]
    if hypixelData == None:
        await interaction.response.send_message(f"{player} hasn't played Hypixel before!")
        return
    housingData = hypixelData.get("housingMeta")
    if housingData == None:
        await interaction.response.send_message(f"{player} hasn't played Housing before!")
        return
    cookies = housingData.get(f"given_cookies_{week}")
    if cookies == None:
        await interaction.response.send_message(f"{player} hasn't given any cookies this week!")
        return  
    for i in cookies:
        house = requests.get(f"https://housing.menu/house-info?id={i}").json()["houseInfo"]
        if not house:
            continue
        houseName = house[0]["name_raw"]
        houseOwner = house[0]["creator"]
        houseOwnerUnformatted = re.sub(r'§[a-zA-Z0-9]', '', houseOwner)
        houses.append(f"{houseName}, by {houseOwnerUnformatted}")
    if not houses:
        await interaction.response.send_message("All searched houses were not found! (Might be private/not on housing.menu yet)")
        return
    await interaction.response.send_message(f"{player} has given cookies to:\n{separater.join(houses)}\nthis week!")

client.run(discordToken)