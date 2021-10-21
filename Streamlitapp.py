import streamlit as st
from bs4 import BeautifulSoup as bs 
import requests
import urllib.request
import re
import pandas as pd
import numpy as np

from google_play_scraper import app
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
#nltk.download('stopwords')
nltk.download('punkt')
from nltk import FreqDist
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import yagmail

numVideosToAnalyse=10
users_url="https://abhigyanresources.com/vwusers"

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


    #Build 3 series based on Top 3 words by frequency of occurance
    tagSeries1=tagSeries[tagSeries.str.contains(tagWordFrame['Words'].value_counts()[:3].index.tolist()[0].lower())]
    tagSeries2=tagSeries[tagSeries.str.contains(tagWordFrame['Words'].value_counts()[:3].index.tolist()[1].lower())]
    tagSeries3=tagSeries[tagSeries.str.contains(tagWordFrame['Words'].value_counts()[:3].index.tolist()[2].lower())]

    #Get unique list of items from tagSeries1,tagSeries2,tagSeries3
    tagList = pd.Series(tagSeries1.unique().tolist()+tagSeries2.unique().tolist()+tagSeries3.unique().tolist()).unique().tolist()

    
    if(demostatus=='N'):
        tagDisplay=""
        for x in range(len(tagList)):
            tagDisplay=tagList[x]+","+tagDisplay
        tagDisplay=tagDisplay[:-1]

    else:
        tagDisplayDemo=""
        for x in range(3):
            tagDisplayDemo=tagList[x]+","+tagDisplayDemo
        tagDisplayDemo=tagDisplayDemo[:-1]
        


    #Generate video names based from tagList based on index generated randomly
    tagnumber=np.random.randint(0,len(tagList),len(tagList))

    numberOfVideosPossible = len(tagList)//2

    vidName1=0
    vidName2=1
    vidNameList=[]

    for i in range(numberOfVideosPossible):
        vidName=tagList[tagnumber[vidName1]]+"-"+tagList[tagnumber[vidName2]]
        vidNameList.append(vidName.title())
        #st.write(f"{i+1}. {vidName.title()}")
        vidName1+=2
        vidName2+=2

    if(demostatus=='N'):
        st.header("Most Used Words :")
        st.write("Word1 : ",tagWordFrame['Words'].value_counts()[:3].index.tolist()[0]) 
        st.write("Word2 : ",tagWordFrame['Words'].value_counts()[:3].index.tolist()[1]) 
        st.write("Word3 : ",tagWordFrame['Words'].value_counts()[:3].index.tolist()[2])  
    else:
        st.header("Most Used Words :")
        st.write("Word1 : Top Used Word Available In Full Version Only\n") 
        st.write("Word2 : ",tagWordFrame['Words'].value_counts()[:3].index.tolist()[1]) 
        st.write("Word3 : ",tagWordFrame['Words'].value_counts()[:3].index.tolist()[2]) 
       

    st.header("\n\nSuggested Tags : \n")
    if(demostatus=='N'):
        st.write(tagDisplay) 
    else:
        st.write(f"Displaying 3 of total {len(tagList)} tags available\n")
        st.write(tagDisplayDemo)       
    

    st.header("Suggested Video Names\n")
    
    if(demostatus=='N'):
        for i in range(len(vidNameList)):
            st.write(f"{i+1}. {vidNameList[i]}\n")
    else:
        st.write(f"Showing 3 of total {len(vidNameList)} suggested video names available \n")
        for i in range(3):
            st.write(f"{i+1}. {vidNameList[i]}\n")

    st.header("Video Duration :")
    if(demostatus=='N'):
        st.write(avgDuration(3,Duration))
        st.write(avgDuration(numVideoIds,Duration))
    else:
        st.write(avgDuration(3,Duration))
        st.write(f"\n Average of top {numVideoIds} videos is available in full version only.")
        st.write("\n\nTo get complete details upgrade to 'Full' version today.")
        st.header("[Click Here To Get Full Version](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=FLA5QGCKTZJSN)")



    st.title("\n\n Special Note ( For Windows Users) \n")
    st.write(" If you are a windows users, then this is special section for you.\n")
    st.write(" Introducing smart software 'Top Search'.\n")
    st.write(" Here 10 videos were analysed. But, 'Top Search' will analyse 20 videos and also generate videos for you.")
    st.write("It will generate 2 regular videos and 5 shorts videos with just 1 click. \n")
    st.header(" Watch the video for details \n")
    st.write("[Click Here To Download & Try Free Demo](https://abhigyanresources.com/top-search/)")
    st.video('https://www.youtube.com/watch?v=vQSAkXcEvOw')

    st.header("[Click Here To Download](https://abhigyanresources.com/top-search/)")


