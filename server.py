from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Favorite, Dog, Shelter, Breed

import datetime, dateutil.parser

import json
import requests
import xmltodict
import os
from helper_funcs import find_labels, find_datasets

app = Flask(__name__)


app.secret_key = "ABC"

app.jinja_env.undefined = StrictUndefined

pf_key=os.environ["PF_KEY"],
pf_secret=os.environ["PF_SECRET"]
map_key=os.environ["MAP_KEY"]

@app.route('/')
def index():
    """Homepage."""

    all_breeds = db.session.query(Breed.breed).all()#always endup with a tuple
    breed_list = []
    for breed in all_breeds:
        breed_list.append(breed[0])

    # breed_list = Breed.query.filter(Breed.description == None).all()

    return render_template("homepage.html", breed_list=breed_list)


def fix_formating(animal_obj):
    """Fix formatting of results from API for multiple pets."""

    last_update = animal_obj['lastUpdate']
    time_format = dateutil.parser.parse(last_update)
    animal_obj['lastUpdate'] = time_format.strftime("%m-%d-%Y %H:%M:%S")

    multiple_breeds = animal_obj['breeds']['breed']

    if type(multiple_breeds) == list:
        s = ", "
        multiple_breeds = s.join(multiple_breeds)

        animal_obj['breeds']['breed'] = multiple_breeds

    description = animal_obj['description'] or ""
    animal_obj['description'] = description.encode('ascii', 'ignore')

    if animal_obj['contact']['address1'] is None or animal_obj['contact']['address2'] is None:
        animal_obj['contact']['address2'] = ""
        animal_obj['contact']['address1'] = ""


def adding_shelter(shelter_id):
    shelter_payload = {'key': pf_key, 'id': shelter_id}

    shelter_location = requests.get('http://api.petfinder.com/shelter.get?', params=shelter_payload)

    shelter_dict = xmltodict.parse(shelter_location.text)

    shelter_id = shelter_dict['petfinder']['shelter']['id']
    zipcode = shelter_dict['petfinder']['shelter']['zip']
    latitude = shelter_dict['petfinder']['shelter']['latitude']
    longitude = shelter_dict['petfinder']['shelter']['longitude']
    latitude = float(latitude)
    longitude = float(longitude)

    #check if shelter exists
    shelter = Shelter.query.get(shelter_id)
    #if shelter doesn't exist
    if shelter is None:
        #add it to the database
        shelter = Shelter(shelter_id=shelter_id, zipcode=zipcode, latitude=latitude, longitude=longitude)
        db.session.add(shelter)
        db.session.commit()

    return shelter


@app.route('/results')
def search_results():
    """Search for the get request pet.find."""


    #### MALE OR FEMALE
    location = request.args.get("location")
    age = request.args.get("age")
    sex = request.args.get("sex")
    count = request.args.get("count")

    status = "A"#pass in?
    animal = "dog"
    payload = {'key': pf_key, 'animal': animal, 'count': count, 'location': location, 'sex': sex}

    animal_response = requests.get('http://api.petfinder.com/pet.find?', params=payload)

    animal_dict = xmltodict.parse(animal_response.text.encode('utf-8'))

    animal_list = animal_dict['petfinder']['pets']['pet']

    #IF USER IS NOT LOGGED IN FLASH MESSAGE
    user_id = session['user_id']

    for animal_obj in animal_list:

        fix_formating(animal_obj)

        shelter_id = animal_obj['shelterId']

        shelter = adding_shelter(shelter_id)
        animal_obj['latitude'] = shelter.latitude
        animal_obj['longitude'] = shelter.longitude

        petfinder_id = animal_obj['id']

        favorited_before = Favorite.query.filter_by(petfinder_id=petfinder_id, user_id=user_id).first()

        if favorited_before is not None:
            animal_obj['favorited_before'] = True
        else:
            animal_obj['favorited_before'] = False

    shelters = Shelter.query.all()

    return render_template("/results.html", animal_list=animal_list, shelters=shelters)



