# Album Ranking – Spec

Prototype spec for a collaborative album-ranking board, written so a coding agent can build it without further questions. Where a choice was left open, a default is given and marked **(default)**.

## 1. Goal

Three people, working from different computers, rank music albums together on one shared canvas. Each person searches for an album, picks the right match, and its cover is added to the canvas. Covers are dragged between four zones to sort them. Everyone sees changes live.

## 2. Users and constraints

- 3 users, no accounts. Access is by a shared link plus a shared room code.
- No custom domain. Hosting must give a free URL.
- Standalone and easy to access: no build step, no server to run, no installation for users.
- Expected size: about 60–100 albums in total.

## 3. Architecture

| Part | Choice |
| --- | --- |
| Front end | One `index.html` with inline CSS and vanilla JavaScript (no framework, no build step) |
| Project files | `Album_Rating_Collaborative/index.html`, `Album_Rating_Collaborative/database.rules.json`, and `Album_Rating_Collaborative/README.md` in the existing `GUI_prototypes` repository |
| Hosting | GitHub Pages from the public `maax-gr/GUI_prototypes` repo, publishing from the repository root; app URL: `https://maax-gr.github.io/GUI_prototypes/Album_Rating_Collaborative/` |
| Shared state and live sync | Firebase Realtime Database at `https://album-ranking-collab-default-rtdb.europe-west1.firebasedatabase.app/`, loaded via Firebase JS SDK 10.14.1 from Google's CDN (modular ES module imports) |
| Cover and album search | iTunes Search API (free, no key) |

The page talks directly to Firebase and iTunes from the browser. There is no backend of our own.

## 4. User interface

### 4.1 Layout

- A search field at the top with a results dropdown or panel.
- A large canvas below, split into four zones (columns or labeled areas that scale to the window):
  1. **Top 20**
  2. **20–40**
  3. **40–60**
  4. **Unsorted** (new albums land here)
- Each zone has a visible label and a live count of albums in it.
- Zones are not capped. A zone can hold more or fewer than 20 albums, and the labels are only names.

### 4.2 Album card

- Cover image (square).
- Directly below the cover: **title** and **artist** as text, truncated with an ellipsis if too long, full text on hover (`title` attribute).
- Cards are draggable. The card's width is fixed (about 120–150 px) so many cards fit per zone, with wrapping inside the zone.

### 4.3 Search flow

1. User types an artist or album name. The search is debounced (about 400 ms).
2. The app queries the iTunes Search API and shows up to 10 album results, each with a cover thumbnail, album title, artist and year.
3. User clicks the intended result.
4. A new album is added to the **Unsorted** zone and written to the database. The results panel then closes and the search field clears.
5. If the same album (same `collectionId`) is already on the board, do not add it again. Briefly highlight the existing card and show a short notice.

### 4.4 Moving albums

- Drag and drop a card to another zone or to a different position in the same zone.
- Use the native HTML5 drag-and-drop API or pointer events. Touch support is nice to have, not required.
- On drop, the card's zone and position are written to the database.
- Remove an album: a small "×" button on the card that appears on hover, with a confirm step.

### 4.5 Live sync

- Every open browser subscribes to the room's data. When anyone adds, moves or removes an album, all other screens update within about a second without a reload.
- Conflict rule: last write wins per album. Concurrent moves of different albums must not interfere.

## 5. Data

### 5.1 iTunes Search API

- Request: `https://itunes.apple.com/search?term=<query>&media=music&entity=album&limit=10`
- Useful fields: `collectionId`, `collectionName`, `artistName`, `artworkUrl100`, `releaseDate`.
- For a larger cover, replace `100x100` in `artworkUrl100` with `300x300` (or `600x600`).
- If a browser CORS problem appears, fall back to the JSONP mode of the API (`&callback=...`).

### 5.2 Database structure (Realtime Database)

```json
{
  "rooms": {
    "<roomCode>": {
      "albums": {
        "<collectionId>": {
          "title": "Album title",
          "artist": "Artist name",
          "coverUrl": "https://.../300x300bb.jpg",
          "year": 1997,
          "zone": "top20",
          "order": 1.5,
          "addedAt": 1730000000000
        }
      }
    }
  }
}
```

- `zone` is one of `top20`, `20to40`, `40to60`, `unsorted`.
- `order` is a number, ascending within a zone. When an album is dropped between two neighbors, set `order` to the average of their values. A new album added to a zone gets the highest `order` plus 1. If values ever get too close together, renumber that zone.
- Using `collectionId` as the key prevents duplicates.
- Only the album text and the cover URL are stored. Image files are not stored.

## 6. Access and security

- The page reads the room code from the URL hash, for example `https://maax-gr.github.io/GUI_prototypes/Album_Rating_Collaborative/#<roomCode>`. If there is none, show an input asking for it. The owner supplies and shares a randomly generated, hard-to-guess code (at least 128 bits of randomness); the app does not create rooms or codes.
- All data lives under `rooms/<roomCode>/`.
- Firebase security rules for the prototype: reads are allowed under `rooms/$room`; writes are allowed only to an individual `rooms/$room/albums/$albumId` record, with validation that required album fields have the expected types, `zone` is from the allowed list, and `order` is numeric. Use `database.rules.json`; do not use open test-mode rules.
- The Firebase web config (API key etc.) is public by design and is placed in the HTML file.
- Known limitation of this prototype: anyone with the room code can edit. That is acceptable for three friends.

## 7. Setup tasks for the owner (not for the code)

1. Use Firebase project `album-ranking-collab` and its Realtime Database at `https://album-ranking-collab-default-rtdb.europe-west1.firebasedatabase.app/`. The web app config is already in `index.html`.
2. Publish the rules from `database.rules.json` in the Realtime Database Rules tab.
3. Ensure `maax-gr/GUI_prototypes` is public, add the three project files under `Album_Rating_Collaborative/`, and enable Pages to publish from the repository root (Settings → Pages).
4. Share `https://maax-gr.github.io/GUI_prototypes/Album_Rating_Collaborative/#<roomCode>` with the other two users.

The agent should deliver the files at the paths in the project-files row: `index.html` with a clearly marked block at the top for the Firebase config, the exact security rules in `database.rules.json`, and a short `README.md` with the four steps above.

## 8. Acceptance criteria

- Search "Radiohead OK Computer" returns a list with covers. Clicking the right result puts the card in Unsorted with cover, title and artist visible below it.
- Dragging the card into Top 20 moves it, and the change appears on a second browser open on the same room within about 2 seconds.
- Reloading the page restores the exact same arrangement.
- Adding the same album twice does not create a duplicate.
- Removing a card removes it for everyone.
- With a different room code, the board is empty and separate.
- The page works from a plain static host with no build step.

## 9. Later features (out of scope for the prototype)

- **Spotify link:** Ctrl+click (Cmd+click on Mac) on a card opens the album on Spotify in a new tab. Simplest first version: open `https://open.spotify.com/search/<artist> <title>`. A precise link needs the Spotify Web API with a token, so it is deferred.
- Showing who added or moved an album.
- Export and import of the board as JSON (backup).
- Rank numbers on cards in Top 20.
- Touch and mobile polish.
- Real logins instead of a shared room code.

## 10. Open points for the owner

- Realtime Database was chosen as the default for simplicity. Firestore would also work.
- Whether the zones should enforce hard limits (for example exactly 20 in Top 20). The spec assumes no limits.
