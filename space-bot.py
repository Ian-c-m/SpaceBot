import logging, disnake, config, tokens, sys, json
import modules.module_news as module_news
import modules.module_iss as module_iss
import modules.module_weather as module_weather
import modules.module_launches as module_launches
import modules.module_astro as module_astro
import modules.module_photos as module_photos
from disnake.ext import commands
from datetime import datetime



bot = commands.InteractionBot(test_guilds=[config.test_guild_id])
#bot = commands.InteractionBot()

#########################################################################################
#    STARTUP FUNCTIONS BELOW

#sets up logging using the standard logging library. Configure the level in the config.py file.
def setup_logging():
    try:
        logging.basicConfig(
            format = "%(asctime)s %(levelname)-8s %(message)s",
            filename=config.log_file,
            encoding="utf-8",
            filemode=config.logging_filemode,
            level = config.logging_level,
            datefmt="%Y-%m-%d %H:%M:%S")
        logging.info("-----------")
        

    except Exception as e:
        print(f"ERROR - failed to setup logging - {e}")
        sys.exit()



#########################################################################################
#    EVENT FUNCTIONS BELOW


#Alerts once the bot is ready to receive commands
@bot.event
async def on_ready():
    now = datetime.now()
    now = now.strftime("%Y-%m-%d %H:%M:%S")
    try:
        
        game = disnake.Game(config.status)
        await bot.change_presence(status = disnake.Status.online, activity = game)
        logging.info(f"{config.bot_name} ready.")
        #print(f"{config.bot_name} ready.")
        

    except Exception as e:
        logging.warning(f"Failed to set status correctly. {e}")


#When the bot gets invited to a guild
@bot.event
async def on_guild_join(guild):
    logging.info(f"Joined {guild.name}.")

#When the bot gets removed (kicked, banned, left etc) from a guild
@bot.event
async def on_guild_remove(guild):
    logging.info(f"Left {guild.name}.")




#########################################################################################
#    COMMAND FUNCTIONS BELOW


@bot.slash_command(description="Gives top ten space news stories.")
async def news(
    inter: disnake.ApplicationCommandInteraction,
    hidden: bool = commands.Param(default = False, description = "Whether to hide this from others or not.")
    ):

    #record who used the command
    logging.info(f"{inter.author} used the news command.")

    #show that we are doing something as command might be slow to respond.
    await inter.channel.trigger_typing()

    #get the news
    news = module_news.get_news()

    if news[0] == 0:
        #there was an error executing the func, so nothing returned.
        #news[1] contains the error message
        logging.warning(news[1])

        await inter.send("Sorry, couldn't get the news at this time.", ephemeral = hidden)
        


    else:
        #returned with some news as an embed object, so reply with the news.
        await inter.send(embed = news[0], ephemeral = hidden)
        



@bot.slash_command(description="Gets the location of the ISS.")
async def iss(
    inter: disnake.ApplicationCommandInteraction, 
    hidden: bool = commands.Param(default = False, description = "Whether to hide this from others or not.")
    ):

    #record who used the command
    logging.info(f"{inter.author} used the iss command.")

    #show that we are doing something as command might be slow to respond.
    await inter.channel.trigger_typing()

    iss_loc = module_iss.get_iss()
    

    if iss_loc[0] == 0:
        #there was an error executing the func, so nothing returned.
        #iss_loc[1] contains the error message
        logging.exception(iss_loc[1])

        await inter.send("Sorry, couldn't find the ISS at this time.", ephemeral = hidden)
        


    else:
        #we got the location of the ISS, so send the map link
        
        #iss_loc has a list of lat and lon
        lat = iss_loc[0][0]
        lon = iss_loc[0][1]
        map_link = f"https://www.google.com/maps/place/{lat},{lon}"

        await inter.send(map_link, ephemeral = hidden)
        




@bot.slash_command(description="Gives the weather a given planet in our solar system.")
async def weather(
    inter: disnake.ApplicationCommandInteraction, 
    planet: module_weather.Planet = commands.Param(default = None, description="Specify a planet to get its weather, or blank for a random planet.", choices = [module_weather.Planet]), 
    hidden: bool = commands.Param(default = False, description = "Whether to hide this from others or not.")
    ):

    #record who used the command
    logging.info(f"{inter.author} used the weather command with {planet} as planet arg.")

    #show that we are doing something as command might be slow to respond.
    await inter.channel.trigger_typing()

    planet_weather = module_weather.get_planet_weather(planet)

    if planet_weather[0] == 0:
        #there was an error running the get_planet_weather() function.
        #planet_weather[1] contains the error message.
        logging.exception(planet_weather[1])
        await inter.send("Sorry, couldn't figure out the weather.", ephemeral = hidden)


    else:
        #succeeded in getting the weather for the planet.
        await inter.send(planet_weather[0], ephemeral = hidden)