def validateUser(user_email):
        emaillist=[]
        demostatus = 'N'
        if user_email.lower() =="demo":
            demostatus = 'Y'

        if demostatus == 'N':
            page = requests.get(users_url)
            soupUserContent = bs(page.content, 'html.parser')
            for i in range(2,(len(soupUserContent.find_all('p'))-1)):
                emaillist.append((str(soupUserContent.find_all('p')[i]).rstrip("</p>")).lstrip("<p>")) 

        if ((user_email in emaillist) or (demostatus=='Y')):
            if demostatus == 'Y':
                st.header("Demo Activated")
                mainSearch(search_term,"Y")
            else:
                st.header("Email id Validated")
                mainSearch(search_term,"N")
        else:
            st.title("Invalid email id. Check and try again.")

def gplayDetails(app_url):

    #app_url="https://play.google.com/store/apps/details?id=com.techniquesandtips.berich&hl=en&gl=us"
    if app_url.find("&") == -1:
        app_id=app_url[app_url.find("=")+1:]
    else:
        app_id=app_url[app_url.find("=")+1:app_url.find("&")]


    stop_words = stopwords.words('english')

    result = app(
        app_id,
        #'com.parakeetsaspets.budgiebirdcare',
        lang='en', # defaults to 'en'
        country='us' # defaults to 'us'
    )

    st.title("App Details :")
    st.write("\nTitle :", result['title'])
    description_sentences=result['description']
    words=""
    description_words=""
    words=word_tokenize(description_sentences)
    description_words = [word for word in words if word not in (stop_words)]

    fd=FreqDist()
    for word in description_words:
        if(word not in ("." , ",","’","!")):
            fd[word.lower()]+=1
    st.header("\nTop 5 Most Used Words:")    
    #fd.most_common(5)
    for i in range(5):
        st.write( f"{i+1}. ", fd.most_common(5)[i][0],"-",fd.most_common(5)[i][1],", Density :" ,fd.most_common(5)[i][1]*100/len(words))
    st.header("\n App Details:")    
    st.write("\nTitle Length :",len(result['title']))
    st.write("\nSummary Length :",len(result['summary']))
    st.write("\nDescription Length :",len(result['description']))
    st.write("\nInstalls :",result['installs'])
    st.write("\nVideo in store listing:",result['video'])
    st.write("\nNumber of Screenshots :",len(result['screenshots']))
    st.write("\nContains Ads:",result['containsAds'])
    #st.write("\nDeveloper Email:",result['developerEmail'])
    st.write("\nNumber of Rating:",result['ratings'])
    st.write("\nNumber of Reviews:",result['reviews'])
    st.write("\nAverage Score:",result['score'])
    st.write("\nNumber of Comments:",len(result['comments']))

    st.header("\n\nLatest Comment Analysis")
    sid_obj = SentimentIntensityAnalyzer()
    pos_num=0
    neu_num=0
    neg_num=0

    for i in range(len(result['comments'])):
        sentiment_dict = sid_obj.polarity_scores(result['comments'][i])
        #st.write("\n\nComment :", result['comments'][i] ) 
        #st.write("Overall sentiment dictionary is : ", sentiment_dict)
        #st.write("Sentence Overall Rated As", end = " ")
     
        # decide sentiment as positive, negative and neutral
        if sentiment_dict['compound'] >= 0.05 :
            #st.write("Positive")
            pos_num+=1
     
        elif sentiment_dict['compound'] <= - 0.05 :
            #st.write("Negative")
            neg_num+=1
     
        else :
            #st.write("Neutral")
            neu_num+=1
            
    st.write("\nTotal Comments: ",len(result['comments']))
    st.write("Total Positive:",pos_num )
    st.write("Total Negative: ",neg_num)
    st.write("Total Neutral: ",neu_num)


    st.title("\n\nSummary")  

    if(fd.most_common(5)[0][1]*100/len(words) <5.0 or fd.most_common(5)[1][1]*100/len(words) < 5.0 ):
        st.header("Keyword Density Of Top Words:")
        st.write("Density of one or both of your top 2 words is less than 5%")
        st.write("Try to keep a density of more than 5 for top 2 words.")
        st.write("This will help google understand the main topic of your app and rank accordingly.")
        st.write("But, donot overdo it by increasing the density beyond 6%") 

    if(len(result['description']) < 3900 ):
        st.header("Length Of Description")
        st.write("Available Limit For Description: 4000")
        st.write("You are using: ", len(result['description']))
        st.write("So, you are wasting available space.")
        st.write("A detailed description will help understand google understand and rank your app better.")
        st.write("\n Note:- In Short Description include a call to action or a strong reason why someone should download your app.")   

    if(result['video'] == None ):
        st.header("Video In Store Listing")
        st.write("You must include a video in play store listing.") 
        st.write("Not just normal video but animated video describing your app and why it should be downloaded.") 
        st.write("Keep it short and to the point.")

    if neg_num > 0:
        st.header("Comments/Reviews")
        if neg_num > pos_num :
            st.write("You have more negative reviews than positive.\nWork on elliminating negative reviews for better ranking and feedback.")
        else:
            st.write("You have more positive comments but still there are few negative comments.")
        st.write("Negative comments impacts downloads.\nAre you doing something to deal with it?")

    if result['score'] < 4.5:
        st.header("Rating Score")
        st.write(f"You have a score of {result['score']}. Work of increasing it to above 4.5 ")

    st.header("\n\nHow we can help you.")     
    #st.write("1. We can write a better description for your app.")
    st.write("1. Create 2 special animated video for your app with male/female voice. You can use any of these in play store.")
    st.write("2. Let you know about a special method to elliminate negative reviews and get more positive reviews.")
    st.header("[Click Here To Contact Us](https://abhigyandms.com/contact-form/)")

