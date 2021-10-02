from tkinter import *
from tkinter import messagebox 
from bs4 import BeautifulSoup as bs 
import requests
import urllib.request
import re
import pandas as pd
import numpy as np
import webbrowser
import datetime

import glob
from PIL import Image as imgpil, ImageDraw, ImageFont
import textwrap
import os
import shutil
import random
import cv2



root=Tk()
root.title('Top Search')
root.iconbitmap(r"SysFiles\Icon\icon.ico")
root.geometry('650x550')

#client_id to download images from unsplash
#client_id = 'qflrAeCohMRX-xD3mrUZ_2WMZSLL9Tz5e6IdTvs9kG4'
#Number of pages for image search - each page has 30 images
num_pages=3
images_per_page=30 #Max 30 possible
num_regular_video=2
num_shorts_video=5
numVideosToAnalyse=20
total_images=num_pages*images_per_page

training_url="https://abhigyanresources.com/vwtraining"
fullversion_url="https://abhigyanresources.com/vwfull"
users_url="https://abhigyanresources.com/vwusers"


vidtxt0=["Welcome To This Video","Welcome","Welcome To This Channel"] 
vidtxt1=["Watch till the end to get surprise",
         "See till the end to get surprise",
         "View till the end to get surprise"]
vidtxt2=["Donot skip this short video",
         "Donot forward this short video"]
vidtxt3=["Subscribe to the channel and click the bell icon"]
vidtxtLast=["Click the link in the description for surprise",
             "Visit the link in the description for surprise",
             "See the link in the description for surprise",
             "Click the link in the description for surprise details",
             "Visit the link in the description for surprise details",
             "See the link in the description for details"]


if os.path.isfile(r"SysFiles\VidTxt\vidtxtfile.txt"):
    f_vid_file=open(r"SysFiles\VidTxt\vidtxtfile.txt",'r')
    vidtxt0=f_vid_file.readline()
    vidtxt1=f_vid_file.readline()
    vidtxt2=f_vid_file.readline()
    vidtxt3=f_vid_file.readline()
    vidtxtLast=f_vid_file.readline()
    vidtxt0=((((vidtxt0.lstrip("slide1=")).replace('''"''',""))).strip()).split(",")
    vidtxt1=((((vidtxt1.lstrip("slide3=")).replace('''"''',""))).strip()).split(",")
    vidtxt2=((((vidtxt2.lstrip("slide6=")).replace('''"''',""))).strip()).split(",")
    vidtxt3=((((vidtxt3.lstrip("slide8=")).replace('''"''',""))).strip()).split(",")
    vidtxtLast=((((vidtxtLast.lstrip("slideLast=")).replace('''"''',""))).strip()).split(",")
    f_vid_file.close()

    
#print(vidtxt0)
#print(vidtxt1) 
#print(vidtxt2) 
#print(vidtxt3) 
#print(vidtxtLast) 

#vidTextSlideList is used for making text slides
vidTextSlideList=[vidtxt0,vidtxt1,vidtxt2,vidtxt3,vidtxtLast]

#For Demo Version
Dvidtxt0=["Welcome To This Demo Video","Welcome Demo Slide","Welcome To This Demo Channel"] 
Dvidtxt1=["Watch Demo till the end to get surprise",
         "See Demo till the end to get surprise",
         "View Demo till the end to get surprise"]
Dvidtxt2=["Donot skip this short Demo video",
         "Donot forward this short Demo video"]
Dvidtxt3=["Demo : Subscribe to the channel and click the bell icon"]
DvidtxtLast=["Demo - Click the link in the description for surprise",
             "Demo - Visit the link in the description for surprise",
             "Demo - See the link in the description for surprise",
             "Demo - Click the link in the description for surprise details",
             "Demo - Visit the link in the description for surprise details",
             "Demo - See the link in the description for details"]

#vidTextSlideDemoList is used for making text slides for demo
vidTextSlideDemoList=[Dvidtxt0,Dvidtxt1,Dvidtxt2,Dvidtxt3,DvidtxtLast]





#colourlist is used for text slides- one colour is randomly is selected for each video
colourlist = ['Maroon','Olive','Green','Purple','Teal','Navy','Magenta','Lime','Blue']

