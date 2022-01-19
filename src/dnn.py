"""
Discrete neural net
"""

import numpy as np
import random as rand
from graphviz import Graph
from typing import TypeVar, Generic, Callable


U = TypeVar('T') # U stands for universe


class Op(Generic[U]):
    

    def __init__(self, arity:int, func:Callable[[list[U]],U], name:str='unknown'):
        self.arity = arity
        self.func = func
        self.name = name
        

    def eval(self, args:list[U]) -> U:
        return self.func(*args)

    
    def __str__(self) -> str:
        return self.name
    

    def arity(self) -> int :
        return self.arity


class Neuron(Generic[U]):
    

    def __init__(self, in_edges) -> None:
        self.in_edges = in_edges
        

    def set_op(self, operation:Op[U]) -> None:
        self.op = operation
        

    def activate(self, inputs:list[U]) -> U:
        self.value = self.op.eval(inputs)
        return self.value

    
    def __str__(self):
        return str(self.op)

    
    def value(self) -> U:
        return self.value


class NeuralNet(Generic[U]):

    
    def __init__(self, arity:int, architecture:list[list[list[int]]], neighborhood_func:Callable[[Op[U]],list[Op[U]]], loss_func:Callable[[Op[U],Op[U]],float]):
        """
        Parameters
        ----------
        architecture : architecture[i][j] is the list of in-edges from the previous layer for jth neuron at ith layer. Input edges not included
        neighborhood_func : Takes an operation on U and returns a list of neighbor operations
        loss_func : Loss function
        """
        self.nbhd_func = neighborhood_func
        self.loss_func = loss_func
        self.arity = arity
        self.layers = [[Neuron[U](n) for n in l] for l in architecture]

        
    def layer_at(self, i:int) -> list[Neuron[U]]:
        return self.layers[i]

    
    def feed_forward(self, args:list[U]) -> U:
        self.input_layer = tuple(x for x in args)
        for neuron in self.layer_at(0):
            input = [args[k] for k in neuron.in_edges]
            neuron.activate(input)
        for i in range(1, len(self.layers)):
            for neuron in self.layer_at(i):
                input = [args[k] for k in neuron.in_edges]
                neuron.activate(input)
        return self.layer_at(len(self.layers)-1)[0].value

    
    def to_graphviz(self, graph_name:str) -> Graph:
        g = Graph(comment=graph_name)
        g.attr('graph', splines='false', rankdir='LR', ranksep='1.4')
        with g.subgraph(name='cluster_0') as c: # input cluster
            c.attr(color='none', label='input', rank='same')
            for j, var in enumerate(self.input_layer):
                c.node('0_'+str(j), label=str(var), shape='square')
        for i in range(len(self.layers)-1):
            id = str(i+1)
            with g.subgraph(name="cluster_"+id) as c:
                c.node_attr['style'] = 'filled'
                c.node_attr['color'] = 'lightblue'
                c.attr(color='none', label='L'+id, rank='same')
                for j, neuron in enumerate(self.layer_at(i)):
                    c.node(id+'_'+str(j), label=str(neuron), shape='circle')
                    id_neuron = id+'_'+str(j)
                    for k in neuron.in_edges:
                        c.edge(str(i)+'_'+str(k), id_neuron)
        i = len(self.layers)-1
        with g.subgraph(name='cluster_'+str(i+1)) as c: # output cluster
            c.attr(color='none', label='output')
            for j, neuron in enumerate(self.layer_at(i)):
                c.node(str(i+1)+'_'+str(j), label=str(neuron), shape='circle')
                id_neuron = str(i+1)+'_'+str(j)
                for k in neuron.in_edges:
                    c.edge(str(i)+'_'+str(k), id_neuron)
        return g