@bot.slash_command(description="Gives information about upcoming rocket launches.")
async def launch(
    inter: disnake.ApplicationCommandInteraction,
    #launch_name: str = commands.Param(default = None, description = "Give more info about a specific launch, leave blank for general info."),
    hidden: bool = commands.Param(default = False, description = "Whether to hide this from others or not.")
    ):

    #record who used the command
    logging.info(f"{inter.author} used the launch command.")

    #show that we are doing something as command might be slow to respond.
    await inter.channel.trigger_typing()


    #if launch_name is None:
        #just get the next 5 launches.
    launch = module_launches.get_basic_launch_info()

    """else:
        #get detailed info about the given launch
        launch = module_launches.get_detailed_launch_info(launch_name)"""


    if launch[0] == 0:
        #there was an error running the command
        logging.exception(launch[1])
        await inter.send("Sorry, couldn't get the info.", ephemeral = hidden)
        

    
    else:
        #send the embed with the basic info of the launch(es).
        await inter.send(embed=launch[0], ephemeral = hidden)        
       




@bot.slash_command(description="Astronauts in space")
async def astro(
    inter: disnake.ApplicationCommandInteraction, 
    hidden: bool = commands.Param(default = False, description = "Whether to hide this from others or not.")
    ):

    logging.info(f"{inter.author} used the astro command")
    await inter.channel.trigger_typing()

    astros_info = module_astro.get_astros()

    if astros_info[0] == 0:
        #there was an error
        logging.exception(astros_info[1])
        await inter.send("Sorry, couldn't get the info", ephemeral=hidden)
        
    
    else:
        #no error, so send the embed with the info
        try:
            await inter.send(astros_info[0], ephemeral=hidden)


        except Exception as e:
            await inter.send("Sorry, couldn't get the info", ephemeral=hidden)
            logging.exception(e)




@bot.slash_command(description="Shows a cool space picture.")
async def photos(
    inter: disnake.ApplicationCommandInteraction,
    location: module_photos.Location = commands.Param(description="Either NASA's photo of the day (space), or Curiosity rover's latest photos (Mars)", choices = [module_photos.Location]),
    #hidden: bool = commands.Param(default = False, description = "Whether to hide this from others or not.")
    ):


    logging.info(f"{inter.author} used photos with {location}.")

    #needed as slow response sometimes. Then use inter.edit_original_message to reply.
    await inter.response.defer()

    #the user wants to look at the apod photo
    if location == module_photos.Location.space:        
        
        #updates the photo data
        apod_info = module_photos.get_apod()

        #there was an error
        if apod_info != 0:
            logging.warning(f"Error running get_apod. {apod_info}")
            await inter.edit_original_message(content="Sorry I couldn't get the photo.") 

        else:
            #open the photo data and convert it to an embed
            with open("apod_data.txt", "r") as json_file:
                metadata = json.load(json_file)
                for data in metadata:
                    try:
                        #if the media is a video, send the URL and explanation in an embed. Can't embed an actual video
                        if data['media_type'] == "video":
                            vid_title = data['title']
                            vid_url = data['url']
                            vid_explain = data['explanation']

                            #create the embed to send back to the user
                            embed = disnake.Embed(title=vid_title)
                            embed.add_field(name="Link", value=vid_url)
                            embed.set_footer(text=vid_explain)

                            await inter.edit_original_message(embed=embed)
                                
                            

                        #if the media is an image, then embed it with a title and explanation
                        elif data['media_type'] == "image":
                            pic_title = data['title']
                            extension = data['file_type']
                            
                            apod_file = "apod." + extension

                            image_file = disnake.File(apod_file, filename="image.png")
                            
                            #create the embed to send back to the user
                            embed = disnake.Embed(title=pic_title)                                       
                            embed.set_image(file = image_file)
                            embed.set_footer(text=data['explanation'])
                            
                            
                            try:
                                await inter.edit_original_message(embed=embed)
                            

                            except disnake.HTTPException as e:
                                if e.code == 40005:
                                    logging.info("Couldn't send the image, it was too big.")
                                    #the image we tried to send was too big, so send link instead.

                                    embed = disnake.Embed(title=pic_title)                                    
                                    embed.add_field(name=data['url'], value=data['explanation'])

                                    await inter.edit_original_message(embed=embed)
                                
                                else:
                                    logging.warning(f"Error with photos sending embedded image. {e}")
                                    await inter.edit_original_message(content="Sorry I couldn't get the photo.")                                    


                        #the media type was not a video or an image
                        else:
                            logging.warning(f"Error with photos. Unknown media type. {data['media_type']}")
                            await inter.edit_original_message(content="Sorry I couldn't get the photo.") 


                    #if the meta data file was empty
                    except json.JSONDecodeError:                
                        logging.exception("apoddata.txt was empty.")
                        await inter.edit_original_message(content="Sorry I couldn't get the photo.")  

                    except Exception as e:                
                        logging.exception(e)
                        await inter.edit_original_message(content="Sorry I couldn't get the photo.") 


    #the member wants to look at mars photos.                
    elif location == module_photos.Location.Mars:
        mars_photos = module_photos.get_mars()
        
        #there was an error message passed from the function
        if mars_photos[0] != "" or mars_photos is False:
            logging.warning(mars_photos[0])
            await inter.edit_original_message(content = "Sorry I couldn't get the photo.")
        
        #no error so show photos
        else:
            front_embed = disnake.Embed(title=f"Front Camera of Curiosity on {mars_photos[4]}")
            front_embed.set_image(mars_photos[1])

            rear_embed = disnake.Embed(title=f"Rear Camera of Curiosity on {mars_photos[4]}")
            rear_embed.set_image(mars_photos[2])

            nav_embed = disnake.Embed(title=f"Navigation Camera of Curiosity on {mars_photos[4]}")
            nav_embed.set_image(mars_photos[3])


            await inter.send(embed = front_embed)
            await inter.send(embed = rear_embed)
            await inter.send(embed = nav_embed)


    #the member somehow looked at another location that doesn't exist!?    
    else:
        logging.warning(f"{inter.author} tried to look at location {location}")  
        await inter.send("Sorry, I don't have photos from there.")


