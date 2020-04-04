# 10 nodes in the network (Figure 6)
# not random select/not PRISM select
# fair select/select in turn
import numpy as np
import random as rm
import operator
from random import choice
import random

import matplotlib as mpl
import matplotlib.pyplot as plt

###############################
#FewList:  [('1', 2), ('3', 2)]
#ManyList:  [('7', 8), ('6', 9)]
#AverageList:  [('5', 3), ('0', 4), ('2', 4), ('4', 4), ('8', 6), ('9', 6)]

numberOfNodes='10'
probability_value='0.5'
#number_Of_SimulationTimes='20'
edges = [[0, 8], [0, 9], [0, 6], [0, 7], [1, 8], [1, 6], [2, 8], [2, 9], [2, 6], [2, 7], [3, 6], [3, 7], [4, 8], [4, 9], [4, 6], [4, 7], [5, 9], [5, 6], [5, 7], [6, 7], [6, 8], [6, 9], [7, 8], [7, 9]]

ideaConnection=[('1', 2), ('3', 2)] # few connection
antiIdeaConnection=[('1', 2), ('3', 2)] # few connection

#ideaConnection=[('5', 3), ('0', 4), ('2', 4), ('4', 4), ('8', 6), ('9', 6)] # average connection
#antiIdeaConnection=[('5', 3), ('0', 4), ('2', 4), ('4', 4), ('8', 6), ('9', 6)] # average connection


#ideaConnection=[('7', 8), ('6', 9)] # many connection
#antiIdeaConnection=[('1', 2), ('3', 2)] # few connection


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
    # print("IdeaSeed: ",ideaSeed)
    # print("AntiSeed: ",antiSeed)
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
    # changes: processedNodes is used to store the last step processed node's state!
    processedNodes = []
    # the number of loops equals to the simulation time? equal to message number?
    while(m < messages):
        InfectedNodes = [] # store all infected nodes and update in time
        # if the state is not 'indifferent', it is infected node
        for key, value in dict.items():
            if dict[key] != state[2]:
                InfectedNodes.append(key)

        #print("Infected Nodes: ",InfectedNodes)



        # changes
        #########################################################################
        # agreeNodes store the nodes agree with the idea
        # disagreeNodes store the nodes disagree with the idea
        agreeNodes = []
        for key, value in dict.items():
            if dict[key] == state[0]:
                agreeNodes.append(key)
        disagreeNodes = []
        for key, value in dict.items():
            if dict[key] == state[1]:
                disagreeNodes.append(key)
        # print("agreeNodes: ",agreeNodes)
        # print("disagreeNodes: ",disagreeNodes)
        # print("processNodes: ",processedNodes)

        if len(processedNodes):
            lastprocessNode=processedNodes[-1] # last step processed node's state
            if dict[lastprocessNode]==state[0]:
                # if the state is agree
                if len(disagreeNodes):
                    # simulation for disagree node this step
                    Random_Infected_Node=choice(disagreeNodes)
                else:
                    Random_Infected_Node = choice(InfectedNodes)
            else:
                # if the state is disagree
                if len(agreeNodes):
                    # simulation for agree node this step
                    Random_Infected_Node=choice(agreeNodes)
                else:
                    Random_Infected_Node = choice(InfectedNodes)
        else:
            # select one infected node at random (for the first step simulation)
            Random_Infected_Node = choice(InfectedNodes)
        # add the chosen node to the processedNodes
        processedNodes.append(Random_Infected_Node)
        #########################################################################




        # select one infected node at random
        #Random_Infected_Node = choice(InfectedNodes)

        # Find the connection of the node and transform the idea based on the probability
        #print("Random_Infected_node: ",Random_Infected_Node,", ",dict[Random_Infected_Node])
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

            #print(dict)
        #print('\n')
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



def statistics(messages, ideaConnection, antiIdeaConnection):
    # messages is integer
    # state: agree, disagree, indifferent
    state = ["agree", "disagree", "indifferent"]
    index=0
    agree=0
    disagree=0
    runs=10000 # run the model 100 times and count the number of agree and disagree
    number_Of_SimulationTimes=str(messages) # transform the integer to string
    while index<runs:
        dict = DTMC_Transition(numberOfNodes, probability_value, ideaConnection, antiIdeaConnection, number_Of_SimulationTimes, edges)
        for key, value in dict.items():
            if dict[key] == state[0]:
                agree += 1

        for key, value in dict.items():
            if dict[key] == state[1]:
                disagree +=1

        index += 1



    # print("*****************************************\n")
    # print("agree: ",agree)
    # print("disagree: ",disagree)
    # print("Agree percent: ",float(agree/runs))
    # print("Disagree percent: ",float(disagree/runs))

    AgreePercent = float(agree / runs) # the average for each run(agree/infection)
    return AgreePercent


##################################################################################

def get_expected_infection(messages, ideaConnection, antiIdeaConnection):
    # message is integer
    # calculate the mean value to decrease the random error
    n = 20
    i = 0
    total = 0.00
    while i < n:
        AgreePercent = statistics(messages,ideaConnection, antiIdeaConnection)
        total = total + AgreePercent
        i += 1
        #print(AgreePercent)
    ExpectedInfection = float(total/n)

    return ExpectedInfection

def output_graph():
    FewideaConnection = [('1', 2), ('3', 2)]  # few connection
    FewantiIdeaConnection = [('1', 2), ('3', 2)]  # few connection

    AverageideaConnection=[('5', 3), ('0', 4), ('2', 4), ('4', 4), ('8', 6), ('9', 6)] # average connection
    AverageantiIdeaConnection=[('5', 3), ('0', 4), ('2', 4), ('4', 4), ('8', 6), ('9', 6)] # average connection

    ManyideaConnection=[('7', 8), ('6', 9)] # many connection
    #antiIdeaConnection=[('1', 2), ('3', 2)] # few connection
    messages = []
    ExpectedInfection_few = []
    ExpectedInfection_average = []
    ExpectedInfection_manyAndfew = []
    i = 0
    while i <= 40:
        messages.append(i)

        y1 = statistics(i, FewideaConnection, FewantiIdeaConnection)
        ExpectedInfection_few.append(y1)

        y2 = statistics(i, AverageideaConnection, AverageantiIdeaConnection)
        ExpectedInfection_average.append(y2)

        y3 = statistics(i, ManyideaConnection, FewantiIdeaConnection)
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


    x_ticks = np.arange(0, 42, 5)
    y_ticks = np.arange(0.0, 6.2, 0.5)
    plt.xticks(x_ticks)
    plt.yticks(y_ticks)


    plt.legend()  # 显示图例
    plt.grid()
    plt.xlabel('messages')
    plt.ylabel('Expected Infection')
    plt.show()


# dict=DTMC_Transition(numberOfNodes,probability_value,ideaConnection,antiIdeaConnection,number_Of_SimulationTimes, edges)
# print("*****************************************\n",dict)
#statistics()

# r = get_expected_infection(10)
# print('Expected Infection: ',r)

output_graph()