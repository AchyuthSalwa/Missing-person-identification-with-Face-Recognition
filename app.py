from flask import Flask,render_template,flash
from flask_mysqldb import MySQL
from flask import request
import yaml
import cv2.cv2 as cv2
import numpy as np
import face_recognition
import base64
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import PIL.Image
import io
import base64
import urllib.request
import smtplib
from email.message import EmailMessage
import json
from geopy.geocoders import Nominatim
from urllib.request import urlopen
#url='http://ipinfo.io/json'
#response=urlopen(url)
#data=json.load(response)
#print(data)
#geoLoc = Nominatim(user_agent="GetLoc")
#locname = geoLoc.reverse("13.4383, 79.5510")
#print(locname)
#loc = data['ip']
#loc=str(loc)
app=Flask(__name__)
db = yaml.full_load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
mysql = MySQL(app)
app.secret_key = 'the random string'
UPLOAD_FOLDER='pics'
UPLOAD_FOLDER1='pics1'
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
app.config['UPLOAD_FOLDER1']=UPLOAD_FOLDER1
@app.route('/', methods=['GET','POST'] )
def index():
    if request.method =='POST':
        usrd=request.form
        uname = usrd['adminname']
        password = usrd['password']
        cur = mysql.connection.cursor()
        cur.execute("select * from  admin where namead=%s and password=%s ",(uname,password))
        account = cur.fetchone()
        if account:
            msg = 'WELCOME!'
            return render_template('regi.html',msg=msg)
        else:
            msg = 'Incorrect username / password !'
            return render_template('index.html', msg=msg)
        mysql.connection.commit()
        cur.close()
        #return 'success'
    return render_template('index.html')


@app.route('/regis', methods=['GET','POST'] )
def regis():
    if request.method == 'POST':
        usrd = request.form
        fname = usrd['fname']
        lname = usrd['lname']
        gender =str(request.form.get('gender'))
        contact=usrd['contact']
        email=usrd['email']
        file=request.files['photo']
        filename=secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
        os.path.splitext(filename)
        fn=os.path.splitext(filename)[0]
        print('File successfully uploaded')
        print(fn)
        cur = mysql.connection.cursor()
        # Execute the query and commit the database.
        query="""INSERT INTO complaints(contact,fname ,lname,pic,gender,scode,email) VALUES(%s, %s, %s , %s , %s,%s,%s)"""
        record = (contact, fname, lname,file,gender,fn,email)
        cur.execute(query, record)
        mysql.connection.commit()
        msg="successfully inserted"
        mysql.connection.commit()


    return render_template('regi.html',msg=msg)

@app.route('/regi', methods=['GET','POST'] )
def regi():
    path = 'pics'
    images = []
    classNames = []
    myList = os.listdir(path)
    print(myList)
    for cl in myList:
        curImg = cv2.imread(f'{path}/{cl}')
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])
    print(classNames)

    def findEncodings(images):
        encodeList = []
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
        return encodeList

    def markAttendance(name):
        with open('frontend/pythonlogin/attendance.csv', 'r+') as f:
            myDataList = f.readlines()
            nameList = []
            for line in myDataList:
                entry = line.split(',')
                nameList.append(entry[0])
            if name not in nameList:
                now = datetime.now()
                dtString = now.strftime('%H:%M:%S')
                f.writelines(f'\n{name},{dtString}')

    encodeListKnown = findEncodings(images)

    print("Encode complete")
    cap = cv2.VideoCapture(0)
    while True:
        success, img = cap.read()
        # img = captureScreen()
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        #  The below code is hidden
        #---------------------------
        #---------------------------
        #---------------------------
        #---------------------------
        #---------------------------
        #---------------------------
        #---------------------------
            if matches[matchIndex] and faceDis[matchIndex]<0.56:
                name = classNames[matchIndex]
                print(name)
                mf=name
                #markAttendance(name)
                cur = mysql.connection.cursor()
                print('hi')
                # return redirect(url_for('static', filename='uploads/' + filename), code=301)
                cur.execute("select * from  complaints where scode=%s", (mf,))
                userDetails = cur.fetchall()
                #cur.execute("SELECT pic FROM complaints WHERE scode=%s", (mf,))
                data = cur.fetchall()
                #file_like = io.BytesIO(data[0][0])
                # imgdata = base64.b64decode(file_like)
                full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'mf.jpg')
                #filename = 'pics/mf.jpg'  # I assume you have a way of picking unique filenames
                msg="person found"
                name=name+".jpg"
                imgmat = face_recognition.load_image_file('pics/'+name)
                imgmat = cv2.cvtColor(imgmat, cv2.COLOR_BGR2RGB)
                imgmat=cv2.resize(imgmat, (720, 600))
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                dest=userDetails[0][6]
                server.login("abc@gmail.com", "Achyuth123")
                estr="ALERT PERSON  "+userDetails[0][1]+"  WAS FOUND!"+"At "+str(locname)+""
                server.sendmail("abc@gmail.com",dest,estr)
                server.quit()
                cv2.imshow('Webcam', imgmat)
                cv2.waitKey(3000)
                return render_template('redgi.html', msg=msg, lname=name, userDetails=userDetails, img_data=full_filename,loc=loc,locname=locname)
        cv2.imshow('Webcam', img)
        cv2.waitKey(1)
    return 'hi'
