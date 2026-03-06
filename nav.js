(function () {
    if (window.innerWidth > 768) return;

    const nav = document.querySelector('.blogtitle + p');
    if (!nav) return;

    // Hide site title and top divider on blog post pages — the post's <h1> is enough
    if (document.querySelector('h1')) {
        const blogtitle = document.querySelector('.blogtitle');
        if (blogtitle) blogtitle.style.display = 'none';
        const pageHr = nav.nextElementSibling;
        if (pageHr && pageHr.tagName === 'HR') pageHr.style.display = 'none';
    }

    nav.style.display = 'none';

    // ── Extract nav items ────────────────────────────────────────────────────
    const items = [];
    nav.childNodes.forEach(function (node) {
        if (node.nodeType === 1) {
            items.push({ type: 'link', el: node.cloneNode(true) });
        } else if (node.nodeType === 3) {
            const text = node.textContent.replace(/\u00a0/g, '').trim();
            if (text) items.push({ type: 'current', text: text });
        }
    });

    // ── Inject styles ────────────────────────────────────────────────────────
    const style = document.createElement('style');
    style.textContent = `
        #m-btn {
            position: fixed;
            top: 18px;
            right: 20px;
            z-index: 200;
            background: none;
            border: none;
            cursor: pointer;
            padding: 6px;
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        #m-btn span {
            display: block;
            width: 22px;
            height: 2px;
            background: var(--fg);
            border-radius: 2px;
            transition: transform 0.22s ease, opacity 0.22s ease;
        }
        #m-btn.open span:nth-child(1) { transform: translateY(7px) rotate(45deg); }
        #m-btn.open span:nth-child(2) { opacity: 0; }
        #m-btn.open span:nth-child(3) { transform: translateY(-7px) rotate(-45deg); }

        #m-overlay {
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.18);
            z-index: 150;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.22s ease;
        }
        #m-overlay.open {
            opacity: 1;
            pointer-events: all;
        }

        #m-sidebar {
            position: fixed;
            top: 0;
            right: 0;
            width: 68vw;
            max-width: 260px;
            height: 100%;
            background: var(--bg);
            z-index: 160;
            display: flex;
            flex-direction: column;
            padding: 56px 28px 40px;
            transform: translateX(100%);
            transition: transform 0.26s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: -4px 0 24px rgba(0,0,0,0.10);
        }
        #m-sidebar.open {
            transform: translateX(0);
        }
        #m-sidebar hr {
            border: none;
            border-top: 1px solid rgba(0,0,0,0.08);
            margin: 16px 0 20px;
        }
        .m-nav-item {
            padding: 10px 0;
            font-family: inherit;
            font-size: 1.05em;
            line-height: 1.3;
            border-bottom: 1px solid rgba(0,0,0,0.05);
        }
        .m-nav-item:last-child { border-bottom: none; }
        .m-nav-item a {
            text-decoration: none;
            color: var(--fg);
        }
        .m-nav-item a:hover { text-decoration: underline; }
        .m-nav-current {
            color: var(--fg);
            opacity: 0.35;
            font-size: 1.05em;
        }
    `;
    document.head.appendChild(style);

    // ── Hamburger button (3 bars → X on open) ───────────────────────────────
    const btn = document.createElement('button');
    btn.id = 'm-btn';
    btn.setAttribute('aria-label', 'Menu');
    btn.innerHTML = '<span></span><span></span><span></span>';
    document.body.appendChild(btn);

    // ── Overlay ──────────────────────────────────────────────────────────────
    const overlay = document.createElement('div');
    overlay.id = 'm-overlay';
    document.body.appendChild(overlay);

    // ── Sidebar ──────────────────────────────────────────────────────────────
    const sidebar = document.createElement('nav');
    sidebar.id = 'm-sidebar';

    const hr = document.createElement('hr');
    sidebar.appendChild(hr);

    items.forEach(function (item) {
        const row = document.createElement('div');
        if (item.type === 'link') {
            row.className = 'm-nav-item';
            row.appendChild(item.el);
        } else {
            row.className = 'm-nav-item m-nav-current';
            row.textContent = item.text;
        }
        sidebar.appendChild(row);
    });

    document.body.appendChild(sidebar);

    // ── Toggle ───────────────────────────────────────────────────────────────
    function open() {
        btn.classList.add('open');
        overlay.classList.add('open');
        sidebar.classList.add('open');
    }
    function close() {
        btn.classList.remove('open');
        overlay.classList.remove('open');
        sidebar.classList.remove('open');
    }

    btn.addEventListener('click', function () {
        sidebar.classList.contains('open') ? close() : open();
    });
    overlay.addEventListener('click', close);
    sidebar.querySelectorAll('a').forEach(function (a) {
        a.addEventListener('click', close);
    });
}());
