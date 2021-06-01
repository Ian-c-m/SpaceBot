import discord, requests, urllib, json
from discord.ext import commands
from spaceBotConfig import discordPrefix, fileLog
from spaceBotTokens import discordToken, NASAApiKey
from datetime import date, datetime
import os.path
import random

bot = commands.Bot(command_prefix=commands.when_mentioned_or(discordPrefix))

debug = True


@bot.event
async def on_ready():
    log("--------------")
    log("Logged in as: {}".format(bot.user.name))
    log("ID: {}".format(bot.user.id))
    log("Discord Version: {}".format(discord.__version__))
    log("Prefix: {}".format(discordPrefix))

    log("Connected to following servers:")
    for guild in bot.guilds:
        log("- " + guild.name)
        
    if debug:
        print("Logged in as: {}".format(bot.user.name))
        print("ID: {}".format(bot.user.id))
        print("Discord Version: {}".format(discord.__version__))
        print("Prefix: {}".format(discordPrefix))
        print("Connected to following servers:")
        for guild in bot.guilds:
            print("- " + guild.name)
        print("--------------")
    else:
        print("Ready")

@bot.command(name="iss", help="Shows current location of the International Space Station. /nThanks to Natronics at https://api.open-notify.org", brief="Finds the ISS")
async def commandISS(ctx):
    if not ctx.author.bot:
        log("{} used ISS command".format(ctx.author))
        await ctx.channel.send("The ISS is in space, obviously!")
        iss = getISS()
        lat = iss[0]
        lon = iss[1]
        response = "Current ISS position: " + lat + " latitude, " + lon + " longitude"
        await ctx.channel.send(response)



@bot.command(name="apod", help="Shows NASA's Astronomy Picture Of the Day. /nThanks to NASA at https://api.nasa.gov", brief="Space picture of the day")
async def commandAPOD(ctx):
    if not ctx.author.bot:
        try:
            log("{} used APOD command".format(ctx.author))
            result = getAPOD()


            #APOD got an error when running
            if result == "api fail":
                await ctx.channel.send("Unable to get Astronomy Picture Of the Day.")
                return

            
            else:
                with open("metadata.txt", "r") as jsonFile:
                    metadata = json.load(jsonFile)
                    for d in metadata:

                        if d['mediaType'] == "video":
                            #if the media is a video, just sends the URL instead of embedding the video
                            await ctx.channel.send("Today's Astronomy Picture Of the Day is a video.")
                            await ctx.channel.send(d['url'])
                            jsonFile.close()
                            return

                        
                        elif d['mediaType'] == "image":
                            #if the media is an image, embeds the image in a message 
                            picTitle = d['title']
                            extension = d['fileType']
                            apodFile = "apod." + extension

                            file = discord.File(apodFile, filename="image.png")
                            
                            embed = discord.Embed()
                            embed.add_field(name="Title", value=picTitle)
                            embed.set_image(url="attachment://image.png")
                            
                            await ctx.channel.send(file=file, embed=embed)
                            jsonFile.close()
                            return

                


        except Exception as e:
            log("Failed to run commandAPOD")
            log(str(e))
            if debug:
                print(str(e))                                
        


@bot.command(name="pw", help="Weather forecast for a given planet in our solar system", brief="Different Planet's Weather")
async def commandPW(ctx, planet):
    if not ctx.author.bot:
        try:
            
            log("{} used PW command".format(ctx.author))
            planet = str(planet).lower()

            #picks a random planet from the list
            if planet == "random":
                listPlanets = ["mercury", "venus", "earth", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]
                planet = random.choice(listPlanets)

            #weather and comments for each planet
            if planet == "mercury":
                message = "Mercury is 800°F (430°C) during the day, -290°F (-180°C) at night. Quite windy, so make sure to grab a jacket before heading out."
            elif planet ==  "venus":
                message = "Venus is 880°F (471°C). Acid rain likely, so bring an umbrella."
            elif planet ==  "earth":
                message = "Earth is 61°F (16°C). Summer is here, so grab that sunscreen!"
            elif planet ==  "mars":
                message = "Mars is -20°F (-28°C). A little chilly out, so don't forget a jumper."
            elif planet ==  "jupiter":
                message = "Jupiter is -162°F (-108°C). There's no solid ground, you'll need a yacht."
            elif planet ==  "saturn":
                message = "Saturn is -218°F (-138°C). Big storms at the north pole, and watch out for the strong winds."
            elif planet ==  "uranus":
                message = "Uranus is -320°F (-195°C). A little nippy, so wrap up well."
            elif planet ==  "neptune":
                message = "Neptune is -331°F (-201°C). Winds are picking up, so be careful out there!"
            elif planet ==  "pluto":
                message = "Pluto is -388°F (-233°C). I'm still in denial that it's not a planet."
            else:
                log("Unknown planet")
                message = "Unknown planet! Try again..."

            await ctx.channel.send(message)
                    

            
        except Exception as e:
            log("Failed to run commandPW")
            log(str(e))
            if debug:
                print(str(e))



