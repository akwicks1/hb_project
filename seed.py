from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Favorite, Dog, Shelter, Breed

from server import app


def breed_with_description():
	
	
	for i, row in enumerate(open("seed_data/popular_breeds")):
		row = row.rstrip()
		breed, description, img_url = row.split("|")
		
		dog = Breed(breed=breed, 
					description=description, 
					img_url=img_url)

		db.session.add(dog)

	db.session.commit()
if __name__ == "__main__":
    connect_to_db(app)
    db.create_all()
    breed_with_description()
