import streamlit as st
from bs4 import BeautifulSoup as bs 
import requests
import urllib.request
import re
import pandas as pd
import numpy as np

numVideosToAnalyse=10

def video_details(video_id):     
    
    result=""
    
    video_url = "https://www.youtube.com/watch?v=" + video_id
    video_url_data = requests.get(video_url)
    
    soup = bs(video_url_data.content, 'html.parser')    
    #title=soup.find("meta", itemprop="name")['content']
    #views=soup.find("meta", itemprop="interactionCount")['content']
    #description=soup.find("meta", itemprop="description")['content']
    #datePublished=soup.find("meta", itemprop="datePublished")['content']
    duration=soup.find("meta", itemprop="duration")['content']
    tags=', '.join([ meta.attrs.get("content") for meta in soup.find_all("meta", {"property": "og:video:tag"}) ])
    
    #result=[title,views,description,datePublished,duration,tags]
    result=[duration,tags]
    
    return result

def avgDuration(numVideos,Duration):
    totalTime=0
    for x in range(numVideos):
        time=((Duration[x].lstrip('PT')).rstrip('S')).replace('M',',').split(",")
        totalTime=totalTime+int(time[0])*60+int(time[1])
    avgTime = totalTime//numVideos
    avgMinutes = avgTime//60
    avgSeconds = avgTime%60
    duration = f"Average of top {numVideos} videos is : {avgMinutes} Min {avgSeconds} Sec"
    return duration

    
def mainSearch(searchTerm,demostatus):    

    searchTerm_filehelp=searchTerm.replace(" ","_")
    #st.write(searchTerm)
    
    #st.write(demostatus)
    
    #Title=[]
    #Views=[]
    #Description=[]
    #DatePublished=[]
    Duration=[]
    Tags=[] 
    
    searchQuery="https://www.youtube.com/results?search_query="+(searchTerm.replace("""#""","")).replace(" ","+") 
    #st.write(searchQuery)
    
    html = urllib.request.urlopen(searchQuery)
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    videoDetailList=[]
    
    numVideoIds=numVideosToAnalyse
    if len(video_ids) < numVideosToAnalyse :
        numVideoIds=len(video_ids)
    #st.write("Number of videos to analyse :",numVideoIds)
    
    for x in range(numVideoIds):
        st.write("Analyzing Video ",x+1," of ",numVideoIds,"... ")
        videoDetailList=video_details(video_ids[x])

        #Title.append(videoDetailList[0])
        #Views.append(videoDetailList[1])
        #Description.append(videoDetailList[2])
        #DatePublished.append(videoDetailList[3])
        #Duration.append(videoDetailList[4])
        #Tags.append(videoDetailList[5])
        
        Duration.append(videoDetailList[0])
        Tags.append(videoDetailList[1])
        
    st.title('Video Details :\n')   
    #tagSeries = pd.Series(Tags[0].split (','))

    #Combine the tags for analysis
    strTags=""
    tagWords=""
    for x in range(len(Tags)):
        strTags=strTags+((Tags[x].lower()).encode("ascii", "ignore")).decode()
        
    #Will split tags to individual words
    tagWords=strTags.replace(',','').split(' ')  
    #Will split all tags to different items 
    tagSeries = pd.Series(strTags.split (','))   

    tagWordFrame = pd.DataFrame(tagWords,columns=['Words'])
    st.header("Most Used Words :")
    st.write("Word1 : ",tagWordFrame['Words'].value_counts()[:3].index.tolist()[0]) 
    st.write("Word2 : ",tagWordFrame['Words'].value_counts()[:3].index.tolist()[1]) 
    st.write("Word3 : ",tagWordFrame['Words'].value_counts()[:3].index.tolist()[2]) 

    #Build 3 series based on Top 3 words by frequency of occurance
    tagSeries1=tagSeries[tagSeries.str.contains(tagWordFrame['Words'].value_counts()[:3].index.tolist()[0].lower())]
    tagSeries2=tagSeries[tagSeries.str.contains(tagWordFrame['Words'].value_counts()[:3].index.tolist()[1].lower())]
    tagSeries3=tagSeries[tagSeries.str.contains(tagWordFrame['Words'].value_counts()[:3].index.tolist()[2].lower())]

    #Get unique list of items from tagSeries1,tagSeries2,tagSeries3
    tagList = pd.Series(tagSeries1.unique().tolist()+tagSeries2.unique().tolist()+tagSeries3.unique().tolist()).unique().tolist()
    st.header("Suggested Tags : ")
    
    if(demostatus=='N'):
        tagDisplay=""
        for x in range(len(tagList)):
            tagDisplay=tagList[x]+","+tagDisplay
        tagDisplay=tagDisplay[:-1]
        st.write(tagDisplay)
    else:
        tagDisplayDemo=""
        for x in range(3):
            tagDisplayDemo=tagList[x]+","+tagDisplayDemo
        tagDisplayDemo=tagDisplayDemo[:-1]
        st.write(tagDisplayDemo)


    #Generate video names based from tagList based on index generated randomly
    tagnumber=np.random.randint(0,len(tagList),len(tagList))

    numberOfVideosPossible = len(tagList)//2

    vidName1=0
    vidName2=1
    vidNameList=[]
    st.header("Suggested Video Names\n")
    for i in range(numberOfVideosPossible):
        vidName=tagList[tagnumber[vidName1]]+"-"+tagList[tagnumber[vidName2]]
        vidNameList.append(vidName.title())
        st.write(f"{i+1}. {vidName.title()}")
        vidName1+=2
        vidName2+=2



    st.header("Video Duration :")
    st.write(avgDuration(3,Duration))
    st.write(avgDuration(numVideoIds,Duration))

    
    
    #st.title("\n\n Special Note : \n")
    #st.write(" If you are a windows users, then this is special section for you.\n")
    #st.write(" Introducing smart software 'Top Search'.\n")
    #st.write(" Here 5 videos were analysed. But, 'Top Search' will analyse 20 videos and also generate videos for you.")
    #st.write("It will generate 2 regular videos and 5 shorts videos with just 1 click. \n")
    #st.header(" Watch the video for details \n")
    #st.write("[Click Here To Download & Try Free Demo](https://abhigyanresources.com/top-search/)")
    #st.video('https://www.youtube.com/watch?v=vQSAkXcEvOw')

    #st.header("[Click Here To Download](https://abhigyanresources.com/top-search/)")
    

hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>

"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

#Render the page 
st.title('Generate Video Details')
form = st.form(key='my-form')
search_term = form.text_input('Enter the search term :')
submit = form.form_submit_button('Submit')

st.write('Press submit to start')




if submit:
    st.write(f'Search Term Is : {search_term}')   
    mainSearch(search_term,"N")
    
    

    
       