#########################################################################################
#    INFO FUNCTIONS BELOW



@bot.slash_command(description="Info about the bot.")
async def info(
    inter: disnake.ApplicationCommandInteraction,
    hidden: bool = commands.Param(default = False, description = "Whether to hide this from others or not.")
    ):

        logging.info(f"{inter.author} checked bot info.")  

        info_embed = disnake.Embed(title=f"{config.bot_name} Info")
        info_embed.add_field(name="Version", value=config.script_version + " - " + config.script_date, inline=True)
        info_embed.add_field(name="Joined servers", value=len(bot.guilds), inline=True)
        info_embed.add_field(name="Discord Support Server", value=config.discord_server, inline=False)
        info_embed.add_field(name="Top.gg page", value=config.topgg, inline=False)
        info_embed.add_field(name="Bot Invite Link", value=config.invite_link_short, inline=False)
        info_embed.add_field(name="Bot Code on Github", value=config.github_link, inline=False)
               
        await inter.send(embed=info_embed, ephemeral=hidden)




#########################################################################################
#    SECRET FUNCTIONS BELOW
    
@bot.slash_command(description="Super Secret")
async def server_info(
    inter: disnake.ApplicationCommandInteraction,
    short: bool = commands.Param(default=True, description="Show only the latest 10 joined servers, or the full info.")
    ):
    
    #only the bot owner can use this command
    if inter.author == bot.owner:   
        
        joined_guilds = []
        guild_count = len(bot.guilds)
        

        for guild in bot.guilds:
            #gather guild info in a tuple in a list(?) so we can sort by joined date in the embed.
            join_date = guild.me.joined_at
            join_date = join_date.strftime("%Y-%m-%d %H:%M:%S")
            joined_guilds.append((join_date, guild.name, guild.member_count))            
        
        #sorting the guilds by join date newest to oldest
        joined_guilds.sort(key = lambda tup: tup[0], reverse=True) # from https://stackoverflow.com/questions/3121979/
        
        
        
        if short == True:
        #only show the 10 most recently joined guilds
            guild_embed = disnake.Embed(title="Joined Server Info")

            for i in range(min(10, guild_count)):
                guild_embed.add_field(name=joined_guilds[i][1], value=f"Joined on {joined_guilds[i][0]}. {joined_guilds[i][2]} members.", inline=False)
            
            guild_embed.set_footer(text=f"{config.bot_name} is in {guild_count} servers.")
            await inter.send(embed=guild_embed, ephemeral=True)

        
        else:
        #show all the guild info in one big message. 2,000 character limit
          
            guild_message = f"**__{config.bot_name} is in {guild_count} servers__** \n\n"
            for guild in joined_guilds:
                guild_message += f"__{guild[1]}__ \n"
                guild_message += f"*Joined on {guild[0]}. {guild[2]} members.* \n\n"
            
            
            try:
                await inter.send(guild_message, ephemeral=True)

            
            except disnake.HTTPException as e:
                if e.code == 50035:
                    #the message we tried to send was more than 2000 characters, so blocked by the API.
                    logging.warning(f"{config.bot_name} is in {guild_count} servers, message length was {len(guild_message)}")
                    await inter.send("I'm so popular, I'm in too many guilds to mention!")
                    

                else:
                    #some other HTTP exception
                    logging.exception(e)
                    await inter.send("Something went wrong, sorry!")
                    
            
            except Exception as e:
                #some other exception
                logging.exception(e)
                await inter.send("Something went wrong, sorry!")
                
          

    else:
        #user was not allowed to use this command.
        logging.info(f"{inter.author} tried to use the server_info command but was not authorised.")
        inter.send("That's not a command, it's a space station.", ephemeral=True)
        return




if __name__ == "__main__":
    setup_logging()
    bot.run(tokens.discord_test_token)
