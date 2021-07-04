# Release v0.4.1 2021-07-04
## Front end
- Removed useless parameters from mars command, now can only see Curiosity photos.
- Added new camera option to mars command, now includes mast camera.
- Fixed planet weather command

# Back end
- Added error catching to news command, now shows if there is no news for today.
- Added error catching to ISS command, now shows if unable to find the ISS.
- Added checks to API limits from api.nasa.gov
- Added more vebose logging for error handling
- Added logging for joining/leaving guilds