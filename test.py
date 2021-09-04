from flask import Flask ,render_template,redirect,request,session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import json
from datetime import datetime
import smtplib
from email.message import EmailMessage
import random
import os

local_server = True
with open('templates\config.json','r') as c:
	params = json.load(c)["params"] 
otp=999999	
def generateOTP():
	return random.randrange(100000, 999999)
def sendemail(to,subject,content):
	server=smtplib.SMTP("smtp.gmail.com",587)
	server.starttls()
	server.login(params['gmail_user'],params['gmail_password'])
	mail=EmailMessage()
	mail['From']=params['gmail_user']
	mail["To"]=to
	mail['Subject']=subject
	mail.set_content(content)
	server.send_message(mail)
	server.close()

app=Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['UPLOAD_FOLDER']= params["files_location"]
if (local_server):
	app.config['SQLALCHEMY_DATABASE_URI'] = params['loc_uri']  #connected to database -username-pass---falana falana
else :
	app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)

class Patientcontacts(db.Model):
	sno = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(80), nullable=False)
	username = db.Column(db.String(30), nullable=False)
	password = db.Column(db.String(8), nullable=False)
	email = db.Column(db.String(120), nullable=False)
	contact_no = db.Column(db.Integer, nullable=False)
	pincode= db.Column(db.Integer, nullable=False)
	date_time = db.Column(db.String(12))
	slug = db.Column(db.String(25), nullable=False)
	filename = db.Column(db.String(30), nullable=True)
	content = db.Column(db.String(30), nullable=False)

class Doctorcontacts(db.Model):
	sno = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(80), nullable=False)
	username = db.Column(db.String(30), nullable=False)
	password = db.Column(db.String(8), nullable=False)
	email = db.Column(db.String(120), nullable=False)
	contact_no = db.Column(db.Integer, nullable=False)
	pincode= db.Column(db.Integer, nullable=False)
	date_time = db.Column(db.String(12))
	slug = db.Column(db.String(25), nullable=False)
	filename = db.Column(db.String(30), nullable=True)
	content = db.Column(db.String(30), nullable=False)


XDuser = Doctorcontacts.query.filter_by().first()
XPuser = Patientcontacts.query.filter_by().first()
arr = params["slug_words"].split(" ")
uname = params['username']
passw = params['password']

@app.route("/")
def default():
	XPuser = Patientcontacts.query.filter_by().all()
	xyz = "Yashwant Dwala"
	return render_template('index.html',name = xyz,Data=XPuser,param=params)

@app.route("/home")
def home():
	xyz = "Yashwant Dwala" 
	return render_template('index.html',param=params,name = xyz)

@app.route("/about")
def about():
	return render_template("about.html",param=params)

@app.route("/services",methods = ['GET','POST'])
def services():
	return render_template("services.html",param=params)

@app.route("/contact",methods = ['GET','POST'])
def contact():
	return render_template("Contact.html",param=params)


@app.route("/signup/<string:who>",methods = ['GET','POST'])
def SignUp(who):
	error=""
	if request.method == 'POST':
		name = request.form.get('name')
		uname = request.form.get('uname')
		password = request.form.get('pass')
		email = request.form.get('email')
		phone = request.form.get('contact_num')
		pincode = request.form.get('pin')
		slug = uname
		# for x in range(4):
			# slug += random.choice(arr)
		entry =  Patientcontacts(name=name,username=uname,password=password,email=email,contact_no=phone,pincode=pincode,date_time =  datetime.now(),slug = slug )
		if who == "patient":
			# 	Xuser= Patientcontacts.query.filter_by(username =uname).first()
			entry =  Patientcontacts(name=name,username=uname,password=password,email=email,contact_no=phone,pincode=pincode,date_time =  datetime.now(),slug = slug )
		if who == "doctor":
			# 	Xuser= Doctorcontacts.query.filter_by(username =uname).first()
			entry =  Doctorcontacts(name=name,username=uname,password=password,email=email,contact_no=phone,pincode=pincode,date_time =  datetime.now(),slug = slug )
		# if Xuser != None:
		# 	error = "username already taken!"
		# 	return render_template("Signup.html",param=params,error_msg=error)
		db.session.add(entry)
		db.session.commit()
		sendemail(email," VHI verification " ,"Congratulations ,you  have successfully registered for VHI as "+ who +" in VirtualHealth Platform.! \n\n " +"Thank you for registraion." )
		return redirect("/home")
	return render_template("Signup.html",param=params,who=who)

