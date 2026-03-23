import requests
from bs4 import BeautifulSoup
import time
from database import get_connection

# Full list of pokemon from pokopia
POKEMON_NAMES = [
    "bulbasaur", "ivysaur", "venusaur", "charmander", "charmeleon", "charizard",
    "squirtle", "wartortle", "blastoise", "pidgey", "pidgeotto", "pidgeot",
    "oddish", "gloom", "vileplume", "bellossom", "paras", "parasect",
    "venonat", "venomoth", "bellsprout", "weepinbell", "victreebel", "slowpoke",
    "slowbro", "slowking", "magnemite", "magneton", "magnezone", "onix",
    "steelix", "cubone", "marowak", "tyrogue", "hitmonlee", "hitmonchan",
    "hitmontop", "koffing", "weezing", "tangela", "professortangrowth", "tangrowth", "scyther",
    "scizor", "pinsir", "magikarp", "gyarados", "ditto", "hoothoot",
    "noctowl", "heracross", "volbeat", "illumise", "gulpin", "swalot",
    "cacnea", "cacturne", "combee", "vespiquen", "shellos", "shelloseastsea", "gastrodon",
    "gastrodoneastsea", "drifloon", "drifblim", "drilbur", "excadrill", "timburr", "gurdurr",
    "conkeldurr", "litwick", "lampent", "chandelure", "axew", "fraxure",
    "haxorus", "goomy", "sliggoo", "goodra", "cramorant", "pichu", "peakychu",
    "pikachu", "raichu", "zubat", "golbat", "crobat", "meowth",
    "persian", "psyduck", "golduck", "growlithe", "arcanine", "farfetch'd",
    "grimer", "muk", "gastly", "haunter", "gengar", "voltorb",
    "electrode", "exeggcute", "exeggutor", "happiny", "chansey", "blissey",
    "elekid", "electabuzz", "electivire", "lapras", "munchlax", "mosslax", "snorlax",
    "spinarak", "ariados", "mareep", "flaaffy", "ampharos", "azurill",
    "marill", "azumarill", "paldeanwooper", "clodsire", "smeargle", "torchic", "combusken", "blaziken",
    "wingull", "pelipper", "makuhita", "hariyama", "absol", "piplup",
    "prinplup", "empoleon", "audino", "trubbish", "garbodor", "zorua",
    "zoroark", "minccino", "cinccino", "grubbin", "charjabug", "vikavolt",
    "mimikyu", "pawmi", "pawmo", "pawmot", "tatsugiricurlyform", "tatsugiridroopyform", 
    "tatsugiristretchyform", "ekans", "arbok",
    "cleffa", "clefairy", "clefable", "igglybuff", "jigglypuff", "wigglytuff",
    "diglett", "dugtrio", "machop", "machoke", "machamp", "geodude",
    "graveler", "golem", "magby", "magmar", "magmortar", "bonsly",
    "sudowoodo", "murkrow", "honchkrow", "larvitar", "pupitar", "tyranitar",
    "lotad", "lombre", "ludicolo", "mawile", "torkoal", "kricketot",
    "kricketune", "chatot", "riolu", "lucario", "stereorotom", "larvesta", "volcarona",
    "rowlet", "dartrix", "decidueye", "scorbunny", "raboot", "cinderace",
    "skwovet", "greedent", "rolycoly", "carkol", "coalossal", "toxel",
    "toxtricityampedform", "toxtricitylowkeyform", "fidough", "dachsbun", "charcadet", "armarouge", "ceruledge",
    "glimmet", "glimmora", "gimmighoul", "gholdengo", "vulpix", "ninetales",
    "poliwag", "poliwhirl", "poliwrath", "politoed", "abra", "kadabra",
    "alakazam", "mimejr.", "mr.mime", "porygon", "porygon2", "porygon-z",
    "dratini", "dragonair", "dragonite", "cyndaquil", "quilava", "typhlosion",
    "misdreavus", "mismagius", "girafarig", "farigiraf", "ralts", "kirlia",
    "gardevoir", "gallade", "plusle", "minun", "trapinch", "vibrava",
    "flygon", "swablu", "altaria", "duskull", "dusclops", "dusknoir",
    "beldum", "metang", "metagross", "snivy", "servine", "serperior",
    "froakie", "frogadier", "greninja", "dedenne", "noibat", "noivern",
    "rookidee", "corvisquire", "corviknight", "dreepy", "drakloak", "dragapult",
    "sprigatito", "floragato", "meowscarada", "wattrel", "kilowattrel",
    "tinkatink", "tinkatuff", "tinkaton", "aerodactyl", "cranidos", "rampardos",
    "shieldon", "bastiodon", "tyrunt", "tyrantrum", "amaura", "aurorus",
    "eevee", "vaporeon", "jolteon", "flareon", "espeon", "umbreon",
    "leafeon", "glaceon", "sylveon", "kyogre", "raikou", "entei",
    "suicune", "volcanion", "articuno", "zapdos", "moltres", "lugia",
    "ho-oh", "mewtwo", "mew"
       
]

