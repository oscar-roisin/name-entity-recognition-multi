class Node:
    """
    A class to represent the nodes in SCRDR tree
    """

    def __init__(self, condition, conclusion, father = None, exceptChild = None, elseChild = None, cornerstoneCases = [], depth = 0):
        self.condition = condition
        self.conclusion = conclusion
        self.exceptChild = exceptChild
        self.elseChild = elseChild
        self.cornerstoneCases = cornerstoneCases
        self.father = father 
        self.depth = depth
        
    def satisfied(self, object):
        return eval(self.condition)
    
    def executeConclusion(self, object):
        exec(self.conclusion)        
        
    def appendCornerstoneCase(self, object):
        self.cornerstoneCases.append(object)
        
    def check(self, object):
        if self.satisfied(object):
            self.executeConclusion(object)
            if self.exceptChild != None:
                self.exceptChild.check(object)
        else:
            if self.elseChild != None:
                self.elseChild.check(object)
                
    def checkDepth(self, object, length):
        if self.depth <= length:
            if self.satisfied(object):
                self.executeConclusion(object)
                if self.exceptChild != None:
                    self.exceptChild.checkDepth(object, length)
            else:
                if self.elseChild != None:
                    self.elseChild.checkDepth(object, length)
                           
    def findRealFather(self):
        node = self
        fatherNode = node.father
        while True and fatherNode != None:
            if fatherNode.exceptChild == node:
                break
            node = fatherNode 
            fatherNode = node.father
        return fatherNode
    
    def addElseChild(self, node):
        fatherNode = self.findRealFather()
        for object in fatherNode.cornerstoneCases:
            if node.satisfied(object):
                print("The new rule fires the cornerstone cases of its father node!!!")
                self.findRealFather().cornerstoneCases.remove(object)
        self.elseChild = node
        return True
        
    def addExceptChild(self, node):
        for object in self.cornerstoneCases:
            if node.satisfied(object):
                print("The new rule fires the cornerstone cases of its father node!!!")
                self.cornerstoneCases.remove(object)
        self.exceptChild = node
        return True
    
    def writeToFileWithSeenCases(self, out, depth):
        space = tabStr(depth)        
        out.write(space + self.condition + " : " + self.conclusion + "\n")
        for case in self.cornerstoneCases:
            out.write(" " + space + "cc: " + case.toStr() + "\n")
        if self.exceptChild != None:
            self.exceptChild.writeToFile(out, depth + 1)
        if self.elseChild != None:
            self.elseChild.writeToFile(out, depth)
    
    def writeToFile(self, out, depth):
        space = tabStr(depth)        
        out.write(space + self.condition + " : " + self.conclusion + "\n")
        if self.exceptChild != None:
            self.exceptChild.writeToFile(out, depth + 1)
        if self.elseChild != None:
            self.elseChild.writeToFile(out, depth)
            
def tabStr(length):
    return "".join(["\t"] * length)

# -*- coding: utf-8 -*-

class Object:
    attributes = ["word",
                  "tag",
                  "prevWord2",
                  "prevWord1",
                  "nextWord1",
                  "nextWord2",
                  "prevTag2",
                  "prevTag1",
                  "nextTag1",
                  "nextTag2",
                  "suffixL2",
                  "suffixL3",
                  "suffixL4"]
    code = "def __init__(self"
    for att in attributes:
        code = code + ", " + att + " = None"
    code = code + "):\n"
    for att in attributes:
        code = code + "    self." + att + "=" + att + "\n"
                
    exec(code)
    
    def toStr(self):
        res = "("
        for att in Object.attributes:
            boo = eval("isinstance(self. " + att + ", str)")
            if not boo:
                res = res + str(eval("self." + att))
            else:
                res = res + "\"" + str(eval("self." + att)) + "\""
                
            if att != Object.attributes[len(Object.attributes) - 1]:
                res = res + ","
        res += ")"
        return res

def getWordTag(wordTag):
    if wordTag == "///":
        return "/", "/"
    index = wordTag.rfind("/")
    if index == -1:
        return None, None
    word = wordTag[:index].strip()
    tag = wordTag[index + 1:].strip()
    return word, tag

