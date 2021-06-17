from json.decoder import JSONDecodeError
import discord, requests, urllib, json, random
from discord.ext import commands
import spaceBotConfig
import spaceBotTokens
from datetime import datetime
import os.path

#uses either prefix or @ mention to activate
bot = commands.Bot(command_prefix=commands.when_mentioned_or(spaceBotConfig.discordPrefix))




#called when successfully logged into Discord API. Don't do any API calls in here though.
@bot.event
async def on_ready():
    await afterReady(True)


#sets up logging and changes status
async def afterReady(status=False):
    
    if status == True:
        log("--------------")
        log("Logged in as: {}".format(bot.user.name))
        log("ID: {}".format(bot.user.id))
        log("Discord Version: {}".format(discord.__version__))
        log("Script Version: {}".format(spaceBotConfig.scriptVersion))
        log("Prefix: {}".format(spaceBotConfig.discordPrefix))

        log("Connected to following servers:")
        for guild in bot.guilds:
            log("- " + guild.name + " " + str(guild.id))
            
        game = discord.Game("{}help".format(spaceBotConfig.discordPrefix))
        await bot.change_presence(status=discord.Status.online, activity=game)
        
        log("Status changed to \"Playing {}help\"".format(spaceBotConfig.discordPrefix))        
        print("Space Bot Ready")

    else:
        print("afterReady called, but was not ready.")
        return




class commandISS(commands.Cog, name="ISS"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="iss", help="Shows current location of the International Space Station", brief="Finds the ISS")
    async def iss(self, ctx):
        if not ctx.author.bot:
            log("{} used ISS command".format(ctx.author))
            async with ctx.typing():
                #await ctx.send("The ISS is in space, dummy!")
                iss = getISS()
                lat = iss[0]
                lon = iss[1]
                response = "Current position: " + lat + ", " + lon
                await ctx.send(response)


class commandPW(commands.Cog, name="Planet Weather"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="pw", help="Weather forecast for a given planet in our solar system. \nTry ?pw pluto", brief="Different Planet's Weather")
    async def weather(self, ctx, planetName):
        if not ctx.author.bot:
            try:
                
                log("{} used PW command".format(ctx.author))
                    
                planet = str(planetName).lower()

                #picks a random planet from the list
                if planet == "random":
                    listPlanets = ["mercury", "venus", "earth", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]
                    planet = random.choice(listPlanets)

                #weather and comments for each planet
                if planet == "mercury":
                    message = "Mercury averages 800°F (430°C) during the day, -290°F (-180°C) at night. Quite windy, so make sure to grab a jacket before heading out."
                elif planet ==  "venus":
                    message = "Venus averages 880°F (471°C). Acid rain likely, so bring an umbrella."
                elif planet ==  "earth":
                    message = "Earth averages 61°F (16°C). There will be weather."
                elif planet ==  "mars":
                    message = "Mars averages -20°F (-28°C). A little chilly out, so don't forget a jumper."
                elif planet ==  "jupiter":
                    message = "Jupiter averages -162°F (-108°C). There's no solid ground, you'll need a yacht."
                elif planet ==  "saturn":
                    message = "Saturn averages -218°F (-138°C). Big storms at the north pole, and watch out for the strong winds."
                elif planet ==  "uranus":
                    message = "Uranus averages -320°F (-195°C). A little nippy, so wrap up well."
                elif planet ==  "neptune":
                    message = "Neptune averages -331°F (-201°C). Winds are picking up, so be careful out there!"
                elif planet ==  "pluto":
                    message = "Pluto averages -388°F (-233°C). I'm still annoyed that it's not a planet."
                else:
                    log("Unknown planet")
                    message = "Unknown planet! Try again..."

                await ctx.send(message)

            except Exception as e:
                log("Error running commandPW")
                log(str(e))



class commandAPOD(commands.Cog, name="Pictures"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="apod", help="Shows NASA's Astronomy Picture Of the Day", brief="Shows a cool space picture")
    async def apod(self, ctx):
        if not ctx.author.bot:
            try:
                #shows the ... typing animation until the message gets sent. shows that the bot has not ignored the request
                async with ctx.typing():
                    log("{} used APOD command".format(ctx.author))
                    result = getAPOD()


                    #APOD() got an error when running
                    if result == "api fail":
                        await ctx.send("Unable to get Astronomy Picture Of the Day.")
                        

                    
                    else:
                    #no error with APOD(), so send data
                        with open("apoddata.txt", "r") as jsonFile:
                            metadata = json.load(jsonFile)
                            for data in metadata:
                                try:
                                    #if the media is a video, then just send the url
                                    if data['mediaType'] == "video":
                                            
                                        await ctx.send("Today's Astronomy Picture Of the Day is a video.")
                                        await ctx.send(data['url'])
                                        jsonFile.close()
                                        

                                    #if the media is an image, then embed it with a title
                                    elif data['mediaType'] == "image":
                                        picTitle = data['title']
                                        extension = data['fileType']
                                        apodFile = "apod." + extension

                                        file = discord.File(apodFile, filename="image.png")
                                        
                                        embed = discord.Embed()
                                        embed.add_field(name="Title", value=picTitle)
                                        embed.set_image(url="attachment://image.png")
                                        
                                        await ctx.send(file=file, embed=embed)
                                        jsonFile.close()
                                        
                                    
                                    #edge case where mediaType is neither video or image
                                    else:
                                        await ctx.send("Unable to send APOD, invalid Media type")
                                        log("Unable to send APOD, media type is {}".format(data['mediaType']))
                                
                                except JSONDecodeError:
                                    log("apoddata.txt was empty in commandAPOD")
                                    await ctx.send("Unable to send APOD, no data.")


            except Exception as e:
                log("Error running commandAPOD")
                log(str(e))
        


