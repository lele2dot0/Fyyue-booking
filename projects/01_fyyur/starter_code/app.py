#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

#from crypt import methods
from email.policy import default
from enum import unique
import json
from pickle import FALSE
from tkinter import Place
from unicodedata import name
from unittest import result
from datetime import datetime
import dateutil.parser
import babel
from flask import Flask, jsonify, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:5uMm!t3ch%40!@localhost:5432/fyyurapp'
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(700))
    website_link = db.Column(db.String(700))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(1000))
    shows = db.relationship('Show', backref = 'place', lazy = True)
    
    def __repr__(self):
      return f'<Venue {self.id} {self.name} {self.city} {self.state} {self.address} {self.phone} {self.genres} {self.image_link} {self.facebook_link} {self.website_link} {self.seeking_talent} {self.seeking_description}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref = 'artist', lazy = True)
    
    def __repr__(self):
      return f'<Artist {self.id} {self.name} {self.city} {self.phone} {self.genres} {self.image_link} {self.facebook_link} {self.website_link} {self.seeking_venue} {self.seeking_description}>'
    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
  __tablename__ = 'Shows'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable = False )
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable = False)
  show_time = db.Column(db.DateTime, nullable = False)

  def __repr__(self):
      return f'<Show {self.id} {self.show_time}, place {self.venue_id}>'

show_lineup = db.Table('show_lineup',
  db.Column('show_id', db.Integer, db.ForeignKey('Shows.id'), primary_key = True),
  db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key = True)
)

