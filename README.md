# logPlot
Python script that can take a syntactic log file as input and produce a plot of the the data on a graph of your choosing
## Syntax
Any log printed in the form (with angle bracket enclosures):

`<Title> <label1:value1, label2:value2, label3:value3,..., labeln:valuen> <plotType1, plotType2, plotType3,..., plotTypen>`

Will output n plots titled 'Title' where each plotType n corresponds to labeln:valuen all plotted over a domain corresponding to the number
of times the log was printed.

In this sense, the plots work best for periodic log statements that print system information such as memory usage, cpu usage, or various states as they progress
over time.

## Installing missing modules
If you run the script and receive errors about missing modules, it is reccomended to create a python virtual environment and install the modules using the `requirements.txt` file.

From within this repository, run

`python -m venv .venv`

then run

`. .venv/bin/activate`

then run

`pip install -r requirements.txt`
Now you will be able to run the script.

type

`deactivate`

when you are done using the script to exit from the virtual environment.
