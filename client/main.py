from flask import Flask, render_template,request,redirect,url_for   
from pymongo import MongoClient   
from flask_pymongo import PyMongo 
import os  
from flask_socketio import SocketIO, emit
from chatbotmain import chat

app = Flask(__name__, template_folder='templates')
client = MongoClient("mongodb+srv://test:test@cluster0.qlmo0.mongodb.net/EmotionalSupportChatbot?retryWrites=true&w=majority")
db = client.EmotionalSupportChatbot
app.config['SECRET_KEY'] = 'jsshiuehnksapasmxjsd'

#initialize flask- SocketIO
socketio = SocketIO(app)

@app.route('/')
def home():
  return render_template('chatbox.html')

def messageRecived():
  print( 'message received !' )

#send data to the server side events
@socketio.on( 'my eventes' )
def handleEvent( json1 ):
  message = json1['message']

  #print  message to  terminal
  print(message)
  answer=chat(message)
  json1['answer'] = answer
  json1['bot']='AI'
  print( 'recived my event: ' + str(json1 ))
  socketio.emit( 'my response', json1, callback=messageRecived )


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


@app.route('/about', methods=['GET'])
def renderabout():
  return render_template("about.html")

if __name__ == '__main__':
  socketio.run( app )

app.run(host='127.0.0.1', port=8080)