db.create_all()
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str):
        date = dateutil.parser.parse(value)
  else:
        date = value
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

  venues = Venue.query.all()
  return render_template('pages/venues.html', venues=venues)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  venues = Venue.query.all()
  search_term = request.form.get('search_term', '')

  result_count = 0
  results  = []
  for venue in venues:
    print(venue.name)
    if search_term in venue.name.lower():
      results.append(venue)
      result_count += 1
  print(" The results are", results)


  return render_template('pages/search_venues.html', results=results, search_term=search_term, result_count=result_count)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  shows = Show.query.filter_by(venue_id = venue_id)
  artists = Artist.query.all()
  performers = []

  for artist in artists:
    for show in shows:
      if show.artist_id == artist.id:
        if artist not in performers:
          performers.append(artist)
  print("List of Artists is below: ")  
  print(performers)   

  upcoming_shows_count = 0
  past_shows_count = 0
  for show in shows:
    if show.show_time > datetime.now():
      upcoming_shows_count += 1
    elif show.show_time < datetime.now():
      past_shows_count += 1

  print("Upcoming Shows count: " + str(upcoming_shows_count))
  print("Past Shows count: " + str(past_shows_count))
  print("These are the shows: ")
  print(shows)

  past_shows = []
  upcoming_shows = []
  for show in shows:
    if show.show_time > datetime.now():
      upcoming_shows.append(show)
    elif show.show_time < datetime.now():
      past_shows.append(show)
  
  print("The following are upcoming shows: ")
  print(upcoming_shows)
  print("The following are past shows: ")
  print(past_shows)

  return render_template('pages/show_venue.html', venue=venue, shows = shows, upcoming_shows_count = upcoming_shows_count, past_shows_count = past_shows_count,
                          past_shows = past_shows, upcoming_shows = upcoming_shows, artists = performers)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  #venue_submission = request.form
  form = VenueForm(request.form)
  error = False
  try:
    venue = Venue(
    name =form.name.data,
    city =form.city.data,
    state =form.state.data,
    address =form.address.data,
    phone = form.phone.data,
    genres = form.genres.data,
    image_link = form.image_link.data,
    website_link = form.website_link.data,
    facebook_link = form.facebook_link.data,
    seeking_talent = form.seeking_talent.data,
    seeking_description = form.seeking_description.data
    )
    
    db.session.add(venue)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  if form.validate_on_submit() and error == False:
  # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  elif error:
    flash('An error occured. Venue ' + request.form['name'] + ' could not be listed. Please try again.')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html') #venue_submission 

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('home')), jsonify({'success':True})

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  form = ArtistForm()
  artists = Artist.query.all()
  
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  artists = Artist.query.all()
  search_term = request.form.get('search_term', '')

  result_count = 0
  results  = []
  for artist in artists:
    print(artist.name)
    if search_term in artist.name.lower():
      results.append(artist)
      result_count += 1
  print(" The results are", results)
  return render_template('pages/search_artists.html', results=results, search_term=search_term, result_count=result_count)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
  shows = Show.query.filter_by(artist_id = artist_id)
  venues = Venue.query.all()
  show_venues = []

  for venue in venues:
    for show in shows:
      if show.venue_id == venue.id:
        if venue not in show_venues:
          show_venues.append(venue)
  print("List of Artist Venues is below: ")  
  print(show_venues)   

  upcoming_shows_count = 0
  past_shows_count = 0
  for show in shows:
    if show.show_time > datetime.now():
      upcoming_shows_count += 1
    elif show.show_time < datetime.now():
      past_shows_count += 1
  past_shows = []
  upcoming_shows = []
  for show in shows:
    if show.show_time > datetime.now():
      upcoming_shows.append(show)
    elif show.show_time < datetime.now():
      past_shows.append(show)
  
  print("The following are upcoming shows: ")
  print(upcoming_shows)
  print("The following are past shows: ")
  print(past_shows)

  

  print("Upcoming Shows count: " + str(upcoming_shows_count))
  print("Past Shows count: " + str(past_shows_count))
  print(shows)

  
  return render_template('pages/show_artist.html', artist=artist, upcoming_shows_count = upcoming_shows_count,
   past_shows_count = past_shows_count, show_venues = show_venues, past_shows = past_shows, upcoming_shows = upcoming_shows)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist= Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  artist= Artist.query.get(artist_id)
  error = False
  try:

    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.genres = form.genres.data
    artist.image_link = form.image_link.data
    artist.website_link = form.website_link.data
    artist.facebook_link = form.facebook_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data

    db.session.commit()
  except:
    db.session.rollback()
    error = True
  finally:
    db.session.close()
  # on successful db insert, flash success
  if error:
    flash('An error occurred. Artist ' + artist.name + ' could not be updated')
  else:
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

  return redirect(url_for('show_artist', artist_id=artist_id, artist=artist))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue= Venue.query.get(venue_id)
  form = VenueForm(obj=venue)
  
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue= Venue.query.get(venue_id)
  form = VenueForm(request.form)
  error = False
  try:

    venue.name =form.name.data
    venue.city =form.city.data
    venue.state =form.state.data
    venue.address =form.address.data
    venue.phone = form.phone.data
    venue.genres = form.genres.data
    venue.image_link = form.image_link.data
    venue.website_link = form.website_link.data
    venue.facebook_link = form.facebook_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data

    db.session.commit()

  except:
    db.session.rollback()
    error = True

  finally:
    db.session.close()
  if error:
    flash('Artist ' + venue.name + ' could no be updated, please try again.')
  # on successful db insert, flash success
  elif error == False and form.validate_on_submit:
    flash('Artist ' + venue.name + ' was successfully updated!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

  return redirect(url_for('show_venue', venue_id=venue_id, venue=venue))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm(request.form)
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    artist = Artist(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      genres = form.genres.data,
      image_link = form.image_link.data,
      website_link = form.website_link.data,
      facebook_link = form.facebook_link.data,
      seeking_venue = form.seeking_venue.data,
      seeking_description = form.seeking_description.data
    )
    db.session.add(artist)
    db.session.commit()
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + artist.name + ' could not be listed.')
  finally:
    db.session.close()
  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.all()
  artists = Artist.query.all()
  venues = Venue.query.all()
  
  return render_template('pages/shows.html', shows=shows, artists=artists, venues=venues)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)
  error = False
  try:
    show = Show (
      artist_id = form.artist_id.data,
      venue_id = form.venue_id.data,
      show_time = form.start_time.data
    )

    db.session.add(show)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    
  finally:
    db.session.close()

  # on successful db insert, flash success
  if error:
    flash('An error occurred. Show could not be listed.')
  else:
    flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