def getObject(wordTags, index):#Sequence of "Word/Tag"
    word, tag = getWordTag(wordTags[index])
    preWord1 = preTag1 = preWord2 = preTag2 = "" 
    nextWord1 = nextTag1 = nextWord2 = nextTag2 = "" 
    suffixL2 = suffixL3 = suffixL4 = ""
    
    decodedW = word
    if len(decodedW) >= 4:
        suffixL3 = decodedW[-3:]
        suffixL2 = decodedW[-2:]
    if len(decodedW) >= 5:
        suffixL4 = decodedW[-4:]
    
    if index > 0:
        preWord1, preTag1 = getWordTag(wordTags[index - 1])
    if index > 1:
        preWord2, preTag2 = getWordTag(wordTags[index - 2])
    if index < len(wordTags) - 1:
        nextWord1, nextTag1 = getWordTag(wordTags[index + 1]) 
    if index < len(wordTags) - 2:
        nextWord2, nextTag2 = getWordTag(wordTags[index + 2]) 
    
    return Object(word, tag, preWord2, preWord1, nextWord1, nextWord2, preTag2, preTag1, nextTag1, nextTag2, suffixL2, suffixL3, suffixL4)
 
def getObjectDictionary(initializedCorpus, goldStandardCorpus):
    goldStandardSens = open(goldStandardCorpus, "r").readlines()
    initializedSens = open(initializedCorpus, "r").readlines()
    
    objects = {}
    
    j = 0
    for i in range(len(initializedSens)):
        init = initializedSens[i].strip()
        if len(init) == 0:
            continue
        
        while j < len(goldStandardSens) and goldStandardSens[j].strip() == "":
            j += 1
            
        if j >= len(goldStandardSens):
            continue
        
        gold = goldStandardSens[j].strip()
        j += 1

        initWordTags = init.replace("“", "''").replace("”", "''").replace("\"", "''").split()
        goldWordTags = gold.replace("“", "''").replace("”", "''").replace("\"", "''").split()
        
        for k in range(len(initWordTags)):
            initWord, initTag = getWordTag(initWordTags[k])
            goldWord, correctTag = getWordTag(goldWordTags[k])
            
            if initWord != goldWord:
                print("\nERROR (Raw texts are mismatched || Some sentence is incorrectly formatted):")
                print(str(i+1) + "th initialized sentence:   " + " ".join(initWordTags))
                print(str(i+1) + "th gold standard sentence: " + " ".join(goldWordTags))
                return None
            
            if initTag not in objects.keys():
                objects[initTag] = {}
                objects[initTag][initTag] = []
                
            if correctTag not in objects[initTag].keys():
                objects[initTag][correctTag] = []
                
            objects[initTag][correctTag].append(getObject(initWordTags, k))
    
    return objects

class FWObject:
    """
    RDRPOSTaggerV1.1: new implementation scheme
    RDRPOSTaggerV1.2: add suffixes
    """
    
    def __init__(self, check = False):
        self.context = [None, None, None, None, None, None, None, None, None, None, None, None, None]
        if(check == True):
            i = 0
            while (i < 10):
                self.context[i] = "<W>"
                self.context[i + 1] = "<T>"
                i = i + 2
            self.context[10] = "<SFX>"# suffix
            self.context[11] = "<SFX>"
            self.context[12] = "<SFX>"
        self.notNoneIds = []
        
    @staticmethod
    def getFWObject(startWordTags, index):
        object = FWObject(True)
        word, tag = getWordTag(startWordTags[index])
        object.context[4] = word
        object.context[5] = tag
        
        decodedW = word
        if len(decodedW) >= 4:
            object.context[10] = decodedW[-2:]
            object.context[11] = decodedW[-3:]
        if len(decodedW) >= 5:
            object.context[12] = decodedW[-4:]
        
        if index > 0:
            preWord1, preTag1 = getWordTag(startWordTags[index - 1])
            object.context[2] = preWord1
            object.context[3] = preTag1
            
        if index > 1:
            preWord2, preTag2 = getWordTag(startWordTags[index - 2])
            object.context[0] = preWord2
            object.context[1] = preTag2
        
        if index < len(startWordTags) - 1:
            nextWord1, nextTag1 = getWordTag(startWordTags[index + 1]) 
            object.context[6] = nextWord1
            object.context[7] = nextTag1
            
        if index < len(startWordTags) - 2:
            nextWord2, nextTag2 = getWordTag(startWordTags[index + 2])
            object.context[8] = nextWord2
            object.context[9] = nextTag2 
           
        return object
    
