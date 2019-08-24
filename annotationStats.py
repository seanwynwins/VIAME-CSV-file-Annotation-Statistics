# -*- coding: utf-8 -*-
"""
"""
from __future__ import division
import csv
import matplotlib.pyplot as plt
import re
#import xlwt 
from xlwt import Workbook

# initial trackID
trackID = -1
# keeps track of the number of each species per frame
species_data = {}
excelFile = input("Enter name of CSV file: ")
# keeps track of community count
community_data = [0]
# keeps count of number of tracks
track_statistics = {}
# keeps count of number of tracks in a family, if user wants
family_track_statistics = {}
# default number of frames per second
fps = 1
# keeps track if frames per second has been asked yet, so you don't have
# to do it more than once
hasbeenCalled = 0
# keeps track of species with phases (terminal, intial, juvenile) to prevent 
# double counting when calculating community MaxN
specieswithPhases = []
# phase identifier, in the form Genus_species_phase
phrase = ".*_{1}.*_{1}.+"
# identifies if only family is present, ex: Acanthurus, wrasse
familyOnly = "^[^_]*$"
# bc i misspelled this whoops
cephalophol = "Cephalophol(?!is)"
# if you want data by family
family_dictionary = {}
# how many times specific graphs are called
specificCallCount = 0

def processCSVFile(row):
    if len(row) > 3 and row[0].isdigit():
        global trackID
        global phrase
        
        oldTrackID = trackID            
        trackID = row[0]  
    
        frameNumber = int("".join(filter(str.isdigit, row[2])))
        
        # is there even a species?
        if len(row) > 9:
            # is there a phase
            if re.match(phrase, row[9]):
                 # so i mispelled cephalopholis_fulva as cephalophol_fulva for
                 # bicolor, correcting this
                 if re.match(cephalophol, row[9]):
                     phase = re.sub('Cephalophol', 'Cephalopholis', row[9])
                     species = re.sub('_[^_]*$', '', phase)
                 else: 
                    species = re.sub('_[^_]*$', '', row[9])
                    phase = row[9]
                    
                 if not species in specieswithPhases:
                     specieswithPhases.append(species)
            else:
                species = row[9]
                phase = None
        else:
            species = "Unknown"
            phase = None
        
        # add contents of row to dictionary
        if not species in species_data:
            track_statistics[species] = 0
            species_data[species] = [0]
                    
        
        # need to append 0's because this thing is weird
        for x in range(len(species_data[species]), frameNumber + 1):
            species_data[species].append(0)
        
        #increment values
        species_data[species][frameNumber] += 1
                
        # add phases if necessary
        if phase:
            if not phase in species_data:
                track_statistics[phase] = 0
                species_data[phase] = [0]
            
            # need to append 0's because this thing is weird
            for x in range(len(species_data[phase]), frameNumber + 1):
                species_data[phase].append(0)
            
            species_data[phase][frameNumber] += 1
        
        if oldTrackID != trackID:
            if phase:
                track_statistics[phase] += 1
                
            track_statistics[species] += 1
        
        # total count
        for x in range(len(community_data), frameNumber + 1):
            community_data.append(0)
        
        community_data[frameNumber] += 1;

# read the csv file
with open(excelFile) as csvfile:
    readCSV = csv.reader(csvfile)    
    # read each row
    for row in readCSV:
        if row:
            processCSVFile(row)
            
def framesPerSecond(): 
    global hasbeenCalled
    global fps
    
    if not hasbeenCalled:
        while True:
            fps = input('What are the frames per second? Enter an integer.')
            if fps.isdigit():
                break
    
    hasbeenCalled = 1

    return int(fps)

# might have to pass in specific figure
def convert():
     while True:
        time = input('Do you want to convert to seconds, minutes or frames? Enter s,m,or f: ')
        # scale x axis      
        if time == 's':
            plt.xlabel("Seconds")
            return framesPerSecond()                
        elif time == 'm':
            plt.xlabel("Minutes")
            return framesPerSecond() * 60            
        elif time == 'f':
            plt.xlabel("Frame Number")
            return 1
        
    
