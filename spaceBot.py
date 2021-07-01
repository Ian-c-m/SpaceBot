import discord, requests, urllib, json, random, spaceBotConfig, spaceBotTokens, feedparser, os.path
from json.decoder import JSONDecodeError
from discord.ext import commands
from datetime import datetime


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
        log(f"INFO - Logged in as: {bot.user.name}")
        log(f"INFO - ID: {bot.user.id}")
        log(f"INFO - Discord Version: {discord.__version__}")
        log(f"INFO - Script Version: {spaceBotConfig.scriptVersion}")
        log(f"INFO - Prefix: {spaceBotConfig.discordPrefix}")

        log("INFO - Connected to following servers:")
        for guild in bot.guilds:
            log("- " + guild.name + " " + str(guild.id))
            
        game = discord.Game(f"{spaceBotConfig.discordPrefix}help")
        await bot.change_presence(status=discord.Status.online, activity=game)
        
        log(f"INFO - Status changed to \"Playing {spaceBotConfig.discordPrefix}help\"")        
        print("Space Bot Ready")

    else:
        log("ERROR - afterReady called, but was not ready")
        print("afterReady called, but was not ready")
        return


#########################################################################################


class commandNews(commands.Cog, name="News"):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="news", brief = "Gets space news", help="Gets today's space news. Courtesy of space.com")
    async def news(self, ctx):
        #could be slow at getting stuff from rss feed, so show that bot is responding.
        with ctx.typing():

            news = getNews()
            if news is False:
                await ctx.send("Unable to gather news.")
            else:
                await ctx.send(embed=news)                               
                                        
                                        


class commandISS(commands.Cog, name="ISS"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="iss", brief="Finds the ISS", help="Shows current location of the International Space Station. Courtesy of open-notify.org")
    async def iss(self, ctx):
        if not ctx.author.bot:
            log(f"INFO - {ctx.author} used ISS command")
            async with ctx.typing():
                iss = getISS()
                lat = iss[0]
                lon = iss[1]
                response = f"Current position: {lat}, {lon}"
                await ctx.send(response)
                mapLink=f"https://www.google.com/maps/place/{lat},{lon}"
                await ctx.send(mapLink)


class commandPW(commands.Cog, name="Planet Weather"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="pw", brief="Different Planet's Weather", help="Weather forecast for a given planet in our solar system. \nTry ?pw pluto")
    async def weather(self, ctx, planetName):
        if not ctx.author.bot:
            try:
                
                log(f"INFO - {ctx.author} used PW command")
                    
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
                    log("ERROR - Unknown planet")
                    message = "Unknown planet! Try again..."

                await ctx.send(message)

            except Exception as e:
                log("ERROR - Error running commandPW")
                log(str(e))



class commandAPOD(commands.Cog, name="Pictures"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="apod", brief="Shows a cool space picture", help="Shows NASA's Astronomy Picture Of the Day. Courtesy of NASA.gov", )
    async def apod(self, ctx):
        if not ctx.author.bot:
            try:
                #shows the ... typing animation until the message gets sent. shows that the bot has not ignored the request
                async with ctx.typing():
                    log(f"INFO - {ctx.author} used APOD command")
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
                                        
                                        embed = discord.Embed(title=picTitle)
                                        
                                        
                                        embed.set_image(url="attachment://image.png")
                                        embed.set_footer(text=data['explanation'])
                                        jsonFile.close()

                                        await ctx.send(file=file, embed=embed)
                                        
                                        
                                    
                                    #edge case where mediaType is neither video or image
                                    else:
                                        await ctx.send("Unable to send APOD, invalid media type")
                                        log(f"ERROR - Unable to send APOD, media type is {data['mediaType']}")
                                

                                except JSONDecodeError:
                                    log("ERROR - apoddata.txt was empty in commandAPOD")
                                    await ctx.send("Unable to send APOD, no data.")


            except Exception as e:
                log("ERROR - Error running commandAPOD")
                log(str(e))
        


