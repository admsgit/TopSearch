import streamlit as st
from bs4 import BeautifulSoup as bs 
import requests
import urllib.request
import re
import webbrowser

import os
import json
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods import media, posts
from wordpress_xmlrpc.compat import xmlrpc_client

from pytrends.request import TrendReq

users_url="https://abhigyanresources.com/vwusers"

def do_post(title,excerpt,content,tags,category):
    #id = user_id
    #password = password
    url = website+r"//xmlrpc.php"
    post_status = 'publish'#'draft'
    wp = Client(url, user_id, password)
    
    post = WordPressPost()
    post.post_status = post_status
    post.title = title
    post.content = content
    post.excerpt = excerpt
    post.terms_names = {
        "post_tag": [tags],
        "category": [category]
    }

    wp.call(posts.NewPost(post))

def video_details(video_id):     
    
    result=""
    
    video_url = "https://www.youtube.com/watch?v=" + video_id
    st.write(video_url)
    video_url_data = requests.get(video_url)
    
    soup = bs(video_url_data.content, 'html.parser')    
    title=soup.find("meta", itemprop="name")['content']
    description=soup.find("meta", itemprop="description")['content']
    tags=', '.join([ meta.attrs.get("content") for meta in soup.find_all("meta", {"property": "og:video:tag"}) ])
    
    result=[title,description,tags]
    
    return result


def mainSearch(demostatus):
    searchwords=[]
    # convert the keywords into a list
    searchwords = keywords.split(',')

    #
    if (len(searchwords)==1 and searchwords[0].lower() == "trends"):
        st.write(f"Trends Section Activated")
        trend_words=[]
        pytrends = TrendReq(hl='en-US', tz=360)
        trend_words_india=pytrends.trending_searches(pn='india')
        for i in range(5):
            trend_words.append((trend_words_india[0][i].encode("ascii", "ignore").decode()).lower())
            
        trend_words_us=pytrends.trending_searches(pn='united_states')
        for i in range(5):
            trend_words.append((trend_words_us[0][i].encode("ascii", "ignore").decode()).lower())
            
        trend_words_uk=pytrends.trending_searches(pn='united_kingdom')
        for i in range(5):
            trend_words.append((trend_words_uk[0][i].encode("ascii", "ignore").decode()).lower())
            
        trend_set=set(trend_words)
        final_trend_words=list(trend_set)
        searchwords = final_trend_words



    #This section will handle the category
    st.write(f"Total Posts : {len(searchwords)}")
    # Run a loop to find videos and post to website for each keyword
    for searchwordNum in range(len(searchwords)):
        searchTerm=""
        searchTerm= searchwords[searchwordNum]
        searchQuery="https://www.youtube.com/results?search_query="+(searchTerm.replace("""#""","")).replace(" ","+") 
        #st.write(searchQuery)
        
        html = urllib.request.urlopen(searchQuery)
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        videoDetailList=[] 
        #st.write(video_ids)
        if len(video_ids)>=1:
            
            st.write(f"{searchwordNum+1}.Posting To Website For : {searchTerm}")        
            #st.write("Starting Post :",videoNumber+1)
            videoDetailList=video_details(video_ids[1])
            Title=""
            Description=""
            Tags=""
            Title=videoDetailList[0].replace(',',' ')
            Description=videoDetailList[1].replace(',',' ')
            Tags=videoDetailList[2]

            if Tags=="":
                Tags = Title

            #st.write('Title :',Title)
            #st.write('Description :',Description)
            #st.write('Tags :',Tags)

            #Select just 4 tags - More will be give error while wordpress post
            tags = Tags.split(',')   
            tagPost=""
            if (len(tags)<=4):
                tagnum = len(tags)
            else:
                tagnum =4

            for i in range(tagnum):
                if(i>0):
                    tagPost = tagPost+","+tags[i]
                else:
                    tagPost = tagPost+tags[i] 

            NewDescription = f'''{Title}<p>
            &nbsp;</p>
            <p>
            <strong>Watch the video to know about {searchTerm}.&nbsp;</strong></p>
            <p>
            <iframe allowfullscreen="" frameborder="0" height="360" src="//www.youtube.com/embed/{video_ids[1]}?rel=0" width="640"></iframe></p>
            <p>
            <br><br>{Description}
            <p>
            <strong style="font-size: 22px;"><a href={affiliate_link} target="_blank">{link_text}&nbsp;</a></strong><br />
            &nbsp;</p>'''
            #st.write('NewDescription :',NewDescription)
            
            do_post(Title,"Watch "+Title,NewDescription,tagPost,"Trending")
            st.write("Post Done")
    st.write("All Posts Completed")


hide_streamlit_style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>

"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 


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
                mainSearch("Y")
            else:
                st.header("Email id Validated")
                mainSearch("N")
        else:
            st.title("Invalid email id. Check and try again.")


#Render the page 
st.title('WP Affiliate Site Builder')
form = st.form(key='my-form')
user_email = form.text_input('Enter registered email :')
#search_term = form.text_input('Enter the search term :')

website=form.text_input("Enter your website : ")
user_id=form.text_input("Enter website userid : ")
password=form.text_input("Enter website password : ")

keywords=form.text_input("Enter keywords - Separate each keyword by comma(,)")
link_text=form.text_input("Enter text for affiliate link : ")
affiliate_link=form.text_input("Enter affilite link : ")

submit = form.form_submit_button('Submit')
st.write("Note:- Enter 'Demo' in registered emailid field To Activate Demo Version")
st.header('Click Submit Button To Start')




if submit:

    if user_email=="" or website=="" or user_id=="" or password=="" or keywords=="" or affiliate_link=="" or link_text=="":
        st.title("Fields cannot be blank")
    else:
        validateUser(user_email)
        
        
        
        

