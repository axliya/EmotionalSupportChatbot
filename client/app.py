# flask app

from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from chatbotmain import chat

#configure app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'jsshiuehnksapasmxjsd'

#initialize flask- SocketIO
socketio = SocketIO(app)

@app.route( '/' )
def home():
  return render_template( 'chatbox.html' )

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


if __name__ == '__main__':
  socketio.run( app )


