from datetime import date, timedelta
import imageio
import json, requests, sys
import config

def getImagesInfo(date):
    #Get the list of images that DSCOVR took at the given date
    path = config.DSCOVR_API_PATH.format(date=date)
    path = config.DSCOVR_BASE_URL + path

    #return ['epic_1b_20151022005948_00', 'epic_1b_20151022024751_00', 'epic_1b_20151022081200_00', 'epic_1b_20151022100003_00', 'epic_1b_20151022114806_00', 'epic_1b_20151022133609_00', 'epic_1b_20151022152413_00', 'epic_1b_20151022171216_00', 'epic_1b_20151022190018_00']

    imagesList = requests.get(config.DSCOVR_BASE_URL + config.DSCOVR_API_PATH, params={'date':date})
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
    newsList = requests.get(config.GUARDIAN_REQUEST.format(api_key=config.GUARDIAN_APIKEY, date=date))
    jsonData = json.loads(newsList.text)

    results = jsonData['response']['results']
    page = 4242
    headline = {}
    for news in results:
        if int(news['fields']['newspaperPageNumber']) < page:
            headline = news
            page = int(news['fields']['newspaperPageNumber'])

    return headline

def writeCaption():
    #Generate the text of the Tumblr post based on the Guadian Headline
    headline = getGuardianHeadline(date.today().strftime('%Y-%m-%d'))
    post = '<a href="{link}">{headline}</a><br/>{standfirst}<p>And so this happened.</p>'.format(link=headline['webUrl'], headline=headline['fields']['headline'], standfirst=headline['fields']['trailText'])

    return post




#Find the images for yesterday
yesterday = (date.today() - timedelta(1)).strftime('%Y%m%d')

print writeCaption()

#sys.exit()

print "getting images for {date}".format(date=yesterday)
imageData = getImagesInfo(yesterday)
gifFramesArray = downloadImages(imageData, 'png')
print "obtained {x} images".format(x=len(gifFramesArray))

#Generate the gif based on yesterday images
print "generating gif..."
imageio.mimwrite(config.GIF_PATH, gifFramesArray, loop=0, duration=0.6, quantizer='wu', subrectangles=True)
print "gif saved to {gif}".format(gif=config.GIF_PATH)



#get yesterday headline from TheGuardian
#combine the gif and headlines to upload to Tumblr
