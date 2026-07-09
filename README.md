# Pokopia Besties

Pokopia Besties is a Pokémon pairing and compatibility app. It lets you search for a Pokémon, view its habitat, specialties, and favorites, and then discover other Pokémon that match selected compatibility filters.

## Features

- Search for a Pokémon by name
- View full Pokémon details from the database
- Filter compatible Pokémon by shared ideal habitat
- Filter compatible Pokémon by shared favorites
- Display Pokémon sprites and formatted details in the UI

## Project Structure

- `backend/` contains the FastAPI app and MySQL database setup code
- `frontend/` contains the React + TypeScript + Vite client
- `railway.json` contains the Railway deploy configuration for the backend

## Tech Stack

- Backend: FastAPI, Uvicorn, MySQL Connector, Python dotenv
- Frontend: React, TypeScript, Vite
- Deployment: Railway

## Requirements

- Python 3.11 or newer
- Node.js 18 or newer
- MySQL database

## Backend Setup

1. Create and activate a virtual environment inside `backend/`.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set the following environment variables for your MySQL database:

   - `DB_HOST`
   - `DB_USER`
   - `DB_PASSWORD`
   - `DB_NAME`
   - `DB_PORT` (optional, defaults to `3306`)

4. Initialize the database tables if needed:

   ```bash
   python database.py
   ```

5. Start the API server:

   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

The API exposes these endpoints:

- `GET /pokemon` returns the Pokémon list
- `GET /pokemon/{name}` returns full Pokémon details
- `GET /compatible/{name}` returns compatible Pokémon based on the selected filters

## Frontend Setup

1. Install dependencies inside `frontend/`:

   ```bash
   npm install
   ```

2. Start the dev server:

   ```bash
   npm run dev
   ```

## Local Development Note

The frontend currently points to the deployed backend URL in `frontend/src/App.tsx`. If you want to run everything locally, update `API_URL` in that file to your local backend, for example `http://localhost:8000`.

## Build and Lint

From `frontend/`:

```bash
npm run build
npm run lint
```

## Deployment

The backend is configured for Railway with `uvicorn main:app --host 0.0.0.0 --port ${PORT}` as the start command.

## Credits

- Logo generator: PixelFrame
- Pokédex and game information: Serebii
- Sprites: PokémonDB
