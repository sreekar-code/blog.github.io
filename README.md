# Sreekar Scribbles

Personal blog at [sreekarscribbles.com](https://sreekarscribbles.com).

## Stack

- Plain HTML, CSS, and vanilla JavaScript — no frameworks, no build tools
- Self-hosted on a Raspberry Pi, served via Nginx + Cloudflare Tunnel
- GitHub as the middleman between local edits and the Pi

## Pages

| Page | Description |
|------|-------------|
| Home | Introduction |
| Blog | All published posts |
| Flow | Weekly writing streak tracker |
| Cooking | Upcoming post titles |

## Publishing a Post

1. Create a new HTML file in `blog/` using the template in `AGENTS.md`
2. Add it to the top of the list in `blog.html`
3. Commit and push to `main`
4. GitHub Action auto-regenerates `feed.xml`
5. `sudo git pull` on the Pi — done

## RSS

Feed available at `/feed.xml`, auto-generated from `blog.html` on every push via GitHub Actions.