#    def isSatisfied(self, fwObject):
#        for i in range(13):
#            key = self.context[i]
#            if (key is not None):
#                if key != fwObject.context[i]:
#                    return False
#        return True

class SCRDRTree:
    """
    Single Classification Ripple Down Rules tree for Part-of-Speech and morphological tagging
    """
    
    def __init__(self, root = None):
        self.root = root
                            
    def findDepthNode(self, node, depth):
        while node.depth != depth:
            node = node.father
        return node                
                
    def classify(self, object):
        self.root.check(object)
        
    def writeToFileWithSeenCases(self, outFile):
        out = open(outFile, "w")
        self.root.writeToFileWithSeenCases(out, 0)
        out.close()
    
    def writeToFile(self, outFile):
        out = open(outFile, "w")
        self.root.writeToFile(out, 0)
        out.close()
    
    #Build tree from file containing rules using FWObject
    def constructSCRDRtreeFromRDRfile(self, rulesFilePath):
        
        self.root = Node(FWObject(False), "NN", None, None, None, [], 0)
        currentNode = self.root
        currentDepth = 0
        
        rulesFile = open(rulesFilePath, "r")
        lines = rulesFile.readlines()
        
        for i in range(1, len(lines)):
            line = lines[i]
            depth = 0           
            for c in line:
                if c == '\t':
                    depth = depth + 1
                else:
                    break

            line = line.strip()
            if len(line) == 0:
                continue
                
            temp = line.find("cc")
            if temp == 0:   
                continue
            
            condition = getCondition(line.split(" : ", 1)[0].strip())
            conclusion = getConcreteValue(line.split(" : ", 1)[1].strip())
            
            node = Node(condition, conclusion, None, None, None, [], depth)
            
            if depth > currentDepth:
                currentNode.exceptChild = node
            elif depth == currentDepth:
                currentNode.elseChild = node
            else:
                while currentNode.depth != depth:
                    currentNode = currentNode.father
                currentNode.elseChild = node
            
            node.father = currentNode
            currentNode = node
            currentDepth = depth
    
    def findFiredNode(self, fwObject):
        currentNode = self.root
        firedNode = None
        obContext = fwObject.context
        while True:
            #Check whether object satisfying the current node's condition
            cnContext = currentNode.condition.context
            notNoneIds = currentNode.condition.notNoneIds
            satisfied = True
            for i in notNoneIds:
                if cnContext[i] != obContext[i]:
                    satisfied = False
                    break
                    
            if(satisfied):
                firedNode = currentNode
                exChild = currentNode.exceptChild
                if exChild is None:
                    break
                else:
                    currentNode = exChild
            else:
                elChild = currentNode.elseChild
                if elChild is None:
                    break
                else:
                    currentNode = elChild
        return firedNode

def getConcreteValue(str):
    if str.find('""') > 0:
        if str.find("Word") > 0:
            return "<W>"
        elif str.find("suffixL") > 0:
            return "<SFX>"
        else:
            return "<T>"
    return str[str.find("\"") + 1 : len(str) - 1]
       
def getCondition(strCondition):
    condition = FWObject(False)
    for rule in strCondition.split(" and "):
        rule = rule.strip()
        key = rule[rule.find(".") + 1 : rule.find(" ")]
        value = getConcreteValue(rule)
             
        if key == "prevWord2": 
            condition.context[0] = value
        elif key == "prevTag2":
            condition.context[1] = value
        elif key == "prevWord1":
            condition.context[2] = value
        elif key == "prevTag1":
            condition.context[3] = value
        elif key == "word":
            condition.context[4] = value
        elif key == "tag":
            condition.context[5] = value
        elif key == "nextWord1":
            condition.context[6] = value
        elif key == "nextTag1":
            condition.context[7] = value
        elif key == "nextWord2":
            condition.context[8] = value
        elif key == "nextTag2":
            condition.context[9] = value
        elif key == "suffixL2":
            condition.context[10] = value
        elif key == "suffixL3":
            condition.context[11] = value
        elif key == "suffixL4":
            condition.context[12] = value
    for i in range(13):
        if condition.context[i] is not None:
            condition.notNoneIds.append(i)        
    return condition


import re

