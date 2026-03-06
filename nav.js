(function () {
    if (window.innerWidth > 768) return;

    const nav = document.querySelector('.blogtitle + p');
    if (!nav) return;

    // Hide the inline nav on mobile
    nav.style.display = 'none';

    // Extract nav items from the existing <p>
    const items = [];
    nav.childNodes.forEach(function (node) {
        if (node.nodeType === 1) {
            items.push({ type: 'link', el: node.cloneNode(true) });
        } else if (node.nodeType === 3) {
            const text = node.textContent.replace(/\u00a0/g, '').trim();
            if (text) items.push({ type: 'text', text: text });
        }
    });

    // Hamburger button
    const btn = document.createElement('button');
    btn.textContent = '☰';
    btn.style.cssText = [
        'background:none', 'border:none', 'cursor:pointer',
        'font-size:1.2em', 'color:var(--fg)', 'font-family:inherit',
        'padding:0', 'position:absolute', 'top:1.2em', 'right:1.4em',
        'line-height:1', 'z-index:10'
    ].join(';');
    document.body.appendChild(btn);
    // body needs relative positioning for the button
    document.body.style.position = 'relative';

    // Overlay
    const overlay = document.createElement('div');
    overlay.style.cssText = [
        'position:fixed', 'inset:0', 'background:rgba(0,0,0,0.25)',
        'z-index:100', 'display:none'
    ].join(';');
    document.body.appendChild(overlay);

    // Sidebar
    const sidebar = document.createElement('nav');
    sidebar.style.cssText = [
        'position:fixed', 'top:0', 'right:-280px', 'width:220px',
        'height:100%', 'background:var(--bg)', 'z-index:101',
        'padding:3em 1.8em', 'transition:right 0.22s ease',
        'display:flex', 'flex-direction:column', 'gap:0.2em',
        'font-family:inherit', 'font-size:1em',
        'box-shadow:-2px 0 12px rgba(0,0,0,0.08)'
    ].join(';');

    items.forEach(function (item) {
        const el = document.createElement('div');
        el.style.cssText = 'padding:0.3em 0; line-height:2;';
        if (item.type === 'link') {
            el.appendChild(item.el);
        } else {
            el.textContent = item.text;
            el.style.cssText += 'opacity:0.45;';
        }
        sidebar.appendChild(el);
    });

    document.body.appendChild(sidebar);

    function open() {
        sidebar.style.right = '0';
        overlay.style.display = 'block';
    }
    function close() {
        sidebar.style.right = '-280px';
        overlay.style.display = 'none';
    }

    btn.addEventListener('click', open);
    overlay.addEventListener('click', close);
    sidebar.querySelectorAll('a').forEach(function (a) {
        a.addEventListener('click', close);
    });
}());