def speciesGraph():     
    
    # all data including individual species
    title = input('Title name? ')

    plt.figure(1)
    
    scale = convert()  
    
    while True:
        phases = input('For species with phases, do you want the\
                    individual phase breakdown, or the entire species count, or both? Enter [i or e or b]: ')
        # if someone knows how to combine these in an or statement w/o getting an error
        # i would be eternally grateful
        if phases == 'i':
             for species in sorted(species_data):
                # don't include species with phases
                if species not in specieswithPhases:
                    xAxis =  list(range(1, len(species_data[species]) + 1))
                    xAxis = [i/scale for i in xAxis]
                    plt.plot(xAxis, species_data[species], label = species)
             break
        elif phases == 'e':
            for species in sorted(species_data):
                # don't include phases
                if not re.match(".*_{1}.*_{1}.+", species):
                    xAxis =  list(range(1, len(species_data[species]) + 1))
                    xAxis = [i/scale for i in xAxis]
                    plt.plot(xAxis, species_data[species], label = species)
            break
        elif phases == 'b':
            for species in sorted(species_data):
                 xAxis =  list(range(1, len(species_data[species]) + 1))
                 xAxis = [i/scale for i in xAxis]
                 plt.plot(xAxis, species_data[species], label = species)
            break
             
    communityCool = input("Do you want a total sum included in the total species graph? Enter [y/anything else]: ")
    if communityCool == 'y':       
        xAxis = list(range(1, len(community_data) + 1))
        xAxis = [i/scale for i in xAxis]
        plt.plot(xAxis, community_data, label = "Community")
		
    plt.ylim(bottom=0)  # this line
    plt.xlim(left=0)
    plt.title(title)
    plt.ylabel("Species Count")
    plt.legend(loc= 'center left', bbox_to_anchor=(1, 0.5));
    plt.savefig(title + '.pdf',bbox_inches='tight')

def communityGraph():
    title = input('Title name? ')
    
    plt.figure(2)
    
    scale = convert()
    
    xAxis = list(range(1, len(community_data)+1))
    xAxis = [i/scale for i in xAxis]
    plt.plot(xAxis, community_data, label = "Community")

    # displays community line only
    plt.ylim(bottom=0)  # this line
    plt.ylim(top=max(community_data)*1.1)
    plt.xlim(left=0)  # this line
    plt.title(title)
    plt.ylabel("Species Count")
    plt.legend(loc= 'center left', bbox_to_anchor=(1, 0.5));
    plt.savefig(title + '.pdf',bbox_inches='tight')

# pass in list of specific species
def specificGraphs(specificList):
    global specificCallCount
    
    plt.figure(4 + specificCallCount)
    
    title = input('Title name? ')
    
    scale = convert()
    
    newCumulative = [0] * len(community_data)
    
    communityCool = input("Do you want a \"total\" line summing the counts of all the species (or families) you've included in this graph? Enter [y/anything else]: ")
    
    for species in sorted(species_data):
        if species not in family_dictionary:
            if species in specificList:
                xAxis =  list(range(1, len(species_data[species])+1))
                xAxis = [i/scale for i in xAxis]
                plt.plot(xAxis, species_data[species], label = species)
            
                if communityCool == 'y':
                    for j in range(0, len(species_data[species])):
                        # sum stuff obviously
                        newCumulative[j] += species_data[species][j]
    
    for family in sorted(family_dictionary):
        if family in specificList:
            xAxis = list(range(1, len(family_dictionary[family])+1))
            xAxis = [i/scale for i in xAxis]
            plt.plot(xAxis, family_dictionary[family], label = family)
            
            if communityCool == 'y':
                for j in range(0, len(family_dictionary[family])):
                    # sum stuff obviously
                    newCumulative[j] += family_dictionary[family][j]
    
    
    if communityCool == 'y':    
        xAxis = list(range(1, (len(community_data)+1)))
        xAxis = [i/scale for i in xAxis]
        plt.plot(xAxis, newCumulative, label = "Total")
    
    # displays community line only
    plt.ylim(bottom=0)  # this line
    plt.xlim(left=0)
    plt.title(title)
    plt.ylabel("Species Count")
    plt.legend(loc= 'center left', bbox_to_anchor=(1, 0.5));
    plt.savefig(title + '.pdf',bbox_inches='tight')
    specificCallCount += 1
    
