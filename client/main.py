from flask import Flask, render_template,request,redirect,url_for   
from pymongo import MongoClient   
from flask_pymongo import PyMongo 
import os  

app = Flask(__name__, template_folder='templates')
client = MongoClient("mongodb+srv://test:test@cluster0.qlmo0.mongodb.net/EmotionalSupportChatbot?retryWrites=true&w=majority")
db = client.EmotionalSupportChatbot

@app.route('/')
def home():
  return render_template('index.html')

@app.route('/testimonials', methods=['GET', 'POST'])
def addtestimonial():
    if(request.method == "POST"):
      testimonial = request.form.get('testimonials')

      db.Testimonials.insert_one({"text": testimonial})

      return redirect("/")

    if(request.method == "GET"):
      testimonials = list(db.Testimonials.find())

      return render_template("testimonials.html", testimonials=testimonials)

@app.route('/resources', methods=['GET'])
def viewresources():
  resources = list(db.Resources.find())

  return render_template("resources.html", resources=resources)

app.run(host='0.0.0.0', port=8080)