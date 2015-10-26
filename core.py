from datetime import date, timedelta
import imageio
import json, requests, sys
import config

def getImagesInfo(date):
    #Get the list of images that DSCOVR took at the given date

    #return ['epic_1b_20151022005948_00', 'epic_1b_20151022024751_00', 'epic_1b_20151022081200_00', 'epic_1b_20151022100003_00', 'epic_1b_20151022114806_00', 'epic_1b_20151022133609_00', 'epic_1b_20151022152413_00', 'epic_1b_20151022171216_00', 'epic_1b_20151022190018_00']

    imagesList = requests.get(config.DSCOVR_BASE_URL + config.DSCOVR_API_PATH, params={'date':date.strftime('%Y%m%d')})
    jsonImages = json.loads(imagesList.text)

    parsedData = []
    for img in jsonImages:
        parsedData.append(img['image'])

    return parsedData;

def downloadImages(imageNames, format):
    #Download the given DSCOVR images as a byteArray
    imageFrames = []
    for img in imageNames:
        path = config.DSCOVR_BASE_URL + config.DSCOVR_IMG_PATH.format(format=format, image=img)
        #path = "http://127.0.0.1:1026/"+img+".png"
        img = imageio.imread(path)
        imageFrames.append(img)

    return imageFrames

def getGuardianHeadline(date):
    #Get the frontmost page of world news in the Guardian, paper edition
    newsList = requests.get(config.GUARDIAN_REQUEST.format(api_key=config.GUARDIAN_APIKEY, date=date.strftime('%Y-%m-%d')))
    jsonData = json.loads(newsList.text)

    results = jsonData['response']['results']
    page = 4242
    headline = {}
    for news in results:
        if int(news['fields']['newspaperPageNumber']) < page:
            headline = news
            page = int(news['fields']['newspaperPageNumber'])

    return headline

def writeCaption(date, hasImages):
    #Generate the text of the Tumblr post based on the Guadian Headline
    headline = getGuardianHeadline(date)
    print headline
    formattedLink = '<a href="{link}">{headline}</a><br/>{standfirst}'.format(link=headline['webUrl'], headline=headline['fields']['headline'], standfirst=headline['fields']['trailText'])
    #[FIXME] Found a case where newspaperPageNumber isn't present (for 8 october 2015)
    #[FIXME] Noticed that trailText can contain html code

    if hasImages:
        caption +="<p>On this great day of {date}</p> We note that:<br/>{link}".format(date=(date - timedelta(1)).strftime('%A %d %B %Y'),link=formattedLink)
        tweet = "Yesterday happened. [URL]"
    else:
        caption +="<p>But the world is nowhere to be found on {date}</p>But we can note that: {link}"
        tweet = "Yesterday the world was nowhere to be found. [URL]"

    return {'caption':caption, 'tweet':tweet}

def postToTumblr(gifPath, text, date, giphyPath):
	#create the post on Tumblr.
	tumblrClient = pytumblr.TumblrRestClient(
				    config.CONSUMER_KEY,
				    config.CONSUMER_SECRET,
				    config.OAUTH_TOKEN,
				    config.OAUTH_SECRET,
					)

	tumblrClient.create_photo('hellospacebot',
							   state="published",
							   tags=["space", "yesterday", "world","news", "gif", "earth", date],
							   data=gifPath,
							   caption=text['caption'],
							   tweet=text['tweet'],
							   link=config.DSCOVR_BASE_URL+"/#"+date,
                               source=giphyPath
							  )

	print "Published to Tumblr"




#Find the images for yesterday
yesterday = (date.today() - timedelta(1))

#yesterday = date.fromtimestamp(1444276800) # 10/8/2015
#imageData = ['epic_1b_20151022005948_00', 'epic_1b_20151022024751_00', 'epic_1b_20151022081200_00', 'epic_1b_20151022100003_00', 'epic_1b_20151022114806_00', 'epic_1b_20151022133609_00', 'epic_1b_20151022152413_00', 'epic_1b_20151022171216_00', 'epic_1b_20151022190018_00']
#if False:
    print "getting images for {date}".format(date=yesterday)
    imageData = getImagesInfo(yesterday)
    gif = None
    giphyPath = None
    if len(imageData) > 0:
        #Download images for yesterday
        gifFramesArray = downloadImages(imageData, 'png')
        print "obtained {x} images".format(x=len(gifFramesArray))
        #Generate the gif based on yesterday images
        print "generating gif..."
        imageio.mimwrite(config.GIF_PATH, gifFramesArray, loop=0, duration=0.6, quantizer='wu', subrectangles=True)
        print "gif saved to {gif}".format(gif=config.GIF_PATH)
        gif = config.GIF_PATH
    else:
        print "The world stopped"
        giphyPath = 'http://i.giphy.com/12KiGLydHEdak8.gif'
        #Use a gif from Giphy (i.e. "World stopped") as illustration?

#Get yesterday headline from TheGuardian
print "obtaining caption text from The Guardian"
text = writeCaption(yesterday, len(imageData) > 0)

print text

#combine the gif and headlines to upload to Tumblr
#postToTumblr(gif, text, yesterday, giphyPath)
