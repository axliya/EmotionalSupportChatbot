# Chatbot code

import nltk
#nltk.download('punkt')
from nltk.stem.lancaster import LancasterStemmer
stemmer=LancasterStemmer()

import numpy, tflearn, tensorflow, random, pickle

# load json data (intents) 
import json
with open("client\intents.json", encoding="utf8") as data:
    dataset=json.load(data,encoding="utf8" )

def punctuations(string):
    punc= '''!()-;:'"\, <>./@#$%^&*_~''' #except '?'
    for j in string:
        if j in punc:
            string = string.replace(j,"")
    return string

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

#for each sentence in intents pattern
    for intent in dataset["intents"]:
        for pattern in intent["patterns"]:
            word=nltk.word_tokenize(pattern) #stemming, tokenize each word in the sentence
            
            if 'context_filter' in intent:
                word.append(intent['context_filter'])
            words.extend(word) #add to words list
            x.append(word) #add to corpus
            y.append(intent["tag"])
        
        if intent["tag"] not in group:
            group.append(intent["tag"])

    # stem, lower and remove duplicated words
    words=[stemmer.stem(punctuations(j.lower())) for j in words if j!="?"]
    words=sorted(list(set(words)))

    group=sorted(group)


#training data creation

    #represent intents numerically as required by NN and ML 
    train=[]
    output=[]

    empty=[0 for _ in range (len(group))] #empty array for output

#bag of words creation
    for w, wrd in enumerate(x):
        bwrds=[] #bag of words

        stemmed=[stemmer.stem(punctuations(j.lower()))for j in wrd]
        for word in words:
            if word in stemmed:
                bwrds.append(1)
            else:
                bwrds.append(0)
    
        #0 for tags and 1 for current tag
        output_row=empty[:]
        output_row[group.index(y[w])]=1

        train.append(bwrds)
        output.append(output_row)

    #convert training data 
    train=numpy.array(train)

    #output to numpy arrays
    output=numpy.array(output)

    with open ("dataset.pickle","wb") as d:
        pickle.dump((words,group,train,output),d)


#set up training model
#reset underlying graph data

#tensorflow.reset_default_graph()
from tensorflow.python.framework import ops
ops.reset_default_graph()

#build NN
#with more intents, add more neurons to hidden layers
network=tflearn.input_data(shape=[None,len(train[0])])
network=tflearn.fully_connected(network,384)
network=tflearn.fully_connected(network,384)
network=tflearn.fully_connected(network,384)
network=tflearn.fully_connected(network,384) #4 hidden layers with 384 neurons, fully connected
network=tflearn.fully_connected(network,len(output[0]), activation="softmax") #probabilities for each output (predictions)
network=tflearn.regression(network)

#define model
model=tflearn.DNN(network)

#train model on dataset
try:
    model.load("model.tflearn")
except:
    model.fit(train,output,n_epoch=2000, batch_size=64, show_metric=True)
    model.save("model.tflearn")



#get user input, convert to numerical value (bag of words), get prediction from model, get most probable group and get response
def bag_of_words(b,words):
    bag=[0 for _ in range(len(words))]

    b_words=nltk.word_tokenize(b)
    b_words=[stemmer.stem(punctuations(word.lower()))for word in b_words]

    #generate bag
    for bw in b_words:
        for i,w in enumerate(words):
            if w==bw:
                bag[i]=1
    return numpy.array(bag)


def chat(user):

#global context
    context=""

    #print("  [type 'quit' to stop talking]  \n Hi there :)")
    #while True:
    #    user=input("You: ")
    #    if punctuations(user.lower())=="quit":
    #        break
    
    results_probability=0
    if context != "":
        con=user + " " + context
        results=model.predict([bag_of_words(con,words)])[0]
        results_index=numpy.argmax(results)
        results_probability=numpy.max(results)

    if results_probability<0.6:
        results=model.predict([bag_of_words(user,words)])[0]
        results_index=numpy.argmax(results)
        results_probability=numpy.max(results)
    invalid=False

    #60% confidence
    if results_probability>0.6:
        tag=group[results_index]

        for i in dataset["intents"]:
            if i["tag"]==tag:
                if 'context_filter' in i and i['context_filter'] != context:
                    invalid=True
                    break
                responses=i['responses']
                if 'context_set' in i:
                    context=i['context_set']
            
        if not invalid: 
            return(random.choice(responses))
    else:
        if "?" in user:
            return("sorry, i didn't get that")
        else:
            return("im listening")

        # print("please rephrase")

#chat()