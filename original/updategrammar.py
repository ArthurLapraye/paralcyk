#!/usr/bin/python3

if __name__=="__main__":
	import pickle
	import fractions
	from argparse import ArgumentParser
	from extracteur import defaultdictmaker
	
	argu=ArgumentParser(prog="dispatch.py",
						description="""Script pour modifier une grammaire en lui adjoignant le lexique d'une autre grammaire."""
						
						)
	
	argu.add_argument("grammairelexique",
						metavar="grammairelexique",
						help="""Le premier argument est la grammaire dont on extrait le lexique.
							""")
	
	argu.add_argument("grammaireupdate",
						metavar="grammaireupdate",
						help="""Le deuxième argument est la grammaire dont on veut enrichir le lexique.
								ATTENTION : Ce script écrase la version originale de cette grammaire.
							""")
	args=argu.parse_args()
	
	grammairetraining=args.grammaireupdate
	grammairelexique=args.grammairelexique
	
	with open(grammairetraining,"rb") as gt:
		gra=pickle.load(gt)
		
	with open(grammairelexique,"rb") as gc:
		grc=pickle.load(gc)
	
	
	(termi,nonter,r)=gra
	
	(terminaux,nonterminaux,regles)=grc
	
	termi.update(terminaux)
	
	for g in regles:
		for d in regles[g]:
			if len(d) == 1:
			#if d[0] in terminaux:
				r[g][d] = regles[g][d]
	
	with open(grammairetraining,"wb") as gt:
		pickle.dump( (termi,nonter,r), gt) 
	