class commandSF(commands.Cog, name="Facts"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="facts", help="Shows interesting facts about space", brief="Space Facts!")
    async def facts(self, ctx):
        if not ctx.author.bot:
            try:

                log("{} used SF command".format(ctx.author))

                #a list of facts            
                lines = open("facts.txt").read().splitlines()
                randFact = random.choice(lines)
                
                await ctx.send(randFact)

                
            except Exception as e:
                log("Error running commandSF")
                log(str(e))



class commandAstros(commands.Cog, name="Astronauts"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="astros", help="Shows the number of astronatus in space. \nThanks to Natronics at https://api.open-notify.org", brief="Astronauts!")
    async def astros(self, ctx):
        if not ctx.author.bot:
            try:
                log("{} used Astros command".format(ctx.author))
                
                getAstros()
                try:
                    with open("astrosdata.txt", "r") as jsonFile:
                        try:
                            metadata = json.load(jsonFile)
                            for data in metadata:
                                numPeople = data['people']
                            jsonFile.close()

                        #if there is no data in the txt file, then set a default value.    
                        except JSONDecodeError:
                            jsonFile.close()
                            numPeople = 0
                            

                #if the file doesn't exist, then create it for next time.
                except IOError:
                    log("astrosdata.txt did not exist, created it.")
                    with open("astrosdata.txt", "w") as jsonFile:
                        jsonFile.close()
                        numPeople = 0
                    

                await ctx.send("There are {} people in space right now!".format(numPeople))


                
            except Exception as e:
                log("Error running commandAstros")
                log(str(e))



#Astronomy Picture of the Day helper function, does API calls.
def getAPOD():
    try:

        with open("apoddata.txt", "r") as jsonFile:
            try:
                metadata = json.load(jsonFile)
                for data in metadata:                
                    lastRun = data['lastRun']   

            #if file is empty, then set a default value
            except JSONDecodeError:
                log("apoddata.txt was empty")
                lastRun = None

            jsonFile.close()
                
        dateToday = datetime.today().strftime('%Y-%m-%d')
        
        #need to fetch new apod if it hasn't been done today        
        if lastRun != dateToday or lastRun is None:
        
            log("Fetching new image for today")
            lastRun = datetime.today().strftime('%Y-%m-%d')
            
            ApodUrl = "https://api.nasa.gov/planetary/apod?api_key={}".format(spaceBotTokens.NASAApiKey)

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

                        with open ("apoddata.txt", "w") as outfile:
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

                        with open ("apoddata.txt", "w") as outfile:
                            json.dump(apodData, outfile)
                            outfile.close()
                        
                        return
                    
                else:
                    log("Failed to get APOD")
                    return "api fail"

            
        else:            
            log("Skipping fetching new image, as still same date")
            return
        
    #if the file doesn't exist, then create it for next time.
    except IOError:
        with open("apoddata.txt", "w") as jsonFile:
            jsonFile.close()
        log("apoddata.txt does not exist, created it.")

    except Exception as e:
        log("Failed to run getAPOD")
        log(str(e))
        





#Astros helper function, does API calls
def getAstros():
    try:
        
        #if os.path.getsize("astrosdata.txt") > 10:
        
        with open("astrosdata.txt", "r") as jsonFile:
    
            metadata = json.load(jsonFile)
            try:                
                for data in metadata:                    
                    lastRun = data['lastRun']                    
                    jsonFile.close()
                
            #if file is empty, set a default value.
            except JSONDecodeError:
                lastRun = None
                log("astrosdata.txt was empty")
        

    #if file does not exist, create it for next time.
    except IOError:
        with open("astrosdata.txt", "w") as jsonFile: 
            jsonFile.close()
        log("astrosdata.txt did not exist, created it.")
                          
    
   
            
    dateToday = datetime.today().strftime('%Y-%m-%d')
    
    #need to fetch new apod if it hasn't been done today, or has no value.        
    if lastRun != dateToday or lastRun is None:

        log("Fetching new astros data")
        
        lastRun = dateToday            
        
        url = "http://api.open-notify.org/astros.json"
        with urllib.request.urlopen(url) as surl:
                
            data = json.loads(surl.read().decode())
            
            if data['message'] == "success":
                people = data['number']

                
                #saving metadata to file to reference later. saves API calls as only checking once a day for new pic.
                astrosData = [{'lastRun':lastRun, 'people':people}]
                
                with open ("astrosdata.txt", "w") as outfile:
                    json.dump(astrosData, outfile)
                    outfile.close()
            
            else:
                log("Failed to getastros")
                return("api fail")

    else:
        log("Same day, skipping checking API for astros")



#ISS location helper fucntion, does API calls.
def getISS():
    
    try:
        r = requests.get("http://api.open-notify.org/iss-now.json")    
        x = r.json()
        lat = x["iss_position"]["latitude"]
        lon = x["iss_position"]["longitude"]
        return lat, lon
    
    except Exception as e:
        log("Failed to run getISS")
        log(str(e))
        return



def log(text):
    try:        
        now = datetime.now()
        now = now.strftime("%Y-%m-%d %H:%M:%S ")
        with open(spaceBotConfig.fileLog, "a") as log:
            log.write("\n")
            log.write(now)
            log.write(text)        
            log.close()
            
    except Exception as e:
        print("Error with log function")
        print(str(e))


#add cogs
bot.add_cog(commandAPOD(bot))
bot.add_cog(commandAstros(bot))
bot.add_cog(commandISS(bot))
bot.add_cog(commandPW(bot))
bot.add_cog(commandSF(bot))

#main bot run command.
bot.run(spaceBotTokens.discordToken)