# family dictionary maker
def familyDictionaryMaker(familyList):
    
    global track_statistics
    # make tracks here
    # one line in familyList is one family
    for line in familyList:
        familyXAxis = [0] * len(community_data)
        family = line.split()
        family_track_statistics[family[0]] = 0
        # individual species in family
        for species in family:
            if species in species_data:
                for j in range(0, len(species_data[species])):
                    # sum stuff obviously
                    familyXAxis[j] += species_data[species][j]
                    
                family_track_statistics[family[0]] += track_statistics[species]
        
        # family[0] is the first element in the array
        family_dictionary[family[0]] = familyXAxis
    
# if you want data by family
def familyGraphs(familyList):
    title = input('Title name? ')
    
    plt.figure(3)
    
    scale = convert()
    
    familyDictionaryMaker(familyList)
                
    # go through family_dictionary and plot
    for family in sorted(family_dictionary):
        xAxis =  list(range(1, len(family_dictionary[family]) + 1))
        xAxis = [i/scale for i in xAxis]
        plt.plot(xAxis, family_dictionary[family], label = family)          
        
    communityCool = input("Do you want a total sum included in the total family graph? Enter [y/anything else]: ")
    
    if communityCool == 'y':       
        xAxis = list(range(1, len(community_data) + 1))
        xAxis = [i/scale for i in xAxis]
        plt.plot(xAxis, community_data, label = "Total")
        
     # displays community line only
    plt.ylim(bottom=0)  # this line
    plt.xlim(left=0)
    plt.title(title)
    plt.ylabel("Family Count")
    plt.legend(loc= 'center left', bbox_to_anchor=(1, 0.5));
    plt.savefig(title + '.pdf',bbox_inches='tight')
        
def timeTable(maxNTable, familyFun):
    sheet3 = maxNTable.add_sheet('Species and Phases Time Record')
    sheet3.write(0, 0, "Frame Number")
    
    for i in range(1, len(community_data)):
        sheet3.write(i, 0, i)
        
    #rows: frames columns: frameNumber, then each species
    column = 1
    
    for species in sorted(species_data):
        sheet3.write(0, column, species)
        
        for i in range(1, len(species_data[species])):    
            sheet3.write(i, column, species_data[species][i])
            
        column += 1
    
    sheet3.write(0, column, "Total")
    
    for i in range(1, len(community_data)):
        sheet3.write(i, column, community_data[i])
        
    if familyFun == 'y':
        sheet4 = maxNTable.add_sheet('Family Time Record')
        sheet4.write(0, 0, "Frame Number")
        
        for i in range(1, len(community_data) + 1):
            sheet4.write(i, 0, i)
        
        column = 1
        
        for family in sorted(family_dictionary):
            sheet4.write(0, column, family)
        
            for j in range(1, len(family_dictionary[family])):    
                sheet4.write(j, column, family_dictionary[family][j])
            
            column += 1

# subphases or no subphases?
yeah = input("Do you want a graph containing all species? Enter [y/anything else]: ")
if yeah == 'y':
    speciesGraph()

yeah = input("Do you want a NEW graph containing just the community frequency?\
                   Enter [y/anything else]: ")
if yeah == 'y':
    communityGraph()

yeah = input("Do you want a graph with all families listed? Enter [y/anything else]: ")

# read text file
if yeah == 'y':
    # put family first
    textFile = input("Enter a text file. Species in the same family should be on the same line.\n")
    with open(textFile, 'r') as f:
       familyList = f.read().splitlines()
    familyGraphs(familyList)
    # specific families