#vidImageSlideList is used for image slides
vidImageSlideList=["Subscribe Channel"," "," "," "," "," ","Like the video",
                   "See Link In Description","Click Link In Description"]   


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

    path = "OutputData"
    searchTerm_filehelp=searchTerm.replace(" ","_")
    datetime_filehelp=datetime.datetime.now().strftime("%d%m%y-%H%M%S")
    filename = path+f"\VideoDetails-{searchTerm_filehelp}-{datetime_filehelp}.txt"
    #print(searchTerm)
    if not os.path.exists(path):
        os.makedirs(path)    
    
    #print(path)
    #print(filename)
    #print(demostatus)
    
    #Title=[]
    #Views=[]
    #Description=[]
    #DatePublished=[]
    Duration=[]
    Tags=[] 
    
    searchQuery="https://www.youtube.com/results?search_query="+(searchTerm.replace("""#""","")).replace(" ","+") 
    #print(searchQuery)
    
    html = urllib.request.urlopen(searchQuery)
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    videoDetailList=[]
    
    numVideoIds=numVideosToAnalyse
    if len(video_ids) < numVideosToAnalyse :
        numVideoIds=len(video_ids)
    #print("Number of videos to analyse :",numVideoIds)
    
    for x in range(numVideoIds):
        #print("Analyzing Video ",x+1," of ",numVideoIds,"... ")
        videoDetailList=video_details(video_ids[x])

        #Title.append(videoDetailList[0])
        #Views.append(videoDetailList[1])
        #Description.append(videoDetailList[2])
        #DatePublished.append(videoDetailList[3])
        #Duration.append(videoDetailList[4])
        #Tags.append(videoDetailList[5])
        
        Duration.append(videoDetailList[0])
        Tags.append(videoDetailList[1])
        
        
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
    #print("Most Used Words :")
    #print("Word1",tagWordFrame['Words'].value_counts()[:3].index.tolist()[0]) 
    #print("Word2",tagWordFrame['Words'].value_counts()[:3].index.tolist()[1]) 
    #print("Word3",tagWordFrame['Words'].value_counts()[:3].index.tolist()[2]) 

    #Build 3 series based on Top 3 words by frequency of occurance
    tagSeries1=tagSeries[tagSeries.str.contains(tagWordFrame['Words'].value_counts()[:3].index.tolist()[0].lower())]
    tagSeries2=tagSeries[tagSeries.str.contains(tagWordFrame['Words'].value_counts()[:3].index.tolist()[1].lower())]
    tagSeries3=tagSeries[tagSeries.str.contains(tagWordFrame['Words'].value_counts()[:3].index.tolist()[2].lower())]

    #Get unique list of items from tagSeries1,tagSeries2,tagSeries3
    tagList = pd.Series(tagSeries1.unique().tolist()+tagSeries2.unique().tolist()+tagSeries3.unique().tolist()).unique().tolist()
    #print("Suggested Tags : ")
    
    if(demostatus=='N'):
        tagDisplay=""
        for x in range(len(tagList)):
            tagDisplay=tagList[x]+","+tagDisplay
        tagDisplay=tagDisplay[:-1]
        #print(tagDisplay)
    else:
        tagDisplayDemo=""
        for x in range(3):
            tagDisplayDemo=tagList[x]+","+tagDisplayDemo
        tagDisplayDemo=tagDisplayDemo[:-1]
        #print(tagDisplayDemo)


    #Generate video names based from tagList based on index generated randomly
    tagnumber=np.random.randint(0,len(tagList),len(tagList))

    numberOfVideosPossible = len(tagList)//2

    vidName1=0
    vidName2=1
    vidNameList=[]
    #print("Suggested Video Names\n")
    for i in range(numberOfVideosPossible):
        vidName=tagList[tagnumber[vidName1]]+"-"+tagList[tagnumber[vidName2]]
        vidNameList.append(vidName.title())
        #print(f"{i+1}. {vidName.title()}")
        vidName1+=2
        vidName2+=2



    #print("Video Duration :")
    #print(avgDuration(3,Duration))
    #print(avgDuration(numVideoIds,Duration))

    #print(filename)
    f=open(filename,'w')
    
    if(demostatus=='N'):
        f.write("Most Used Words :\n")
        f.write(f"Word1 : {tagWordFrame['Words'].value_counts()[:3].index.tolist()[0]}\n") 
        f.write(f"Word2 : {tagWordFrame['Words'].value_counts()[:3].index.tolist()[1]}\n") 
        f.write(f"Word3 : {tagWordFrame['Words'].value_counts()[:3].index.tolist()[2]}\n") 
    else:
        f.write("Most Used Words :\n")
        f.write("Word1 : Top Used Word Available In Full Version Only\n") 
        f.write(f"Word2 : {tagWordFrame['Words'].value_counts()[:3].index.tolist()[1]}\n") 
        f.write(f"Word3 : {tagWordFrame['Words'].value_counts()[:3].index.tolist()[2]}\n")        

    f.write("\n\nSuggested Tags : \n")
    if(demostatus=='N'):
        f.writelines(tagDisplay)   
    else:
        f.write(f"Displaying 3 of total {len(tagList)} tags available\n")
        f.writelines(tagDisplayDemo)       
    

    f.write("\n\nSuggested Video Names\n")
    
    if(demostatus=='N'):
        for i in range(len(vidNameList)):
            f.writelines(f"{i+1}. {vidNameList[i]}\n")
    else:
        f.write(f"Showing 3 of total {len(vidNameList)} suggested video names available \n")
        for i in range(3):
            f.writelines(f"{i+1}. {vidNameList[i]}\n")

    f.write("\n\nVideo Duration :")
    if(demostatus=='N'):
        f.write(f"\n {avgDuration(3,Duration)}")
        f.write(f"\n {avgDuration(numVideoIds,Duration)}")
    else:
        f.write(f"\n {avgDuration(3,Duration)}")
        f.write(f"\n Average of top {numVideoIds} videos is available in full version only.")
        f.write("\n\nTo get complete details upgrade to 'Full' version today.")
       
    
    
    f.close()

    # Function mainSearch Ends here

    
 


  
