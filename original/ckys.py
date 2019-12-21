#!/usr/bin/python3
# coding: utf8

import fractions
import logging

def CYKmaker(cnf):
	"""
		Fonction qui construit le dictionnaire inverse des productions
			Pour une règle
				a -> b,c
		Le dictionnaire a une entrée
			b -> c -> a -> prob
		Ce qui accélère le traitement.
		
		La fonction CYK proprement dite est incluse dans cette fonction, afin de ne pas devoir reconstruire
		le dictionnaire inverse à chaque fois : ce dernier est inclus dans la clôture lexicale de CYKmaker.
	"""
	terminaux,nonterminaux,gr=cnf
	debuts=dict()
	
	#Construction du dictionnaire inverse des productions
	#à partir de la grammaire
	for n in gr:
		for p in gr[n]:
			if len(p) == 2:
				if not p[0] in debuts:
					debuts[p[0]]=dict()
				if p[1] not in debuts[p[0]]:
					debuts[p[0]][p[1]]= dict()
					debuts[p[0]][p[1]][n]= float(gr[n][p])
				else:
						#print(n,p)
					if n in debuts[p[0]][p[1]]:
						logging.warn("Production déjà connue :"+str(n)+"=>"+str(p)+" " +str(gr[n][p] ))
					
					debuts[p[0]][p[1]][n] = float( gr[n][p] )
			
			else:
				#Si la grammaire n'est pas en CNF
				if len(p) >  1 or p[0] not in terminaux:
					raise ValueError("Production invalide :",p)
	
	#Fonction CYK proprement dite	
	def cyk(u,verbose=False) :
		"""
			Fonction de parsing ascendant CYK probabiliste.
			Prend en entrée une phrase et renvoie un tableau rempli avec les réécritures possibles.
		"""
		T=dict()
		
		#Remplissage du premier rang du tableau
		#Utilisation des règles unaires de production lexicales	
		for i in range(1,len(u)+1) :
		#On parcourt le mot à reconnaitre
			for l in gr :
				if (u[i-1],) in gr[l]:
					r=(u[i-1],)
					
					if (i,i+1) not in T :
						T[(i,i+1)]=dict()
					if l not in T[i,i+1]:
						T[i,i+1][l]=dict()
							
					if r not in T[(i,i+1)][l]:
						T[(i,i+1)][l][(r,)] = float(gr[l][r])										
							 #On remplit la case
					else :
						T[(i,i+1)][l][(r,)] += float( gr[l][r] )										   
							#On rajoute une autre règle s'il y en a + qu'une
			
			if (i,i+1) not in T :
				T[(i,i+1)]=dict()														  
				#Si une case est vide, on ajoute un tableau vide dedans pour qu'elle apparaisse dans le dico
		
		
		#Remplissage des rangs supérieurs du tableau
		#i correspond aux longueurs de spans de plus en plus larges que CYK 
		#va tenter d'associer à des non-terminaux
		for i in range(2,len(u)+1):
			
			#Y correspond à l'index de l'élément de départ de la case en cours
			#de remplissage T[span]
			for y in range(1,(len(u)-i+2)) :
				span=(y,i+y)
				if span not in T:
					T[span]=dict()
				
				#J est le pivot qui détermine quelle paire de non-terminaux B C
				#Va correspondre aux non-terminaux de la case T[span]
				#Qui doivent pouvoir se récrire BC
				for j in range(y+1,i+y) :
					
					sp1=(y,j)
					sp2=(j,i+y)
					cds=T[sp2]
					
					#A représente les non-terminaux de la case de gauche			  
					for a in T[(y,j)]:
						probA=T[y,j][a]
						if a in debuts:
								#Suite est un dictionnaire contenant toutes les récritures
								#Dont a est le premier élément
								suite=debuts[a]
								g=(a,sp1)
								mpa=0
								
								#mpa est la meilleure probabilité pour A
								for z in probA:
									pa=probA[z]
									if pa > mpa:
										mpa=pa
								
								#C représente les non-terminaux de la case de droite.
								for c in cds:
									if c in suite:
										r=(g,(c,sp2))
										recrits=suite[c]
										
										mpc=0
										for d in cds[c]:
											pc=cds[c][d]
											if pc > mpc:
												mpc = pc
										
										pz=mpa*mpc
										
										#L est un non-terminal qui possède une récriture 
										#L => A C
										for l in recrits:
											pb=recrits[l]
											maximum=0
											
											newpb=pz*pb
											
											if newpb > maximum:
												maximum=newpb
									
											
											if l not in T[span]:
												T[span][l]=dict()
											
											T[span][l][r] = maximum
				
			
			if verbose:
				print(i)	
		
		return T
	
	return cyk

