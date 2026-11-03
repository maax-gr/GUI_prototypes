# Album Ranking

A static, collaborative album board hosted from the `Album_Rating_Collaborative/` folder in the public `maax-gr/GUI_prototypes` repository.

## Setup

1. In Firebase project `album-ranking-collab`, open **Realtime Database → Rules**, replace the rules with the contents of [`database.rules.json`](./database.rules.json), and publish them. The database URL is already configured in [`index.html`](./index.html).
2. Confirm the Firebase web config at the top of the JavaScript module in `index.html` matches your Firebase web app. The supplied project config is already filled in. The web API key is public; database access relies on the room code and Firebase rules, not on keeping that key secret.
3. Ensure `maax-gr/GUI_prototypes` is public. In the repository's **Settings → Pages**, publish from the `prototyping` branch and `/ (root)` (or the branch you use for deployment). The app URL is `https://maax-gr.github.io/GUI_prototypes/Album_Rating_Collaborative/`.
4. Generate a random room code with at least 128 bits of randomness (for example, 32 random hexadecimal characters), then share this link privately with the other players: `https://maax-gr.github.io/GUI_prototypes/Album_Rating_Collaborative/#<roomCode>`.

The app also accepts the room code on its join screen and adds it to the URL hash. Use the same code on every device. Anyone who obtains the code can read, add, move, or remove albums in that room, so don't post the link publicly.

## How it works

- Album search uses the public iTunes Search API. It searches both albums and tracks, then shows unique album results ranked against the query; the track search helps find an album when its tracks match better than the album title.
- Firebase Realtime Database stores each album under `rooms/<roomCode>/albums/<collectionId>`.
- The app is a single `index.html` with inline CSS and JavaScript. It uses Firebase's modular JavaScript SDK from Google's CDN; there is no build step or app server.
- Album artwork is loaded from iTunes and is not copied into Firebase.

For local development, serve this folder from a static HTTP server. The Firebase ES module imports and browser network requests are not supported when opening `index.html` directly as a `file://` URL. A local static server is only needed for development; GitHub Pages serves the deployed app.

## Using the board

1. Open the private room link. All players must use the exact same room code.
2. Search by album title, artist, or both, then choose the right album from the results to add it to **Unsorted**.
3. Drag cards between zones, or between cards within a zone, to order them. Changes sync automatically.
4. Hover a card (or look at its corners on a phone). **★** toggles your vote, **♫** searches the album on Spotify (Ctrl/Cmd+click on a card also works on desktop), and **×** removes it for everyone after confirmation.

## Players and votes

The first time you open the board, enter your name and pick a color (red, blue or yellow). The choice is stored in your browser; use "Playing as…" in the header to change it. Each player should use a different color. Adding an album counts as your vote, and ★ toggles it. Votes show as colored borders around the cover, always stacked red, blue, yellow.