class commandSF(commands.Cog, name="Facts"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="facts", help="Shows interesting facts about space", brief="Space Facts!")
    async def facts(self, ctx):
        if not ctx.author.bot:
            try:

                log(f"INFO - {ctx.author} used SF command")

                #a list of facts            
                lines = open("facts.txt").read().splitlines()
                randFact = random.choice(lines)
                
                await ctx.send(randFact)

                
            except Exception as e:
                log("ERROR - Error running commandSF")
                log(str(e))



class commandAstros(commands.Cog, name="Astronauts"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="astros", brief="Astronauts!", help="Shows the number of astronauts in space. Courtesy of open-notify.org")
    async def astros(self, ctx):
        if not ctx.author.bot:
            try:
                async with ctx.typing():
                    log(f"INFO - {ctx.author} used Astros command")
                    
                    #updates astros data if neccessary
                    getAstros()                 


                    #turns json file into pretty text for discord
                    with open ("astrosjson.txt", "r") as jsonFile:
                        try:
                            data = json.load(jsonFile)
                            numPeople = data['number']
                            names = data['people']

                            replyDetails = ""
                            for person in names:
                                replyDetails = replyDetails + f"{person['name']} - {person['craft']} \n"
                                
                                
                        #if there is no data in the txt file, then set default values.    
                        except JSONDecodeError:
                            jsonFile.close()
                            numPeople = 0
                            replyDetails = "Unable to fetch details"

                    #sends the list of people in space and their craft.
                    await ctx.send(f"There are {numPeople} people in space right now!")
                    await ctx.send(replyDetails)


                
            except Exception as e:
                log("ERROR - Error running commandAstros")
                log(str(e))

#########################################################################################

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
                log("INFO - apoddata.txt was empty")
                lastRun = None

            jsonFile.close()
                
        dateToday = datetime.today().strftime('%Y-%m-%d')
        
        #need to fetch new apod if it hasn't been done today        
        if lastRun != dateToday or lastRun is None:
        
            log("INFO - Fetching new image for today")
            lastRun = datetime.today().strftime('%Y-%m-%d')
            
            ApodUrl = f"https://api.nasa.gov/planetary/apod?api_key={spaceBotTokens.NASAApiKey}"

            with urllib.request.urlopen(ApodUrl) as surl:
                data = json.loads(surl.read().decode())

                #check that we actually got a response from the API
                if data is not None:

                    #check if media is a video
                    if data['media_type'] == "video":
                        vidUrl = data['url']
                        vidTitle = data['title']
                        

                        #saving metadata to file to reference later. saves API calls as only checking once a day for new pic.
                        apodData = [{'lastRun':lastRun, 'mediaType':'video', 'url':vidUrl, 'title':vidTitle}]

                        with open ("apoddata.txt", "w") as outfile:
                            json.dump(apodData, outfile)
                            outfile.close()
                            
                        return

                    
                    #media is an image
                    elif data['media_type'] == "image":
                        
                        picUrl = data['hdurl']                        
                        picTitle = data['title']
                        picExplanation = data['explanation']
                        
                        response = requests.get(picUrl)
                        extension = os.path.splitext(picUrl)[1][1:]
                        apodFile = "apod." + extension
                        
                        #saving image to file
                        file = open(apodFile, "wb")
                        file.write(response.content)
                        file.close()
                        
                        #saving metadata to file to reference later. saves API calls as only checking once a day for new pic.
                        apodData = [{'lastRun':lastRun, 'mediaType':'image', 'url':picUrl, 'title':picTitle, 'explanation':picExplanation, 'fileType':extension}]

                        with open ("apoddata.txt", "w") as outfile:
                            json.dump(apodData, outfile)
                            outfile.close()
                        
                        return

                    else:
                        log(f"ERROR - APOD was not an image or video, instead was {data['media_type']}")
                        return "api fail"

                    
                else:
                    log("ERROR - Failed to get APOD")
                    return "api fail"

            
        else:            
            log("INFO - Skipping fetching new image, as still same date")
            return
        
    #if the file doesn't exist, then create it for next time.
    except IOError:
        with open("apoddata.txt", "w") as jsonFile:
            jsonFile.close()
        log("INFO - apoddata.txt does not exist, created it.")

    except Exception as e:
        log("ERROR - Failed to run getAPOD")
        log(str(e))
  


