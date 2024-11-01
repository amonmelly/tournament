import urllib.parse as up
import psycopg2

def connection():
    up.uses_netloc.append("postgres")
    db_url = "postgres://khtaqtum:fAHElElEcJAuKQxItJ8LynTS1JRaigEZ@hattie.db.elephantsql.com/khtaqtum"
    url = up.urlparse(db_url)

    conn = psycopg2.connect(database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port
    )

    return conn