def scrape_pokemon(name):
    url = f"https://www.serebii.net/pokemonpokopia/pokedex/{name}.shtml"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"Failed to fetch {name}: status {response.status_code}")
            return None

        soup = BeautifulSoup(response.content, "html.parser")

        specialties = []
        ideal_habitat = None
        favorites = []

        tables = soup.find_all("table")
        stats_table = tables[3]
        rows = stats_table.find_all("tr")

        data_row = rows[2]
        cells = data_row.find_all("td")

        # Specialty links are in cell 0
        specialty_links = cells[0].find_all("a")
        specialties = [a.get_text(strip=True) for a in specialty_links if a.get_text(strip=True)]

        # Habitat and favorites are always the last 2 cells
        habitat_links = cells[-2].find_all("a")
        if habitat_links:
            ideal_habitat = habitat_links[0].get_text(strip=True)

        favorite_links = cells[-1].find_all("a")
        favorites = [a.get_text(strip=True) for a in favorite_links if a.get_text(strip=True)]

        if not ideal_habitat and not specialties and not favorites:
            print(f"Could not parse data for {name}")
            return None

        return {
            "name": name,
            "ideal_habitat": ideal_habitat,
            "specialties": specialties,
            "favorites": favorites
        }

    except Exception as e:
        print(f"Error scraping {name}: {e}")
        return None
    
def save_pokemon(data):
    conn = get_connection()
    if not conn:
        return
    
    cursor = conn.cursor()

    try:
        # Insert pokemon
        cursor.execute(
            "INSERT IGNORE INTO pokemon (name, ideal_habitat) VALUES (%s, %s)",
            (data["name"], data["ideal_habitat"])
        )
        conn.commit()

        # Get the pokemon's ID
        cursor.execute("SELECT id FROM pokemon WHERE name = %s", (data["name"],))
        row = cursor.fetchone()
        if not row:
            return
        pokemon_id = row[0]

        # Insert specialties
        for specialty in data["specialties"]:
            cursor.execute(
                "INSERT INTO specialties (pokemon_id, specialty) VALUES (%s, %s)",
                (pokemon_id, specialty)
            )

        # Insert favorites
        for favorite in data["favorites"]:
            cursor.execute(
                "INSERT INTO favorites (pokemon_id, favorite) VALUES (%s, %s)",
                (pokemon_id, favorite)
            )

        conn.commit()
        print(f"Saved {data['name']} — habitat: {data['ideal_habitat']}, specialties: {data['specialties']}, favorites: {data['favorites']}")

    except Exception as e:
        print(f"Error saving {data['name']}: {e}")
        conn.rollback()

    finally:
        cursor.close()
        conn.close()

def run_scraper():
    print(f"Starting scraper for {len(POKEMON_NAMES)} Pokémon...\n")
    success = 0
    failed = []

    for name in POKEMON_NAMES:
        data = scrape_pokemon(name)
        if data:
            save_pokemon(data)
            success += 1
        else:
            failed.append(name)

        # wait time between requests        
        time.sleep(0.5)

    print(f"\nDone! {success} Pokémon saved successfully.")
    if failed:
        print(f"Failed: {failed}")

if __name__ == "__main__":
    
    print(len(POKEMON_NAMES))
    run_scraper()