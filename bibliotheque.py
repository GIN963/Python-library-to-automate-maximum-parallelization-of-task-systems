import concurrent.futures
import networkx as nx
import matplotlib.pyplot as plt



# Classe qui permet de définir des tâches
class Task:
    name = ""
    reads = []
    writes = []
    run = None
    
    def __init__(self, name, reads, writes, run):
        self.name = name
        self.reads = reads
        self.writes = writes
        self.run = run
    
# Classe qui permet de définir un système de tâches
class TaskSystem:
    Tasklist = []
    Dico = {}
    #run= None
    
    def __init__(self, Tasklist, Dico):
        self.Tasklist = Tasklist
        self.Dico = Dico
        
        
#######################getDependencies#########################################
        
    def getDependencies(self, nomTache): 
        # Liste de toutes les tâches qui ont une interférence avec nomTache
        ListPrec = []
        
        # Domaine de lecture et d'écriture de nomTache qu'on va récupérer
        R = []
        W = []   
        
        for tache in self.Tasklist:
            # Récupérer les domaines d'écriture L et R de nomTache
            if tache.name == nomTache:
                R = tache.reads.copy()
                W = tache.writes.copy()
        
        
        # Pour chaque tâche dans Tasklist, vérifier si chacune de leurs variables dans leur domaine de lecture se trouve dans W
        # et les ajouter à la liste d'interférence si c'est le cas   
        for tache in self.Tasklist:
            
            #Cette ligne sert à gerer le cas ou on tombe sur nomTache dans TaskList pour ne pas le prendre en compte
            if tache.name != nomTache:
               
                for VL1 in tache.reads:
                   
                    if VL1 in W:
                        
                        #si on trouve une interférrence, on test si l'interference se trouve dans le dictionnaire de précedence dans les valeurs de la clef nomTache rt on l'ajoute si oui
                        if tache.name in self.Dico.get(nomTache):  
                            ListPrec.append(tache)
                     
                # Pareil avec chaque variable dans le domaine d'écriture de chaque tâche
                for VE1 in tache.writes:
                   
                   if VE1 in W or VE1 in R:
                       
                       if tache.name in self.Dico.get(nomTache):
                           
                           ListPrec.append(tache)
                           
        """for tache in ListPrec:
            print(tache.name)"""
            
        return ListPrec
    
###############################Decoupage####################################### 
    
    
    #fonction qui renvoi l'ordre d'execution en fonction des nouvelle dépendences, renvoi une liste de liste, si des taches sont dans une meme liste alors elle peuvent etre executées en meme temps das run()
    def decoupage(self):
        
        #List de taches temporaires initialisé par la Tasklist de Tasksystème
        TempTaskList= self.Tasklist.copy()
        
        #decoupage de l'ordre d'execution des taches
        Decoupage=[]
        
        #tant que la liste temporaire n'est pas vide (elle se videra au fur est a mesure lorsqu'on enlevera les taches déja "visité")
        while TempTaskList!= []:
            
            #tant qu'on est pas sorti de cette boucle while afin de dir tant qu'on est pas sorti de la boucle for qui vient juste apres
            # cela permet de ne pas sorti avant le break donc de ne pas sortir avant d'avoir parcouru toute la liste de tache temporaire qui est mis a jours avant le break
        
            while True:
                #on cree un liste qui repertori toutes les taches sans dependances lors de l'itération en cours
                #cela fournira le premier découpage, s'il y a plusieurs taches dans ce découpage cea veux dire qu'elle peuvent etre parqlelisée
                paraTask=[]
                for task in TempTaskList:
                    #les taches sans dependance vont contituer Le premier découpage ensuite ce seront les taches avec des dependance qi ne se trouvent plus dans 
                    #TempTaskList car on les aura enlever car déja "visité"
                    if (self.getDependencies(task.name)==[])or not any(dep in TempTaskList for dep in self.getDependencies(task.name)):
                        # on rajoute la tache sans dependance dans par(par rapport à TaskList) dans paraTask
                        paraTask.append(task)
                
                #bloc de mise en forme pour afficher les différent découpages (permet de verifier)        
                print("PARATASK / [",end="")
                for i in paraTask: 
                    print(i.name+",",end=" ")
                print("]\n")
                
                
                #On enleve de Temptasklist les taches déja repertorier dans paraTask
                for i in paraTask: 
                    TempTaskList.remove(i)

                
                #on ajoute  le premier découage à Decoupage    
                Decoupage.append(paraTask)
                
                # On sort de la boucle while true pour repeter les memes opérations sur TempTaskList mis à jour jusqu'a ce qu'il soit vide  
                break
            
        #mise en forme pour bien afficher le tableau de découpage
        print("DECOUPE: [ ",end=" ")
        for i in  Decoupage:
            print("[ ",end=" ")
            for t in i:
                print(t.name+", ",end=" ")
            print("], ",end=" ")
            
        print("]\n") 

        return Decoupage
    
