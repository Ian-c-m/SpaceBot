import discord, requests, urllib, json
from discord.ext import commands
from spaceBotConfig import discordPrefix, fileLog
from spaceBotTokens import discordToken, NASAApiKey
from datetime import date, datetime
import os.path
import random

bot = commands.Bot(command_prefix=commands.when_mentioned_or(discordPrefix))
debug = False


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
        log("Debug: {}".format(str(debug)))
        log("Discord Version: {}".format(discord.__version__))
        log("Prefix: {}".format(discordPrefix))

        log("Connected to following servers:")
        for guild in bot.guilds:
            log("- " + guild.name + " " + str(guild.id))
            
        game = discord.Game("{}help".format(discordPrefix))
        await bot.change_presence(status=discord.Status.online, activity=game)
        
        log("Status changed to \"Playing {}help\"".format(discordPrefix))
            
        if debug:
            print("Logged in as: {}".format(bot.user.name))
            print("ID: {}".format(bot.user.id))
            print("Debug: {}".format(str(debug)))
            print("Discord Version: {}".format(discord.__version__))
            print("Prefix: {}".format(discordPrefix))
            print("Connected to following servers:")
            for guild in bot.guilds:
                print("- " + guild.name + " " + str(guild.id))
            print("Status changed to \"Playing {}help\"".format(discordPrefix))                
            print("--------------")
        else:
            print("Ready")

            
            


#shows location of ISS in lat and lon, from open-notify APIdiscord
@bot.command(name="iss", help="Shows current location of the International Space Station. \nThanks to Natronics at https://api.open-notify.org", brief="Finds the ISS")
async def commandISS(ctx):
    try:
        if not ctx.author.bot:
            
            log("{} used ISS command".format(ctx.author))
            if debug:
                print("{} used ISS command".format(ctx.author))
                
            await ctx.send("The ISS is in space, obviously!")
            iss = getISS()
            
            if iss == "api fail":
                await ctx.send("Failed to get ISS location. Try again later")

            else:            
                lat = iss[0]
                lon = iss[1]
                response = "Current ISS position: " + lat + " latitude, " + lon + " longitude"
                await ctx.send(response)
                
    except Exception as e:
        log("Error running commandISS")
        log(str(e))
        if debug:
            print("Error running commandISS")
            print(str(e))


#shows a cool space pic, from NASA API
@bot.command(name="apod", help="Shows NASA's Astronomy Picture Of the Day. \nThanks to NASA at https://api.nasa.gov", brief="Space picture of the day")
async def commandAPOD(ctx):
    if not ctx.author.bot:
        
        try:
            
            log("{} used APOD command".format(ctx.author))
            if debug:
                print("{} used APOD command".format(ctx.author))
                
            result = getAPOD()


            #APOD got an error when running
            if result == "api fail":
                await ctx.send("Unable to get Astronomy Picture Of the Day.")
                log("Unable to get Astronomy Picture Of the Day.")
                if debug:
                    print("Unable to get Astronomy Picture Of the Day.")
                    
                

            #APOD suceeded.
            else:
                with open("apoddata.txt", "r") as jsonFile:
                    metadata = json.load(jsonFile)
                    for d in metadata:

                        if d['mediaType'] == "video":
                            #if the media is a video, just sends the URL instead of embedding the video
                            await ctx.send("Today's Astronomy Picture Of the Day is a video.")
                            await ctx.send(d['url'])
                            jsonFile.close()
                            return

                        
                        elif d['mediaType'] == "image":
                            #if the media is an image, embeds the image in a message 
                            picTitle = d['title']
                            extension = d['fileType']
                            apodFile = "apod." + extension

                            file = discord.File(apodFile, filename="image.png")
                            
                            embed = discord.Embed()
                            embed.add_field(name="NASA Astronomy Picture Of the Day", value=picTitle)
                            embed.set_image(url="attachment://image.png")
                            
                            await ctx.send(file=file, embed=embed)
                            jsonFile.close()
                            return


        except Exception as e:
            log("Error running commandAPOD")
            log(str(e))
            if debug:
                print("Error running commandAPOD")
                print(str(e))                               
        


