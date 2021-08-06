import discord, requests, urllib, json, random, spaceBotConfig, spaceBotTokens, feedparser, os.path
from json.decoder import JSONDecodeError
from discord.ext import commands
from discord.ext.commands import CommandNotFound
from datetime import datetime, timedelta

#neededIntents = discord.Intents(guilds=True, messages=True)

#########################################################################################

#uses prefix to activate, passes intents needed to function as well.
bot = commands.Bot(command_prefix=spaceBotConfig.discordPrefix, intents=spaceBotConfig.neededIntents)


#########################################################################################
#    EVENT FUNCTIONS BELOW

#called when successfully logged into Discord API. Don't do any API calls in here though.
@bot.event
async def on_ready():
    await afterReady(True)


#called when joining/invited to a guild
@bot.event
async def on_guild_join(guild):
    log(f"INFO - guild - Got invited to {guild.name}, {guild.id}")


#called when kicked/banned from a guild.
@bot.event
async def on_guild_remove(guild):
    log(f"INFO - guild - Got removed from {guild.name}, {guild.id}")
    

#ignore errors when command is not found, otherwise raise the error
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return


#########################################################################################
#    STARTUP FUNCTIONS BELOW

#sets up logging and changes status
async def afterReady(status=False):
    now = datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    
    if status == True:        

        log("--------------")
        log(f"INFO - afterReady - Logged in as: {bot.user.name}")
        log(f"INFO - afterReady - ID: {bot.user.id}")
        log(f"INFO - afterReady - Discord Version: {discord.__version__}")
        log(f"INFO - afterReady - Script Version: {spaceBotConfig.scriptVersion}")
        log(f"INFO - afterReady - Prefix: {spaceBotConfig.discordPrefix}")

        log("INFO - afterReady - Connected to following servers:")
        for guild in bot.guilds:
            log(f"INFO - afterReady - Name: {guild.name}, ID: {guild.id}") 

        bot.owner_id = spaceBotConfig.ownerID
        log(f"INFO - afterReady - Set owner ID to {spaceBotConfig.ownerID}")

        game = discord.Game(f"{spaceBotConfig.discordPrefix}help")
        await bot.change_presence(status=discord.Status.online, activity=game)
        
        log(f"INFO - afterReady - Status changed to \"Playing {spaceBotConfig.discordPrefix}help\"")    

        print(f"{now} - Space Bot Ready")

    else:
        log("ERROR - afterReady - afterReady called, but was not ready")
        print(f"{now} - afterReady called, but was not ready")
        return




#########################################################################################
#   COMMAND FUNCTIONS BELOW


class commandNews(commands.Cog, name="News"):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="news", brief = "Gets space news", help="Gets today's space news. Courtesy of space.com")
    async def news(self, ctx):
        log(f"INFO - news - {ctx.author} used {spaceBotConfig.discordPrefix}news")
        #could be slow at getting stuff from rss feed, so show that bot is responding.
        await ctx.trigger_typing()

        news = getNews()
        if news == "error":
            await ctx.send("Unable to gather news for today.")
        elif news == "no news":
            await ctx.send("No news for today yet. Try later.")
        else:
            await ctx.send(embed=news)                                                                
                                        


class commandISS(commands.Cog, name="ISS"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="iss", brief="Finds the ISS", help="Shows current location of the International Space Station. Courtesy of open-notify.org")
    async def iss(self, ctx):
        if not ctx.author.bot:

            log(f"INFO - pw - {ctx.author} used {spaceBotConfig.discordPrefix}iss")
            
            await ctx.trigger_typing()
            iss = getISS()

            if iss is False:
                await ctx.send("Unable to find the ISS.")
            else:
                lat = iss[0]
                lon = iss[1]
                response = f"Current position: {lat}, {lon}"
                await ctx.send(response)
                mapLink=f"https://www.google.com/maps/place/{lat},{lon}"
                await ctx.send(mapLink)



