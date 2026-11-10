"""Generate test data for the platform.

Usage:  python seed_data.py            (resets instance/idp_platform.db)
        python seed_data.py --accounts 200

Creates four fixed demo logins (one per role) plus randomly generated accounts,
so every data type has 100+ records as the project spec requires.
"""
import argparse
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from werkzeug.security import generate_password_hash

import db

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB = BASE_DIR / "instance" / "idp_platform.db"
DEMO_PASSWORD = "password123"
DEMO_DESIGNER_ID, DEMO_CUSTOMER_ID = 2, 3

DEMO_ACCOUNTS = [
    # (full name, username, email, profile id)
    ("Alice Admin", "admin", "admin@idp.test", 1),
    ("Daniel Designer", "designer", "designer@idp.test", 2),
    ("Cindy Customer", "customer", "customer@idp.test", 3),
    ("Patrick Platform", "platform", "platform@idp.test", 4),
]

FIRST = ["Aaron", "Bella", "Chen", "Divya", "Ethan", "Fatimah", "Gavin", "Hui Min", "Irfan",
         "Jasmine", "Kai", "Lina", "Marcus", "Nur", "Oliver", "Priya", "Qi Hao", "Rachel",
         "Siti", "Tom", "Umar", "Vanessa", "Wei Jie", "Xin Yi", "Yusuf", "Zoe"]
LAST = ["Tan", "Lim", "Lee", "Ng", "Wong", "Goh", "Chua", "Ong", "Koh", "Teo", "Kumar",
        "Rahman", "Singh", "Ismail", "Chong", "Yeo", "Low", "Sim", "Ho", "Pillai"]

STYLES = ["Scandinavian", "Japandi", "Modern Luxe", "Industrial", "Minimalist", "Contemporary",
          "Mid-Century Modern", "Peranakan", "Tropical Resort", "Wabi-Sabi"]
STYLE_NOTES = {
    "Scandinavian": "light woods, white walls and cosy textiles",
    "Japandi": "Japanese calm meets Nordic function",
    "Modern Luxe": "marble, brass accents and rich materials",
    "Industrial": "exposed brick, concrete and black metal",
    "Minimalist": "clean lines and hidden storage",
    "Contemporary": "current trends with neutral palettes",
    "Mid-Century Modern": "1950s-60s forms, teak and bold colour",
    "Peranakan": "heritage tiles, colour and ornate detail",
    "Tropical Resort": "natural materials and indoor greenery",
    "Wabi-Sabi": "raw textures and imperfect beauty",
}
ROOMS = ["Living Room", "Kitchen", "Master Bedroom", "Bathroom", "Study", "Dining Room",
         "Kids Room", "Balcony", "Walk-in Wardrobe", "Entryway"]
COMPANY_WORDS = ["Atelier", "Studio", "Interiors", "Design Co", "Living", "Spaces", "Concepts", "Works"]
COMPANY_PREFIX = ["Oak", "Linen", "Haven", "Nest", "Ember", "Stone", "Willow", "Arch", "Loft", "Moss",
                  "Cove", "Ivory", "Slate", "Canvas", "Harbour", "Juniper", "Terra", "Lumen"]
STREETS = ["Ubi Avenue 1", "Kaki Bukit Road 3", "Tai Seng Street", "Bukit Merah Central", "Jalan Besar",
           "Geylang Bahru", "Changi South Lane", "Toa Payoh Lorong 8", "Sin Ming Road", "Paya Lebar Road"]

# Weighted so most generated users are customers and designers, as on a real platform.
PROFILE_WEIGHTS = {1: 5, 2: 35, 3: 55, 4: 5}


def generate_accounts(count: int, rng: random.Random):
    used = {u for _, u, _, _ in DEMO_ACCOUNTS}
    rows = []
    while len(rows) < count:
        first, last = rng.choice(FIRST), rng.choice(LAST)
        username = f"{first.lower().replace(' ', '')}{last.lower()}{rng.randint(1, 999)}"
        if username in used:
            continue
        used.add(username)
        profile = rng.choices(list(PROFILE_WEIGHTS), weights=PROFILE_WEIGHTS.values())[0]
        status = "SUSPENDED" if rng.random() < 0.08 else "ACTIVE"
        created = stamp(random_moment(rng, 150))
        rows.append((f"{first} {last}", username, f"{username}@example.com", profile, status, created))
    return rows


