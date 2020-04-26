# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue', lazy=True)
    genres = db.Column(db.ARRAY(db.String()))

    @property
    def past_shows(self):
        now = datetime.now()
        past_shows = [show for show in self.shows if datetime.strptime(
            show.start_time, '%Y-%m-%d %H:%M:%S') < now]
        return past_shows

    @property
    def upcoming_shows(self):
        now = datetime.now()
        future_shows = [show for show in self.shows if datetime.strptime(
            show.start_time, '%Y-%m-%d %H:%M:%S') > now]
        return future_shows

    @property
    def past_shows_count(self):
        return len(self.past_shows)

    @property
    def upcoming_shows_count(self):
        return len(self.upcoming_shows)

    # TODO: implement any missing fields, as a database migration using
    # Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref='artist', lazy=True)
    genres = db.Column(db.ARRAY(db.String()))

    @property
    def past_shows(self):
        now = datetime.now()
        past_shows = [show for show in self.shows if datetime.strptime(
            show.start_time, '%Y-%m-%d %H:%M:%S') < now]
        return past_shows

    @property
    def upcoming_shows(self):
        now = datetime.now()
        future_shows = [show for show in self.shows if datetime.strptime(
            show.start_time, '%Y-%m-%d %H:%M:%S') > now]
        return future_shows

    @property
    def past_shows_count(self):
        return len(self.past_shows)

    @property
    def upcoming_shows_count(self):
        return len(self.upcoming_shows)


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)

    venue_id = db.Column(db.Integer, db.ForeignKey(
        'Venue.id'), nullable=False)

    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), nullable=False)

    start_time = db.Column(db.String(), nullable=False)

    @property
    def artist_name(self):
        return Artist.query.get(self.artist_id).name

    @property
    def artist_image_link(self):
        return Artist.query.get(self.artist_id).image_link

    @property
    def venue_name(self):
        return Venue.query.get(self.venue_id).name

    @property
    def venue_image_link(self):
        return Venue.query.get(self.venue_id).image_link


db.create_all()
# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    # num_shows should be aggregated based on number of upcoming shows per
    # venue.
    data = Venue.query.all()
    # create a list of cities
    cities = [(d.city, d.state) for d in data]
    cities = set(cities)
    return render_template('pages/venues.html', cities=cities, venues=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live
    # Music & Coffee"
    venues = Venue.query.filter(func.lower(Venue.name).contains(
        request.form.get('search_term').lower())).all()
    count = len(venues)
    response = {
        "count": count,
        "data": venues
    }
    return render_template(
        'pages/search_venues.html',
        results=response,
        search_term=request.form.get(
            'search_term',
            ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.get(venue_id)
    return render_template('pages/show_venue.html', venue=venue)

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
    data = request.form
    venues = Venue.query.filter_by(name=data['name']).all()
    count = len(venues)
    if count > 0:
        flash('An error occurred. Venue ' +
              request.form['name'] + ' already exists!')
        return render_template('pages/home.html')

    try:
        venue = Venue(
            name=data['name'],
            city=data['city'],
            state=data['state'],
            address=data['address'],
            phone=data['phone'],
            genres=[
                data['genres']],
            facebook_link=data['facebook_link'])
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully created!')
    except BaseException:
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be created.')
        db.session.rollback()
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit
    # could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the
    # homepage
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
        flash('Venue was successfully deleted!')
    except BaseException:
        db.session.rollback()
        flash('Venue failed to delete!')
    finally:
        db.session.close()

    return None

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    artists = Artist.query.filter(func.lower(Artist.name).contains(
        request.form.get('search_term').lower())).all()

    count = len(artists)
    response = {
        "count": count,
        "data": artists
    }
    return render_template(
        'pages/search_artists.html',
        results=response,
        search_term=request.form.get(
            'search_term',
            ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    data = Artist.query.get(artist_id)
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist.query.get(artist_id)
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link

    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    try:
        data = request.form
        artist = Artist.query.get(artist_id)
        artist.name = data['name']
        artist.city = data['city']
        artist.state = data['state']
        artist.genres = [data['genres']]
        artist.phone = data['phone']
        artist.facebook_link = data['facebook_link']
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully edited!')
    except BaseException:
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be edited.')
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue.query.get(venue_id)
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.address.data = venue.address
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link

    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    try:
        data = request.form
        venue = Venue.query.get(venue_id)
        venue.name = data['name']
        venue.city = data['city']
        venue.state = data['state']
        venue.genres = [data['genres']]
        venue.phone = data['phone']
        venue.address = data['address']
        venue.facebook_link = data['facebook_link']
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully edited!')
    except BaseException:
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be edited.')
        db.session.rollback()
    finally:
        db.session.close()

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
    data = request.form
    artist = Artist.query.filter_by(name=data['name']).all()
    count = len(artist)
    if count > 0:
        flash('An error occurred. Artist ' +
              request.form['name'] + ' already exists!')
        return render_template('pages/home.html')

    try:
        data = request.form
        artist = Artist(
            name=data['name'],
            city=data['city'],
            state=data['state'],
            phone=data['phone'],
            genres=[
                data['genres']],
            facebook_link=data['facebook_link'])
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully created!')
    except BaseException:
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be created.')
        db.session.rollback()
    finally:
        db.session.close()

    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------


@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    # num_shows should be aggregated based on number of upcoming shows per
    # venue.
    data = Show.query.all()
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

    # on successful db insert, flash success
    # flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    try:
        data = request.form
        show = Show(artist_id=data['artist_id'],
                    venue_id=data['venue_id'], start_time=data['start_time'])
        db.session.add(show)
        db.session.commit()
        flash('The show was successfully created!')
    except BaseException:
        flash('An error occurred. The show could not be created.')
        db.session.rollback()
    finally:
        db.session.close()

    return render_template('pages/home.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
