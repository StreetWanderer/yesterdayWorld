from PIL import Image, ImageDraw, ImageFont
from numpy import array
import imageio, pytumblr, requests, tweepy

import json, sys, textwrap, random, re
from datetime import date, timedelta, datetime

import config

def getImagesInfo(date):
    #Get the list of images that DSCOVR took at the given date

    #return ['epic_1b_20151022005948_00', 'epic_1b_20151022024751_00', 'epic_1b_20151022081200_00', 'epic_1b_20151022100003_00', 'epic_1b_20151022114806_00', 'epic_1b_20151022133609_00', 'epic_1b_20151022152413_00', 'epic_1b_20151022171216_00', 'epic_1b_20151022190018_00']

    imagesList = requests.get(config.DSCOVR_BASE_URL + config.DSCOVR_API_PATH, params={'date':date.strftime('%Y%m%d')})
    if imagesList.status_code != requests.codes.ok:
        print "Can't contact EPIC, stopping. HTTP error {code}".format(code=imagesList.status_code)
        return

    jsonImages = json.loads(imagesList.text)

    parsedData = []
    for img in jsonImages:
        parsedData.append(img['image'])

    return parsedData;

def downloadImages(imageNames, format, headline):
    #Download the given DSCOVR images as a byteArray
    imageFrames = []
    if len(headline) > 0:
        title = headline['fields']['headline'].encode('utf_8')
    else:
        title = "Nothing of importance happened"

    for img in imageNames:
        path = config.DSCOVR_BASE_URL + config.DSCOVR_IMG_PATH.format(format=format, image=img)

        image = Image.fromarray(imageio.imread(path))
        image = image.resize((600,600), Image.ANTIALIAS)
        im = writeOnImage(image, title)

        imageFrames.append(array(im))

    return imageFrames

def writeOnImage(image, headline):
    base = image.convert('RGBA')

    txt = Image.new('RGBA', base.size, (255,255,255,0))
    fnt = ImageFont.truetype('./Anonymous.ttf', 20)
    d = ImageDraw.Draw(txt)
    height = base.height - 50
    splitHeadline = textwrap.wrap(headline, 44)
    for line in splitHeadline:
        d.text((10,height), line, font=fnt, fill=(255,255,255,255))
        height = height + 22

    im = Image.alpha_composite(base, txt)

    return im


def getGuardianHeadline(date):
    #Get the frontmost page of world news in the Guardian, paper edition
    newsList = requests.get(config.GUARDIAN_REQUEST.format(api_key=config.GUARDIAN_APIKEY, date=(date).strftime(config.DATE_SHORTFORM)))
    jsonData = json.loads(newsList.text)

    results = jsonData['response']['results']
    page = 4242
    headline = {}
    #[FIXME] Found a case where newspaperPageNumber isn't present (for 8 october 2015)
    for news in results:
        if 'newspaperPageNumber' in news['fields'] and ('trailText' in news['fields'] or 'standfirst' in news['fields']):
            if int(news['fields']['newspaperPageNumber']) < page:
                headline = news
                page = int(news['fields']['newspaperPageNumber'])

    return headline

def writeCaption(date, headline):
    #Generate the text of the Tumblr post based on the Guadian Headline
    #headline = getGuardianHeadline(date + timedelta(1))
    if len(headline) > 0:
        title = headline['fields']['headline'].encode('utf_8')
        if 'trailText' in headline['fields']:
            standfirst = headline['fields']['trailText']
        else:
            standfirst = headline['fields']['standfirst']
        standfirst = standfirst.encode('utf_8')
        webUrl = headline['webUrl']
        #[FIXME] Noticed that trailText can contain html code, it's usually <strong>, do I leave it?
    else:
        title = "Nothing of importance happened"
        standfirst = ""
        webUrl = "#"

    formattedLink = '<a href="{link}">{headline}</a><br/>{standfirst}'.format(link=webUrl, headline=title, standfirst=standfirst)
    caption ="<p>On this great day of {date} {earth}.</p> We note that:<br/>{link}"
    tweet = "On {date} {earth}:"

    earth = random.choice(config.EARTH_METAPHORS)
        # Idea if no data for that date
        #caption ="<p>The world was nowhere to be found on {date}</p>But we can note that:<br/>{link}"
        #tweet = "Yesterday the world was nowhere to be found. {link}"

    caption = caption.format(date=date.strftime(config.DATE_LONGFORM),link=formattedLink, earth=earth)
    tweet = tweet.format(date=date.strftime(config.DATE_LONGFORM), earth=earth)
    tweet = tweet + ' {link}'

    return {'caption':caption, 'tweet':tweet}

