# Sreekar Scribbles

Personal blog at [sreekarscribbles.com](https://sreekarscribbles.com).

## Stack

- Plain HTML, CSS, and vanilla JavaScript — no frameworks, no build tools
- Self-hosted on a Raspberry Pi, served via Nginx + Cloudflare Tunnel
- GitHub as the middleman between local edits and the Pi

## Design

- **Font:** Caveat (Google Fonts) — handwritten, weights 400 and 700
- **Theme:** Journal paper — cream page (`#f4ecce`) on a dark wood desk (`#1a0e06`)
- The `html` element is the desk; `body` is the paper page elevated above it
- Paper has ruled lines, a red margin line, grain texture, and age-darkening effects
- Single stylesheet: `styles.css`, manually cache-busted with `?v=N`

### Scrapbook elements

- Photos appear as tilted prints with a cream border, sepia tint, and tape strips at the top-left and bottom-right corners
- Blockquotes render as sticky notes — warm aged-yellow, slight tilt, warm drop shadow

## Pages

| Page | Description |
|------|-------------|
| Home | Introduction |
| Blog | All published posts |
| Flow | Monthly writing streak tracker — calendar + streak count |
| Cooking | Upcoming post titles |

## Publishing a Post

1. Create a new HTML file in `blog/` using the template in `AGENTS.md`
2. Add it to the top of the list in `blog.html`
3. Commit and push to `main`
4. GitHub Action auto-regenerates `feed.xml`
5. `sudo git pull` on the Pi — done

## RSS

Feed available at `/feed.xml`, auto-generated from `blog.html` on every push via GitHub Actions.

## Flow Tracker

`flow.html` tracks writing streaks using a monthly calendar view.
- Post dates stored in `dates.json`, synced via GitHub API
- Admin panel hidden behind a secret key combo (`l` pressed three times)
- Desktop: two-column layout — calendar left, streak stat right