def make_text_slides(colour,typeVid,textimgpath,demostatus):   
    global txt_file_list
    
    #Setting parameters for 'shorts' and 'regular' videos
    if typeVid == "shorts":
        M_W, M_H,cur_h, pd,parawidth,fontsize = 1080,1920,200,10,20,100
    else:
        M_W, M_H,cur_h, pd,parawidth,fontsize = 1280,720,50,10,30,80 
    
    
    #print(M_W, M_H,cur_h, pd,parawidth,fontsize)
    txt_file_list=[]
    for i in range(len(vidTextSlideList)):
        MAX_W, MAX_H = M_W, M_H
        image=imgpil.new('RGB', (MAX_W, MAX_H), (colour))
        image=image.resize((MAX_W, MAX_H))
        
        if(demostatus=='N'):
            astr = vidTextSlideList[i][np.random.randint(0,len(vidTextSlideList[i]))].title()
        else:
            astr = vidTextSlideDemoList[i][np.random.randint(0,len(vidTextSlideList[i]))].title()       

        current_h, pad = cur_h, pd
        para = textwrap.wrap(astr, width=parawidth)
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(r"SysFiles\Font\Lato-Regular.ttf", fontsize)

        for line in para:
            w, h = draw.textsize(line, font=font)
            draw.text(((MAX_W - w) / 2, current_h), line, font=font)
            current_h += h + pad
        txtfilename=textimgpath+r"\img_text"+f"{i}"+".jpg"
        txt_file_list.append(txtfilename)
        image.save(txtfilename)  
  
    
    

