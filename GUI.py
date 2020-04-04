# -*- coding: utf-8 -*-
# author: Yu

import tkinter as tk
from tkinter import ttk

import urllib.request
import ssl

from lark import Lark
from lark import Tree, Transformer, Visitor

import operator

from random import choice

import random

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

def parseURL(HTML,numberOfNodes,probability_value,Idea_Seed_Connections,AntiIdea_Seed_Connections,number_Of_SimulationTimes):
    # grammar
    json_parser = Lark(r"""
        ?value: object
            | array              
            | data
            | string             
            | SIGNED_NUMBER      -> number
        
        data : "{" [info("," info)*]"}" || "[" [value("," value)*] "]"
        array : "[" [data("," data)*]"]"       
        object : "{" [label ("," label)*] "}"
        
        label : string ":" array
        info : string ":" value
        string : ESCAPED_STRING
        
        %import common.ESCAPED_STRING
        %import common.SIGNED_NUMBER
        %import common.WS
        %ignore WS
        
    """, start='value')


    tree = json_parser.parse(HTML)
    # Print the tree structure in a pretty way (use for test)
    #print(tree.pretty())
    print('\n')

    # list l used to store all id in the network
    l=[]
    for subtree in tree.iter_subtrees():
        if(subtree.data=="number"):
            #print(int(subtree.children[0]))
            l.append(int(subtree.children[0]))


    l[-int(numberOfNodes):]=[]

    # get the edges connection in the network, which will be used in building DTMCs
    # work as input in DTMCs method.
    edges=[]
    for i in range(len(l)-1):
        item=[]
        if (i%2)==0:
            item.append(l[i])
            item.append(l[i+1])
            edges.append(item)

    # Show the edges with nodes number connection
    print("Edges: ",edges)



    #####################################################################################
    # This part calculate the connections of each node in the network
    # Based on the number of connections choose the idea and anti-idea initial seed from the network
    #connections=[]
    connections={}
    for connection in range(int(numberOfNodes)):
        count=0

        for i in edges:
            # i is edges like [0,2] [0,3] [1,2]...
            for j in i:
                # j is nodes number like 0 2 0 3 1 2...
                if j==connection:
                    count=count+1
        #print(count)
        #connections.append(count)
        connections[str(connection)]=count
    #print("Connections: ",connections)

    sortedConnections=sorted(connections.items(), key=operator.itemgetter(1))
    #print("Sorted Connections: ",sortedConnections)

    # seed connections: many is top 0.25, few is the last 0.25
    ManyNumber=FewNumber=int(float(numberOfNodes)*0.25)

    FewList=sortedConnections[:FewNumber]
    ManyList=sortedConnections[-ManyNumber:]
    AverageList=sortedConnections[FewNumber:-ManyNumber]
    #print("FewList: ",FewList)
    #print("ManyList: ",ManyList)
    #print("AverageList: ",AverageList)
    #print("\n")

    if Idea_Seed_Connections=="Few":
        ideaCon=FewList
    elif Idea_Seed_Connections=="Many":
        ideaCon=ManyList
    elif Idea_Seed_Connections == "Average":
        ideaCon=AverageList
    else:
        ideaCon=[]

    if AntiIdea_Seed_Connections=="Few":
        antiCon=FewList
    elif AntiIdea_Seed_Connections=="Many":
        antiCon=ManyList
    elif AntiIdea_Seed_Connections == "Average":
        antiCon=AverageList
    else:
        antiCon=[]

    #adjacent_matrix(numberOfNodes,edges)


    #DTMC_Transition(numberOfNodes,probability_value,ideaCon,antiCon,number_Of_SimulationTimes,edges)
    output_graph(FewList,AverageList,ManyList, numberOfNodes, probability_value, edges, number_Of_SimulationTimes)



def DTMC_Transition(numberOfNodes,probability_value,ideaConnection,antiIdeaConnection,number_Of_SimulationTimes, edges):
    # number of nodes in the network
    N=numberOfNodes

    # probability of infection
    probability=float(probability_value)

    # state: agree, disagree, indifferent
    state = ["agree", "disagree", "indifferent"]

    # number of messages
    messages=int(number_Of_SimulationTimes)


    # Two different initial infected seeds (type of string)
    if ideaConnection==[]:
        ideaSeed=None
    else:
        ideaSeed = choice(ideaConnection)[0]
    if antiIdeaConnection==[]:
        antiSeed=None
    else:
        antiSeed = choice(antiIdeaConnection)[0]
    while ideaSeed==antiSeed:
        antiSeed = choice(antiIdeaConnection)[0]


    ################################################
    # construct a dictionary to store the state of each node (key: node name; value: state)
    dict={}
    # initially set all nodes' state indifferent
    for n in range(int(numberOfNodes)):
        dict[str(n)]=state[2]

    # set two seeds' state: agree or disagree
    if ideaSeed!=None:
        dict[ideaSeed]=state[0]
    if antiSeed!=None:
        dict[antiSeed]=state[1]


    m = 0 # messages
    # the number of loops equals to the simulation time? equal to message number?
    while(m < messages):
        InfectedNodes = [] # store all infected nodes and update in time
        # if the state is not 'indifferent', it is infected node
        for key, value in dict.items():
            if dict[key] != state[2]:
                InfectedNodes.append(key)

        print("Infected Nodes: ",InfectedNodes)

        # select one infected node at random
        Random_Infected_Node = choice(InfectedNodes)

        # Find the connection of the node and transform the idea based on the probability
        #print("Random_Infected_node: ",Random_Infected_Node)
        connectednodes=find_connected_nodes(Random_Infected_Node,edges)
        #print("Connected nodes: ",connectednodes)
        # The state of the random selected infected node: agree or anti
        x_state = dict[Random_Infected_Node]

        # The state of each connected nodes: initialized is indifferent
        for n in connectednodes:
            n_state = dict[n]

            # for the connected node n, update the opinions of it according to the relevant probabilities
            updateResult = random_pick([x_state, n_state], [probability, 1 - probability])

            # if the state of node n is changed, update it in the dictionary
            if updateResult!=n_state:
                dict[n]=updateResult

            print(dict)
        m += 1
    return dict


