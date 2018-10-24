import re
import requests as r
import bs4 as bs
import os
from clint.textui import progress
import time


def checkEpisodeNumber(episodeNumber, highest):
    if int(episodeNumber) > int(highest):
        print("Sorry but the latest episode of %s is %s" %
              (animeName, highest))
        return False
    return True


def oneEpisode(episodeNumber, animeEpisodeUrl):
    return animeEpisodeUrl+episodeNumber


def rangeEpisode(firstEpisode, lastEpisode, animeEpisodeUrl):
    for i in range(firstEpisode, lastEpisode+1):
        episodeRangeList.append(animeEpisodeUrl+str(i))


def allEpisodes(highest, animeEpisodeUrl):
    for i in range(1, highest+1):
        allEpisodesList.append(animeEpisodeUrl+str(i))


def getRapidVideoPage(url, episodeNumber):
    page = r.get(url)
    print('In getRapidVideoPage: ', page.status_code)
    soup = bs.BeautifulSoup(page.text, 'lxml')
    for link in soup.find('div', class_="download-anime").find_all("a"):
        getVideoQuality(link.get('href'), episodeNumber)


def getVideoQuality(url, episodeNumber):
    page = r.get(url)
    print('In getVideoQuality: ', page.status_code)
    soup = bs.BeautifulSoup(page.text, 'lxml')
    for link in soup.find('div', class_="content_c_bg").find_all("a"):
        if 'Rapidvideo' in link.text:
            linkLists.append(link.get('href'))
    print('Length is: ', len(linkLists))
    fillEpisodeQuality(linkLists, episodeNumber)


def fillEpisodeQuality(linkLists, episodeNumber):
    for i in linkLists:
        page = r.get(i)
        print('In fillEpisodeQuality', page.status_code)
        if page.status_code is 200:
            soup = bs.BeautifulSoup(page.text, 'lxml')
            for link in soup.find_all("a", id="button-download"):
                qualityOfEpisode[link.text.strip('\n')] = link.get('href')
            break
    downloadEpisodes(qualityOfEpisode, episodeNumber)
    linkLists.clear()


def downloadEpisodes(qualityOfEpisode, episodeNumber):
    global flag, finalVideoQualityChoice
    # print(flag)
    if flag is True:
        print('In which quality you want to download')
        qualityNumber = 1
        for i in qualityOfEpisode.keys():
            print(qualityNumber, i)
            qualityNumber += 1
        print('Enter', end=' ')
        for i in range(1, qualityNumber):
            print(i, end=" ")
        qualityChoice = input()
        if qualityChoice == '1':
            finalVideoQualityChoice = 'Download 480p'
            qualityUrl = qualityOfEpisode['Download 480p']
        elif qualityChoice == '2':
            finalVideoQualityChoice = 'Download 720p'
            qualityUrl = qualityOfEpisode['Download 720p']
        elif qualityChoice == '3':
            finalVideoQualityChoice = 'Download 1080p'
            qualityUrl = qualityOfEpisode['Download 1080p']
        flag = False
    else:
        if finalVideoQualityChoice not in qualityOfEpisode:
            print(finalVideoQualityChoice +
                  " isn't available for this episode, downgrading the quality of episode!")
            finalVideoQualityChoice = 'Download 480p'
        qualityUrl = qualityOfEpisode[finalVideoQualityChoice]
    print(qualityUrl)
    print("Downloading........Check internet usage in Task Manager if you think it isn't:p")

    particularFile = r.get(qualityUrl)
    filePath = os.path.join(myPath, animeName+" "+str(episodeNumber)+'.mp4')
    with open(filePath, 'wb') as file:
        total_length = int(particularFile.headers.get('content-length'))
        for chunk in progress.bar(particularFile.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1):
            if chunk:
                file.write(chunk)
                file.flush()


linkLists = []
qualityOfEpisode = {}
episodeRangeList = []
allEpisodesList = []
flag = True
finalVideoQualityChoice = ''
myPath = "D:\\Anime\\"

parentUrl = "https://www3.gogoanime.in/"
animeEpisodeListUrl = "https://www3.gogoanime.in/category/"

animeName = input("Enter the name of the anime: ")
myPath = os.path.join(myPath, animeName)
if not os.path.isdir(myPath):
    os.makedirs(myPath)
urlFormatName = re.split(
    r'[`\-=~!@#$%^&*()_+\[\]{};\'\\:"|<,./<>? ]', animeName)
# print(urlFormatName)
if len(urlFormatName) > 1:
    if "" in urlFormatName:
        urlFormatName.remove("")

    urlFormatName = "-".join(urlFormatName)
    animeUrl = animeEpisodeListUrl+urlFormatName
    print(animeUrl)
else:
    animeUrl = animeEpisodeListUrl+urlFormatName[0]
    print(animeUrl)

page = r.get(animeUrl)
print('Outside: ', page.status_code)
soup = bs.BeautifulSoup(page.text, 'lxml')
for link in soup.find('div', class_="anime_video_body").find_all("a"):
    highest = link.get('ep_end')

animeEpisodeUrl = animeUrl.replace("/category", "")+'-episode-'
print('What you want to do?')
print('1. Download a specific episode')
print('2. Download a range of episodes')
print('3. Download all episodes')
print('Enter 1, 2 or 3')
choice = input()

if choice == '1':
    episodeNumber = input('Which episode?')
    if checkEpisodeNumber(episodeNumber, highest):
        url = oneEpisode(episodeNumber, animeEpisodeUrl)
        getRapidVideoPage(url, episodeNumber)

elif choice == '2':
    firstEpisode = int(input('From which episode?'))
    lastEpisode = int(input('Till which episode?'))
    if checkEpisodeNumber(lastEpisode, highest):
        rangeEpisode(firstEpisode, lastEpisode, animeEpisodeUrl)
        for i in episodeRangeList:
            getRapidVideoPage(i, firstEpisode)
            firstEpisode += 1

elif choice == '3':
    allEpisodes(int(highest), animeEpisodeUrl)
    completeEpisodeNumber = 1
    for i in allEpisodesList:
        getRapidVideoPage(i, completeEpisodeNumber)
        completeEpisodeNumber += 1

# print(episodeRangeList)

# print(allEpisodesList)


# MP4Upload, Rapidvideo link page
# url = "https://vidstream.co/download?id=MTEwNjk0&typesub=Gogoanime-SUB&title=One+Piece+Episode+858"
# page = r.get(url)
# print(page.status_code)
# soup = bs.BeautifulSoup(page.text, 'lxml')
# for link in soup.find('div', class_="content_c_bg").find_all("a"):
#     if 'Rapidvideo' in link.text:
#         linkLists.append(link.get('href'))


# #Get the quality of episode page

# page = r.get(linkLists[0])
# # print(page.status_code)
# soup = bs.BeautifulSoup(page.text, 'lxml')
# for link in soup.find_all("a", id="button-download"):
#     qualityOfEpisode[link.text.strip('\n')] = link.get('href')


# Downloading part

# print(qualityOfEpisode)
# print('Downloading........')
# print(qualityOfEpisode['Download 480p'])
# particularFile = r.get(qualityOfEpisode['Download 480p'])
# filePath = os.path.join(myPath, 'Episode 858.mp4')
# with open(filePath, 'wb') as file:
#     total_length = int(particularFile.headers.get('content-length'))
#     for chunk in progress.bar(particularFile.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1):
#         if chunk:
#             file.write(chunk)
#             file.flush()
