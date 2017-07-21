from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):
    """User of find a dog website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64))
    password = db.Column(db.String(64))
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    zip_code = db.Column(db.String(15))
    phone_number = db.Column(db.String(10), nullable=True)
    
    def __repr__(self):
        """Provide user's information."""

        return "<User user_id=%s email=%s>" % (self.user_id, self.email)

class Favorite(db.Model):
	"""Favorites Assoication Table."""

	__tablename__ = "favorites"

	fave_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
	petfinder_id = db.Column(db.Integer, db.ForeignKey('dogs.petfinder_id'))

	user = db.relationship("User",
							backref=db.backref("favorites"))

	def __repr__(self):
		"""Provide favorites details."""

		return "<Fave fave_id=%s User user_id=%s PF_id petfinder_id%s>" % (
			self.user_id, self.fave_id, self.petfinder_id)


class Dog(db.Model):
	"""Information about dog from petfinder."""

	__tablename__ = "dogs"

	petfinder_id = db.Column(db.Integer, primary_key=True)
	shelter_id = db.Column(db.String(6), db.ForeignKey('shelters.shelter_id'))
	name = db.Column(db.String(20))
	adopted_status = db.Column(db.String(1))
	img_url = db.Column(db.String(300))
	age = db.Column(db.String(10))
	breed = db.Column(db.String(50))

	favorites = db.relationship("Favorite",
								 backref=db.backref("dogs"))
	def __repr__(self):
		"""Provide dog details."""

		return "<PF_id petfinder_id=%s Shelter shelter_id%s>" % (self.petfinder_id, self.shelter_id)

class Shelter(db.Model):
	"""Information about shelters."""

	__tablename__ = "shelters"

	shelter_id = db.Column(db.String(6), primary_key=True)
	zipcode = db.Column(db.String(15))
	latitude = db.Column(db.String(12))
	longitude = db.Column(db.String(13))
	name = db.Column(db.String(100), nullable=True)


	dogs = db.relationship("Dog",
							backref=db.backref("shelters"))

	def __repr__(self):
		"""Provide shelter details."""

		return "<Shelter shelter_id=%s Zipcode zipcode=%s" % (self.shelter_id, self.zipcode)

class Breed(db.Model):
	"""Information about breeds."""

	__tablename__ = "breeds"

	breed_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
	breed = db.Column(db.String(50))
	description = db.Column(db.String(10000), nullable=True)
	img_url = db.Column(db.String(300), nullable=True)

	def __repr__(self):
		"""Provide breed details."""

		return "<Breed_id breed_id=%s Breed breed=%s" % (self.breed_id, self.breed)
def example_data():
    """Create some sample data."""

    # In case this is run more than once, empty out existing data
   
    User.query.delete()
    Favorite.query.delete()
    Dog.query.delete()
    Shelter.query.delete()
    Breed.query.delete()


    u1 = User(user_id='1', email='abby@gmail.com', password='abc123')
    u2 = User(user_id='2', email='mimi@gmail.com', password='def456')
    u3 = User(user_id='3', email='brie@gmail.com', password='ghi789')

    abby = Favorite(fave_id='34', user_id='1', petfinder_id='12345')
    mimi = Favorite(fave_id='23', user_id='2', petfinder_id='65390')
    brie = Favorite(fave_id='54', user_id='3', petfinder_id='83567')

    honey = Dog(petfinder_id='12345', shelter_id='CA3452')
    margo = Dog(petfinder_id='65390', shelter_id='WA41')
    louise = Dog(petfinder_id='83567', shelter_id='CA1212')

    sh1 = Shelter(shelter_id='CA3452', zipcode='94108')
    sh2 = Shelter(shelter_id='WA41', zipcode='98383')
    sh3 = Shelter(shelter_id='CA1212', zipcode='90210')

    cav = Breed(breed_id='1', breed='Cavalier King Charles Spaniel')
    lab = Breed(breed_id='2', breed='Labrador Retriever')
    pug = Breed(breed_id='3', breed='Pug')

    db.session.add_all([u1, u2, u3, abby, mimi, brie, honey, margo, louise, 
    					sh1, sh2, sh3, cav, lab, pug])
    db.session.commit()


##############################################################################
# Helper functions

def connect_to_db(app, db_uri="postgresql:///dogs"):
    """Connect the database to our Flask app."""

    # Configure to use our PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)