@bot.command(name="facts", help="Shows interesting facts about space", brief="Space Facts!")
async def commandSF(ctx):
    if not ctx.author.bot:
        try:

            log("{} used SF command".format(ctx.author))

            #a list of facts
            facts = [
                "Space is completely silent",
                "The hottest planet in our solar system is 450° C.",
                "A full NASA space suit costs $12,000,000.",
                "The Sun’s mass takes up 99.86% of the solar system."
                "One million Earths can fit inside the Sun",
                "There are more trees on Earth than stars in the Milky Way",
                "The sunset on Mars appears blue",
                "There are more stars in the universe than grains of sands on Earth",
                "One day on Venus is longer than one year.",
                "There is a planet made of diamonds"
                ]

            #picks a random fact from the list.
            message = random.choice(facts)
            await ctx.channel.send(message)

            
        except Exception as e:
            log("Failed to run commandSF")
            log(str(e))
            if debug:
                print(str(e))


@bot.command(name="people", help="Shows the number of people in space. /nThanks to Natronics at https://api.open-notify.org", brief="People in Space!")
async def commandPIS(ctx):
    try:
        log("{} used PIS command".format(ctx.author))

        
        numPeople = getPeopleInSpace()
        await ctx.channel.send("There are {} people in space right now!".format(numPeople))


        
    except Exception as e:
            log("Failed to run commandPIS")
            log(str(e))
            if debug:
                print(str(e))

      

def getAPOD():
    try:

        with open("metadata.txt", "r") as jsonFile:
            metadata = json.load(jsonFile)
            for m in metadata:
                lastRun = m['lastRun']
                jsonFile.close()
                
        dateToday = datetime.today().strftime('%Y-%m-%d')
        
        #need to fetch new apod if it hasn't been done today        
        if lastRun != dateToday:
        
            log("Fetching new image for today")
            lastRun = datetime.today().strftime('%Y-%m-%d')
            
            ApodUrl = "https://api.nasa.gov/planetary/apod?api_key={}".format(NASAApiKey)

            with urllib.request.urlopen(ApodUrl) as surl:
                data = json.loads(surl.read().decode())

                #check that we actually got a response from the API
                if data is not None:

                    #if media is not an image, it must be a video
                    if data['media_type'] != "image":
                        vidUrl = data['url']
                        vidTitle = data['title']

                        #saving metadata to file to reference later. saves API calls as only checking once a day for new pic.
                        apodData = [{'lastRun':lastRun, 'mediaType':'video', 'url':vidUrl, 'title':vidTitle}]

                        with open ("metadata.txt", "w") as outfile:
                            json.dump(apodData, outfile)
                            outfile.close()
                            
                        return

                    
                    #media is an image
                    else:
                        
                        picUrl = data['hdurl']                        
                        picTitle = data['title']
                        
                        response = requests.get(picUrl)
                        extension = os.path.splitext(picUrl)[1][1:]
                        apodFile = "apod." + extension
                        
                        #saving image to file
                        file = open(apodFile, "wb")
                        file.write(response.content)
                        file.close()
                        
                        #saving metadata to file to reference later. saves API calls as only checking once a day for new pic.
                        apodData = [{'lastRun':lastRun, 'mediaType':'image', 'url':picUrl, 'title':picTitle, 'fileType':extension}]

                        with open ("metadata.txt", "w") as outfile:
                            json.dump(apodData, outfile)
                            outfile.close()
                        
                        return
                    
                else:
                    log("Failed to get APOD")
                    return "api fail"

            
        else:
            
            log("Skipping fetching new image, as still same date")
            return "same day"

        
        
            
    except Exception as e:
        log("Failed to run getAPOD")
        log(str(e))
        if debug:
            print(str(e))
        

def getPeopleInSpace():
    try:
        url = "http://api.open-notify.org/astros.json"
        with urllib.request.urlopen(url) as surl:
               
            data = json.loads(surl.read().decode())
            
            if data['message'] == "success":
                people = data['number']
                if debug:
                    print(people)
                    print(type(people))
                return(people)
            
            else:
                log("Failed to getPeopleInSpace")
                if debug:
                    print("Failed to getPeopleInSpace")
                return(0)
                
            
    except Exception as e:
        log("Failed to run getPeopleInSpace")
        log(str(e))
        if debug:
            print(str(e))



def getISS():
    
    try:
        url = "http://api.open-notify.org/astros.json"
        with urllib.request.urlopen(url) as surl:
               
            data = json.loads(surl.read().decode())
            if data['message'] == "success":
                lat = data["iss_position"]["latitude"]
                lon = data["iss_position"]["longitude"]
                return lat, lon
        
      
    except Exception as e:
        log("Failed to run getISS")
        log(str(e))
        if debug:
            print(str(e))

def log(text):
    try:        
        now = datetime.now()
        now = now.strftime("%Y-%m-%d %H:%M:%S ")
        with open(fileLog, "a") as log:
            log.write("\n")
            log.write(now)
            log.write(text)        
            log.close()
            
    except Exception as e:
        print(str(e))
             


bot.run(discordToken)