@app.route('/aac')
def aac():
    return render_template('aac.html', data=[{'name':'Select Gender...'},{'name':'Male'}, {'name':'Female'}, {'name':'Other'}])
@app.route('/pro')
def pro():
    return render_template('index.html')

@app.route('/delete')
def delete():
    return render_template('delete.html')

@app.route('/delwork', methods=['POST'] )
def delwork():
    cur = mysql.connection.cursor()
    if request.method =='POST':
        usrd=request.form
        uname = usrd['fname']
        contact = usrd['contact']
        #cur.execute("select * from  complaints where scode=%s", (mf,))
        cur.execute("delete from complaints where contact=%s ",(contact,))
        if cur.rowcount>0:
            msg = 'DELETION SUCCESSFUL'
            cur.execute("delete from complaints where contact=%s ", (contact,))
            mysql.connection.commit()
            return render_template('regi.html',msg=msg)
        else:
            msg = 'NO COMPLAINT FOUND !'
            return render_template('delete.html', msg=msg)
        mysql.connection.commit()
        cur.close()
        #return 'success'
    return render_template('delete.html')


@app.route('/user_uploads',methods=['GET','POST'])
def user_uploads():
    if request.method == 'POST':
        flag=0
        usrd = request.form
        uname = usrd['uname']
        email = usrd['email']
        #gender =str(request.form.get('gender'))
        contact=usrd['contact']
        file=request.files['photo']
        filename=secure_filename(file.filename)
        print(filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER1'],filename))
        os.path.splitext(filename)
        fn=os.path.splitext(filename)[0]
        print('File successfully uploaded')
        print(fn)
        path = 'pics'
        images = []
        classNames = []
        myList = os.listdir(path)
        print(myList)
        for cl in myList:
            curImg = cv2.imread(f'{path}/{cl}')
            images.append(curImg)
            classNames.append(os.path.splitext(cl)[0])
        print(classNames)

        def findEncodings(images):
            encodeList = []
            for img in images:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                encode = face_recognition.face_encodings(img)[0]
                encodeList.append(encode)
            return encodeList

        encodeListKnown = findEncodings(images)

        print("Encode complete")
        imgsus=face_recognition.load_image_file('pics1/'+filename)
        imgsus=cv2.cvtColor(imgsus,cv2.COLOR_BGR2RGB)

        #  The below code is hidden
        # ---------------------------
        # ---------------------------
        # ---------------------------
        # ---------------------------
        # ---------------------------
        # ---------------------------
        # ---------------------------

        if matches[matchIndex] and faceDis[matchIndex] <0.55:
                name = classNames[matchIndex]
                print(name)
                mf=name
                name=name+".jpg"
                imgmat = face_recognition.load_image_file('pics/'+name)
                imgmat = cv2.cvtColor(imgmat, cv2.COLOR_BGR2RGB)
                imgmat=cv2.resize(imgmat, (720, 600))
                imgsus = cv2.resize(imgsus, (720, 600))
                cv2.imshow('imgsus', imgsus)
                cv2.imshow('imgmat', imgmat)
                cv2.waitKey(6000)
                msg="MATCH FOUND"
                cur = mysql.connection.cursor()
                cur.execute("select * from  complaints where scode=%s", (mf,))
                userDetails = cur.fetchall()
                server = smtplib.SMTP("smtp.gmail.com", 587)
                server.starttls()
                dest = userDetails[0][6]
                server.login("abc@gmail.com", "Achyuth123")
                emsg=EmailMessage()
                emsg.set_content("ALERT : PERSON  " + userDetails[0][1] + "  WAS FOUND!")
                emsg['Subject']='IMPORTANT NOTICE'
                emsg['From']="abc@gmail.com"
                emsg['To']=dest
                #estr = "ALERT PERSON  " + userDetails[0][1] + "  WAS FOUND!"
                #server.sendmail("salvaachyuth@gmail.com", dest, estr)
                server.send_message(emsg)
                server.quit()
            else:
                msg="NO MATCHES"
                flag=-1
            if(flag==-1):
                return render_template('index.html',msg=msg)
            else:
                return render_template('redgi.html', msg=msg, lname=mf, userDetails=userDetails,loc=loc)
        return render_template('index.html')


@app.route('/aac1')
def aac1():
    return render_template('aac1.html', data=[{'name':'Select Gender...'},{'name':'Male'}, {'name':'Female'}, {'name':'Other'}])
if __name__== '__main__':
    app.run(debug=True)