# Release v0.7.4 2022-12-17
## Front end
- /launch command now uses Discord's relative times feature

## __Back end__
- None.

# Release v0.7.3 2022-06-06
## Front end
- Updated server_info command to handle large amounts of joined servers

## __Back end__
- Exception handling for too large messages.


# Release v0.7.2 2022-05-30
## Front end
- No changes

## __Back end__
- Tweaked code for use on RPI


# Release v0.7.2 2022-05-16
## Front end
- Migrated to slash commands. Try using / and see what happens!

## __Back end__
- Finalised transition to new library.


# Release v0.7.1 2022-04-14
## Front end
- No changes

## Back end
- Finished transition to disnake.py and slash commands



# Release v0.7.0 2022-02-25
## Front end
- No changes

## Back end
- Starting transition to disnake.py and slash commands



# Release v0.6.1 2022-02-10
## Front end
- Added extra details to info command

## Back end
- Cleaned up planet weather command
- Cleaned up news command



# Release v0.6.0 2022-02-10
## Front end
- Removed astros command as data source was no longer working.
- Fixed mars command, now shows pictures from different cameras.

## Back end
- Begin planning for transition of API's


# Release v0.5.2 2021-08-06
## Front end
- Removed custom prefix command, lots of issues with it. May return in the future.

## Back end
- Cleaned up comments


# Release v0.5.0 2021-07-30
## Front end
- Added custom prefix command (only in Guilds, and only for people with the Administrator permission). Limited to 1 custom prefix
- Added Info command to show links to the GitHub, support Discord server and Top.gg page
- Mars command now shows a random photo from the given camera, instead of the latest photo

## Back end
- Improved checks for API limits
- Astros command now lists people and the craft as an embed instead of text
- PW command returns warning not error when planet is not recognised


# Release v0.4.3 2021-07-08
## Front end
- Added APOD video explanation

# Back end
- Added APOD embedding for videos
- Changed typing method (trigger_typing instead of  with typing) to avoid infinite typing
- Added encoding option to log function to solve charmap error


# Release v0.4.2 2021-07-07
## Front end
- Added admin command for bot owner only

## Back end
- Potentially fixed bug with logging function
- Added invalid command ignoring


# Release v0.4.1 2021-07-04
## Front end
- Removed useless parameters from mars command, now can only see Curiosity photos
- Added new camera option to mars command, now includes mast camera
- Fixed planet weather command

# Back end
- Added error catching to news command, now shows if there is no news for today
- Added error catching to ISS command, now shows if unable to find the ISS
- Added checks to API limits from api.nasa.gov
- Added more vebose logging for error handling
- Added logging for joining/leaving guilds