ESTATES = ["Punggol", "Tampines", "Bishan", "Queenstown", "Sengkang", "Jurong East", "Toa Payoh",
           "Bukit Timah", "Clementi", "Hougang", "Pasir Ris", "Woodlands", "Tiong Bahru", "Marine Parade"]
HOMES = ["3-room HDB", "4-room HDB", "5-room HDB", "Executive Maisonette", "Condo", "Landed Terrace",
         "Semi-D", "Shophouse"]
DESCRIPTIONS = [
    "Full renovation focused on {style_l} ideas: {note}. The {room_l} was opened up for better light and flow.",
    "The owners wanted a calm, practical home. We used {note} and custom carpentry throughout the {room_l}.",
    "A {home} makeover in {style_l} style. Highlights include {note}, concealed storage and warm lighting.",
    "Space-saving layout for a young family, with {note}. The {room_l} now doubles as a work area.",
]


def stamp(moment: datetime) -> str:
    return moment.strftime("%Y-%m-%d %H:%M:%S")


def random_moment(rng: random.Random, max_days_ago: int, min_days_ago: int = 0) -> datetime:
    """A random daytime moment between min_days_ago and max_days_ago, never in the future."""
    now = datetime.now()
    moment = now - timedelta(days=rng.uniform(min_days_ago, max_days_ago))
    moment = moment.replace(hour=rng.randint(8, 23), minute=rng.randint(0, 59), second=rng.randint(0, 59))
    return min(moment, now - timedelta(minutes=1))


def generate_idps(designer_ids, category_ids, rng: random.Random, per_designer=(4, 10)):
    """Mix of current and past projects for each designer. category_ids maps name -> id."""
    rows = []
    for designer_id in designer_ids:
        count = 12 if designer_id == DEMO_DESIGNER_ID else rng.randint(*per_designer)
        for n in range(count):
            style, room, home = rng.choice(STYLES), rng.choice(ROOMS[:8]), rng.choice(HOMES)
            estate = rng.choice(ESTATES)
            title = f"{estate} {home} – {style} {room}"
            client = f"{rng.choice(FIRST)} {rng.choice(LAST)}"
            description = rng.choice(DESCRIPTIONS).format(style_l=style, note=STYLE_NOTES[style],
                                                          room_l=room.lower(), home=home)
            category = category_ids.get(f"{style} {room}") or category_ids[style]
            created = random_moment(rng, 150)
            if (designer_id == DEMO_DESIGNER_ID and n < 5) or (designer_id != DEMO_DESIGNER_ID and rng.random() < 0.4):
                rows.append((designer_id, category, title, client, description, style, "",
                             rng.randint(5, 95), None, "CURRENT", stamp(created)))
            else:
                completed = (datetime.now() - timedelta(days=rng.randint(30, 6 * 365))).date().isoformat()
                rows.append((designer_id, category, title, client, description, style, "",
                             100, completed, "PAST", stamp(created)))
    return rows


def generate_categories():
    """10 styles x 10 room types = 100 categories."""
    rows = [(style, f"{STYLE_NOTES[style].capitalize()}.") for style in STYLES]
    rows += [(room, f"Projects focused on the {room.lower()}.") for room in ROOMS]
    rows += [(f"{style} {room}", f"{room} projects in {style} style: {STYLE_NOTES[style]}.")
             for style in STYLES for room in ROOMS[:8]]
    return rows


def generate_companies(designer_ids, rng: random.Random, per_designer=(2, 4)):
    rows, used_names, used_uens = [], set(), set()
    for designer_id in designer_ids:
        for _ in range(rng.randint(*per_designer)):
            name = f"{rng.choice(COMPANY_PREFIX)} {rng.choice(COMPANY_WORDS)}"
            while name in used_names:
                name = f"{rng.choice(COMPANY_PREFIX)} & {rng.choice(COMPANY_PREFIX)} {rng.choice(COMPANY_WORDS)}"
            used_names.add(name)
            uen = f"{rng.randint(2005, 2025)}{rng.randint(10000, 99999)}{rng.choice('ABCDEGHKMNRZ')}"
            while uen in used_uens:
                uen = f"{rng.randint(2005, 2025)}{rng.randint(10000, 99999)}{rng.choice('ABCDEGHKMNRZ')}"
            used_uens.add(uen)
            styles = rng.sample(STYLES, 2)
            rows.append((designer_id, name, uen,
                         f"Residential renovation specialists in {styles[0]} and {styles[1]} interiors.",
                         f"{rng.randint(1, 80)} {rng.choice(STREETS)}, #0{rng.randint(1, 9)}-{rng.randint(10, 99)}, Singapore {rng.randint(300000, 599999)}",
                         f"6{rng.randint(100, 999)} {rng.randint(1000, 9999)}"))
    return rows