while True: 
    yeah = input("Do you want a/another NEW graph containing specific species and/or families only? Enter [y/anything else]: ")

    if yeah == 'y':
        # if family_dictionary doesn't exist yet
        if len(family_dictionary) == 0:
            yayFamilies = input("Are you planning to plot specific families in this graph? Enter [y/anything else]: ")
            if yayFamilies == 'y':
                textFile = input("Enter a text file. Species in the same family should be on the same line.\n")
                with open(textFile, 'r') as f:
                    familyList = f.read().splitlines()
                familyDictionaryMaker(familyList)
        something = input("Enter species, families, and/or phases that you want to plot in one graph. Case matters.\n\n")
        specificGraphs(something.split())
    else: 
        break
    
title = input("What name do you want the MaxN file to have? ")
# column iterator
j = 0
# maxNTable
maxNTable = Workbook()
sheet1 = maxNTable.add_sheet('Species MaxN')
# species, maxN, time at which it is first reached in video
sheet1.write(0, 0, "Species Name")
sheet1.write(0, 1, "MaxN")
sheet1.write(0, 2, "MaxN Frame Number")
fps = framesPerSecond()
sheet1.write(0, 3, "MaxN Minutes")
sheet1.write(0, 4, "MaxN Seconds")
sheet1.write(0, 5, "Track Count")
sheet1.write(0, 6, "Track Percentage")

# row iterator
i = 1
# total tracks
totalTracks = 0
species_richness = 0
# sum everything except for species in species data
for track in track_statistics:
    if track not in specieswithPhases:
            totalTracks += track_statistics[track]

for species in sorted(species_data):
    # if species has subphases or family Only, skip when counting species richness 
    if not (re.match(phrase, species) or re.match(familyOnly, species)):
        species_richness += 1
    
    sheet1.write(i, 0, species)
    maxN = max(species_data[species])
    maxCount = species_data[species].index(maxN) #+ 1
    sheet1.write(i, 1, maxN)
    sheet1.write(i, 2, maxCount)
    sheet1.write(i, 3, maxCount / (60 * fps))
    sheet1.write(i, 4, maxCount / fps)
    sheet1.write(i, 5, track_statistics[species])
    sheet1.write(i, 6, track_statistics[species] / totalTracks)
    i += 1

maxCount = max(community_data)
maxN = community_data.index(maxCount) + 1

# community MaxN
sheet1.write(i, 0, "Community MaxN")
sheet1.write(i, 1, maxCount)
sheet1.write(i, 2, maxN)
sheet1.write(i, 3, maxN /(60 * fps))
sheet1.write(i, 4, maxN / fps)

# species richness
sheet1.write(i+1, 0, "Species Richness")
sheet1.write(i+1, 1, species_richness)

familyFun = input("Do you want the MaxN count for families? Enter [y/anything else]: ")
if familyFun == 'y':
    i = 1
    # if family_dictionary doesn't exist yet
    if len(family_dictionary) == 0:
        textFile = input("Enter a text file. Species in the same family should be on the same line.\n")
        with open(textFile, 'r') as f:
            familyList = f.read().splitlines()
        familyDictionaryMaker(familyList)
    sheet3 = maxNTable.add_sheet('Family MaxN')
    sheet3.write(0, 0, "Family Name")
    sheet3.write(0, 1, "MaxN")
    sheet3.write(0, 2, "MaxN Frame Number")
    sheet3.write(0, 3, "MaxN Minutes")
    sheet3.write(0, 4, "MaxN Seconds")
    sheet3.write(0, 5, "Track Count")
    sheet3.write(0, 6, "Track Proportion")
    
    for family in sorted(family_dictionary):
        sheet3.write(i, 0, family)
        maxN = max(family_dictionary[family])
        maxCount = family_dictionary[family].index(maxN)
        sheet3.write(i, 1, maxN)
        sheet3.write(i, 2, maxCount)
        sheet3.write(i, 3, maxCount / (60 * fps))
        sheet3.write(i, 4, maxCount / fps)
        sheet3.write(i, 5, family_track_statistics[family])
        sheet3.write(i, 6, family_track_statistics[family] / totalTracks)
        i += 1
    
    

# more table stuff
yeah = input("Do you want a time record? Enter [y/anything else]: ")
if yeah == 'y':
    timeTable(maxNTable, familyFun)

maxNTable.save(title + ".xls")