def make_image_slides(typeVid,vidimgpath,imgpath):
    
        #Setting parameters for 'shorts' and 'regular' videos
        if typeVid == "shorts":
            M_W, M_H,cur_h, pd,parawidth,fontsize,numImageFiles = 1080,1920,900,10,30,80,15
        else:
            M_W, M_H,cur_h, pd,parawidth,fontsize,numImageFiles = 1280,720,260,10,30,60,30 
        
        
        #print(M_W, M_H,cur_h, pd,parawidth,fontsize,numImageFiles)
        #Select random images files for video
        imgNumber=random.sample(range(1, (num_pages*images_per_page)+1), numImageFiles)
        #print(imgNumber)
        file_list=[]
        for i in imgNumber:
            vidImgfilename = imgpath+"\img"+f"{i}"+".jpg"
            file_list.append(vidImgfilename)

        #Copy the files to video images folder
        for f in file_list:
            shutil.copy(f, vidimgpath)    


        #File Resize Section
        global vid_file_list
        vid_file_list=[]
        vid_file_list = glob.glob(vidimgpath+"\*.jpg")  

        for i in range(len(vid_file_list)):
            image = imgpil.open(vid_file_list[i])
            image=image.convert('RGB')
            image=image.resize((M_W, M_H))
            astr = vidImageSlideList[np.random.randint(0,len(vidImageSlideList))].title()
            current_h, pad = cur_h, pd

            para = textwrap.wrap(astr, width=parawidth)
            MAX_W, MAX_H = M_W, M_H
            draw = ImageDraw.Draw(image)
            font = ImageFont.truetype(r"SysFiles\Font\Lato-Regular.ttf", fontsize) 

            for line in para:
                w, h = draw.textsize(line, font=font)
                draw.text(((MAX_W - w) / 2, current_h), line, font=font)
                current_h += h + pad

            image.save(vid_file_list[i])
            

def make_video(typeVid,demostatus):

    path = "OutputData"
    imgpath = path+"\img"
    textimgpath = imgpath+r"\textImg" 
    vidimgpath=imgpath+r"\vidImg"
  
    if typeVid=="shorts":
        numVideosRequired=num_shorts_video
    else:
        numVideosRequired=num_regular_video
       
    for numVideos in range(0,numVideosRequired):
        coloruse = colourlist[np.random.randint(0,len(colourlist),1)[0]] 
        make_text_slides(coloruse,typeVid,textimgpath,demostatus)
        make_image_slides(typeVid,vidimgpath,imgpath)

        
        vid_file_list=[]
        vid_file_list = glob.glob(vidimgpath+"\*.jpg")          
        
        #Adding text files to image files
        vid_file_list.insert(0,txt_file_list[0])
        vid_file_list.insert(2,txt_file_list[1])
        vid_file_list.insert(5,txt_file_list[2])
        vid_file_list.insert(7,txt_file_list[3])
        vid_file_list.append(txt_file_list[4])

        
        if typeVid=="shorts":
            video = cv2.VideoWriter(path+r"\vid"+f"{numVideos+1}"+"shorts.mp4", 0, 0.5, (1080,1920))
            for time in range(9):
                vid_file_list.append(txt_file_list[4])   
        else:
            video = cv2.VideoWriter(path+r"\vid"+f"{numVideos+1}"+"regular.mp4", 0, 0.5, (1280,720))
            for time in range(300):
                vid_file_list.append(txt_file_list[4])

        for image in vid_file_list:
            video.write(cv2.imread(image))

        # Deallocating memories taken for window creation
        cv2.destroyAllWindows()
        video.release() # releasing the video generated                
        
        #Delete image slides
        for f in set(vid_file_list):
            os.remove(f)
        #Delete text slides    
        text_img_file_list = glob.glob(textimgpath+"\*.jpg") 
        for f in text_img_file_list:
            os.remove(f) 
         



        