def find_connected_nodes(originalNode,edges):
    connectednodes = []
    for i in edges:
        if i[0] == int(originalNode):
            connectednodes.append(str(i[1]))
        if i[1] == int(originalNode):
            connectednodes.append(str(i[0]))

    #print(connectednodes)
    return(connectednodes)


def random_pick(some_list,probabilities):
    x = random.uniform(0,1)
    cumulative_probability=0.0
    for item,item_probability in zip(some_list,probabilities):
        cumulative_probability+=item_probability
        if x < cumulative_probability:
            break
    return item


def statistics(messages, ideaConnection, antiIdeaConnection, numberOfNodes, probability_value, edges, number_Of_SimulationTimes):
    # messages is integer
    # state: agree, disagree, indifferent
    state = ["agree", "disagree", "indifferent"]
    index=0
    agree=0
    disagree=0
    runs=int(number_Of_SimulationTimes) # run the model 100 times and count the number of agree and disagree
    Messages=str(messages) # transform the integer to string
    while index<runs:
        dict = DTMC_Transition(numberOfNodes, probability_value, ideaConnection, antiIdeaConnection, Messages, edges)
        for key, value in dict.items():
            if dict[key] == state[0]:
                agree += 1

        for key, value in dict.items():
            if dict[key] == state[1]:
                disagree +=1

        index += 1

    AgreePercent = float(agree / runs)  # the average for each run(agree/infection)
    return AgreePercent


###################################################################################
# not used yet
def get_expected_infection(messages, ideaConnection, antiIdeaConnection, numberOfNodes, probability_value, edges, number_Of_SimulationTimes):
    # message is integer
    # calculate the mean value to decrease the random error
    n = 50
    i = 0
    total = 0.00
    while i < n:
        AgreePercent = statistics(messages, ideaConnection, antiIdeaConnection, numberOfNodes, probability_value, edges, number_Of_SimulationTimes)
        total = total + AgreePercent
        i += 1
        #print(AgreePercent)
    ExpectedInfection = float(total/n)

    return ExpectedInfection



def output_graph(FewList, AverageList, ManyList, numberOfNodes, probability_value, edges, number_Of_SimulationTimes):
    FewideaConnection = FewList  # few connection
    FewantiIdeaConnection = FewList  # few connection

    AverageideaConnection=AverageList # average connection
    AverageantiIdeaConnection=AverageList # average connection

    ManyideaConnection=ManyList # many connection
    #antiIdeaConnection=[('1', 2), ('3', 2)] # few connection

    print('FewideaConnection: ',FewideaConnection)
    print("FewantiIdeaConnection: ", FewantiIdeaConnection)
    print("AverageideaConnection: ", AverageideaConnection)
    print("AverageantiIdeaConnection", AverageantiIdeaConnection)
    print("ManyideaConnection", ManyideaConnection)


    messages = []
    ExpectedInfection_few = []
    ExpectedInfection_average = []
    ExpectedInfection_manyAndfew = []
    i = 0
    while i <= 40:
        messages.append(i)

        y1 = statistics(i, FewideaConnection, FewantiIdeaConnection, numberOfNodes, probability_value, edges, number_Of_SimulationTimes)
        ExpectedInfection_few.append(y1)

        y2 = statistics(i, AverageideaConnection, AverageantiIdeaConnection, numberOfNodes, probability_value, edges, number_Of_SimulationTimes)
        ExpectedInfection_average.append(y2)

        y3 = statistics(i, ManyideaConnection, FewantiIdeaConnection, numberOfNodes, probability_value, edges, number_Of_SimulationTimes)
        ExpectedInfection_manyAndfew.append(y3)

        i += 2
        print(messages)
        print(ExpectedInfection_few)
        print(ExpectedInfection_average)
        print(ExpectedInfection_manyAndfew)


    plt.plot(messages, ExpectedInfection_few, color='blue', label='initial agent have few connections', marker='o',
             markersize='3', linestyle='-')
    plt.plot(messages, ExpectedInfection_average, color='green', label='initial agent have average connections', marker='s',
             markersize='3', linestyle='-')
    plt.plot(messages, ExpectedInfection_manyAndfew, color='red', label='initial agent have many and few connections', marker='v',
             markersize='3', linestyle='-')


    x_ticks=np.arange(0, 42, 5)
    y_ticks=np.arange(0.0, max(ExpectedInfection_manyAndfew)+0.5, 0.5)
    plt.xticks(x_ticks)
    plt.yticks(y_ticks)


    plt.legend()  # 显示图例
    plt.grid()
    plt.xlabel('messages')
    plt.ylabel('Expected Infection')
    plt.show()