@app.route("/doctor_dashboard",methods = ['GET','POST'])
def Doctor_Dashboard():
	global username
	XDuser = Doctorcontacts.query.filter_by().all() 
	if request.method=='POST': 
		username = request.form.get('uname')
		userpass = request.form.get('pass')
		XDuser = Doctorcontacts.query.filter_by(username=username).first()
		uname = XDuser.username
		if(XDuser!=None):
			# for x in XDuser:
			if username== uname and userpass == XDuser.password:
				#set the  session variable
				session['user'] = username
				XDuser = Doctorcontacts.query.filter_by(username=username).first()
				return render_template("Ddashboard.html", param=params,Data=XDuser,x=session['user'] )
		else :
			XDuser = Doctorcontacts.query.filter_by(username =username).all()
			return render_template("DLogin.html", param=params,)
		XDuser = Doctorcontacts.query.filter_by(username = username).all()
		if ('user' in session and session['user'] == username ):
			return render_template("Ddashboard.html",param=params,Data=XDuser ,x=session['user']) 		
	return render_template("DLogin.html", param=params)

@app.route("/patient_dashboard",methods = ['GET','POST'])
def Patient_Dashboard():
	global username
	XPuser = Patientcontacts.query.filter_by().all() 
	if request.method=='POST': 
		username = request.form.get('uname')
		userpass = request.form.get('pass')
		XPuser = Patientcontacts.query.filter_by(username=username).first()
		if(XPuser!=None):
			# for x in XDuser:
			if username == uname and userpass == passw:
				#set the  session variable
				session['user'] = username
				XPuser = Patientcontacts.query.filter_by(username=username).first()
				return render_template("forDoctors.html", param=params,Data=XPuser,x=session['user'],msg=" ")
		else :
			XPuser = Patientcontacts.query.filter_by(username =username).all()
			return render_template("PLogin.html", param=params,)
		XPuser = Patientcontacts.query.filter_by(username =username).all()
		if ('user' in session and session['user'] == uname ):
			return render_template("Pdashboard.html",param=params,Data=XDuser ,x=session['user']) 		
	return render_template("PLogin.html", param=params)

@app.route("/logout",methods = ['GET','POST'])
def Logout():
	session.pop('user')
	return redirect('/doctor_dashboard')

# @app.route("/patient_verification",methods = ['GET','POST'])
# def patient_verification():
	
# 	return render_template("ClickedData.html", Data =patientData, param=params)

@app.route("/datafetch",methods = ['GET'])
def DataFetch():
	XData = Patientcontacts.query.filter_by().all()
	return render_template("patientData.html", param=params,XData=XData,DATA=XData)

@app.route("/uploader",methods = ['GET','POST'])
def Uploader():
	global XPuser
	if ('user' in session and session['user'] == uname ):
		XPuser = Patientcontacts.query.filter_by(username =session['user']).first()
		if request.method=='POST': 
			content = request.form.get('content')
			f = request.files['file']
			filename =f.filename
			f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename) ))
			entry =  Patientcontacts(name=XPuser.name,username=session['user'],password=XPuser.password,email=XPuser.email,contact_no=XPuser.contact_no,pincode=XPuser.pincode,date_time =  datetime.now(),slug = XPuser.slug,content=content,filename=filename )
			db.session.add(entry)
			db.session.commit()
			sendemail(XPuser.email," VHI - file Uploaded Successfully" ,"File has been successfully Uploaded on your  VHI account! \n\n "  )
			return render_template("index.html", param=params)

@app.route("/otp-verification",methods = ['GET','POST'])
def OTPverify():
	global XPuser,otp
	if request.method=='POST':
		Puser_name = request.form.get('uname')
		XPuser = Patientcontacts.query.filter_by(username = Puser_name).first()	
		otp = generateOTP()
		sendemail(XPuser.email,"VHI OTP - Verification ","Your OTP is "+str(otp) +",Please share this otp with "+ XDuser.name)
	return render_template("OTPverification.html", param=params,XData=XPuser)	

@app.route("/datafetch/<string:patientcontacts_slug>",methods = ['GET','POST'])
def DataFetchBySlug(patientcontacts_slug):
	if request.method=='POST':
		OTP = request.form.get('OTP')	
		if (otp == OTP):
			patientData = Patientcontacts.query.filter_by(slug =patientcontacts_slug).all()
	return render_template("PatientData.html", Data =patientData, param=params)

app.run(debug=True)
