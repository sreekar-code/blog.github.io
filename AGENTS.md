# AGENTS.md - Coding Guidelines for sreekarscribbles

## Build / Lint / Test Commands

This is a **static HTML/CSS site** hosted on GitHub Pages. There are no build tools, package managers, or test frameworks configured.

- **No build process**: Files are served directly as static assets
- **No linting**: No ESLint, Stylelint, or other linters configured
- **No tests**: No test framework (Jest, Vitest, etc.) configured
- **To preview locally**: Open HTML files directly in browser or use `python -m http.server 8000`

## Code Style Guidelines

### HTML

- Use HTML5 doctype: `<!DOCTYPE html>`
- Include viewport meta tag: `<meta name="viewport" content="width=device-width, initial-scale=1.0">`
- Use semantic tags: `<main>`, `<section>`, `<header>`, `<footer>`
- Indent with 4 spaces
- Use double quotes for attributes
- Analytics script (umami) should be included in `<head>`:
  ```html
  <script async src="https://analytics.balla.dev/script.js" data-website-id="2d661ca0-e926-4c3c-8d8c-e948998a7ac8"></script>
  ```

### CSS

- All styles in `styles.css` (shared across all pages)
- Mobile-first approach with media queries at bottom
- Use kebab-case for class names (e.g., `.blogtitle`, `.like-button`)
- No CSS frameworks (Tailwind, Bootstrap, etc.)
- CSS custom properties not currently used

### JavaScript

- Vanilla JavaScript only (no frameworks)
- Use `DOMContentLoaded` event listener for initialization
- Use `const` and `let` (avoid `var`)
- Function declarations preferred over arrow functions for top-level functions
- Use `localStorage` for client-side persistence

### File Organization

```
/
├── index.html              # Homepage
├── blog.html               # Blog listing page
├── socials.html            # Social links page
├── styles.css              # Global styles
├── like-button.js          # Like button functionality
├── images/                 # Image assets
│   ├── me.jpg
│   ├── myway.jpg
│   └── gokarna.jpg
└── coffee/                 # Subdirectory for coffee posts
    ├── index.html
    ├── notes-1.html
    ├── cup-1.html
    ├── cup-2.html
    ├── cup-3.html
    └── cup-4-and-5.html
```

### Blog Post Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Post Title</title>
    <link rel="stylesheet" href="styles.css">
    <script async src="https://analytics.balla.dev/script.js" data-website-id="2d661ca0-e926-4c3c-8d8c-e948998a7ac8"></script>
</head>
<body>
<main>
    <header class="blogtitle">Sreekar Scribbles</header>
    <p><a href="index.html">Home</a> &nbsp;&nbsp; <a href="blog.html">Blog</a> &nbsp;&nbsp; <a href="socials.html">Socials</a></p>
    <hr>
    <h1>Post Title</h1>
    <section>
        <p class="date">DD MMM, YYYY</p>
    </section>
    <section>
        <!-- Post content here -->
    </section>
</main>
</body>
</html>
```

### Naming Conventions

- **HTML files**: Title Case with hyphens for spaces (e.g., `What-Is-A-Problem.html`, `getting-back-to-things-i-love.html`)
- **CSS classes**: lowercase, hyphenated (e.g., `.blogtitle`, `.like-button-container`)
- **Images**: lowercase, hyphenated (e.g., `myway.jpg`, `gokarna.jpg`)

### Images

- Use `<img>` tags with descriptive alt text
- Images should have rounded corners and shadow (handled by CSS)
- Max dimensions: `max-width: 100%`, `max-height: 75vh`
- Store in `images/` directory

### Links

- Internal links: relative paths (e.g., `blog.html`, `../index.html`)
- External links: use `target='_blank'` attribute
- Navigation uses `&nbsp;&nbsp;` for spacing between links

### Git Conventions

- Commit messages should describe the change (e.g., "Add new blog post about...", "Update styles for mobile")
- Push to `main` branch for GitHub Pages deployment
- No CI/CD configured

## External Dependencies

- Umami analytics (loaded from analytics.balla.dev)
- No npm packages, CDN links, or build tools