#Astros helper function, does API calls
def getAstros():
    try:
        
        
        with open("astrosdata.txt", "r") as jsonFile:
            try:
                metadata = json.load(jsonFile)
                            
                for data in metadata:                    
                    lastRun = data['lastRun']                    
                    jsonFile.close()
                
            #if file is empty, set a default value.
            except JSONDecodeError:
                lastRun = None
                log("INFO - astrosdata.txt was empty")
        

    #if file does not exist, create it for next time.
    except IOError:
        with open("astrosdata.txt", "w") as jsonFile: 
            jsonFile.close()
            lastRun = None
        log("INFO - astrosdata.txt did not exist, created it.")
                          
    
   
            
    dateToday = datetime.today().strftime('%Y-%m-%d')
    
    #need to fetch new apod if it hasn't been done today, or has no value.        
    if lastRun != dateToday or lastRun is None:

        log("INFO - Fetching new astros data")
        
        lastRun = dateToday
        
        url = "http://api.open-notify.org/astros.json"
        with urllib.request.urlopen(url) as surl:
                
            data = json.loads(surl.read().decode())
            
            if data['message'] == "success":
                with open ("astrosjson.txt", "w") as outfile:
                    json.dump(data, outfile)
                    outfile.close()
                
                #saving metadata to file to reference later. 
                astrosData = [{'lastRun':lastRun}]
                
                with open ("astrosdata.txt", "w") as outfile:
                    json.dump(astrosData, outfile)
                    outfile.close()
            
            else:
                log("ERROR - Failed to getastros")
                return("api fail")

    else:
        log("INFO - Same day, skipping checking API for astros")




#ISS location helper fucntion, does API calls.
def getISS():
    
    try:
        r = requests.get("http://api.open-notify.org/iss-now.json")    
        x = r.json()
        lat = x["iss_position"]["latitude"]
        lon = x["iss_position"]["longitude"]
        return lat, lon
    
    except Exception as e:
        log("ERROR - Failed to run getISS")
        log(str(e))
        return


#news helper function. gets today's news from space.com rss feed. returns as discord embed object.
def getNews():
   

    today = datetime.now()
    year = int(today.strftime("%Y"))
    month = int(today.strftime("%m"))
    day = int(today.strftime("%d"))
    stringToday = today.strftime("%Y-%m-%d")

    url = "https://www.space.com/feeds/all"

    #error catching incase url is down/can't connect
    try:
        newsfeed = feedparser.parse(url)
    except Exception as e:
        log(f"ERROR - Failed to run getNews, url parsing failed. {e}")
        return False

    embedTitle = f"Space news for {stringToday}"
    todaysNews = discord.Embed(title=embedTitle)


    for entry in newsfeed.entries:
        #only get today's news.
        if entry.published_parsed[0] == year and entry.published_parsed[1] == month and entry.published_parsed[2] == day:
            todaysNews.add_field(name=entry.title, value=entry.link, inline=False)

    return todaysNews
    
        

#########################################################################################


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

#########################################################################################
#add cogs
bot.add_cog(commandAPOD(bot))
bot.add_cog(commandAstros(bot))
bot.add_cog(commandISS(bot))
bot.add_cog(commandPW(bot))
bot.add_cog(commandSF(bot))
bot.add_cog(commandNews(bot))

#main bot run command.
bot.run(spaceBotTokens.spaceBotToken)