class commandPW(commands.Cog, name="Planet Weather"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="pw", brief="Different Planet's Weather", help=f"Weather forecast for a given planet in our solar system. \nTry {spaceBotConfig.discordPrefix}pw pluto")
    async def weather(self, ctx, planetName=None):
        if not ctx.author.bot:
            try:
                await ctx.trigger_typing()
                planet = ""
                log(f"INFO - pw - {ctx.author} used pw {planetName}")
                if planetName is not None:
                    planet = str(planetName).lower()

                #picks a random planet from the list
                if planet == "random" or planetName is None:
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
                    log("WARNING - pw - Unknown planet")
                    message = "Unknown planet! Try again..."

                await ctx.send(message)

            except Exception as e:
                log(f"ERROR - pw - Error running commandPW. {e}")
                


class commandPhotos(commands.Cog, name="Pictures"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="apod", brief="Shows a cool space picture", help="Shows NASA's Astronomy Picture Of the Day. Courtesy of NASA.gov", )
    async def apod(self, ctx):
        if not ctx.author.bot:
            try:
                #shows the ... typing animation until the message gets sent. shows that the bot has not ignored the request
                await ctx.trigger_typing()
                log(f"INFO - apod - {ctx.author} used {spaceBotConfig.discordPrefix}apod")

                result = getAPOD()

                #APOD() got an error when running
                if result == "api fail":
                    await ctx.send("Error retrieving APOD")
                
                else:
                #no error with APOD(), so send data
                    with open("apoddata.txt", "r") as jsonFile:
                        metadata = json.load(jsonFile)
                        for data in metadata:
                            try:
                                #if the media is a video, send the URL and explanation in an embed. Can't embed an actual video
                                if data['mediaType'] == "video":
                                    vidTitle = data['title']
                                    vidUrl = data['url']
                                    vidExp = data['explanation']

                                    embed = discord.Embed(title=vidTitle)
                                    embed.add_field(name="Link", value=vidUrl)
                                    embed.set_footer(text=vidExp)
                                    await ctx.send(embed=embed)
                                    jsonFile.close()

                                #if the media is an image, then embed it with a title and explanation
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
                                    log(f"ERROR - apod - Unable to send APOD, media type is {data['mediaType']}")
                                    await ctx.send("Error retrieving APOD")                                
                            

                            except JSONDecodeError:
                                log("ERROR - apod - apoddata.txt was empty in commandAPOD")
                                await ctx.send("Error retrieving APOD")  

                            except Exception as e:
                                await ctx.send("Error retrieving APOD")
                                log(f"ERROR - apod - Error running commandAPOD. {e}")



            except Exception as e:
                await ctx.send("Error retrieving APOD")
                log(f"ERROR - apod - Error running commandAPOD. {e}")


    
    @commands.command(name="mars", brief="Shows photos from Mars", help="""Shows the latest photo from Mars from Curiosity. \nUse ?mars <camera>. Camera is either "f", "r", "m" or "n" for Front, Rear, Mast or Navigation cameras on board""")
    async def mars(self, ctx, camArg=None):
        if not ctx.author.bot:
            
            await ctx.trigger_typing()
                
            log(f"INFO - mars - {ctx.author} used {spaceBotConfig.discordPrefix}mars {camArg}")

            photoEmbed = getMarsPhoto(camArg)

            if photoEmbed is False:
                await ctx.send("Error retrieving photo.")        

            elif photoEmbed is None:
                await ctx.send("Error retrieving photo.")
                log("ERROR - mars - photoEmbed was none.")

            else:
                
                photoLink = photoEmbed[0]
                photoDate = photoEmbed[1]
                photoCamera = photoEmbed[2]
                                                        
                embed = discord.Embed(title=f"Photo from Curiosity's {photoCamera} on {photoDate}")
                embed.set_image(url=photoLink)
                await ctx.send(embed=embed)                 
                


class commandSF(commands.Cog, name="Facts"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="facts", help="Shows interesting facts about space", brief="Space Facts!")
    async def facts(self, ctx):
        if not ctx.author.bot:
            try:

                log(f"INFO - facts - {ctx.author} used {spaceBotConfig.discordPrefix}facts")

                #a list of facts            
                lines = open("facts.txt").read().splitlines()
                randFact = random.choice(lines)
                
                await ctx.send(randFact)

                
            except Exception as e:
                log("ERROR - facts - Error running commandSF")
                log(str(e))



