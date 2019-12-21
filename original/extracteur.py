#!/usr/bin/python3
# coding: utf8

import evaluation
from collections import defaultdict
import fractions
from copy import deepcopy
from collections import defaultdict

def defaultdictmaker():
	return defaultdict(fractions.Fraction)

def CNF(terminaux,nonterminaux,regles,markov=None):
	"""
		Fonction pour mettre une PCFG sous forme normale de Chomsky.
		Binarise, puis supprime les productions singulières pour les non-terminaux.
	"""
	cnf=deepcopy(regles)
	
	#Unit test pour vérifier qu'aucun symbole ne se récrit en epsilon
	for nt in regles:
		for prod in regles[nt]:
			if not prod:
				#if nt == prod[0]:
				raise ValueError("Production vide pour",nt)
			
	def binariser(nterm,prod,proba=1):
		"""Fonction interne, qui binarise récursivement une production donnée.
		   Si la production est plus longue que 2, elle crée un nouveau nonterminal 
		   (en concaténant les nonterminaux après le premier, séparés par une flèche descendante)
		   puis transforme la production existante en production binaire
		   Et s'appelle récursivement sur la nouvelle production.
		"""
		if len(prod) > 2:
			nuNT="↓".join(prod[1:])
			nonterminaux.add(nuNT)
			cnf[nterm][prod[0],nuNT]=proba
			binariser(nuNT,prod[1:])
		else:
			cnf[nterm][prod]=proba
	
	for nterm in regles:
		for production in regles[nterm]:
			if len(production) > 2:
				binariser(nterm,production,proba=regles[nterm][production])
				del cnf[nterm][production]
	
	
	#Test : vérifier l'intégrité de la grammaire
	#Que toutes les règles sont au plus binaires
	#Que toutes les probabilités somment toujours à 1
	for nt in cnf:
		sumproba=0
		for prod in cnf[nt]:
			if len(prod) > 2:
				raise ValueError("Production trop longue : "+prod)
			else:
				sumproba += cnf[nt][prod]
		if not (sumproba==1):
			raise RuntimeWarning("Erreur : somme incorrecte"+str(sumproba)+"pour "+nt+" après binarisation.")
	
	#regles=cnf
	#cnf=deepcopy(cnf)
	modified=True
	
	#Boucle pour supprimer les productions singulières de non-terminaux.
	while modified:
		modified=False
		#La liste des clefs d'un dictionnaire doit être maintenue 
		#dans une variable à part si on veut modifier
		#le dictionnaire
		clefs=list(cnf.keys())
		for nt in clefs:
			pz=list(cnf[nt].keys())
			for prod in pz:
				if len(prod) == 1:
					if prod[0] in nonterminaux:
						modified=True
						singulier=prod[0]
						proba1=cnf[nt][prod]
						comproba1=1-proba1
						nuNT=nt+"↑"+singulier
						nonterminaux.add(nuNT)
						
						prds=list(cnf[singulier].keys())
						for p in prds:
							cnf[nuNT][p] = cnf[singulier][p]
						
						del cnf[nt][prod]
						
						prds2=list(cnf[nt].keys())
						
						if len(prds2) > 0:
							for p in prds2:
								cnf[nt][p]=fractions.Fraction(cnf[nt][p],comproba1)
						else:
							del cnf[nt]
						
						klefs=list(cnf.keys())
						for k in klefs:
							pdz=list(cnf[k].keys())
							for p in pdz:
								proba2=cnf[k][p]
								#if proba2 == 0:
									#print(nt,pz,proba2)
								if len(p) == 2:
									g,d=p
									if g == nt and d == nt:
										cnf[k][g,d] = proba2*comproba1*comproba1
										cnf[k][nuNT,d] = proba1*proba2*comproba1
										cnf[k][g,nuNT] = comproba1*proba2*proba1
										cnf[k][nuNT,nuNT]= proba2*proba1*proba1
									elif g == nt:
										cnf[k][g,d]=proba2*comproba1
										cnf[k][nuNT,d]=proba2*proba1
									elif d == nt:
										cnf[k][g,d]=proba2*comproba1
										cnf[k][g,nuNT]=proba2*proba1
								
								#elif p[0]==nt:
								#	cnf[k][p]=proba2*comproba1
								#	cnf[k][tuple(nuNT)]=proba2*proba1
									
						
	
	#Test pour vérifier que tout s'est bien passé
	#Vérifie qu'il n'y a plus de productions singulières
	#Et que les probabilités somment toujours à un, comme il se doit.
	for nt in cnf:	
		sumproba=0
		for prod in cnf[nt]:
			if len(prod) < 2 and prod[0] in nonterminaux:
				raise ValueError("Production singulière :",nt,prod)
			else:
				sumproba += cnf[nt][prod]
		
		#print(sumproba)
		if not (sumproba == 1 ):
			raise RuntimeWarning("Somme incorrecte "+str(sumproba)+" pour "+nt+" après suppression des productions singulières.")
	
	return terminaux,nonterminaux, cnf

if __name__ == '__main__':
	
	import argparse
	import codecs
	from pickle import dump as pdump

	argumenteur = argparse.ArgumentParser(
		prog="extracteur.py",
		description="""
			Ce programme sert à prendre un fichier au format parenthésé,
			puis d'en extraire une grammaire binarisée sans productions singulières.
		"""
	)

	argumenteur.add_argument(
		"input",
		metavar="MRG",
		help="""
			input doit être une chaine de caractères
			représentant le nomdu fichier s'entrée.
		"""
	)
	argumenteur.add_argument(
		"output",
		metavar="GRAMMAIRE",
		help="""
			output doit être une chaine de caractères
			qui représentera le nom du fichier de sortie.
		"""
	)
	
	args = argumenteur.parse_args()
	
	rightside=defaultdict(defaultdictmaker)
	leftside =defaultdict(int)
	nonterminaux=set()
	terminaux=set()
	
	with codecs.open(args.input, 'r', 'utf-8') as entree:
		for ligne in entree:
			phrase=""
			numero=None
			if not ligne.startswith('('):
				(nomcorpus_numero, phrase) = ligne.split('\t')
				(nomcorpus, numero) = nomcorpus_numero.rpartition('_')[::2]
			
			else:
				phrase=ligne
		
		
			arbre= evaluation.readtree(evaluation.tokenize(phrase))[0]
			n,t = evaluation.nodesandleaves(arbre)
			nonterminaux.update(n)
			terminaux.update(t)
			
			productions=evaluation.getchildren(arbre)
		
			for elem in productions:
				leftside[elem] += len(productions[elem])
				for prod in productions[elem]:
					rightside[elem][prod] += 1
					
	for nt in rightside:
		sumproba=0
		for prod in rightside[nt]:
			prodproba=fractions.Fraction(rightside[nt][prod],leftside[nt])
			rightside[nt][prod]=prodproba
			sumproba += prodproba
		assert(sumproba==1)

	grammaire=CNF(terminaux, nonterminaux,rightside)
	
	with open(args.output,"wb") as f:
		pdump(grammaire,f)
	