def download_images(searchTermEntry,client_id):

        imgsearchTerm = searchTermEntry
        #print(f"Client Id: {client_id}")
        path = "OutputData"
        imgpath = path+"\img"
        textimgpath = imgpath+r"\textImg" 
        vidimgpath=imgpath+r"\vidImg"
        errmsg=""
       
        if not os.path.exists(vidimgpath):
            os.makedirs(vidimgpath)
        if not os.path.exists(textimgpath):
            os.makedirs(textimgpath)

        #Clear the video image folder at the start    
        vid_file_list = glob.glob(vidimgpath+"\*.jpg") 
        for f in vid_file_list:
            os.remove(f) 
        vid_file_list=[]

        #Clear the image folder at the start  
        img_file_list = glob.glob(imgpath+"\*.jpg") 
        for f in img_file_list:
            os.remove(f) 

        #Clear the text image folder at the start  
        text_img_file_list = glob.glob(textimgpath+"\*.jpg") 
        for f in text_img_file_list:
            os.remove(f) 
            
        #Initially do a query to validate client_id and get number of available pages
        unsplash_url=f"https://api.unsplash.com/search/photos?query={imgsearchTerm}&page=1&per_page={images_per_page}&client_id={client_id}"
        r1=requests.get(unsplash_url)
        ims1 = r1.json()
        
        if not 'errors' in ims1:
            search_page_number = random.sample(range(1, ims1['total_pages']), num_pages)
            #img_num_help is used for generating image file names
            img_num_help=0
            
            for pages in search_page_number:
                unsplash_url=f"https://api.unsplash.com/search/photos?query={imgsearchTerm}&page={pages}&per_page={images_per_page}&client_id={client_id}"
                r=requests.get(unsplash_url)
                ims = r.json()
                if not 'errors' in ims:        
                    opener=urllib.request.build_opener()
                    opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
                    urllib.request.install_opener(opener)

                    for i in range(len(ims['results'])):
                        # setting filename and image URL
                        filename = imgpath+"\img"+f"{(img_num_help*images_per_page)+i+1}"+".jpg"
                        image_url = ims['results'][i]['urls']['regular']

                        # calling urlretrieve function to get resource
                        urllib.request.urlretrieve(image_url, filename)
                    img_num_help+=1                    
                else:
                    errmsg=ims['errors']
                    messagebox.showinfo("Image Error","Error downloading images. Check client_id and try after some time.")
            
        else:
            errmsg=ims1['errors']
            messagebox.showinfo("Image Error","Error downloading images. Check client_id and try after some time.")
        return errmsg
        
        
def generateVideo(searchTermEntry,client_id,demostatus):

    path = "OutputData"
    imgpath = path+"\img"    
    if searchTermEntry=="":
            messagebox.showinfo("Warning","Enter Search Term")
    else:
        if client_id=="":
            messagebox.showinfo("Warning","Enter Unsplash Client Id")
        else:  
            messagebox.showinfo("Video Generation",f"This will download {total_images} images and generate {num_regular_video} regular videos and {num_shorts_video} shorts videos. It should take 5-10 mintues. This will do your week's work in just few minutes. So, click 'OK' to start. ")
            #Write the client_id to file for future, so that it is populated automatically.
            if not os.path.exists(r"SysFiles\ClientId"):
                os.makedirs(r"SysFiles\ClientId")    
            f_client_id=open(r"SysFiles\ClientId\client_id.txt",'w')
            f_client_id.write(client_id)
            f_client_id.close()
            
            #Download images for video generation
            errmsg=download_images(searchTermEntry,client_id)
            
            #Execute make_video only if images downloaded successfully
            if errmsg=="":
                #call make_video to make regular videos
                make_video("regular",demostatus)

                #call make_video to make shorts videos
                make_video("shorts",demostatus)
                messagebox.showinfo("Success","Video generation completed. See the output folder.")
            
            #Remove all downloaded images after video generation
            img_file_list = glob.glob(imgpath+"\*.jpg") 
            for f in img_file_list:
                os.remove(f) 
            
    
def startSearch(searchTermEntry,demostatus):
    if searchTermEntry=="":
            messagebox.showinfo("Warning","Enter Search Term")
    else:    
        messagebox.showinfo("Video Details Generation",f"Top {numVideosToAnalyse} videos will be analysed for '{searchTermEntry}' to generate video details. This should take less than 2 minutes. Click OK to continue. ")
        mainSearch(searchTermEntry,demostatus)
        messagebox.showinfo("Success","Your file is generated. See the output folder")
    
