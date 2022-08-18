#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import datetime
import collections
collections.Callable = collections.abc.Callable
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)


# TODO: connect to a local postgresql database
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# venue_genres = db.Table('venuegenre',
    # db.Column('venue_id', db.Integer, db.ForeignKey('venue.id'), primary_key=True),
    # db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True))

# artist_genres = db.Table('artistgenre',
#     db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'), primary_key=True),
#     db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True)
# )


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String))
    # genres = db.relationship('Genre', backref=db.backref('venue', lazy=True))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String))
    # genres = db.relationship('Genre', secondary=artist_genres, backref=db.backref('artist', lazy=True))
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'show'
    
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))

# class Genre(db.Model):
#     __tablename__ = 'genre'

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(120), nullable=False)
#     venue_genres=db.Column( db.Integer, db.ForeignKey('venue.id'), nullable=False)

    
       

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
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
  data=[]
  areas = Venue.query.distinct('city','state').all()
  for area in areas:
    venues = Venue.query.filter(Venue.city==area.city, Venue.state==area.state)
    record = {
      "city": area.city,
      "state": area.state,
      "venues": [{
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": Show.query.filter(Show.venue_id == venue.id, Show.start_time > datetime.utcnow()).count()
      } for venue in venues]
    }
    data.append(record)
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  data = request.form.get('search_term', '')
  search_results = Venue.query.filter(Venue.name.ilike('%' + data + '%')).all()
  response={
    "count": len(search_results),
    "data": [{
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": Show.query.filter(Show.venue_id == venue.id, Show.start_time > datetime.utcnow()).count(),
    } for venue in search_results]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id

  venue = Venue.query.filter_by(id=venue_id).first()

  # TODO: replace with real venue data from the venues table, using venue_id

  data = venue.__dict__

  data_past = []
  past_shows = Show.query.filter(Show.venue_id == venue_id, Show.start_time < datetime.utcnow()).all()
  for past_show in past_shows:
    artist = Artist.query.filter_by(id=past_show.artist_id).first()
    record = {
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": str(past_show.start_time)
    }
    data_past.append(record)

  data_upcoming = []
  upcoming_shows = Show.query.filter(Show.venue_id == venue_id, Show.start_time > datetime.utcnow()).all()
  for upcoming_show in upcoming_shows:
    artist = Artist.query.filter_by(id=upcoming_show.artist_id).first()
    record = {
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": str(upcoming_show.start_time)
    }
    data_upcoming.append(record)

  data["past_shows"] = data_past
  data["upcoming_shows"] = data_upcoming
  
  return render_template('pages/show_venue.html', venue=data)

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

  error = False
  try:
    data = request.form
    venue = Venue(name=data['name'], city=data['city'], state=data['state'], address=data['address'], phone=data['phone'], facebook_link = data['facebook_link'], image_link=data['image_link'], website=data['website'],
    genres = data.getlist('genres'), seeking_description=data['seeking_description'])
    if 'seeking_talent' in data:
      venue.seeking_talent=(data['seeking_talent'] == 'y')
    # genres = data.getlist('genres')
    # for g in genres:
    #   genre = Genre.query.filter(Genre.name == g).first()
    #   venue.genres.append(genre)

    db.session.add(venue)

    
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()

  if error:
    # on unsuccessful db insert, flash error
    flash('An error occurred. Venue ' + data['name'] + ' could not be listed.')

     # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()

  if error:
    # on unsuccessful db insert, flash error
    flash('An error occurred. Venue could not be deleted.')
  else:
    # on successful db insert, flash success
    flash('Venue was successfully deleted!')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  data= Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  data = request.form.get('search_term', '')
  search_results = Artist.query.filter(Artist.name.ilike('%' + data + '%')).all()

  response={
    "count": 1,
    "data": [{
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": Show.query.filter(Show.artist_id == artist.id, Show.start_time > datetime.utcnow()).count(),
    } for artist in search_results]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  artist = Artist.query.filter_by(id=artist_id).first()

  # TODO: replace with real artist data from the artist table, using artist_id
  data = artist.__dict__
  
  data_past = []
  past_shows = Show.query.filter(Show.artist_id==artist_id, Show.start_time < datetime.utcnow()).all()
  past_shows_cnt = len(past_shows)
  for past_show in past_shows:
    venue = Venue.query.filter_by(id=past_show.venue_id).first()
    record = {
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": str(past_show.start_time)
    }
    data_past.append(record)

  data_upcoming = []
  upcoming_shows = Show.query.filter(Show.artist_id==artist_id, Show.start_time > datetime.utcnow()).all()
  upcoming_shows_cnt = len(upcoming_shows)
  for upcoming_show in upcoming_shows:
    venue = Venue.query.filter_by(id=upcoming_show.venue_id).first()
    record = {
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link,
      "start_time": str(upcoming_show.start_time)
    }
    data_upcoming.append(record)

  data["past_shows"] = data_past
  data["upcoming_shows"] = data_upcoming
  data["past_shows_count"] = past_shows_cnt
  data["upcoming_shows_count"] = upcoming_shows_cnt
  

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist= Artist.query.filter_by(id=artist_id).first()
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  try:
    data = request.form
    artist = Artist.query.filter_by(id=artist_id).first()
    artist.name = data['name']
    artist.city = data['city']
    artist.state = data['state']
    artist.phone = data['phone']
    artist.facebook_link = data['facebook_link']
    artist.image_link = data['image_link']
    artist.website = data['website']
    artist.seeking_venue = (data['seeking_venue'] == 'y')
    artist.seeking_description = data['seeking_description']
    
    artist.genres = []

    genres = data.getlist('genres')
    for g in genres:
      genre = Genre.query.filter(Genre.name == g).first()
      artist.genres.append(genre)

    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()

  if error:
    # on unsuccessful db insert, flash error

    flash('An error occurred. Artist ' + data['name'] + ' could not be edited.')
  else:
    # on successful db insert, flash success

    flash('Artist ' + data['name'] + ' was successfully edited!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
# TODO: populate form with values from venue with ID <venue_id>
def edit_venue(venue_id):
  form = VenueForm()
  venue= Venue.query.filter_by(id=venue_id).first()
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  try:
    data = request.form
    venue = Venue.query.filter_by(id=venue_id).first()
    venue.name = data['name']
    venue.city = data['city']
    venue.state = data['state']
    venue.phone = data['phone']
    venue.address = data['address']
    venue.facebook_link = data['facebook_link']
    venue.image_link = data['image_link']
    venue.website = data['website']
    if 'seeking_talent' in data:
      venue.seeking_talent = (data['seeking_talent'] == 'y')
      venue.seeking_description = data['seeking_description']
    else:
      venue.seeking_talent = False
      venue.seeking_description = []
    
    venue.genres = []
    genres = data.getlist('genres')
    for g in genres:
      genre = Genre.query.filter(Genre.name == g).first()
      venue.genres.append(genre)

    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()

  if error:
    # on unsuccessful db insert, flash error
    flash('An error occurred. Venue ' + data['name'] + ' could not be edited.')
  else:
    # on successful db insert, flash success
    flash('Venue ' + data['name'] + ' was successfully edited!')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion


  error = False
  try:
    data = request.form
    artist = Artist(name=data['name'], city=data['city'], state=data['state'], phone=data['phone'], facebook_link = data['facebook_link'], image_link=data['image_link'], website=data['website'],
    genres = data.getlist('genres'), seeking_description=data['seeking_description'])
    if 'seeking_venue' in data:
      artist.seeking_venue=(data['seeking_venue'] == 'y')

    db.session.add(artist)


    db.session.commit()

  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()

  if error:
    # on unsuccessful db insert, flash error
    flash('An error occurred. Artist ' + data['name'] + ' could not be listed.')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Artist ' + data['name'] + ' was successfully listed!')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  shows = Show.query.filter((Show.start_time > datetime.utcnow())).all()
  for show in shows:
    record = {
      "venue_id": show.venue_id,
      "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
      "artist_id": show.artist_id,
      "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
      "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
      "start_time": str(show.start_time)
    }
    data.append(record)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  error = False
  try:
    data = request.form
    show = Show(artist_id=data['artist_id'], venue_id=data['venue_id'], start_time=data['start_time'])
    db.session.add(show)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    # on unsuccessful db insert, flash error
    flash('An error occurred. Show could not be listed.')
    # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  else:
    # on successful db insert, flash success
    flash('Show was successfully listed!')
  
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