# not used yet
def adjacent_matrix(numberOfNodes,edges):
    aMatrix=[]
    # x-axis
    x=0

    while x < int(numberOfNodes):
        # y-axis
        y = 0
        eachNode = []
        while y < int(numberOfNodes):
            value = 0
            for e in edges:
                if x==int(e[0]) and y==int(e[1]):
                    value = 1
                if x==int(e[1]) and y==int(e[0]):
                    value = 1
            eachNode.append(value)
            y+=1
        print(x,": ",eachNode)
        print('\n')
        aMatrix.append(eachNode)
        x+=1

    #print(aMatrix)
    return (aMatrix)










def getInput():
    model_Type=modelChosen.get()
    probability_value=PV.get()
    number_Of_NetworkNodes=NN.get()
    #number_Of_RandomSeeds="1"
    number_Of_SimulationTimes=NS.get()
    Idea_Seed_Connections=ISeedConections.get()
    AntiIdea_Seed_Connections=ASeedConections.get()


    # test the value get from the input
    print("Model Type: ", model_Type)
    print("Probability Value: ", probability_value)
    print("Number of Network Nodes: ", number_Of_NetworkNodes)
    #print("Number of Random Seeds: ", number_Of_RandomSeeds)
    print("Idea Seed connections: ", Idea_Seed_Connections)
    print("Anti-Idea Seed connections: ", AntiIdea_Seed_Connections)
    print("Number of Simulation Times: ", number_Of_SimulationTimes)

    url="https://imdb.uib.no/info132nettverk/"+number_Of_NetworkNodes+"/1"
    html=getHtml(url)
    HTML=bytes.decode(html)
    #print(html)
    parseURL(HTML,number_Of_NetworkNodes,probability_value,Idea_Seed_Connections,AntiIdea_Seed_Connections,number_Of_SimulationTimes)




def getHtml(url):
    ssl._create_default_https_context = ssl._create_unverified_context
    page = urllib.request.urlopen(url)
    html = page.read()
    return html






if __name__=="__main__":

    window = tk.Tk() # initial the window
    window.title('GUI') # window title
    window.geometry('650x600') # window size

    # title label
    titleLabel=tk.Label(window, text="GUI", font=('Arial', 30, 'bold'))
    titleLabel.pack()

    # select model type label
    labelModelSelect = tk.Label(window,text = "Select a model", font=('Arial',20, 'bold')).place(x=40, y=60)
    model=tk.StringVar()
    modelChosen=ttk.Combobox(window, width=17, textvariable=model, state='readonly')
    modelChosen['values']=("DTMC infection model", "DTMC influence model")
    modelChosen.place(x=400, y=65)


    # probability value
    PV=tk.StringVar()
    labelProbability = tk.Label(window,text = "Value of λ", font=('Arial',20, 'bold')).place(x=40, y=125)
    probabilityValue = tk.Entry(window, font=('Arial', 14), textvariable=PV).place(x=400,y=125)

    # number of network nodes
    NN=tk.StringVar()
    labelNumberNodes = tk.Label(window,text = "The number of network nodes", font=('Arial',20, 'bold')).place(x=40, y=185)
    numberOfNetworkNodes = tk.Entry(window, font=('Arial', 14), textvariable=NN).place(x=400,y=185)

    # select idea seed connections
    labelISeedSelect = tk.Label(window,text = "Select idea seed connections", font=('Arial',20, 'bold')).place(x=40, y=240)
    ISeed=tk.StringVar()
    ISeedConections=ttk.Combobox(window, width=17, textvariable=ISeed, state='readonly')
    ISeedConections['values']=("Few", "Average", "Many")
    ISeedConections.place(x=400, y=245)


    # select anti-idea seed connections
    labelASeedSelect = tk.Label(window,text = "Select anti-idea seed connections", font=('Arial',20, 'bold')).place(x=40, y=300)
    ASeed=tk.StringVar()
    ASeedConections=ttk.Combobox(window, width=17, textvariable=ASeed, state='readonly')
    ASeedConections['values']=("Few", "Average", "Many")
    ASeedConections.place(x=400, y=305)

    # number of simulation times
    NS=tk.StringVar()
    labelSimulationTimes = tk.Label(window,text = "Times of running simulation", font=('Arial',20, 'bold')).place(x=40, y=365)
    numberOfSimulationTimes = tk.Entry(window, font=('Arial', 14), textvariable=NS).place(x=400,y=365)


    btn_finish = tk.Button(window, height=3, width=10, text='Finish', command=getInput)
    btn_finish.place(x=500, y=465)

    window.mainloop()