class commandAstros(commands.Cog, name="Astronauts"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="astros", brief="Astronauts!", help="Shows the number of astronauts in space. Courtesy of open-notify.org")
    async def astros(self, ctx):
        if not ctx.author.bot:

            log(f"INFO - astros - {ctx.author} used {spaceBotConfig.discordPrefix}astros")
            
            try:
                #async with ctx.typing():
                await ctx.trigger_typing()   
                #updates astros data if neccessary
                getAstros()                 


                #turns json file into pretty text for discord
                with open ("astrosjson.txt", "r") as jsonFile:
                    try:
                        data = json.load(jsonFile)
                        numPeople = data['number']
                        names = data['people']
                        
                        replyEmbed = discord.Embed(title=f"There are {numPeople} people in space.")
                        for person in names:
                            replyEmbed.add_field(name=person['name'], value=person['craft'], inline=False)
                                                        
                            
                    #if there is no data in the txt file, then set default values.    
                    except JSONDecodeError:
                        jsonFile.close()
                        numPeople = 0
                        

                #sends the list of people in space and their craft.
                await ctx.send(embed=replyEmbed)

                
            except Exception as e:
                log(f"ERROR - astros - Error running commandAstros. {e}")
                


#special command for bot owner only
class commandAdmin(commands.Cog, name="admin"):
    def __init__(self, bot):
        self.bot = bot
    

    @commands.command(name="server", hidden=True)
    async def serverInfo(self, ctx):
        
        if ctx.message.author.id == bot.owner_id:
            #only runs if user is the owner of the bot
            guildEmbed = discord.Embed(title="Server Info")

            for guild in bot.guilds:
                guildEmbed.add_field(name=guild.name, value=guild.id, inline=False)
                log(f"INFO - server - Name: {guild.name}, ID: {guild.id}")

            await ctx.send(embed=guildEmbed)

        else:
            log(f"INFO - server - {ctx.author.id} was not allowed to use this command.")
            #user is not the owner of the bot
            return



    @commands.command(name="info")
    async def adminInfo(self, ctx):
        infoEmbed = discord.Embed(title="Space Bot Info")
        infoEmbed.add_field(name="Discord Support Server", value=spaceBotConfig.discordServer, inline=False)
        infoEmbed.add_field(name="Bot Code on Github", value=spaceBotConfig.githubLink, inline=False)
        infoEmbed.add_field(name="Top.gg page", value=spaceBotConfig.topgg, inline=False)
        await ctx.send(embed=infoEmbed)



#########################################################################################
#    HELPER FUNCTIONS BELOW