#st.title('Generate Video Details')
#form = st.form(key='my-form')
#user_email = form.text_input('Enter registered email :')
#search_term = form.text_input('Enter the search term :')
#submit = form.form_submit_button('Submit')
#st.write("Note:- Enter 'Demo' in registered emailid field To Activate Demo Version")
#st.header('Click Submit Button To Start')


col1, col2 = st.columns(2)

with col1:
    st.header('Generate Youtube Video Details')
    form = st.form(key='youtube-form')
    #user_email = form.text_input('Enter your email :')
    search_term = form.text_input('Enter the search term :')
    submit_youtube = form.form_submit_button('Submit')
    #st.write("Note:- Enter 'Demo' in registered emailid field To Activate Demo Version")
    


with col2:
    st.header('Generate Google Play Details')
    form_gplay = st.form(key='form_gplay')
    #user_email_gplay = form_gplay.text_input('Enter your email :')
    app_url = form_gplay.text_input('Enter app url :')
    #search_term = form.text_input('Enter the search term :')
    submit_gplay = form_gplay.form_submit_button('Submit')
    #st.write("Note:- Enter 'Demo' in registered emailid field To Activate Demo Version")
    #st.write('Click Submit Button To Start')
st.header('Click Submit Button To Start')
#st.write('Note:- Your email is safe and will not be shared with third parties or sold anytime.')

if submit_youtube:
    if search_term=="":# or user_email=="":
        #st.title("Email and Search Term cannot be blank")
        st.title("Search Term cannot be blank")
    else:
        #validateUser(user_email) 
        mainSearch(search_term,"N")  
    
if submit_gplay:
    if app_url=="": #or user_email_gplay=="":
        #st.title("Email and App URL cannot be blank")
        st.title("App URL cannot be blank")
    else:
        gplayDetails(app_url)

    
       
