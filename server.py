import os
import sqlite3

from fastapi import FastAPI
from fastapi.responses import FileResponse


# =========================
# FASTAPI APP
# =========================

app = FastAPI()


# =========================
# CONFIG
# =========================

DB = "subtitles.db"

UPLOAD_FOLDER = "uploads"


os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)



# =========================
# DATABASE INIT
# =========================

def init_database():

    conn = sqlite3.connect(DB)

    cursor = conn.cursor()


    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS subtitles (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            filename TEXT,

            path TEXT,

            type TEXT,

            imdb TEXT,

            season TEXT,

            episode TEXT,

            created_at TEXT

        )
        """
    )


    conn.commit()

    conn.close()



init_database()



# =========================
# HOME TEST
# =========================

@app.get("/")
def home():

    return {
        "status": "online",
        "service": "Rizal Malay Subtitle Addon"
    }




# =========================
# STREMIO MANIFEST
# =========================

@app.get("/manifest.json")
def manifest():

    return {


        "id":
        "rizal.malay.subtitle",


        "version":
        "1.0.0",


        "name":
        "Rizal Malay Subtitle",


        "description":
        "Malay subtitle addon",



        "resources":[

            "subtitles"

        ],



        "types":[

            "movie",
            "series"

        ],



        "idPrefixes":[

            "tt"

        ],



        "catalogs":[]

    }




# =========================
# STREMIO SUBTITLE API
# =========================

@app.get(
    "/subtitles/{imdb_id}/{season}/{episode}"
)

def get_series_subtitle(

    imdb_id:str,

    season:str,

    episode:str

):


    conn = sqlite3.connect(DB)

    cursor = conn.cursor()



    cursor.execute(

        """

        SELECT filename,path

        FROM subtitles


        WHERE imdb=?

        AND season=?

        AND episode=?


        """,

        (

            imdb_id,

            season,

            episode

        )

    )



    result = cursor.fetchone()


    conn.close()



    if not result:


        return {

            "subtitles":[]

        }



    filename, path = result



    return {


        "subtitles":[


            {


                "id":

                f"{imdb_id}-{season}-{episode}",



                "url":

                f"/subtitle/file/{filename}",



                "lang":

                "ms",



                "label":

                "Malay"

            }


        ]

    }





# =========================
# MOVIE SUPPORT
# =========================

@app.get(
    "/subtitles/movie/{imdb_id}"
)

def get_movie_subtitle(

    imdb_id:str

):


    conn = sqlite3.connect(DB)

    cursor = conn.cursor()



    cursor.execute(

        """

        SELECT filename

        FROM subtitles


        WHERE imdb=?


        AND type='movie'


        """,

        (

            imdb_id,

        )

    )



    result = cursor.fetchone()


    conn.close()



    if not result:


        return {

            "subtitles":[]

        }



    filename = result[0]



    return {


        "subtitles":[


            {


                "id":

                imdb_id,


                "url":

                f"/subtitle/file/{filename}",


                "lang":

                "ms",


                "label":

                "Malay"

            }


        ]

    }





# =========================
# SERVE SRT FILE
# =========================


@app.get(

    "/subtitle/file/{filename}"

)

def subtitle_file(

    filename:str

):


    path = os.path.join(

        UPLOAD_FOLDER,

        filename

    )



    if os.path.exists(path):


        return FileResponse(

            path,

            media_type="text/plain"

        )



    return {


        "error":

        "File not found"

    }
