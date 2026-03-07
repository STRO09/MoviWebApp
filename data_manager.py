import os

import requests

from models import Movie, User, db


class DataManager:
    OMDB_API_KEY = os.environ.get("OMDB_API_KEY", "")

    # USERS
    def create_user(self, name, password):
        """Return (user, created). created=False if username already existed."""
        existing = User.query.filter_by(username=name).first()
        if existing:
            return existing, False
        user = User(username=name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user, True

    def get_user_by_username(self, username):
        return User.query.filter_by(username=username).first()

    def get_users(self):
        return User.query.all()

    def delete_user(self, user_id):
        user = db.session.get(User, user_id)
        if not user:
            return False
        Movie.query.filter_by(user_id=user_id).delete()
        db.session.delete(user)
        db.session.commit()
        return True

    # MOVIES
    def get_movies(self, user_id, sort="title"):
        movies = Movie.query.filter_by(user_id=user_id).all()
        if sort == "rating":
            movies.sort(key=lambda m: m.rating or 0, reverse=True)
        elif sort == "year":
            movies.sort(key=lambda m: m.year or "", reverse=True)
        else:
            movies.sort(key=lambda m: m.title.lower())
        return movies

    def fetch_omdb_data(self, title):
        """Fetch movie metadata from OMDb. Returns a dict or {} if unavailable."""
        if not self.OMDB_API_KEY:
            return {}
        try:
            resp = requests.get(
                "https://www.omdbapi.com/",
                params={"t": title, "apikey": self.OMDB_API_KEY},
                timeout=5,
            )
            data = resp.json()
            if data.get("Response") == "True":
                poster = data.get("Poster", "")
                return {
                    "year": data.get("Year", "")[:10],
                    "director": data.get("Director", "")[:120],
                    "plot": data.get("Plot", ""),
                    "poster_url": poster if poster != "N/A" else "",
                }
        except Exception:
            pass
        return {}

    def add_movie(self, movie):
        db.session.add(movie)
        db.session.commit()
        return movie

    def update_movie(self, movie_id, new_title, new_rating=None):
        movie = db.session.get(Movie, movie_id)
        if not movie:
            return None
        movie.title = new_title
        movie.rating = new_rating
        meta = self.fetch_omdb_data(new_title)
        if meta:
            movie.year = meta.get("year")
            movie.director = meta.get("director")
            movie.plot = meta.get("plot")
            movie.poster_url = meta.get("poster_url")
        db.session.commit()
        return movie

    def delete_movie(self, movie_id):
        movie = db.session.get(Movie, movie_id)
        if not movie:
            return False
        db.session.delete(movie)
        db.session.commit()
        return True
