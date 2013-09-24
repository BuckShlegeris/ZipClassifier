#!/usr/bin/python3

# ZipClassifier.py
# Buck Shlegeris, 2013

# This is a program which does tree clustering using the gzip compressor.
# I wrote it because I couldn't figure out how to install CompLearn.

# Usage: ./ZipClassifier.py [list of files to compare]

from subprocess import call
from os.path import getsize
from sys import argv

############## Compression related stuff
def zipsize(string):
    open("tempZipClassifier",'wb').write(string)
    call(["gzip","tempZipClassifier", "--best", "-f"])
    answer = getsize("tempZipClassifier.gz")
    return answer

def normalized_compression_distance(x,y):
    Cx, Cy = zipsize(x), zipsize(y)
    return (zipsize(x+y)-min(Cx,Cy))/max(Cx,Cy)

def similarity(file_name_1,file_name_2):
    str1 = open(file_name_1,"rb").read()
    str2 = open(file_name_2,"rb").read()
    return normalized_compression_distance(str1,str2)

################ Tree related stuff

def equivalent(inlist,x,y):
    for a in inlist:
        if x in a:
            return y in a

def make_equivalent(inlist,x,y):
    newList= set()
    for a in inlist:
        if x in a:
            newList = newList.union(a)
        if y in a:
            newList = newList.union(a)
    out = [eqClass for eqClass in inlist if x not in eqClass 
                                        and y not in eqClass]+[newList]
    return out
    

def get_pairs(similarity_matrix):
    partition = list({x} for x in range(len(similarity_matrix)))

    def closest_pair():
        minDist = 9999999999
        minPlace = None
        for (posx,row) in enumerate(similarity_matrix):
            for (posy, val) in enumerate(row):
                if not equivalent(partition,posx,posy) and val<minDist:
                    minDist = val
                    minPlace = (posx,posy)
        posx,posy = minPlace
        newPart = make_equivalent(partition,posx,posy)
        return (minPlace, newPart)
       
    outlist = []

    while True:
        try:
            new_pair, partition = closest_pair()
            outlist.append(new_pair)
        except TypeError:
            return outlist

##### I wrote this bit in Haskell and translated it over, so the camelCase is
#  acceptable :)    
def inTree(x,tree):
    if tree[0]=="Leaf":
        return x==tree[1]
    else:
        return inTree(x,tree[1]) or inTree(x,tree[2])

def mergeBranches(pair,forest):
    a,b = pair    
    for tree in forest:
        if inTree(a,tree):
            aTree = tree
        if inTree(b,tree):
            bTree = tree
    return [("Node",aTree,bTree)]+[x for x in forest if x not in [aTree,bTree]]

def makeTree(pairs):
    forest = [("Leaf",z) for z in range(max(max(x,y) for (x,y) in pairs)+1)]
    for pair in pairs:
        forest = mergeBranches(pair,forest)
    return forest[0]


## This is the main function
def treeify(similarity_matrix):
    return makeTree(get_pairs(similarity_matrix))

def name_tree(tree,names):
    return tree_to_string(tree).format(*names)

def tree_to_string(tree):
    if tree[0]=="Leaf":
        return "{%d}"%tree[1]
    else:
        return "("+tree_to_string(tree[1])+" "+tree_to_string(tree[2])+")"

#################### Main function and stuff

def make_tree(inlist):
    similarity_matrix = [[similarity(x,y) for x in inlist] for y in inlist]
    #print(similarity_matrix)
    return treeify(similarity_matrix)

def example():
    animals = ["blueWhale","chimpanzee","graySeal","horse","mouse", 
                   "cat","finWhale","harborSeal","human","rat"]

    print(name_tree(
        make_tree(["examples/10-mammals/"+x+".txt" for x in animals]),animals))


if __name__ == "__main__":
    names = [x for x in argv[1:] if "tempZipClassifier" not in x]
    print(name_tree(make_tree(names),names))
