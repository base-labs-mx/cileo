
// Tooltips over nums: takes the text according to the step
document.querySelectorAll('.imgwrap').forEach(wrap => {
    const marks = [...wrap.querySelectorAll('.mark')];
    if (!marks.length) return;
    const scope = wrap.closest('.slide') || wrap.closest('section') || wrap.parentElement;
    const steps = [...scope.querySelectorAll('.steps .step')];
    marks.forEach(m => {
        const n = parseInt(m.textContent.trim(), 10);
        const step = steps[n - 1];
        if (!step) return;
        const h = (step.querySelector('h4')?.textContent || '').trim();
        const p = (step.querySelector('p')?.textContent || '').trim();
        m.setAttribute('data-tip', (h ? h + ' — ' : '') + p);
        m.setAttribute('aria-label', (h ? h + ': ' : '') + p);
    });
});
// Floating tooltip over <body> (not clipped by any container; flips/adjusts)
(function () {
    const tip = document.createElement('div'); tip.className = 'mark-tip'; document.body.appendChild(tip);
    const place = (m) => {
        tip.textContent = m.getAttribute('data-tip') || ''; tip.style.display = 'block';
        const r = m.getBoundingClientRect(), tr = tip.getBoundingClientRect();
        let top = r.top - tr.height - 10; if (top < 8) top = r.bottom + 10;
        let left = r.left + r.width / 2 - tr.width / 2;
        left = Math.max(8, Math.min(left, window.innerWidth - tr.width - 8));
        tip.style.left = Math.round(left) + 'px'; tip.style.top = Math.round(top) + 'px';
    };
    document.querySelectorAll('.mark[data-tip]').forEach(m => {
        m.addEventListener('mouseenter', () => place(m));
        m.addEventListener('mouseleave', () => { tip.style.display = 'none'; });
    });
})();

const body = document.body, menuBtn = document.getElementById('menuBtn'), backdrop = document.getElementById('backdrop');
menuBtn.addEventListener('click', () => body.classList.toggle('nav-open'));
backdrop.addEventListener('click', () => body.classList.remove('nav-open'));
document.querySelectorAll('.sb-nav a, .sb-cta a').forEach(a => a.addEventListener('click', () => body.classList.remove('nav-open')));

const links = [...document.querySelectorAll('.sb-nav a')];
const byId = id => links.find(a => a.getAttribute('href') === '#' + id);
const io = new IntersectionObserver((es) => { es.forEach(e => { if (e.isIntersecting) { const l = byId(e.target.id); if (l) { links.forEach(x => x.classList.remove('active')); l.classList.add('active'); } } }) }, { rootMargin: '-15% 0px -75% 0px' });
document.querySelectorAll('section[id], h3.sub[id]').forEach(t => io.observe(t));

const search = document.getElementById('navSearch');
search.addEventListener('input', () => {
    const q = search.value.trim().toLowerCase();
    document.querySelectorAll('.sb-nav a').forEach(a => { const hay = (a.textContent + ' ' + (a.dataset.t || '')).toLowerCase(); a.classList.toggle('hidden', q && !hay.includes(q)); });
    document.querySelectorAll('.sb-group').forEach(g => { g.style.display = [...g.querySelectorAll('a')].some(a => !a.classList.contains('hidden')) ? '' : 'none'; });
});

(function () {
    const track = document.getElementById('dashTrack'), tabs = [...document.querySelectorAll('#dashCar .car-tab')];
    const dotsWrap = document.getElementById('dashDots'); const n = track.children.length;
    for (let i = 0; i < n; i++) { const d = document.createElement('button'); d.className = 'dot' + (i === 0 ? ' active' : ''); d.addEventListener('click', () => go(i)); dotsWrap.appendChild(d); }
    const dots = [...dotsWrap.children];
    function go(i) { track.scrollTo({ left: track.clientWidth * i, behavior: 'smooth' }); }
    function sync() { const i = Math.round(track.scrollLeft / track.clientWidth); tabs.forEach((t, k) => t.classList.toggle('active', k === i)); dots.forEach((d, k) => d.classList.toggle('active', k === i)); }
    tabs.forEach((t, i) => t.addEventListener('click', () => go(i)));
    document.getElementById('carPrev').addEventListener('click', () => go(Math.max(0, Math.round(track.scrollLeft / track.clientWidth) - 1)));
    document.getElementById('carNext').addEventListener('click', () => go(Math.min(n - 1, Math.round(track.scrollLeft / track.clientWidth) + 1)));
    track.addEventListener('scroll', () => { clearTimeout(track._t); track._t = setTimeout(sync, 60); });
})();