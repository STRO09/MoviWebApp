"""Run once to populate the DB with sample users and movies."""
from dotenv import load_dotenv
load_dotenv()

from app import app, db, data_manager
from models import Movie

# Each user has a distinct taste. Ratings reflect personal preference, not quality.
SEED_DATA = {
    "alice": [                          # Nolan obsessive
        ("The Dark Knight",         5),
        ("Inception",               5),
        ("Interstellar",            4),
        ("The Prestige",            4),
        ("Memento",                 5),
        ("Dunkirk",                 3),
    ],
    "bob": [                            # Crime & gangster
        ("Pulp Fiction",            5),
        ("Fight Club",              4),
        ("The Godfather",           5),
        ("Goodfellas",              4),
        ("Heat",                    5),
        ("No Country for Old Men",  5),
        ("Se7en",                   4),
    ],
    "carol": [                          # International & arthouse
        ("Parasite",                5),
        ("Everything Everywhere All at Once", 5),
        ("Spirited Away",           4),
        ("Amelie",                  5),
        ("Pan's Labyrinth",         4),
        ("City of God",             5),
    ],
    "dave": [                           # Sci-fi geek
        ("Blade Runner 2049",       5),
        ("2001: A Space Odyssey",   5),
        ("Arrival",                 5),
        ("The Matrix",              4),
        ("Dune",                    4),
        ("Ex Machina",              4),
        ("Moon",                    4),
    ],
    "emma": [                           # Horror & thriller
        ("Hereditary",              5),
        ("Get Out",                 5),
        ("The Shining",             5),
        ("A Quiet Place",           4),
        ("Midsommar",               4),
        ("Alien",                   5),
        ("The Silence of the Lambs", 5),
    ],
    "frank": [                          # Action & blockbusters
        ("Mad Max: Fury Road",      5),
        ("John Wick",               5),
        ("Die Hard",                4),
        ("Mission: Impossible - Fallout", 4),
        ("Top Gun: Maverick",       5),
        ("The Raid",                4),
    ],
    "grace": [                          # Animation lover
        ("Spirited Away",           5),
        ("The Lion King",           4),
        ("WALL-E",                  5),
        ("Up",                      5),
        ("Princess Mononoke",       5),
        ("Spider-Man: Into the Spider-Verse", 5),
        ("Coco",                    4),
    ],
    "henry": [                          # Classic Hollywood
        ("Casablanca",              5),
        ("Singin' in the Rain",     5),
        ("Sunset Blvd.",            5),
        ("Rear Window",             5),
        ("Some Like It Hot",        4),
        ("12 Angry Men",            5),
        ("To Kill a Mockingbird",   4),
    ],
    "iris": [                           # Drama & romance
        ("Before Sunrise",          5),
        ("Lost in Translation",     5),
        ("Her",                     5),
        ("Eternal Sunshine of the Spotless Mind", 5),
        ("The Notebook",            3),
        ("Normal People",           4),
    ],
    "jake": [                           # Comedy first
        ("The Grand Budapest Hotel", 5),
        ("Superbad",                4),
        ("Monty Python and the Holy Grail", 5),
        ("This Is Spinal Tap",      4),
        ("Knives Out",              5),
        ("The Nice Guys",           5),
        ("Game Night",              3),
    ],
    "kate": [                           # Biopics & documentaries
        ("Bohemian Rhapsody",       3),
        ("Whiplash",                5),
        ("I, Tonya",                4),
        ("The Social Network",      5),
        ("Oppenheimer",             5),
        ("Steve Jobs",              4),
        ("Sully",                   3),
    ],
}

with app.app_context():
    db.create_all()
    for username, movies in SEED_DATA.items():
        user, created = data_manager.create_user(username, "password123")
        if created:
            print(f"Created user: {username}")
        else:
            print(f"User already exists: {username}")
        for title, rating in movies:
            existing = Movie.query.filter_by(user_id=user.id, title=title).first()
            if existing:
                print(f"  - skipping '{title}'")
                continue
            meta = data_manager.fetch_omdb_data(title)
            movie = Movie(
                title=title,
                user_id=user.id,
                rating=rating,
                year=meta.get("year"),
                director=meta.get("director"),
                plot=meta.get("plot"),
                poster_url=meta.get("poster_url"),
            )
            db.session.add(movie)
            db.session.commit()
            print(f"  + '{title}' ({meta.get('year', '?')}) poster={'yes' if meta.get('poster_url') else 'no'}")

print("\nDone.")