def seed(db_path=DEFAULT_DB, accounts: int = 120, seed_value: int = 314, views_count: int = 3000,
         favourites_count: int = 400, sessions_count: int = 1500) -> dict:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db.init_db(db_path)
    rng = random.Random(seed_value)
    # Hash once and reuse: hashing 100+ passwords individually is slow and adds nothing for test data.
    password_hash = generate_password_hash(DEMO_PASSWORD)

    connection = sqlite3.connect(db_path)
    connection.executemany(
        "INSERT INTO user_account (full_name, username, email, password_hash, profile_id) VALUES (?, ?, ?, ?, ?)",
        [(n, u, e, password_hash, p) for n, u, e, p in DEMO_ACCOUNTS],
    )
    connection.executemany(
        """INSERT INTO user_account (full_name, username, email, password_hash, profile_id, status, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        [(n, u, e, password_hash, p, s, c) for n, u, e, p, s, c in generate_accounts(accounts, rng)],
    )
    designer_ids = [r[0] for r in connection.execute(
        "SELECT account_id FROM user_account WHERE profile_id = 2 ORDER BY account_id")]
    connection.executemany(
        """INSERT INTO company (designer_id, company_name, reg_number, description, address, contact_number)
           VALUES (?, ?, ?, ?, ?, ?)""", generate_companies(designer_ids, rng))
    connection.executemany("INSERT INTO idp_category (name, description) VALUES (?, ?)", generate_categories())
    category_ids = {name: cid for cid, name in connection.execute("SELECT category_id, name FROM idp_category")}

    connection.executemany(
        """INSERT INTO idp (designer_id, category_id, title, client_name, description, design_style, image_url,
                            progress, completion_date, status, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", generate_idps(designer_ids, category_ids, rng))

    customer_ids = [r[0] for r in connection.execute("SELECT account_id FROM user_account WHERE profile_id = 3")]
    idp_ids = [r[0] for r in connection.execute("SELECT idp_id FROM idp")]
    # Some projects are far more popular than others, like a real platform.
    popularity = [rng.paretovariate(1.3) for _ in idp_ids]
    views = [(idp, rng.choice(customer_ids), stamp(random_moment(rng, 120)))
             for idp in rng.choices(idp_ids, weights=popularity, k=views_count)]
    connection.executemany("INSERT INTO idp_view (idp_id, customer_id, viewed_at) VALUES (?, ?, ?)", views)

    # The demo customer starts with a few saved projects so the favourites page has something to show.
    pairs = {(DEMO_CUSTOMER_ID, i) for i in rng.sample(idp_ids, min(6, len(idp_ids)))}
    favourites_count = min(favourites_count, len(customer_ids) * len(idp_ids) // 2)
    while len(pairs) < favourites_count:
        pairs.add((rng.choice(customer_ids), rng.choices(idp_ids, weights=popularity)[0]))
    connection.executemany("INSERT INTO favourite (customer_id, idp_id, saved_at) VALUES (?, ?, ?)",
                           [(c, i, stamp(random_moment(rng, 120))) for c, i in pairs])

    all_ids = [r[0] for r in connection.execute("SELECT account_id FROM user_account WHERE status = 'ACTIVE'")]
    sessions = []
    for _ in range(sessions_count):
        login = random_moment(rng, 120)
        sessions.append((rng.choice(all_ids), stamp(login), stamp(login + timedelta(minutes=rng.randint(3, 90)))))
    connection.executemany("INSERT INTO user_session (account_id, login_at, logout_at) VALUES (?, ?, ?)", sessions)

    connection.commit()
    counts = {t: connection.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
              for t in ("user_profile", "user_account", "company", "idp_category", "idp",
                        "idp_view", "favourite", "user_session")}
    connection.close()
    return counts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--accounts", type=int, default=120)
    parser.add_argument("--db", default=str(DEFAULT_DB))
    args = parser.parse_args()
    for table, n in seed(args.db, args.accounts).items():
        print(f"{table}: {n} records")
    print(f"Demo logins (password '{DEMO_PASSWORD}'): " + ", ".join(u for _, u, _, _ in DEMO_ACCOUNTS))
