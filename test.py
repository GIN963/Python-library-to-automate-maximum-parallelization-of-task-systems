#Ensemble de test fait our v√©rifier le fonctionnement
from biblio import Task,TaskSystem
import time

# creer 3 taches:

def run1():
    
    print("je suis T1 ")
    
def runT2():
    print("je suis T2")
    
def runT3():
    print("je suis T3")
    
t1= Task("t1",[],["X"],run1)
t2= Task("t2",[],["Y"],runT2)
t3= Task("t3",["X","Y"],["Z"],runT3)

#creer une instance de TaskSystem pour le premier exemple
task_system= TaskSystem([t1,t2,t3],{"t1":["t2"],"t2":[],"t3":["t1","t2"]})


task_system.getDependencies("t3")
task_system.decoupage()

task_system.run()
task_system.runSeq()
task_system.draw()
    
