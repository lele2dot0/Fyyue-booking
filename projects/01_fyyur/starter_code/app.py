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
from flask_wtf.csrf import CSRFError
from forms import *
from models import *

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
  venue_details = Venue.query.get(venue_id)
  artists = Artist.query.all()
  upcoming_shows_count = 0
  past_shows_count = 0
  performers = []
  past_shows = []
  upcoming_shows = []

  past_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.show_time < datetime.now()).all()
  upcoming_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.show_time > datetime.now()).all()

  for show in past_shows_query:
    past_shows.append(show)
    past_shows_count += 1
    print("past show:", show)

  for show in upcoming_shows_query:
    upcoming_shows.append(show)
    upcoming_shows_count += 1
    print("upcoming show:", show)

  show_details = db.session.query(Venue, Artist, Show).select_from(Show).join(Artist).join(Venue).all()
  
  for artist in artists:
    for show in past_shows_query:
        if show.artist_id == artist.id:
          if artist not in performers:
            performers.append(artist)

  print("List of Artists is below: ")  
  print(performers)   

  print("Upcoming Shows count: " + str(upcoming_shows_count))
  print("Past Shows count: " + str(past_shows_count))

  
  print("The following are upcoming shows: ")
  print(upcoming_shows)
  print("The following are past shows: ")
  print(past_shows)

  return render_template('pages/show_venue.html', venue = venue_details, upcoming_shows_count = upcoming_shows_count, past_shows_count = past_shows_count,
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
    '''.replace("-","")'''
    form = VenueForm(request.form)
    error = False
    if form.validate_on_submit():

      try:
        venue = Venue(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        address = form.address.data,
        phone = form.phone.data.replace("-",""), 
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
    else:
      for error in form.errors:
        flash(error)
        
    if error == False:
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    elif error:
      flash('An error occured. Venue ' + request.form['name'] + ' could not be listed. Please try again.')

      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return redirect('/venues')

@app.route('/venues/<venue_id>', methods=['DELETE'])
@csrf.exempt
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
  return render_template('pages/venues.html')

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
  artist_details = Artist.query.get(artist_id)
  past_shows = []
  upcoming_shows = []
  upcoming_shows_count = 0
  past_shows_count = 0
  past_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.show_time < datetime.now()).all()
  upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.show_time > datetime.now()).all()

  for show in past_shows_query:
    past_shows.append(show)
    past_shows_count += 1

  for show in upcoming_shows_query:
    upcoming_shows.append(show)
    upcoming_shows_count += 1
  
  show_details = db.session.query(Venue, Artist, Show).select_from(Show).join(Artist).join(Venue).all()
  for venue, artist, show in show_details:
    print("Show details", show.id, venue.name, artist.name )
  print(show_details)

  print("The following are upcoming shows: ")
  print(upcoming_shows)
  print("The following are past shows: ")
  print(past_shows)

  print("Upcoming Shows count: " + str(upcoming_shows_count))
  print("Past Shows count: " + str(past_shows_count))

  
  return render_template('pages/show_artist.html', artist_details=artist_details, upcoming_shows_count = upcoming_shows_count,
   past_shows_count = past_shows_count, past_shows = past_shows, upcoming_shows = upcoming_shows, show_details = show_details)

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
   
  if form.validate_on_submit():
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
    
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
  else:
    flash('An error occurred. Artist ' + artist.name + ' could not be updated')
    for error in form.errors:
      flash(error)
  # on successful db insert, flash success
      
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

  return redirect('/artists/' + str(artist_id))

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

  if form.validate_on_submit:
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
  else:
      for error in form.errors:
        flash(error)
  if error:
    flash('Venue ' + request.form['name'] + ' could no be updated, please try again.')
  # on successful db insert, flash success
  elif error == False and form.validate_on_submit:
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')

  return redirect('/venues/' + str(venue_id))

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
  error = False
  if form.validate_on_submit:
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
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    finally:
      db.session.close()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  else:
      for error in form.errors:
        flash(error)
  
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return redirect('/artists')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.all()
  artists = Artist.query.all()
  venues = Venue.query.all()
  
  return render_template('pages/shows.html', shows=shows, artist=artist, venues=venues)

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
  if form.validate_on_submit:
    try:
      show = Show (
        artist_id = form.artist_id.data,
        venue_id = form.venue_id.data,
        show_time = form.start_time.data
      )

      show_lineup

      db.session.add(show)
      db.session.commit()
    except:
      db.session.rollback()
      error = True
      
    finally:
      db.session.close()
  else:
      for error in form.errors:
        flash(error)

  # on successful db insert, flash success
  if error:
    flash('An error occurred. Show could not be listed.')
  else:
    flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return redirect('/shows')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('errors/500.html', reason=e.description), 400


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