@bot.command(name="pw", help="Weather forecast for a given planet in our solar system. \nTry ?pw pluto", brief="Different Planet's Weather")
async def commandPW(ctx, planetName):
    if not ctx.author.bot:
        try:
            
            log("{} used PW command".format(ctx.author))
            if debug:
                print("{} used PW command".format(ctx.author))
                
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
                message = "Earth averages 61°F (16°C). Summer is here, so grab that sunscreen!"
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
            if debug:
                print("Error running commandPW")
                print(str(e))



@bot.command(name="facts", help="Shows interesting facts about space", brief="Space Facts!")
async def commandSF(ctx):
    if not ctx.author.bot:
        try:

            log("{} used SF command".format(ctx.author))
            if debug:
                print("{} used SF command".format(ctx.author))

            #a list of facts
            
            lines = open("facts.txt").read().splitlines()
            randFact = random.choice(lines)
            
            await ctx.send(randFact)

            
        except Exception as e:
            log("Error running commandSF")
            log(str(e))
            if debug:
                print("Error running commandSF")
                print(str(e))


@bot.command(name="astros", help="Shows the number of astronatus in space. \nThanks to Natronics at https://api.open-notify.org", brief="Astronauts!")
async def commandAstros(ctx):
    try:
        log("{} used Astros command".format(ctx.author))
        if debug:
                print("{} used Astros command".format(ctx.author))
        
        getAstros()
        
        with open("astrosdata.txt", "r") as jsonFile:
                metadata = json.load(jsonFile)
                for data in metadata:
                    numPeople = data['people']
                jsonFile.close()
                    
        await ctx.send("There are {} people in space right now!".format(numPeople))


        
    except Exception as e:
        log("Error running commandAstros")
        log(str(e))
        if debug:
            print("Error running commandAstros")
            print(str(e))

      
#helper function to get NASA's picture of the day. will only fetch new picture if day has rolled over.
def getAPOD():
    try:

        if os.path.getsize("apoddata.txt") > 50:
            with open("apoddata.txt", "r") as jsonFile:
                metadata = json.load(jsonFile)
                for meta in metadata:
                    lastRun = meta['lastRun']
                    jsonFile.close()
        else:
            lastRun = None
            
        dateToday = datetime.today().strftime('%Y-%m-%d')
        
        #need to fetch new apod if it hasn't been done today        
        if lastRun != dateToday or lastRun == None:
        
            log("Fetching new image for today")
            if debug:
                print("Fetching new image for today")
                
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
                    if debug:
                        print("Failed to get APOD")
                    return "api fail"
            
        else:
            log("Same day, no new image")
            if debug:
                print("Same day, no new image")
            return 
        
        
            
    except Exception as e:
        log("Error running getAPOD")
        log(str(e))
        if debug:
            print("Error running getAPOD")
            print(str(e))


        
#Astros helper function - does the API calls
def getAstros():
    try:
        
        if os.path.getsize("astrosdata.txt") > 10:
            with open("astrosdata.txt", "r") as jsonFile:
            
                metadata = json.load(jsonFile)                
                for data in metadata:                    
                    lastRun = data['lastRun']                    
                    jsonFile.close()
                    
        else:
            lastRun = None
            
        dateToday = datetime.today().strftime('%Y-%m-%d')
        
        #need to fetch new apod if it hasn't been done today        
        if lastRun != dateToday or lastRun == None:
            if debug:
                print("Fetching new astros data")
            
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
                    if debug:
                        print("Failed to getastros")
                    return("api fail")

        else:
            log("Same day, skipping checking API for astros")
            if debug:
                print("Same day, skipping checking API for astros")
                
            
                
                    
                    
            
            
    except Exception as e:
        log("Error running getAstros")
        log(str(e))
        if debug:
            print("Error running getAstros")
            print(str(e))



#ISS location helper function - does the API calls
def getISS():
    
    try:
        url = "http://api.open-notify.org/iss-now.json"
        with urllib.request.urlopen(url) as surl:
                
            data = json.loads(surl.read().decode())
            if data['message'] == "success":
                lat = data["iss_position"]["latitude"]
                lon = data["iss_position"]["longitude"]
                return lat, lon
            else:
                log ("ISS API fail")
                if debug:
                    print("ISS API fail")
                return "api fail"
        
      
    except Exception as e:
        log("Error running getISS")
        log(str(e))
        if debug:
            print("Error running getISS")
            print(str(e))
            


#helper function to log info.
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
        print("Error in logging")
        print(str(e))
             

#base "run" command.
bot.run(discordToken)



