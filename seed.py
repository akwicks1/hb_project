from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Favorite, Dog, Shelter, Breed

from server import app


def breed_with_description():
	"""Add breed with description to breed table."""
	
	for i, row in enumerate(open("seed_data/popular_breeds")):
		row = row.rstrip()
		breed, description, img_url = row.split("|")
		
		dog = Breed(breed=breed,
					description=description,
					img_url=img_url)
		print "description", dog
		db.session.add(dog)
	


def breeds_into_db():
	"""Add remaining breeds to breed table."""

	for i, row in enumerate(open("seed_data/breeds_db")):
		row = row.rstrip()
		row = row.split("\t")
		breed = row[0]

		dog = Breed(breed=breed,
					description=None,
					img_url=None)
		print "dog", dog 
		db.session.add(dog)
		


# if __name__ == "__main__":
#     connect_to_db(app)
#     db.create_all()
#     breed_with_description()
#     breeds_into_db()
#     db.session.commit()