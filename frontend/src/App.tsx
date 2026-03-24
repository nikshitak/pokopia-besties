import { useState, useEffect } from "react";
import "./App.css";
import logo from "/src/assets/logo.png";

const API_URL = "http://127.0.0.1:8000";

interface Pokemon {
  id: number;
  name: string;
  ideal_habitat: string | null;
  specialties: string[];
  favorites: string[];
}

interface PokemonListItem {
  id: number;
  name: string;
}

function formatName(name: string): string {
  return name
    .split("-")
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");
}

function getSpriteUrl(name: string): string {
  const specialCases: Record<string, string> = {
    "farfetchd": "farfetch-d",
    "mrmime": "mr-mime",
    "mimejr": "mime-jr",
    "porygonz": "porygon-z",
    "hooh": "ho-oh",
  };
  const imgName = specialCases[name] || name;
  return `https://img.pokemondb.net/sprites/home/normal/${imgName}.png`;
}

interface PokemonCardProps {
  pokemon: Pokemon;
  selectedFavorites: string[];
  onFavoriteClick?: (fav: string) => void;
  isSource: boolean;
}

function PokemonCard({ pokemon, selectedFavorites, onFavoriteClick, isSource }: PokemonCardProps) {
  return (
    <div className={`pokemon-card ${isSource ? "source" : ""}`}>
      <img
        src={getSpriteUrl(pokemon.name)}
        alt={formatName(pokemon.name)}
        width={96}
        height={96}
        onError={e => (e.target as HTMLImageElement).src = "https://img.pokemondb.net/sprites/scarlet-violet/normal/substitute.png"}
        className="pokemon-card-sprite"
      />
      <h3 className="pokemon-card-name">{formatName(pokemon.name)}</h3>
      <p className="pokemon-card-info"><strong>Habitat:</strong> {pokemon.ideal_habitat || "Unknown"}</p>
      <p className="pokemon-card-info"><strong>Specialty:</strong> {pokemon.specialties?.join(", ") || "None"}</p>
      <div>
        <strong className="favorites-label">Favorites</strong>
        <div className="favorites-list">
          {pokemon.favorites?.map(fav => {
            const isSelected = selectedFavorites.includes(fav);
            return (
              <span
                key={fav}
                onClick={() => isSource && onFavoriteClick && onFavoriteClick(fav)}
                className={`favorite-chip ${isSelected ? "selected" : ""} ${isSource ? "clickable" : ""}`}
              >
                {fav}
              </span>
            );
          })}
        </div>
      </div>
    </div>
  );
}

interface CompatibleCardProps {
  pokemon: Pokemon;
  selectedFavorites: string[];
}

function CompatibleCard({ pokemon, selectedFavorites }: CompatibleCardProps) {
  return (
    <div className="compatible-card">
      <img
        src={getSpriteUrl(pokemon.name)}
        alt={formatName(pokemon.name)}
        width={80}
        height={80}
        onError={e => (e.target as HTMLImageElement).src = "https://img.pokemondb.net/sprites/scarlet-violet/normal/substitute.png"}
        className="compatible-card-sprite"
      />
      <h4 className="compatible-card-name">{formatName(pokemon.name)}</h4>
      <p className="compatible-card-info"><strong>Habitat:</strong> {pokemon.ideal_habitat || "Unknown"}</p>
      <p className="compatible-card-info"><strong>Specialty:</strong> {pokemon.specialties?.join(", ") || "None"}</p>
      <div>
        <strong className="compatible-favorites-label">Favorites</strong>
        <div className="compatible-favorites-list">
          {pokemon.favorites?.map(fav => {
            const isMatched = selectedFavorites.includes(fav);
            return (
              <span
                key={fav}
                className={`compatible-favorite-chip ${isMatched ? "matched" : ""}`}
              >
                {fav}
              </span>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default function App() {
  const [allPokemon, setAllPokemon] = useState<PokemonListItem[]>([]);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedPokemon, setSelectedPokemon] = useState<Pokemon | null>(null);
  const [selectedFavorites, setSelectedFavorites] = useState<string[]>([]);
  const [matchHabitat, setMatchHabitat] = useState<boolean>(false);
  const [compatiblePokemon, setCompatiblePokemon] = useState<Pokemon[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    fetch(`${API_URL}/pokemon`)
      .then(res => res.json())
      .then(data => setAllPokemon(Array.isArray(data) ? data : []));
  }, []);

  useEffect(() => {
    if (!selectedPokemon) return;
    setLoading(true);
    const params = new URLSearchParams();
    params.set("match_habitat", String(matchHabitat));
    if (selectedFavorites.length > 0) {
      params.set("selected_favorites", selectedFavorites.join(","));
    }
    fetch(`${API_URL}/compatible/${selectedPokemon.name}?${params}`)
      .then(res => res.json())
      .then(data => {
        setCompatiblePokemon(data.results || []);
        setLoading(false);
      });
  }, [selectedPokemon, selectedFavorites, matchHabitat]);

  function handleSelectPokemon(name: string): void {
    setSelectedFavorites([]);
    setMatchHabitat(false);
    setCompatiblePokemon([]);
    fetch(`${API_URL}/pokemon/${name}`)
      .then(res => res.json())
      .then(data => setSelectedPokemon(data));
  }

  function handleFavoriteClick(fav: string): void {
    setSelectedFavorites(prev =>
      prev.includes(fav) ? prev.filter(f => f !== fav) : [...prev, fav]
    );
  }

  const filteredPokemon = allPokemon.filter(p =>
    p.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="app-container">
      <img src={logo} alt="Pokopia Besties" className="app-logo" />

      <div className="search-wrapper">
        <input
          type="text"
          placeholder="Search for a Pokémon..."
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
          className="search-input"
        />
      </div>

      {searchQuery && (
        <div className="dropdown-wrapper">
          <div className="dropdown-list">
            {filteredPokemon.length === 0 ? (
              <p className="dropdown-empty">No Pokémon found</p>
            ) : (
              filteredPokemon.map(p => (
                <div
                  key={p.id}
                  onClick={() => {
                    handleSelectPokemon(p.name);
                    setSearchQuery("");
                  }}
                  className="dropdown-item"
                >
                  {formatName(p.name)}
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {selectedPokemon && (
        <div className="selected-section">
          <PokemonCard
            pokemon={selectedPokemon}
            selectedFavorites={selectedFavorites}
            onFavoriteClick={handleFavoriteClick}
            isSource={true}
          />
          <div className="filter-panel">
            <label className="habitat-label">
              <input
                type="checkbox"
                checked={matchHabitat}
                onChange={e => setMatchHabitat(e.target.checked)}
              />
              Match ideal habitat
            </label>
            {selectedFavorites.length > 0 && (
              <button className="clear-button" onClick={() => setSelectedFavorites([])}>
                Clear favorites
              </button>
            )}
            <p className="filter-hint">
              Click favorites on the card to filter compatible Pokémon
            </p>
          </div>
        </div>
      )}

      {selectedPokemon && (
        <>
          <h2 className="results-title">
            {loading ? "Finding compatible Pokémon..." : `${compatiblePokemon.length} compatible Pokémon`}
          </h2>
          <div className="results-grid">
            {compatiblePokemon.map(p => (
              <CompatibleCard
                key={p.id}
                pokemon={p}
                selectedFavorites={selectedFavorites}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
