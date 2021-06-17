import discord, requests, urllib, json
from discord.ext import commands
from spaceBotConfig import discordPrefix, fileLog
from spaceBotTokens import discordToken, NASAApiKey
from datetime import datetime
import os.path

bot = commands.Bot(command_prefix=commands.when_mentioned_or(discordPrefix))




@bot.event
async def on_ready():
    log("Logged in as {}, prefix {}".format(bot.user, discordPrefix))
    print("Logged in as {}, prefix {}".format(bot.user, discordPrefix))



@bot.command(name="iss", help="Shows current location of the International Space Station", brief="Finds the ISS")
async def commandISS(ctx):
    if not ctx.author.bot:
        log("{} used ISS command".format(ctx.author))
        await ctx.channel.send("The ISS is in space, dummy!")
        iss = getISS()
        lat = iss[0]
        lon = iss[1]
        response = "Current position: " + lat + ", " + lon
        await ctx.channel.send(response)



@bot.command(name="apod", help="Shows NASA's Astronomy Picture Of the Day", brief="Shows a cool space picture")
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
                             
                            await ctx.channel.send("Today's Astronomy Picture Of the Day is a video.")
                            await ctx.channel.send(d['url'])
                            jsonFile.close()
                            return

                        
                        elif d['mediaType'] == "image":
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
        print(str(e))
        return



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
        print(str(e))
        return


bot.run(discordToken)



