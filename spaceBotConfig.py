import discord
discordPrefix = "?"
fileLog = "spaceBotLog.txt"
scriptVersion = "v0.6.1"
scriptDate = "2022-02-10"
cams = ["f", "n", "r", "m"]
ownerID = 195617048569708545
githubLink = "https://github.com/quackersian/space-bot"
discordServer = "https://discord.gg/9KeQnS94gS"
topgg = "https://top.gg/bot/849246857309323284"
neededIntents = discord.Intents(guilds=True, messages=True)
planetWeather = {
    "mercury": "Mercury averages 800°F (430°C) during the day, -290°F (-180°C) at night. Quite windy, so make sure to grab a jacket before heading out.",
    "venus": "Venus averages 880°F (471°C). Acid rain likely, so bring an umbrella.",
    "earth": "Earth averages 61°F (16°C). There will be weather.",
    "mars": "Mars averages -20°F (-28°C). A little chilly out, so don't forget a jumper.",
    "jupiter": "Jupiter averages -162°F (-108°C). There's no solid ground, you'll need a yacht.",
    "saturn": "Saturn averages -218°F (-138°C). Big storms at the north pole, and watch out for the strong winds.",
    "uranus": "Uranus averages -320°F (-195°C). A little nippy, so wrap up well.",
    "neptune": "Neptune averages -331°F (-201°C). Winds are picking up, so be careful out there!",
    "pluto": "Pluto averages -388°F (-233°C). I'm still annoyed that it's not a planet."
}