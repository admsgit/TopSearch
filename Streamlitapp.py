import streamlit as st
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
from bs4 import BeautifulSoup as bs 
import requests
import urllib.request
import re
import pandas as pd
import numpy as np

Title=[]
Views=[]
Description=[]
DatePublished=[]
Duration=[]
Tags=[] 

def video_details(video_id):     
    
    result=""
    
    video_url = "https://www.youtube.com/watch?v=" + video_id
    video_url_data = requests.get(video_url)
    
    soup = bs(video_url_data.content, 'html.parser')    
    title=soup.find("meta", itemprop="name")['content']
    views=soup.find("meta", itemprop="interactionCount")['content']
    description=soup.find("meta", itemprop="description")['content']
    datePublished=soup.find("meta", itemprop="datePublished")['content']
    duration=soup.find("meta", itemprop="duration")['content']
    tags=', '.join([ meta.attrs.get("content") for meta in soup.find_all("meta", {"property": "og:video:tag"}) ])
    
    result=[title,views,description,datePublished,duration,tags]
    
    return result

def avgDuration(numVideos):
    totalTime=0
    for x in range(numVideos):
        time=((Duration[x].lstrip('PT')).rstrip('S')).replace('M',',').split(",")
        totalTime=totalTime+int(time[0])*60+int(time[1])
    avgTime = totalTime//numVideos
    avgMinutes = avgTime//60
    avgSeconds = avgTime%60
    duration = f"Average of top {numVideos} videos is : {avgMinutes} Min {avgSeconds} Sec"
    return duration

st.title('Generate Video Details')
form = st.form(key='my-form')
search_term = form.text_input('Enter the search term :')
submit = form.form_submit_button('Submit')

st.write('Press submit to start')

if submit:
    st.write(f'Search Term Is : {search_term}')

    numberOfVideosRequired = 10#int(input("Enter number of videos required :"))
    html = urllib.request.urlopen("https://www.youtube.com/results?search_query="+search_term.replace(" ","+"))
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    videoDetailList=[]

    numVideoIds=10
    #if len(video_ids) >= 10 :
    #    numVideoIds=10
    #else:
    #    numVideoIds=len(video_ids)

    for x in range(numVideoIds):
        st.write("Analyzing Video ",x+1," of ",numVideoIds,"... ")
        videoDetailList=video_details(video_ids[x])

        Title.append(videoDetailList[0])
        Views.append(videoDetailList[1])
        Description.append(videoDetailList[2])
        DatePublished.append(videoDetailList[3])
        Duration.append(videoDetailList[4])
        Tags.append(videoDetailList[5])

    tagSeries = pd.Series(Tags[0].split (','))
    #print("title : ",Title)
    #print("views : ",Views)
    #print("description : ",Description)
    #print("datePublished : ",DatePublished)
    #print("duration : ",Duration)
    #print("tags : ",Tags)

    #Combine the tags for analysis
    strTags=""
    tagWords=""
    for x in range(len(Tags)):
        strTags=strTags+Tags[x].lower()         
    #Will split tags to individual words
    tagWords=strTags.replace(',','').split(' ')  
    #Will split all tags to different items 
    tagSeries = pd.Series(strTags.split (','))   

    tagWordFrame = pd.DataFrame(tagWords,columns=['Words'])
    #tagWordFrame['Words'].value_counts()[:3].index.tolist()[0]
    #tagWordFrame['Words'].value_counts()[0]
    st.header("Most Used Words :")
    st.write("Word1",tagWordFrame['Words'].value_counts()[:3].index.tolist()[0]) 
    st.write("Word2",tagWordFrame['Words'].value_counts()[:3].index.tolist()[1]) 
    st.write("Word3",tagWordFrame['Words'].value_counts()[:3].index.tolist()[2]) 

    #Build 3 series based on Top 3 words by frequency of occurance
    tagSeries1=tagSeries[tagSeries.str.contains(tagWordFrame['Words'].value_counts()[:3].index.tolist()[0].lower())]
    tagSeries2=tagSeries[tagSeries.str.contains(tagWordFrame['Words'].value_counts()[:3].index.tolist()[1].lower())]
    tagSeries3=tagSeries[tagSeries.str.contains(tagWordFrame['Words'].value_counts()[:3].index.tolist()[2].lower())]

    #Get unique list of items from tagSeries1,tagSeries2,tagSeries3
    tagList = pd.Series(tagSeries1.unique().tolist()+tagSeries2.unique().tolist()+tagSeries3.unique().tolist()).unique().tolist()
    st.header("Suggested Tags : ")
    tagDisplay=""
    for x in range(len(tagList)):
        tagDisplay=tagList[x]+","+tagDisplay
    tagDisplay=tagDisplay[:-1]
    st.write(tagDisplay)


    #Generate video names based from tagList based on index generated randomly
    tagnumber=np.random.randint(0,len(tagList),len(tagList))

    numberOfVideosPossible = len(tagList)//2


    if numberOfVideosPossible < numberOfVideosRequired :
        st.write(f"Only {numberOfVideosPossible} are required for your search term")


    vidName1=0
    vidName2=1
    vidNameList=[]
    st.header("Suggested Video Names\n")
    for i in range(numberOfVideosPossible):
        vidName=tagList[tagnumber[vidName1]]+"-"+tagList[tagnumber[vidName2]]
        vidNameList.append(vidName)
        st.write(f"{i+1}. {vidName}")
        vidName1+=2
        vidName2+=2



    st.header("Video Duration :")
    st.write(avgDuration(3))
    st.write(avgDuration(numVideoIds))
    
    f=open(r"C:\Users\hp\Desktop\YoutubeData\Youtube1.txt",'w')

    f.write("Most Used Words :\n")
    f.write(f"Word1 : {tagWordFrame['Words'].value_counts()[:3].index.tolist()[0]}\n") 
    f.write(f"Word2 : {tagWordFrame['Words'].value_counts()[:3].index.tolist()[1]}\n") 
    f.write(f"Word3 : {tagWordFrame['Words'].value_counts()[:3].index.tolist()[2]}\n") 


    f.write("\n\nSuggested Tags : \n")
    f.writelines(tagDisplay) #list,tuple

    f.write("\n\nSuggested Video Names\n")
    for i in range(len(vidNameList)):
        f.writelines(f"{i+1}. {vidNameList[i]}\n")

    f.write("\n\nVideo Duration :")
    f.write(f"\n {avgDuration(3)}")
    f.write(f"\n {avgDuration(numVideoIds)}")

    f.close()
