# load json data (intents) 

import nltk
#nltk.download('punkt')
from nltk.stem.lancaster import LancasterStemmer
stemmer=LancasterStemmer()

import numpy, tflearn, tensorflow, random, pickle

import json
with open("intents.json") as data:
    dataset=json.load(data)

#print (dataset["intents"])

#load model and data if it has already been created
#delete saved model files/rename them if changes are made to model
try:
    with open("dataset.pickle","rb") as d:
        words,group,train,output=pickle.load(d)

except:

    # data preprocessing
    # extract data 
    words=[]
    group=[]
    x=[] #list of different patterns
    y=[] #corressponds to x

    for intent in dataset["intents"]:
        for pattern in intent["patterns"]:
            word=nltk.word_tokenize(pattern) #stemming
            words.extend(word)
            x.append(word)
            y.append(intent["tag"])
        
        if intent["tag"] not in group:
            group.append(intent["tag"])

    # list of stemmeed words, no duplicates
    words=[stemmer.stem(j.lower()) for j in words if j!="?"]
    words=sorted(list(set(words)))

    group=sorted(group)


    #represent intents numerically as required by NN and ML 
    train=[]
    output=[]

    empty=[0 for _ in range (len(group))]

    for w, wrd in enumerate(x):
        wrds=[] #bag of words

        word=[stemmer.stem(j.lower())for j in wrd]
        for j in words:
            if j in word:
                wrds.append(1)
            else:
                wrds.append(0)
        
        output_row=empty[:]
        output_row[group.index(y[w])]=1

        train.append(wrds)
        output.append(output_row)

    #convert training data 
    train=numpy.array(train)

    #output to numpy arrays
    output=numpy.array(output)

    with open ("dataset.pickle","wb") as d:
        pickle.dump((words,group,train,output),d)


#set up training model

#tensorflow.reset_default_graph()
from tensorflow.python.framework import ops
ops.reset_default_graph()

##wuth more intents, add more neurons to hidden layers
network=tflearn.input_data(shape=[None,len(train[0])])
network=tflearn.fully_connected(network,8)
network=tflearn.fully_connected(network,8) #2 hidden layers with 8 neurons, fully connected
network=tflearn.fully_connected(network,len(output[0]), activation="softmax") #probabilities for each output (predictions)
network=tflearn.regression(network)

model=tflearn.DNN(network)

#train model on dataset
try:
    model.load("model.tflearn")
except:
    model.fit(train,output,n_epoch=1000, batch_size=8, show_metric=True)
    model.save("model.tflearn")



#get user input, convert to numerical value (bag of words), get prediction from model, get most probable group and get response
def bag_of_words(b,words):
    bag=[0 for _ in range(len(words))]

    b_words=nltk.word_tokenize(b)
    b_words=[stemmer.stem(word.lower())for word in b_words]

    #generate bag
    for bw in b_words:
        for i,w in enumerate(words):
            if w==bw:
                bag[i]=1
    return numpy.array(bag)


def chat():
    print("Hi there :) ['type quit' to stop talking']")
    while True:
        user=input("You: ")
        if user.lower()=="quit":
            break

        results=model.predict([bag_of_words(user,words)])
        results_index=numpy.argmax(results)
        tag=group[results_index]

        for t in dataset["intents"]:
            if t['tag']==tag:
                responses=t['responses']
        print(random.choice(responses))


chat()