def getMarsPhoto(camArg=None):
    
    try:
        if camArg is not None: #check that the arguments have been supplied
            
            cams = spaceBotConfig.cams

            if camArg in cams: #check that the arguments supplied are correct

                if camArg == "f": cam = "FHAZ"
                elif camArg == "r": cam = "RHAZ"
                elif camArg == "n": cam = "NAVCAM"
                elif camArg == "m": cam = "MAST"
                else:
                    log(f"WARNING - getMarsPhoto - Incorrect camArg supplied - {camArg}")
                    return False
                    
                

                manifestUrl = f"https://api.nasa.gov/mars-photos/api/v1/manifests/Curiosity?api_key={spaceBotTokens.NASAApiKey}"
                #get last photo date - maxSol
                with urllib.request.urlopen(manifestUrl) as mUrl:
                    

                    #checking remaining API limits
                    headers = mUrl.headers
                    hourlyLmitRemaining = int(headers['X-RateLimit-Remaining'])
                    
                    if hourlyLmitRemaining <= 100:
                        log(f"WARNING - getMarsPhoto - Only {hourlyLmitRemaining}/1000 requests left this hour.")
                        print(f"WARNING - getMarsPhoto - Only {hourlyLmitRemaining}/1000 requests left this hour.")

                    if hourlyLmitRemaining == 0:
                        #we used all our api calls up
                        log("WARNING - getMarsPhoto - No requests left this hour.")
                        print("WARNING - getMarsPhoto - No requests left this hour.")
                        return False
                    
                    data = json.loads(mUrl.read().decode())

                    if data is not None: #check that we actually got data back
                        log("INFO - getMarsPhoto - Manifest data retrieved successfully.")
                        maxSol = data['photo_manifest']['max_sol']
        
                        availCams = data['photo_manifest']['photos'][-1]['cameras']                        
                        numPhotos = data['photo_manifest']['photos'][-1]['total_photos']

                        if cam not in availCams: #if the chosen camera is not available this time.
                            log(f"WARNING - getMarsPhoto - {cam} not available for Curiosity, available cameras {availCams}.")
                            return False
                        
                            
                    else:
                        log(f"ERROR - getMarsPhoto - No data returned from manifestUrl.")
                        return False
                        



                photoUrl = f"https://api.nasa.gov/mars-photos/api/v1/rovers/Curiosity/photos?camera={cam}&sol={maxSol}&api_key={spaceBotTokens.NASAApiKey}"
                with urllib.request.urlopen(photoUrl) as pUrl:

                    data = json.loads(pUrl.read().decode())

                    #checking remaining API limits
                    headers = pUrl.headers
                    hourlyLmitRemaining = int(headers['X-RateLimit-Remaining'])

                    if hourlyLmitRemaining <= 100:
                        log(f"WARNING - getMarsPhoto - Only {hourlyLmitRemaining}/1000 requests left this hour.")
                        print(f"WARNING - getMarsPhoto - Only {hourlyLmitRemaining}/1000 requests left this hour.")

                    if hourlyLmitRemaining == 0:
                        #we used all our api calls up
                        log("WARNING - getMarsPhoto - No requests left this hour.")
                        print("WARNING - getMarsPhoto - No requests left this hour.")
                        return False

                    if data is not None:
                        log("INFO - getMarsPhoto - Photo data retrieved successfully.")
                        
                        #selects a random photo from the given camera on the latest day available
                        photoSelect = random.randint(1,numPhotos)

                        photoDate = data['photos'][photoSelect]['earth_date']
                        photoLink = data['photos'][photoSelect]['img_src']
                        
                    else:
                        log(f"ERROR - getMarsPhoto - No data returned from photoUrl.")
                        return False

                return photoLink, photoDate, cam

            else: 
                log(f"INFO - getMarsPhoto - Incorrect arg supplied in {spaceBotConfig.discordPrefix}mars")
                return False                    
        
        else:
            log(f"INFO - getMarsPhoto - Missing arg in {spaceBotConfig.discordPrefix}mars")
            return False

    except Exception as e:
        log(f"ERROR - getMarsPhoto - Error running getMarsPhoto {e}")
        return False