def treemaker(T,u):
	"""
		Fonction de backtracking pour extraire le meilleur arbre de la charte CYK.
	"""
	longueur=len(u)
	
	def maketree(Z):
		"""Fonction interne qui fait effectivement le backtracking descendant dans la charte
		en prenant les meilleures probabilités pour chaque récriture à chaque étage.
		"""
		retour=[]
		for tup in Z:
			if len(tup) > 1:
				Y=sorted(T[tup[1]][tup[0]],key= lambda x : (T[tup[1]][tup[0]][x]) ,reverse=True )
				Z=Y[0]
				if len(Y) > 1:
					if T[tup[1]][tup[0]][Z] == T[tup[1]][tup[0]][Y[1]]:
						logging.warn("probabilités identiques : "+str(Y[1])+" "+str(Z))
				
				if len(Z) == 1:
					retour.append([tup[0],Z[0][0]])
				else:
					next=[tup[0] ]
					for child in maketree(Z):
						next.append(child)
					retour.append(next)
			else:
				retour.append(tup[0])
		
		return retour

	maxprob=0
	maxZ=[]
	maxelem=None
	
	#Boucle qui démarre le backtracking pour les non-terminaux commençant par SENT.
	#Du fait de la création de nouveau non-terminaux lors de l'élimination des productions singulières
	#Il y a en effet plusieurs axiomes dans la grammaire utilisée 
	#Cette boucle permet de gérer ce cas particulier 
	for elem in T[1,1+longueur]:
		if elem.startswith("SENT"):
			Z=max(T[1,1+longueur][elem],key=lambda x : (T[1,1+longueur][elem][x] ))
			
			newprob=T[1,1+longueur][elem][Z]
			
			if maxelem:
				if newprob > maxprob:
					maxprob=newprob
					maxZ=Z
					maxelem=elem
				elif newprob == maxprob:
					if len(elem) < len(maxelem):
						maxelem=elem
						maxZ=Z
			else:
				maxelem = elem
				maxprob = newprob
				maxZ = Z
			
	return [maxelem]+maketree(maxZ)



if __name__ == '__main__':
	from extracteur import defaultdictmaker
	from collections import defaultdict
	
	
	import pickle
	import evaluation
	import sys, codecs
	
	from argparse import ArgumentParser
	from flatten import flatten
	
	import re
	
	logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
	
	argu=ArgumentParser(prog="ckys.py",
						description="""Implémentation d'un parser CYK probabiliste 
						prenant en entrée une PCFG et un corpus de phrases MRG"""
						
						)
	argu.add_argument("fichiergrammaire",
						metavar="grammaire",
						help="""Le fichier de grammaire est un pickle produit par extracteur.py
							""")
	
	argu.add_argument("corpus",metavar="corpus",help="""Le deuxième argument contient le corpus au format MRG.""")
	
	argu.add_argument('-i','--inter', 
						dest='interactif', 
						action='store_true',
						#default=False,
						help="""Si cette option est active le script fonctionne en mode interactif.""")
	
	argu.add_argument("-p",
						"--position",
						dest='position',
						default="0")
	
	
	args=argu.parse_args()
	
	with open(args.fichiergrammaire, 'rb') as fichiergrammaire:
		cnf = pickle.load(fichiergrammaire)

	parse=CYKmaker(cnf)
	
	i=0
	
	position=int(args.position)
	
	with codecs.open(args.corpus, "r") as corpus:
		for phrase in corpus:
			i+=1
			
			if i < position:
				continue
			
			if not phrase.startswith('('):
				(nomcorpus_numero, phrase) = phrase.split('\t')
				(nomcorpus, numero) = nomcorpus_numero.rpartition('_')[::2]
			arbre=evaluation.readtree(evaluation.tokenize(phrase))[0]
			
			phrase = evaluation.getleaves(arbre)
			
			if args.interactif:
				print("n°",i)
				print("Longueur de la phrase :",len(phrase))
				print("phrase : ", re.sub(r"'([^']+)'",r"\1"," ".join(phrase)) )
				try:
					goon=input()
				except EOFError:
					break
				if goon == "quit" or goon == "exit":
					break
				elif goon.startswith("goto"):
					go=goon[4:]
					try:
						position=int(go.strip())
						if position  > i:
							continue
						else:
							print("Impossible de retourner en arrière !")
					except ValueError as e:
						print("Nombre invalide :",go)
				elif goon == "y":
					try:
						z=parse(phrase,verbose=True)
						arbre=treemaker(z,phrase)
					except KeyboardInterrupt as e:
						print("Parsing interrompu...\n")
						continue
					
					if arbre[0]:
						print(evaluation.writetree(flatten(arbre)))
					else:
						print("Échec du parsing")
					del z
					print()
				else:
					if goon:
						print("Commande inconnue :",goon)
					
					continue
			
			else:
				logging.info("phrase numéro "+str(i)+" en cours de traitement. Longueur : "+str(len(phrase)))
				z=parse(phrase)
				arbre=treemaker(z,phrase)
				if arbre[0]:
					print("("+evaluation.writetree(flatten(arbre))+")")
				else:
					print("( (SENT "+ " ".join(phrase)+") )")
					logging.error("Échec du parsing pour la phrase n°"+str(i))
				del z





