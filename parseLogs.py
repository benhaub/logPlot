################################################################################
#Date: April 19th, 2023                                                        #
#File: parseLogs.py                                                            #
#Authour: Ben Haubrich                                                         #
#Synopsis: Parses logs printed the follow the format                           #
#          <Title> <label1:value1, label2:value, label3:value3,...labeln:valuen>
#          and presents them graphically                                       #
################################################################################

import argparse
import subprocess
import sys
import re
import textwrap
try:
  import matplotlib.pyplot as plot
except ModuleNotFoundError:
  print("Error: matplotlib is not installed.")
  exit(1)
try:
   import numpy as np
except ModuleNotFoundError:
  print("Error: numpy is not installed.")
  exit(1)

from datetime import datetime
from matplotlib.backends.backend_pdf import PdfPages

if __name__ == '__main__':

  parser = argparse.ArgumentParser(prog='parseLogs.py',
                                       formatter_class=argparse.RawDescriptionHelpFormatter,
                                       description=textwrap.dedent('''\
                                              Parse and visualize logs.

                                              Logs that have a graph associated with them have the following format:
                                              [<Title>] <label1:value1, label2:value2, label3:value3,..., labeln:valuen> [<ChartType>]\n\
                                              Syntax is case sensitive.\n\
                                              [] are optional. Any part of the log in square brackets can be skipped.\n\
                                              <> are part of the syntax and must be written with the log to enclose the data to be graphed\n\
                                              If the <Title> is skipped, the entire log is skipped. If <ChartType> is skipped, then the plots default to a line chart.\n\
                                              Excepted ChartTypes are: Line, Bar, Scatter, Pie, and Omit. Omit will not create a plot for the respective label:value pair.\n\
                                              All graphs are plotted against the number of times they have printed so it's best to print them in a known period (like once a minute)\n\
                                              Examples:\n\
                                              //Produce 2 line graphs each with title "StorageStatus".
                                              <StorageStatus> <Storage:100, Free:90>
                                              //Log formatted data, but do not graph it. Still helpful for parsing later.
                                              StorageStatusNotGraphed <Storage:100, Free:90>
                                              //Produce a pie char for the idle percentage and a bar chart for bytes received. The state is ommitted and will not be graphed.
                                              <OperatingSystem> <Idle:100, bytesReceived:90, State:Running> <Pie, Bar, Omit>
                                       '''),
                                       epilog='Created by Ben Haubrich October 16th, 2024')
  parser.add_argument('-f', '--log-file', type=ascii, nargs='?', default=None, help='Path to the log file')

  args = parser.parse_args()
  #Uncomment for help with debugging.
  #print("{}".format(args))

  if args.log_file == None:
    print("Error: No log file provided. Please provide the path to the log file using the -f or --log-file argument.")
    exit(1)

  plotData = {}
  plotTitles = []

  with open(args.log_file.strip('\''), 'r') as logFile:
    for line in logFile:
      if '<' in line and '>' in line:
        enclosedData = re.findall(r'<[^>]+>', line)
        if len(enclosedData) > 1:
            title = enclosedData[0].strip('<').strip('>')
            #If there are any nested angle brackets in the title or commas then skip it.
            if '<' in title or '>' in title or ',' in title:
                continue
            if title not in plotTitles:
                plotTitles.append(title)
                if plotTitles.index(title) not in plotData:
                    print("Creating new plot data for title: {}".format(title))
                    plotData[plotTitles.index(title)] = {"title": []}
                    plotData[plotTitles.index(title)]["title"].append(title)

            labelValuePairs = enclosedData[1].strip('<').strip('>').split(',')
            for pair in labelValuePairs:
                pair = pair.split(':')
                if (len(pair) > 1):
                    label = pair[0].strip(" ")
                    try:
                        value = float(pair[1].strip(" "))
                    except ValueError:
                        value = pair[1]
                    if label not in plotData[plotTitles.index(title)]:
                        print("Creating new axis for label: {}".format(label))
                        plotData[plotTitles.index(title)][label] = []

                    plotData[plotTitles.index(title)][label].append(value)

            #Grab the chart types if specified
            chartTypesWereSpecified = (len(enclosedData) > 2)
            if chartTypesWereSpecified:
              chartType = enclosedData[2].strip('<').strip('>')

              plotData[plotTitles.index(title)]["title"].append(chartType)

i = 1
figures = []
for plotNumberForTitle in range (0, len(plotTitles)):
    xLabel = "Time (minutes)"
    j = 0

    for label in plotData[plotNumberForTitle]:

        if label == "title":
            continue

        title = plotData[plotNumberForTitle]["title"][0]
        axisValuesForLabel = plotData[plotNumberForTitle][label]

        chartTypeSpecified = (len(plotData[plotNumberForTitle]["title"]) > 1 and j < len(plotData[plotNumberForTitle]["title"][1].split(",")))
        if chartTypeSpecified:
            chartTypes = plotData[plotNumberForTitle]["title"][1].split(",")
            chartType = chartTypes[j].strip(" ")
            j += 1
        else:
            chartType = "Line"

        if chartType == "Omit":
            print("Skipping plot for label: {}".format(label))
            continue

        currentFigure, axis = plot.subplots()
        axis.figure = plot.figure(i)
        axis.title.set_text(title)
        axis.set_xlabel(xLabel)
        axis.set_ylabel(label)

        print('Creating {} plot {} for {}'.format(chartType, i, label))
        if chartType == "Line":
            axis.plot(axisValuesForLabel)
        elif chartType == "Bar":
            axis.bar(0.5 + np.arange(len(axisValuesForLabel)), axisValuesForLabel, width=1, edgecolor='black', linewidth=0.7)
        elif chartType == "Pie":
            axis.set_axis_off()
            axis.title.set_text(title + "({})".format(label))
            countOfEachUniqueValue = []
            #convert the list to a set to get unique values
            uniqueValues = set(axisValuesForLabel)
            for value in uniqueValues:
                countOfEachUniqueValue.append(axisValuesForLabel.count(value))

            axis.pie(countOfEachUniqueValue, labels=uniqueValues, radius=1.5, center=(1.5,1.5), autopct='%1.1f%%', wedgeprops={"linewidth":1, "edgecolor": "black"}, frame=True)
        elif chartType == "Stairs":
            axis.stairs(axisValuesForLabel)

        figures.append(axis.figure)
        i += 1


for figure in figures:
    figure.show()

# The option to save the pdf and the input required is placed after we show the plots so that the program is halted while the user views the shown plots.
# otherwise the program closes and the plots close before you have a chance to view them
saveToPdf = input("Save to pdf? (y/n)")
if saveToPdf == "y":
    with PdfPages("logPlots.pdf") as pdf:
        for figure in figures:
            plot.rc('text', usetex=True)
            pdf.savefig(figure)
            plot.close(figure)
   
    pdfInfo = pdf.infodict()
    pdfInfo["Title"] = "Log Plots"
    pdfInfo["Author"] = "Automatically generated by parseLogs.py"
    pdfInfo["Subject"] = "Log Plots"
    pdfInfo["Keywords"] = "Log, Plot, Graph"
    pdfInfo["CreationDate"] = datetime.now()
    pdfInfo["ModDate"] = datetime.now()