def initializeSentence(FREQDICT, sentence):
    words = sentence.strip().split()
    taggedSen = []
    for word in words:
        if word in ["“", "”", "\""]:
            #taggedSen.append("''/" + FREQDICT["''"])
            if "''" in FREQDICT:
                taggedSen.append("''/" + FREQDICT["''"])
            elif "." in FREQDICT:
                taggedSen.append("''/" + FREQDICT["."])
            elif "," in FREQDICT:
                taggedSen.append("''/" + FREQDICT[","])
            else:
                print("\n'' is not in the dictionary \nManually add '' with a possible POS tag into the .DICT file!")
                taggedSen.append("''/" + FREQDICT["''"])   
            continue
        
        tag = ''
        decodedW = word
        lowerW = decodedW.lower()
        if word in FREQDICT:
            tag = FREQDICT[word]
        elif lowerW in FREQDICT:
            tag = FREQDICT[lowerW]
        else:
            if re.search(r"[0-9]+", word) != None:
                tag = FREQDICT["TAG4UNKN-NUM"]
            else:
                suffixL2 = suffixL3 = suffixL4 = suffixL5 = None
                wLength = len(decodedW)
                if wLength >= 4:
                    suffixL3 = ".*" + decodedW[-3:]
                    suffixL2 = ".*" + decodedW[-2:]
                if wLength >= 5:
                    suffixL4 = ".*" + decodedW[-4:]
                if wLength >= 6:
                    suffixL5 = ".*" + decodedW[-5:]
                
                if suffixL5 in FREQDICT:
                    tag = FREQDICT[suffixL5]
                elif suffixL4 in FREQDICT:
                    tag = FREQDICT[suffixL4] 
                elif suffixL3 in FREQDICT:
                    tag = FREQDICT[suffixL3]
                elif suffixL2 in FREQDICT:
                    tag = FREQDICT[suffixL2]
                elif decodedW[0].isupper():
                    tag = FREQDICT["TAG4UNKN-CAPITAL"]
                else:
                    tag = FREQDICT["TAG4UNKN-WORD"]
           
        taggedSen.append(word + "/" + tag)                                
    
    return " ".join(taggedSen)

def initializeCorpus(FREQDICT, inputFile, outputFile):
    lines = open(inputFile, "r").readlines()
    fileOut = open(outputFile, "w")
    for line in lines:
        fileOut.write(initializeSentence(FREQDICT, line) + "\n")
    fileOut.close()

class RDRPOSTagger(SCRDRTree):
    """
    RDRPOSTagger for a particular language
    """
    def __init__(self):
        self.root = None
    
    def tagRawSentence(self, DICT, rawLine):
        line = initializeSentence(DICT, rawLine)
        sen = []
        wordTags = line.split()
        for i in range(len(wordTags)):
            fwObject = FWObject.getFWObject(wordTags, i)
            word, tag = getWordTag(wordTags[i])
            node = self.findFiredNode(fwObject)
            if node.depth > 0:
                sen.append(word + "/" + node.conclusion)
            else:# Fired at root, return initialized tag
                sen.append(word + "/" + tag)
        return " ".join(sen)

    def tagRawCorpus(self, DICT, rawCorpusPath):
        lines = open(rawCorpusPath, "r").readlines()
        #Change the value of NUMBER_OF_PROCESSES to obtain faster tagging process!
        pool = Pool(processes = NUMBER_OF_PROCESSES)
        taggedLines = pool.map(unwrap_self_RDRPOSTagger, zip([self] * len(lines), [DICT] * len(lines), lines))
        outW = open(rawCorpusPath + ".TAGGED", "w")
        for line in taggedLines:
            outW.write(line + "\n")  
        outW.close()
        print("\nOutput file: " + rawCorpusPath + ".TAGGED")


def getWordTag(wordTag):
    if wordTag == "///":
        return "/", "/"
    index = wordTag.rfind("/")
    if index == -1:
        return wordTag, None
    word = wordTag[:index].strip()
    tag = wordTag[index + 1:].strip()
    return word, tag

def getRawText(inputFile, outFile):
    out = open(outFile, "w")
    sents = open(inputFile, "r").readlines()
    for sent in sents:
        wordTags = sent.strip().split()
        for wordTag in wordTags:
            word, tag = getWordTag(wordTag)
            out.write(word + " ")
        out.write("\n")
    out.close()
    
def readDictionary(inputFile):
    dictionary = {}
    lines = open(inputFile, "r").readlines()
    for line in lines:
        wordtag = line.strip().split()
        dictionary[wordtag[0]] = wordtag[1]
    return dictionary
