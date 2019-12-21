#!/usr/bin/python3

if __name__=="__main__":
	import random
	
	from argparse import ArgumentParser
	
	
	argu=ArgumentParser(prog="dispatch.py",
						description="""Script pour répartir les lignes d'un fichier au hasard entre deux autres fichiers.
									90% des lignes vont dans le premier fichier et 10% dans le deuxième,
									afin que le premier serve comme corpus d'entraînement et le second de corpus de test."""
						
						)
	
	argu.add_argument("entree",
						metavar="entree",
						help="""Le premier argument doit être le fichier à couper en deux.
							""")
	
	argu.add_argument("training",
						metavar="training",
						help="""Le deuxième argument est le nom du fichier de sortie pour le corpus d'entraînement.
							""")
	
	argu.add_argument("test",
						metavar="test",
						help="""Le test argument est le nom du fichier de sortie pour le corpus de test.
							""")
	
	args=argu.parse_args()
	
	entree=args.entree
	fichiertest=args.test
	fichiertraining=args.training
	
	TEST=9
	
	t = random.randint(0,TEST)
	sortietest=""
	sortietraining=""
	
	with open(entree) as f:
		for ligne in f:
			if t == TEST:
				sortietest+=ligne
			else:
				sortietraining+=ligne
			
			t=random.randint(0,TEST)
	
	with open(fichiertest,"w") as fte:
		fte.write(sortietest)
	
	with open(fichiertraining,"w") as ftr:
		ftr.write(sortietraining)
		