#######################################run()###################################
 
    def run(self):
        
       Dec= self.decoupage()
       
       for i in Dec:
           print("[  ",end=" ")
           for t in i:
               print(t.name+", ",end=" ")
           print("], ",end=" ")
       print("]==DEC \n") 
       
       tache_execute =[]
       future=[]
             
       for liste_tache in Dec:

                with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            
                    if not future:
        
                        tache_execute.append(executor.submit(tache.run)for tache in liste_tache)
                    
                    else:
                        for tache in liste_tache:
                            
                                if not any(dependency in future and future[dependency].done() for dependency in self.getDependencies(tache.name)):
            
                                    tache_execute.append(executor.submit(tache.run))      
                        
                    for result in tache_execute:
                        
                        future.append( result)

                    
                    for result in tache_execute:
                        
                        tache_execute.remove(result)
                        
                        
##############################runSeq()#########################################


    def runSeq(self):
    
      Dec = self.decoupage()
    
      #executer les taches une par une à patir de l liste de decoupage
      for list_tache in Dec:
        
         for tache in list_tache:
            
             tache.run()

            
################################Draw()#########################################

    
    def draw(self):
        newDico = {}
        for task in self.Tasklist:
            # Création d'une liste de dépendances pour chaque tâche
            dependencies = [dep.name for dep in self.getDependencies(task.name)]
            newDico[task.name] = dependencies

        # Affichage du dictionnaire (si nécessaire)
        print("Dictionnaire des dépendances :", newDico)

         # Création du graphe dirigé avec NetworkX
        G = nx.DiGraph()

        # Ajout des nœuds au graphe
        for task_name in newDico:
            G.add_node(task_name)

        # Ajout des arêtes en fonction des dépendances définies dans newDico
        for task_name, dependencies in newDico.items():
            for dep in dependencies:
                G.add_edge(dep, task_name)

        # Dessin du graphe
        nx.draw(G, with_labels=True, node_size=2000, node_color="lightblue", font_size=10, font_weight="bold")

        # Affichage du graphe
        plt.show()
############################################parCost###############################

    def parCost(self):
    # Liste pour stocker les temps d'exécution de runSeq
    tempsSeq = []
    # Compteur
    t = 0
    # On exécute runSeq 2000 fois pour avoir 2000 temps d'exécution
    while t != 2000:
        t += 1
        # Mesure du temps d'exécution séquentiel
        start_seq = time.time()
        self.runSeq()  # Exécution séquentielle
        end_seq = time.time()
        tempsSeq.append(end_seq - start_seq)

    # Calcul de la somme des temps d'exécution
    sumTSeq = sum(tempsSeq)
    # Calcul de la moyenne des temps d'exécution
    MoyenneSeq = sumTSeq / len(tempsSeq)
    print("moySeq = ", MoyenneSeq)

    # Liste pour stocker les temps d'exécution de run()
    tempPara = []
    i = 0
    while i != 2000:
        i += 1
        # Mesure du temps d'exécution parallèle
        start_par = time.time()
        self.run()  # Exécution parallèle
        end_par = time.time()
        tempPara.append(end_par - start_par)

    # Calcul de la somme des temps d'exécution de run()
    sumTempPara = sum(tempPara)
    # Calcul de la moyenne des temps d'exécution de run()
    MoyennePara = sumTempPara / len(tempPara)
    print("moyPara = ", MoyennePara)
    print("moySeq = ", MoyenneSeq)
