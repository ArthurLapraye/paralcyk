
Manuel utilisateur pour le projet CYK probabiliste.

I - Exemple 
	
	Cette section présente de façon rapide l'ensemble des scripts du projet CYK probabiliste.
	En lançant les commandes présentées dans l'ordre, on obtient successivement 
	un corpus d'entraînement et de test, une grammaire tirée du corpus d'entraînement
	un ensemble de parse candidats et enfin leur évaluation vis-à-vis du corpus de test.
	
	NB : Tout les scripts sont écrits en python3 - Ils ne marcheront sans doute pas avec python2

	Étant donné un fichier mrg fi.mrg :
	
	I.1
	
		La commande : 
	
			dispatch.py fi.mrg train.mrg test.mrg 
		
		crée deux fichiers, 
			train.mrg, qui doit servir de corpus d'entraînement (90 % de fi.mrg)
			test.mrg qui doit servir de corpus de test (10% de fi.mrg )
		
			(La répartition entre les deux fichiers est faite au hasard)
	
	I.2
	
		La commande 
		
			extracteur.py fi.mrg grammaire.pickle 
		
		extrait une PCFG (sous forme normale de Chomsky) à partir de fi.mrg et l'enregistre dans le fichier grammaire.pickle
	
			extracteur.py train.mrg grammaire_train.pickle 
		
		extrait une PCFG à partir de train.mrg et l'enregistre dans le fichier grammaire_train.pickle
	
	I.3
	
		La commande
	
			updategrammar.py grammaire.pickle grammaire_train.pickle 
		
		modifie le fichier grammaire_train.pickle : elle sert à transférer dans la grammaire d'entraînement l'ensemble des 
		règles lexicales du corpus afin d'éviter d'avoir des erreurs dues à des mots inconnus.
		
	I.4
		
		La commande 
			
			ckys.py grammaire_train.pickle test.mrg > sortie_test.mrg 
			
		Lance l'analyse des phrases de test.mrg par CYK probabiliste et les rassemble dans sortie_test.mrg
		
		ATTENTION : cette étape peut durer extrêmement longtemps (plusieurs heures), 
		en particulier si l'une des phrases fait plus de cent mots.
		 
		Pour voir rapidement le fonctionnement de cky, utiliser le "mode interactif" (cf ci-dessous).
	
	I.5
		La commande 
			
			evaluation.py --gold test.mrg sortie_test.mrg 
		
		Calcule précision, rappel et f-mesure non-étiquetés sur sortie_test.mrg en prenant pour référence les parses originaux
		dans test.mrg.

II - Le script ckys.py
	
	Le script ckys implémente l'algorithme CYK et permet l'analyse de phrases tirées d'un corpus au format mrg.
	
	I.1
		Le script ckys.py se lance avec deux arguments. 
		Le premier est un pickle (objet python sérialisé) contenant une PCFG 
		sous forme normale de Chomsky produite par le script extracteur.py.
		Le deuxième argument est un corpus, un fichier mrg contenant les phrases que le script devra analyser.
			
		ckys.py grammaire_train.pickle test.mrg 
	
		Par défaut, le script est lancé de façon non-interactive : 
		il traite toutes les phrases du corpus en commençant par la première et imprime l'analyse sur 
		stdin et des messages d'informations ou d'erreur sur stderr.
		
	
	I.2 Options
		
		I.2.1 L'option -i
			
			L'option -i permet de lancer le script en mode interactif
			Le mode interactif affiche chaque phrase une par une avec leur longueur et leur numéro, 
			et attend des commandes de l'utilisateur 
				Les commandes acceptées par le script sont les suivantes :
				
					exit,
					quit ,
					Ctrl+D : quitte le script
					
					y : lance l'analyse de la phrase courante et l'affiche
					
					goto NOMBRE : va à la phrase numéro NOMBRE si NOMBRE est plus grand que le numéro de la phrase actuelle
				
				Le parsing d'une phrase peut être interrompu à tout moment avec 
				le raccourci Ctrl-C (ou équivalent)
					
		I.2.2 L'option -p
			
			L'option p donne la position de départ dans le corpus du script. 
			Par défaut le script commence au début du fichier. 
			Spécifier un numéro avec l'option -p permet de le faire commencer à la phrase correspondant à ce numéro.
		
	
III - Le script extracteur.py
	I.1	Fonctions de base :
		
		extracteur.py est un script qui permet d'extraire une grammaire probabilisée sous forme normale de Chomsky
		à partir d'un fichier au format mrg (mrg_strict ou id_mrg)
		
		Le script extracteur.py se lance avec deux arguments : 
			le nom d'un fichier mrg à partir du quel construire la grammaire
			le nom du fichier où sauvegarder la grammaire.
			
		
		La grammaire ainsi créée est un fichier pickle (objet python sérialisé)
		contenant un tuple de trois éléments:
			L'ensemble (set) des terminaux de la grammaire
			L'ensemble des nonterminaux
			Un dictionnaire contenant les règles de productions et leur probabilités.

IV - Le script evaluation.py
	
	I.1 Fonctions de base : 
		
		evaluation.py est un script qui calcule précision, rappel et f-mesure étiquetés ou non pour 
		les constituants d'un ensemble d'analyses lues soit depuis un fichier, 
		soit depuis stdin, ce qui permet de l'utiliser avec un pipe unix.
		
		Les analyses gold doivent être obligatoirement lues depuis un fichier
		spécifié avec l'option -g ou --gold.
		
		Pour l'utiliser avec un fichier, il faut le lui passer comme argument :
			evaluation.py -g fichiergold.mrg candidats.mrg
		
		ou 
			evaluation.py candidats.mrg -g fichiergold.mrg
		
		ou
			cat candidats.mrg | evaluation.py -g fichiergold.mrg
			
		ou même
			
			ckys.py grammaire.pickle fichiergold.mrg | evaluation.py -g fichiergold.mrg
		
		Le script affiche, outre précision, rappel et f-mesure normaux
		les précisions, rappels et f-mesure moyens pour l'ensemble du corpus.
	
	I.2 Options
		
		I.2.1 L'option -l
			
			Si l'option -l ou --labeled est activée, les constituants seront 
			considérés comme correct uniquement s'ils ont le même span ET la même étiquette
			
			Sinon, seul le span sera considéré.
			
		I.2.2 L'option -v
			
			L'option -v ou --verbose affiche précision, rappel et f-mesure pour chaque analyse
			Ainsi que les spans manquant du gold ou les spans supplémentaires de l'analyse candidate.
			

V - Scripts supplémentaires :

	V.1 dispatch.py
		
		Dispatch.py répartit au hasard dans deux fichiers de sortie les lignes d'un fichier d'entrée. 
		90% des lignes vont dans le premier fichier passé en argument
		10% vont dans le deuxième. 
		
		Il sert à créer rapidement un corpus de test et un corpus d'entraînement.
		
		Il se lance ainsi :
		
			dispatch.py corpus training test
		
	V.2 updategrammar.py
		
		updategrammar.py sert à enrichir le lexique d'une grammaire créée par extracteur.py
		à partir d'une autre de ces grammaires. Il permet ainsi d'utiliser une grammaire extraite
		d'un corpus d'entraînement sur un corpus de test sans avoir d'erreur due à des mots inconnus.
		
		Il se lance ainsi :
				updategrammar.py grammaire_source grammaire_cible
				
		Attention : le grammaire_cible original est écrasé par cette opération.
	
	
			

	