#Astronomy Picture of the Day helper function, does API calls.
def getAPOD():
    try:
        
        #check the last time we got the photo
        with open("apoddata.txt", "r") as jsonFile:
            try:
                metadata = json.load(jsonFile)
                for data in metadata:                
                    lastRun = data['lastRun']   

            #if file is empty, then set a default value
            except JSONDecodeError:
                log("WARNING - getAPOD - apoddata.txt was empty")
                lastRun = None

            jsonFile.close()
                
        dateToday = datetime.today().strftime('%Y-%m-%d')
        
        #need to fetch new apod if it hasn't been done today        
        if lastRun != dateToday or lastRun is None:
        
            log("INFO - getAPOD - Fetching new image for today")
            lastRun = datetime.today().strftime('%Y-%m-%d')
            
            ApodUrl = f"https://api.nasa.gov/planetary/apod?api_key={spaceBotTokens.NASAApiKey}"

            with urllib.request.urlopen(ApodUrl) as sUrl:
                data = json.loads(sUrl.read().decode())

                #checking remaining API limits
                headers = sUrl.headers
                hourlyLmitRemaining = int(headers['X-RateLimit-Remaining'])
                #log(f"INFO - getAPOD - X-RateLimit-Limit = {headers['X-RateLimit-Limit']}. X-RateLimit-Remaining = {headers['X-RateLimit-Remaining']}")
                if hourlyLmitRemaining <= 100:
                    log(f"WARNING - getAPOD - Only {hourlyLmitRemaining}/1000 requests left this hour.")

                #check that we actually got a response from the API
                if data is not None:
                    #check if media is a video
                    if data['media_type'] == "video":
                        vidUrl = data['url']
                        vidTitle = data['title']
                        vidExplanation = data['explanation']
                        

                        #saving metadata to file to reference later. saves API calls as only checking once a day for new pic.
                        apodData = [{'lastRun':lastRun, 'mediaType':'video', 'url':vidUrl, 'title':vidTitle, 'explanation':vidExplanation}]

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
                        log(f"ERROR - getAPOD - APOD was not an image or video, instead was {data['media_type']}")
                        return "api fail"

                    
                else:
                    #data is None
                    log("ERROR - getAPOD - Failed to get APOD")
                    return "api fail"

            
        else:            
            log("INFO - getAPOD - Skipping fetching new image, as still same date")
            return
        
    #if the file doesn't exist, then create it for next time.
    except IOError:
        with open("apoddata.txt", "w") as jsonFile:
            jsonFile.close()
        log("INFO - getAPOD - apoddata.txt does not exist, created it.")

    except Exception as e:
        log("ERROR - getAPOD - Failed to run getAPOD")
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
                log("INFO - getAstros - astrosdata.txt was empty")
        

    #if file does not exist, create it for next time.
    except IOError:
        with open("astrosdata.txt", "w") as jsonFile: 
            jsonFile.close()
            lastRun = None
        log("INFO - getAstros - astrosdata.txt did not exist, created it.")
                          
    
   
            
    dateToday = datetime.today().strftime('%Y-%m-%d')
    
    #need to fetch new apod if it hasn't been done today, or has no value.        
    if lastRun != dateToday or lastRun is None:

        log("INFO - getAstros - Fetching new astros data")
        
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
                log("ERROR - getAstros - Failed to getastros")
                return("api fail")

    else:
        log("INFO - getAstros - Same day, skipping checking API for astros")




#ISS location helper fucntion, does API calls.
def getISS():
    
    try:
        r = requests.get("http://api.open-notify.org/iss-now.json")    
        x = r.json()
        lat = x["iss_position"]["latitude"]
        lon = x["iss_position"]["longitude"]
        return lat, lon
    
    except Exception as e:
        log("ERROR - getISS - Failed to run")
        log(str(e))
        return False


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
        log(f"ERROR - getNews - Failed to run, url parsing failed. {e}")
        return "error"

    embedTitle = f"Space news for {stringToday}"
    todaysNews = discord.Embed(title=embedTitle)

 
    for entry in newsfeed.entries:
        #only get today's news.
        if entry.published_parsed[0] == year and entry.published_parsed[1] == month and entry.published_parsed[2] == day:
            todaysNews.add_field(name=entry.title, value=entry.link, inline=False)
        
        #only want to return 10 news articles at once.
        if len(todaysNews) == 10:
            log(f"INFO - getNews - todaysNews is 10")
            break
                
                
    #check if fields list is empty (implying we have no news for today)
    if not todaysNews.fields:
        #no news for today, so return False.
        log(f"INFO - getNews - No news for {stringToday}.")
        return "no news"
        
    else:
        #there is news for today, so return the Embed object.
        return todaysNews






def log(text):

    now = datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M:%S ")
    now = str(now)

    try:
        text = str(text)
        #added encoding in v0.4.3 to solve charmap error
        with open(spaceBotConfig.fileLog, "a", encoding="utf-8") as log:
            log.write("\n")
            log.write(now)
            log.write(text)        
            log.close()
            
    except Exception as e:
        print(f"{now} - Error with log function {e}")


#########################################################################################
#   COG SETUP BELOW


#add cogs
bot.add_cog(commandPhotos(bot))
bot.add_cog(commandAstros(bot))
bot.add_cog(commandISS(bot))
bot.add_cog(commandPW(bot))
bot.add_cog(commandSF(bot))
bot.add_cog(commandNews(bot))
bot.add_cog(commandAdmin(bot))

#main bot run command.
bot.run(spaceBotTokens.spaceBotToken)
