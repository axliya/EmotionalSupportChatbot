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

@app.route('/addtestimonial', methods=['GET', 'POST'])
def addtestimonial():
    if(request.method == "POST"):
      testimonial = request.form.get('testimonials')
      rating = request.form.get('ratings')

      db.Testimonials.insert_one({"text": testimonial, "rating": rating})

      return redirect('/testimonials')
    return render_template('addtestimonial.html')
      

@app.route('/testimonials', methods=['GET', 'POST'])
def rendertestimonials():
  testimonials = list(db.Testimonials.find())

  if(request.method == "POST"):
    sorting = request.form.get('sort')

    if(sorting == "1"):
      testimonials = list(db.Testimonials.find().sort('_id', -1))
    elif (sorting == "2"):
      testimonials = list(db.Testimonials.find().sort("rating", -1))
    else:
      testimonials = list(db.Testimonials.find().sort("rating", 1))

  return render_template("testimonials.html", testimonials=testimonials)


@app.route('/resources', methods=['GET'])
def viewresources():
  resources = list(db.Resources.find())

  return render_template("resources.html", resources=resources)

app.run(host='0.0.0.0', port=8080)