def validateUser():

    emailid = emailIdEntry.get()
    if emailid=="":
            messagebox.showinfo("Warning","Enter Email id")
    else:
        emaillist=[]
        demostatus = 'N'
        if emailid.lower() =="demo":
            demostatus = 'Y'

        if demostatus == 'N':
            page = requests.get(users_url)
            soupUserContent = bs(page.content, 'html.parser')
            for i in range(2,(len(soupUserContent.find_all('p'))-1)):
                emaillist.append((str(soupUserContent.find_all('p')[i]).rstrip("</p>")).lstrip("<p>")) 

        if ((emailid in emaillist) or (demostatus=='Y')):

            for widgets in UserFrame.winfo_children():
                widgets.destroy()
            if demostatus == 'N':  
                UserLabel=Label(UserFrame,text="Email Id Validated. Start Using The Software Now")
                UserLabel.pack() 
            else:
                UserLabel=Label(UserFrame,text="Demo Activated. Start Using The Software Now")
                UserLabel.pack()    


            searchFrame = LabelFrame(root, text="Enter Search Term", padx=5, pady=5)
            searchFrame.pack(padx=10, pady=10)

            searchTermEntry=Entry(searchFrame,width=50)
            searchTermEntry.pack()

            imageApiFrame = LabelFrame(root, text="Enter Unsplash Client Id", padx=5, pady=5)
            imageApiFrame.pack(padx=10, pady=10)

            if os.path.isfile(r"SysFiles\ClientId\client_id.txt"):
                f_client_id=open(r"SysFiles\ClientId\client_id.txt",'r')
                imageApiEntry_data = f_client_id.readline()
                f_client_id.close()
                         
            imageApiEntry=Entry(imageApiFrame,width=50)
            imageApiEntry.pack()
            imageApiEntry.insert(0,imageApiEntry_data)


            startButtonFrame = LabelFrame(root,text="Get Video Details", padx=5, pady=5)
            startButtonFrame.pack(padx=10, pady=10)

            vidFrame = LabelFrame(root, text="Start Video Generation", padx=5, pady=5)
            vidFrame.pack(padx=10, pady=20)

            startSearchButton = Button(startButtonFrame, text="Generate Video Details",command=lambda: startSearch(searchTermEntry.get(),demostatus))    
            startSearchButton.pack()
            generateVideoButton = Button(vidFrame, text="Generate Video",command=lambda: generateVideo(searchTermEntry.get(),imageApiEntry.get(),demostatus)  )    
            generateVideoButton.pack()

            if demostatus=='Y':
                UpgradeLabel=Label(root,text="Upgrade to full version. Click 'Register' button below for details. ")
                UpgradeLabel.pack() 
                messageheading="Payment Information"
                messagetext="After you click 'OK' you will be taken to paypal for payment. \nWe will verify the payment and activate your id within 24-48hrs."
                UpgradeButton = Button(root, text = "Register",command=lambda: openurlwithmessage(fullversion_url,messageheading,messagetext))
                UpgradeButton.pack()                


        else:
            messagebox.showinfo("Validation Error","Invalid email id. Check and try again.")

def openurlwithmessage(url,messageheading,messagetext):    
    messagebox.showinfo(messageheading,messagetext)
    openweb(url)            
            
def openweb(url):
    webbrowser.open_new_tab(url)
    
       
UserFrame = LabelFrame(root, text="Enter Email Id", padx=5, pady=5)
UserFrame.pack(padx=10, pady=10)

emailIdEntry=Entry(UserFrame,width=50)
emailIdEntry.pack()

userValidateButton = Button(UserFrame, text="Validate User",command=validateUser)    
userValidateButton.pack()


UserLabel=Label(UserFrame,text="Note:- Enter 'Demo' To Activate Demo Version")
UserLabel.pack() 

UpgradeLabel=Label(UserFrame,text=" ")
UpgradeLabel.pack() 
UpgradeLabel=Label(UserFrame,text="To register an account click 'Register' button below for details. ")
UpgradeLabel.pack() 

messageheading="Payment Information"
messagetext="After you click 'OK' you will be taken to paypal for payment. \nWe will verify the payment and activate your id within 24-48hrs."
UpgradeButton = Button(UserFrame, text = "Register",command=lambda: openurlwithmessage(fullversion_url,messageheading,messagetext))
UpgradeButton.pack()
TrainingButton = Button(root, text = "Click To Watch Training",command=lambda: openweb(training_url))
TrainingButton.pack()


root.mainloop()