@app.route('/dogbybreed')
def show_dog_by_breed(): 


    breed = request.args.get("breed")
    animal = "dog"
    by_breed = {'key': pf_key, 'animal': animal, 'breed': breed}

    breed_response = requests.get('http://api.petfinder.com/shelter.listByBreed?', params=by_breed)
    
    by_breed_dict = xmltodict.parse(breed_response.text)
    
    shelter_breed_list = by_breed_dict['petfinder']['shelters']['shelter']

    for shelter_obj in shelter_breed_list:

        shelter_id = shelter_obj['id']
        zipcode = shelter_obj['zip']
        latitude = shelter_obj['latitude']
        longitude = shelter_obj['longitude']
        name = shelter_obj['name']

        if shelter_obj['address1'] is None or shelter_obj['address2'] is None:
            shelter_obj['address2'] = ""
            shelter_obj['address1'] = "N/A"

        shelter = Shelter.query.get(shelter_id)
        #if shelter doesn't exist
        if shelter is None:
            #add it to the database WITH NAME
            shelter = Shelter(shelter_id=shelter_id, zipcode=zipcode, latitude=latitude, longitude=longitude, name=name)
            db.session.add(shelter)
            db.session.commit()

    return render_template('/dog_by_breed.html', shelter_breed_list=shelter_breed_list, breed=breed)

@app.route('/shelterpets')
def show_pets_at_shelter():
    """Show pets at a shelter."""

    shelter_id = request.args.get("shelterid")

    shelter_pets = {'key': pf_key, 'id': shelter_id}

    shelter_animals = requests.get('http://api.petfinder.com/shelter.getPets?', params=shelter_pets)

    shelter_animals_dict = xmltodict.parse(shelter_animals.text)

    shelter_animals_list = shelter_animals_dict['petfinder']['pets']['pet']

    for animal_obj in shelter_animals_list:

        fix_formating(animal_obj)

    return render_template("shelter_pets.html", shelter_animals_list=shelter_animals_list)

@app.route('/randomresult')
def show_random():
    """Search for a random dog."""

    location = request.args.get("location")
    age = request.args.get("age")
    sex = request.args.get("sex")

    status = "A"
    output = "full"
    animal = "dog"
    count = 1
    payload = {'key': pf_key, 'output': output, 'animal': animal, 'count': count, 'location': location, 'sex': sex}

    animal_response = requests.get('http://api.petfinder.com/pet.getRandom?', params=payload)

    animal_dict = xmltodict.parse(animal_response.text)

    last_update = animal_dict['petfinder']['pet']['lastUpdate']

    time_format = dateutil.parser.parse(last_update)
    time_updated = time_format.strftime("%m-%d-%Y %H:%M:%S")


    return render_template('random_result.html', animal_dict=animal_dict, time_updated=time_updated)


@app.route("/shelter-results.json", methods=['GET'])
def shelter_results():
    """Shelters from results."""

    locations = {}
    shelter_ids = request.args.getlist("list_of_shelters[]")
    shelters = []

    for shelter_id in shelter_ids:
        s = Shelter.query.filter_by(shelter_id=shelter_id).first()
        shelters.append(s)

    for shelter in shelters:
        zipcode = str(shelter.zipcode)
        latitude = str(shelter.latitude)
        longitude = str(shelter.longitude)
        s_id = str(shelter.shelter_id)
        if (latitude != "None") and (longitude != "None"):
            locations[shelter.shelter_id] = {'latitude': latitude, 'longitude': longitude, 'shelter_id': s_id, 'zipcode': zipcode}

    print 'locations', locations
    print 'shelters', shelters
    return jsonify(locations)

@app.route('/breedchart')
def breed_chart():
    """Display Breed Chart."""

    breeds = Breed.query.filter(Breed.description != None).all()

    return render_template("breed_chart.html", breeds=breeds)