def wasAlreadyPosted(date):

    tumblrClient = pytumblr.TumblrRestClient(config.TUMBLR_CONSUMER_KEY,
                                            config.TUMBLR_CONSUMER_SECRET,
                                            config.TUMBLR_OAUTH_TOKEN,
                                            config.TUMBLR_OAUTH_SECRET)
    postList = tumblrClient.posts('yesterdaybot', tag=date.strftime(config.DATE_SHORTFORM))

    if len(postList['posts']) > 0:
        if date.strftime(config.DATE_SHORTFORM) in postList['posts'][0]['tags']:
            return True

    return False

def postToTumblr(gifPath, text, date):
	#create the post on Tumblr.
    tumblrClient = pytumblr.TumblrRestClient(config.TUMBLR_CONSUMER_KEY,
                                            config.TUMBLR_CONSUMER_SECRET,
                                            config.TUMBLR_OAUTH_TOKEN,
                                            config.TUMBLR_OAUTH_SECRET)
    post = tumblrClient.create_photo('yesterdaybot',
                                        state="published",
                                        tags=["space", "yesterday", "world","news", "gif", "earth", date.strftime(config.DATE_SHORTFORM)],
                                        data=gifPath,
                                        caption=text['caption'],
                                        tweet=text['tweet'],
                                        link=config.DSCOVR_BASE_URL+"/#"+date.strftime(config.DATE_SHORTFORM),
                                        )

    if 'id' in post:
        print "Published to Tumblr"
    else:
        print "Error posting to Tumblr!"
        print post
        sys.exit()
    return post

def postToTwitter(gifPath, text, tumblrId):

    auth = tweepy.OAuthHandler(config.TWITTER_CONSUMER_KEY, config.TWITTER_CONSUMER_SECRET)
    auth.set_access_token(config.TWITTER_OAUTH_TOKEN, config.TWITTER_OAUTH_SECRET)

    api = tweepy.API(auth)

    api.update_with_media(filename=gifPath, status=text['tweet'].format(link='http://yesterdaybot.tumblr.com/post/'+tumblrId))
    #api.update_status(status='Hello World')

    print "Published to Twitter"

def getAvailableDates():

    request = requests.get(config.DSCOVR_BASE_URL + config.DSCOVR_API_PATH, params={'dates':''})
    if request.status_code != requests.codes.ok:
        print "Can't contact EPIC, stopping. HTTP error {code}".format(code=request.status_code)
        return

    result = re.search('(\[.*\])', request.text)
    rawList = result.group(0)
    jsonList = json.loads(rawList)

    return jsonList

def lastPostDate():
    tumblrClient = pytumblr.TumblrRestClient(config.TUMBLR_CONSUMER_KEY,
                                            config.TUMBLR_CONSUMER_SECRET,
                                            config.TUMBLR_OAUTH_TOKEN,
                                            config.TUMBLR_OAUTH_SECRET)
    postList = tumblrClient.posts('yesterdaybot')

    datePost = ''
    if len(postList['posts']) > 0:

        for tag in postList['posts'][0]['tags']:
            try:
                datePost = datetime.strptime(tag, "%Y-%m-%d")
            except ValueError:
                continue

    return datePost.strftime(config.DATE_SHORTFORM)


def extractNextDate(date, dateList):

    try:
        #index = dateList.index(datetime.strptime(date, "%Y-%m-%d"))
        index = dateList.index(date)
    except ValueError:
        print "{date} not in list".format(date=date)
        return None

    if index + 1 < len(dateList):
        return dateList[index + 1]
    else:
        return False


dates = getAvailableDates()
lastDate = lastPostDate()
nextDateString = extractNextDate(lastDate, dates)
if not nextDateString:
    print "All was posted, skipping"
    sys.exit()

nextDateImages = datetime.strptime(nextDateString, "%Y-%m-%d")
nextDateHeadline = nextDateImages + timedelta(days=1)

print "getting images for {date}".format(date=nextDateImages)
imageData = getImagesInfo(nextDateImages)
gif = None
if len(imageData) > 0:
    #Get yesterday headline from TheGuardian
    print "obtaining {date} headline from The Guardian".format(date=nextDateHeadline)
    headline = getGuardianHeadline(nextDateHeadline)
    #Download images for yesterday
    print "downloading images from DSCOVR and writing headline"
    gifFramesArray = downloadImages(imageData, 'png', headline)
    print "obtained {x} images".format(x=len(gifFramesArray))
    #Generate the gif based on yesterday images
    print "generating gif..."
    imageio.mimwrite(config.GIF_PATH, gifFramesArray, loop=0, duration=0.6, quantizer='wu', subrectangles=False)
    print "gif saved to {gif}".format(gif=config.GIF_PATH)
    gif = config.GIF_PATH
else:
    print "The world stopped"
    sys.exit()
    #gif = config.GIF_PATH_NODATA
    #Use a gif from Giphy (i.e. "World stopped") as illustration?



print "Writing Tumblr caption"
text = writeCaption(nextDateImages, headline)

print "Posting to Tumblr"
post = postToTumblr(gif, text, nextDateImages)

print "Posting to Twitter"
postToTwitter(gif, text, str(post['id']))
