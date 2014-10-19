#! /usr/bin/env python
import re
#import getopt, sys
import argparse
import os
import time

NEW_LINE="\n"
FILE_NAME = "tmp.dot"
GRAPH_HEADER = "graph i {\nnode [shape=\"none\"]\nrankdir=LR\n"
GRAPH_FOOTER = "}\n"
TABLE_MAIN_HEADER = "Tab [label =<<TABLE BORDER=\"0\" CELLBORDER=\"0\" CELLSPACING=\"0\" CELLPADDING=\"0\">"
TABLE_MAIN_FOOTER = "</TABLE>>]"
TABLE_HELP_BEGIN="<TABLE BORDER=\"0\" CELLBORDER=\"0\" CELLSPACING=\"1\" CELLPADDING=\"0\">"
TABLE_HELP_END="</TABLE>"
TR_BEGIN="<TR>"
TR_END="</TR>"
TD_BEGIN="<TD>"
TD_END="</TD>"

class ProcMapElement :
    def __init__(self, addrB_, addrE_, perm_, offset_, dev_, inode_, name_):
        self.addrB = int(addrB_, 16)
        self.addrE = int(addrE_, 16)
        self.perm = perm_
        self.offset = offset_
        self.dev = dev_
        self.inode = inode_
        self.name = name_

def generateTdTop(addr) :
    return "<TR><TD VALIGN=\"TOP\" ALIGN=\"LEFT\"><FONT POINT-SIZE=\"4\">"+hex(addr).rstrip("L")+"</FONT></TD></TR>"

def generateTdMiddle(height, data=str()) :
    return "<TR><TD ALIGN=\"LEFT\" HEIGHT=\""+ str(height)+"\">"+data+"</TD></TR>"

def generateTdBottom(addr) :
    return "<TR><TD VALIGN=\"BOTTOM\" ALIGN=\"LEFT\"><FONT POINT-SIZE=\"4\">"+hex(addr).rstrip("L")+"</FONT></TD></TR>"

def generateSegment(data=str()) :
    return "<TD BORDER=\"1\">"+data+"</TD>"

def generateRow(begin, end, data=str(), height=0) :
    if height>100:
        height=100
    return NEW_LINE+TR_BEGIN+NEW_LINE+generateSegment(data)+NEW_LINE+TD_BEGIN+NEW_LINE+TABLE_HELP_BEGIN+generateTdTop(end)+generateTdMiddle(height)+generateTdBottom(begin)+TABLE_HELP_END+NEW_LINE+TD_END+TR_END+NEW_LINE

def generateUnused(addrB, addrE):
    return ProcMapElement(addrB, addrE, "----", 0, 0, 0, "unused")

def fillHoles(elements):
    copy = elements
    for i in range(1, len(elements)+1, 2):
        if elements[i-1].addrB != elements[i].addrE:
            copy.insert(i, generateUnused(hex(elements[i].addrE)[2:-1], hex(elements[i-1].addrB)[2:-1]))
    return copy 

def getSegmentsList(procFile) :
    stack = list()
    try:
        fP = open(procFile, "r")

        for line in fP:
            res = line.split();
            address = res[0]
            addrBegin, addrEnd = address.split("-")
            perms = res[1]
            offset = res[2]
            dev = res[3]
            inode = res[4]
            pathname = str()
            if len(res) > 5 :
                pathname = res[5]
            e = ProcMapElement(addrBegin, addrEnd, perms, offset, dev, inode, pathname)
            stack.append(e)
        fP.close()

    except IOError:
        print "Problem with ("+procFile+") file. Is the process still running??"
        exit(1)

    if (len(stack) == 0):
        print "Problem with ("+procFile+") file. It seems to be empty (or wrong format)!!!"
        exit(1)

    return stack

def formSegments(stack):
    #order in maps file is reversed
    stack.reverse();
    stack = fillHoles(stack)

def generateDot(stack):
    dotContent = str();
    dotContent = GRAPH_HEADER + TABLE_MAIN_HEADER
    for last in stack :
        dotContent += generateRow(last.addrB, last.addrE, last.name+"<BR/>"+last.perm, (last.addrE-last.addrB)/4096)
    dotContent += TABLE_MAIN_FOOTER+GRAPH_FOOTER

    return dotContent

def saveOutputFile(outFile, content):
    f = open(outFile,"w")
    f.write(content)
    f.close();

def main():
    pid="self"

    parser = argparse.ArgumentParser()
    #group1 = parser.add_mutually_exclusive_group()
    #group1.add_argument("-p", "--pid", type=int, help="process id nr")
    #group1.add_argument("-n", "--name", help="process name")
    parser.add_argument("-p", "--pid", type=int, help="process id nr")
    args = parser.parse_args()

    if args.pid:
        pid=str(args.pid)
    #if args.name:
    #    pid=args.name
        
    procFile="/proc/"+pid+"/maps"
    
    segments = getSegmentsList(procFile)
    
    formSegments(segments)

    dotContent = generateDot(segments)

    outFile = pid+"_"+str((time.time()))+".dot"
    saveOutputFile(outFile, dotContent)
    
    print "Out saved to", outFile

if __name__ == "__main__":
    main()
