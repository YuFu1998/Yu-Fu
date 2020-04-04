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

import networkx as nx


number_Of_NetworkNodes = "10"
probability_value = "0.5"
Idea_Seed_Connections = AntiIdea_Seed_Connections = "Three cases"
number_Of_SimulationTimes=1000

def Infection_Model(number_Of_NetworkNodes, probability_value, Idea_Seed_Connections, AntiIdea_Seed_Connections, number_Of_SimulationTimes):
    N = int(number_Of_NetworkNodes)
    addEdges = 2
    seedNumber = 1
    probability = float(probability_value)

    G = nx.random_graphs.barabasi_albert_graph(N, addEdges, seedNumber)
    pos = nx.spring_layout(G)  # layout style of the graph
    #nx.draw(G, pos, with_labels=False, node_size=30, node_color='blue')
    # Show the graph of the network(structure)
    #plt.show()

    edges = list(G.edges())
    print("Edges: ", edges)


    connections = {}
    for node in range(N):
        connections[str(node)] = len(list(G.neighbors(node)))

    sortedConnections = sorted(connections.items(), key=operator.itemgetter(1))
    print("Sorted Connections: ", sortedConnections)
    # seed connections: many is top 0.25, few is the last 0.25
    ManyNumber = FewNumber = int(float(N) * 0.25)

    FewList = sortedConnections[:FewNumber]
    ManyList = sortedConnections[-ManyNumber:]
    AverageList = []
    Left = sortedConnections[FewNumber:-ManyNumber]
    for i in Left:
        if i[1] > FewList[-1][1] and i[1] < ManyList[0][1]:
            AverageList.append(i)

    # print("FewList: ", FewList)
    # print("ManyList: ", ManyList)
    # print("AverageList: ", AverageList)
    # print("\n")



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


    #DTMC_Transition(numberOfNodes,probability_value,ideaCon,antiCon,number_Of_SimulationTimes,edges)
    output_graph(FewList,AverageList,ManyList, N, probability_value, edges, number_Of_SimulationTimes)


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
    #(when there are 10 nodes the number of messages is 40, so quadruple here)
    while i <= numberOfNodes*4:
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
              linestyle='-')
    plt.plot(messages, ExpectedInfection_average, color='green', label='initial agent have average connections', marker='s',
              linestyle='-')
    plt.plot(messages, ExpectedInfection_manyAndfew, color='red', label='initial agent have many and few connections', marker='v',
              linestyle='-')


    x_ticks=np.arange(0, numberOfNodes*4+2, 5)
    y_ticks=np.arange(0.0, max(ExpectedInfection_manyAndfew)+0.5, 0.5)
    plt.xticks(x_ticks)
    plt.yticks(y_ticks)


    plt.legend()  # 显示图例
    plt.grid()
    plt.xlabel('messages')
    plt.ylabel('Expected Infection')
    plt.show()




Infection_Model(number_Of_NetworkNodes, probability_value, Idea_Seed_Connections, AntiIdea_Seed_Connections, number_Of_SimulationTimes)