@app.route("/breeds/<breed>")
def breed_details(breed):
    """Dog breed detail page."""
    #ADD LOGIC TO NOT LET USER TYPE IN A BREED THAT DOESNT HAVE A DESCRIPTION
    breed = Breed.query.filter(Breed.description != None, Breed.breed == breed).first()

    return render_template("breed_description.html", breed=breed)

@app.route('/breed-info.json', methods=['GET'])
def breed_chart_data():

    breed_labels = find_labels('breeds.csv')
    breed_datasets = find_datasets('breeds.csv')

    data_dict = {
                "labels": breed_labels,
                "datasets": [
                    {
                        "data": breed_datasets,
                        "backgroundColor": [
                            "#FF6384",
                            "#36A2EB",
                        ],
                        "hoverBackgroundColor": [
                            "#FF6384",
                            "#36A2EB",
                        ]
                    }]
                }

    return jsonify(data_dict)
    
  

@app.route('/favorites', methods=['POST'])
def add_to_favorite():
    """Adds dog to favorites."""

    user_id = session["user_id"]
    petfinder_id = request.form.get("petfinder_id")
    shelter_id = request.form.get("shelter")
    adopted_status = request.form.get("status")
    img_url = request.form.get("url")
    breed = request.form.get("breed")
    age = request.form.get("age")
    name = request.form.get("name")
    ##TODO check that user is logged in 
    dog_exists_in_db = Dog.query.get(petfinder_id)

    if dog_exists_in_db is None:

        new_dog = Dog(petfinder_id=petfinder_id, shelter_id=shelter_id, adopted_status=adopted_status, img_url=img_url, age=age, breed=breed, name=name)

        db.session.add(new_dog)
        db.session.commit()

    fave_exists_in_db = Favorite.query.filter_by(petfinder_id=petfinder_id, user_id=user_id).first()

    if fave_exists_in_db is None:

        fave_dog = Favorite(petfinder_id=petfinder_id, user_id=user_id)

        db.session.add(fave_dog)
        db.session.commit()

        response = {'status': "success", 'id': petfinder_id}

    else:
        remove_fave_dog = Favorite.query.filter_by(user_id=user_id, petfinder_id=petfinder_id).one()

        db.session.delete(remove_fave_dog)
        db.session.commit()

    
        response = {'status': "successfully removed", 'id': petfinder_id}
    
    return jsonify(response)


@app.route('/register')
def register_user():
    """Register user."""


    return render_template('register.html')

@app.route('/register-success', methods=['POST'])
def register_process():
    """Process registration."""

    # Get form variables
    email = request.form["email"]
    password = request.form["password"]
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    zip_code = request.form["zip_code"]
    phone_number = request.form["phone_number"]

    new_user = User(email=email, password=password, first_name=first_name,
                    last_name=last_name, zip_code=zip_code, phone_number=phone_number)

    db.session.add(new_user)
    db.session.commit()

    flash("User %s added." % email)
    return redirect("/")




@app.route('/login', methods=['GET'])
def login_form():
    """Show login form."""

    return render_template("login_form.html")

@app.route('/login', methods=['POST'])
def login_process():
    """Process login."""

    
    email = request.form["email"]
    password = request.form["password"]

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("No such user")
        return redirect("/login")

    if user.password != password:
        flash("Incorrect password")
        return redirect("/login")

    session["user_id"] = user.user_id

    flash("Logged in")
    return redirect("/users/%s" % user.user_id)

@app.route("/users/<int:user_id>")
def profile_page(user_id):
    """User's profile page."""

    user = User.query.get(user_id)

    all_favorites = user.favorites

    fave_dogs = []
    for fave in all_favorites:
        fave_dogs.append(fave.dogs)



    return render_template("profile_page.html", user=user, dogs=fave_dogs)

@app.route('/logout')
def logout():
    """Log out."""

    del session["user_id"]
    flash("Logged Out.")

    return redirect("/")


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = True
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")