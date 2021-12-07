#!/usr/bin/env python
# coding: utf-8

#############################################
#           FRAGMENTATOR                    #
#############################################
#
#Generates a pseudo orca input from a PDB file
# containing a molecular cluster. 
#
#The program is not general yet. It only works
#if the molecules are all of the same size
#
#Call:
#
#   ./fragmentator.py <inputfile.pdb> <molSize> <fragNum>
#
# molSize: number of atoms per molecule
#
# fragNum: total number of fragments (molecules)
#
#
#imports
import sys
import math
from tqdm import tqdm
from time import sleep


## parameters needed
#molSize=34 # number of atoms per molecule
#fragNum=14 # number of fragments

#input file (pdb file)
ifile=sys.argv[1]

#parameters
molSize=sys.argv[2]
fragNum=sys.argv[3]


#            #
# READ INPUT #
#            #
with open(ifile, "r") as f:
    input_list = f.read().splitlines()

l = [x for x in input_list[2:] if 'CONECT' in x]
l2 = [x for x in input_list[2:] if 'HETATM' in x]

#
# Definitions
#
##parse input lists
def pdb_parse(l1, l2):
    connectivity=[[int(i) for i in line.split()[1:]] for line in l1 ]
    atomList=[[i for i in line.split()[1:]] for line in l2 ]

    for atom in atomList:
        atom[0]=int(atom[0])
        atom[1]=atom[-1]
        del atom[5:]
    return connectivity, atomList

def create_frag_dictionary(fragNum):
    fragDict=dict()
    for i in range(fragNum):
        fragDict['frag{}'.format(i)]=None
    return fragDict

# FRAGMENTATION
# Parameters: connectivity : list
#                             list of atoms connections parsed from a PDB file
#             molSize : int
#                      number of atoms per molecule
#             fragNum : int
#                     number of fragments
# Returns:    fragments: dict
#                     dictionary of atoms divided by fragment
#
# NOTE: it's not yet general, only works for molecules of the same size
#
def fragmentation(connectivity, molSize, fragNum):
    fragments=create_frag_dictionary(fragNum)

    count=0

    while len(connectivity)>1:
        newList=connectivity[0]
        while(len(set(newList))<molSize):
            fragment=[]
            for i in newList:
                for j in connectivity:
                    if i in j:
                        fragment.append(j)
    #         fragment

            #create unique set of atoms assigned to fragment
            newList=[]
            for i in fragment:
                for j in i:
                    newList.append(j)
            set(newList)

        #remove assigned lines from connectivity
        for atom in newList:
            [connectivity.remove(line) for line in connectivity if atom in line]
    #     print(set(newList))
        fragments['frag{}'.format(count)]=set(newList)
        count+=1
        print('step {0} / {1}'.format(count, fragNum))
    return fragments

# Assigns atoms to fragments based on a pregenerated fragment dictionary
# Parameters: atomList: list
#                     list of atoms. Generated by pdb_parse()
#             fragments: dict
#                     dictionary of fragments, as output by fragmentation()
# Returns: atomList: list
#                     updated with fragmets for each atom
#
def assign_frags(atomList, fragments):
    for atom in atomList:
        for key in fragments.keys():
            if atom[0] in fragments.get(key):
                atom.append(key)
    return atomList

#
# CALLS
# 

connectivity, atomList=pdb_parse(l,l2)
fragments=fragmentation(connectivity, 34, 14)
atomList=assign_frags(atomList, fragments)

#
# WRITE OUTPUT
#

with open('fragmented_orca.inp', 'w') as ofile:
    ofile.write('! input line \n\n\n')
    ofile.write('*xyz 0 1 \n')
    for atom in atomList:
        formattedFrag=int(atom[5][4:])+1
        ofile.write(atom[1]+ ' '+ ' (' +str(formattedFrag)+ ') ' +atom[2]+ ' ' +atom[3]+ ' ' +atom[4]+'\n')
    ofile.write('*')
