import feedparser, disnake, logging
from datetime import datetime
from modules.module_config import news_url


log = logging.getLogger(__name__)


def get_news():

    """Returns 10 items of space related news.
   
    Parameters
    ----------
    None

    returns
    ----------
        todays_news: :class:`disnake.Embed` | :class:`int`
            A disnake Embed object containing 10 news articles as titles and links. 0 if there was an error.
        error_message: :class:`str` | :class:`int`
            The error/exception message if there is one. 0 if no error occurred.
    """

    try:

        today = datetime.now()
        today_year = int(today.strftime("%Y"))
        today_month = int(today.strftime("%m"))
        today_date = int(today.strftime("%d"))
        string_today = today.strftime("%Y-%m-%d")
        added_articles = 0        
        avail_articles = 0

        newsfeed = feedparser.parse(news_url)


    except Exception as e:
        error_message = f"Failed to get_news. {e}"
        log.exception(f"module_news - get_news - Failed to get_news. {e}")
        return (0, error_message)


    todays_news = disnake.Embed(title=f"Space news for {string_today}")
    todays_news.set_footer(text="News courtesy of www.space.com")
 
    
    for entry in newsfeed.entries:
        #only get today's news.

        if entry.published_parsed[0] == today_year and entry.published_parsed[1] == today_month and entry.published_parsed[2] == today_date:
            avail_articles += 1

    log.debug(f"module_news - get_news - there are {avail_articles} articles for today.")

    while added_articles < 10 and added_articles < avail_articles:
        for entry in newsfeed.entries:
            if entry.published_parsed[0] == today_year and entry.published_parsed[1] == today_month and entry.published_parsed[2] == today_date:

            #loop through all articles, and add to embed.
            #only add while we have less than 10 articles, and only loop through avail_articles number of stories, because
            #   there may not be 10 stories for today.
            
                todays_news.add_field(name=entry.title, value=entry.link, inline=False)
                added_articles += 1


        return (todays_news, 0)
                    
        
    #check if fields list is empty (implying we have no news for today)
    if not todays_news.fields or avail_articles == 0:
        #no news for today.
        error_message = "No news to be found today."
        log.warning(f"module_news - get_news - no news found today")
        return (0, error_message)
