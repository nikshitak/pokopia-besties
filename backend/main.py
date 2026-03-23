from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from database import get_connection
from typing import Optional
import os

app = FastAPI()

cors_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000"
)
allow_origins = [origin.strip() for origin in cors_origins.split(",") if origin.strip()]

# Allow React frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Helper ──────────────────────────────────────────────────────────────────

def get_pokemon_data(name: str):
    """Fetch a single Pokémon's full data from the database."""
    conn = get_connection()
    if not conn:
        return None
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM pokemon WHERE name = %s", (name,))
        pokemon = cursor.fetchone()
        if not pokemon:
            return None

        cursor.execute("SELECT specialty FROM specialties WHERE pokemon_id = %s", (pokemon["id"],))
        pokemon["specialties"] = [row["specialty"] for row in cursor.fetchall()]

        cursor.execute("SELECT favorite FROM favorites WHERE pokemon_id = %s", (pokemon["id"],))
        pokemon["favorites"] = [row["favorite"] for row in cursor.fetchall()]

        return pokemon
    finally:
        cursor.close()
        conn.close()


# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/pokemon")
def list_pokemon():
    """Return all Pokémon names and ids — used to populate the search/select dropdown."""
    conn = get_connection()
    if not conn:
        return {"error": "Database connection failed"}
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT id, name FROM pokemon ORDER BY name")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


@app.get("/pokemon/{name}")
def get_pokemon(name: str):
    """Return full data for a single Pokémon."""
    pokemon = get_pokemon_data(name)
    if not pokemon:
        return {"error": f"Pokemon '{name}' not found"}
    return pokemon


@app.get("/compatible/{name}")
def get_compatible(
    name: str,
    match_habitat: bool = Query(default=False),
    selected_favorites: Optional[str] = Query(default=None)
):
    """
    Return Pokémon compatible with the given Pokémon.
    
    - match_habitat: if true, only return Pokémon with the same ideal habitat
    - selected_favorites: comma-separated list of favorites that compatible Pokémon must ALL have
    """
    conn = get_connection()
    if not conn:
        return {"error": "Database connection failed"}
    cursor = conn.cursor(dictionary=True)

    try:
        # Get the selected pokemon
        cursor.execute("SELECT * FROM pokemon WHERE name = %s", (name,))
        source = cursor.fetchone()
        if not source:
            return {"error": f"Pokemon '{name}' not found"}

        # Parse selected favorites from comma-separated string
        favorites_filter = []
        if selected_favorites:
            favorites_filter = [f.strip() for f in selected_favorites.split(",") if f.strip()]

        # Base query - exclude the selected pokemon itself
        query = """
            SELECT DISTINCT p.id, p.name, p.ideal_habitat
            FROM pokemon p
            WHERE p.id != %s
        """
        params = [source["id"]]

        # Habitat filter
        if match_habitat:
            query += " AND p.ideal_habitat = %s"
            params.append(source["ideal_habitat"])

        # Favorites filter - pokemon must have ALL selected favorites
        for favorite in favorites_filter:
            query += """
                AND EXISTS (
                    SELECT 1 FROM favorites f
                    WHERE f.pokemon_id = p.id AND f.favorite = %s
                )
            """
            params.append(favorite)

        query += " ORDER BY p.name"

        cursor.execute(query, params)
        results = cursor.fetchall()

        # Enrich each result with specialties and favorites
        enriched = []
        for pokemon in results:
            cursor.execute("SELECT specialty FROM specialties WHERE pokemon_id = %s", (pokemon["id"],))
            pokemon["specialties"] = [row["specialty"] for row in cursor.fetchall()]

            cursor.execute("SELECT favorite FROM favorites WHERE pokemon_id = %s", (pokemon["id"],))
            pokemon["favorites"] = [row["favorite"] for row in cursor.fetchall()]

            enriched.append(pokemon)

        return {
            "source": name,
            "match_habitat": match_habitat,
            "selected_favorites": favorites_filter,
            "results": enriched
        }

    finally:
        cursor.close()
        conn.close()