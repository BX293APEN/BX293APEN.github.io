window.addEventListener('load', () => {
        (function () {
        const app = document.getElementById('attack-app');
        const rows = [...app.querySelectorAll('tbody tr')];
        const q = app.querySelector('#q'), cnt = app.querySelector('#count');
        const sel = new Set();
        const norm = s => s.normalize('NFKC').toLowerCase();
        
        rows.forEach(tr => {
            tr._text = norm(tr.textContent);
            tr._tags = tr.dataset.tags.split('|');
        });
    
        /** ヘッダ2段目の固定位置を1段目の高さに合わせる */
        const r1 = app.querySelector('thead tr.r1');
        const fit = () => app.querySelector('.scroller').style.setProperty('--r1h', r1.offsetHeight + 'px');
        fit(); addEventListener('resize', fit);
    
        function apply() {
            const words = norm(q.value).split(/\s+/).filter(Boolean);
            let n = 0;
            rows.forEach(tr => {
                const ok = [...sel].every(t => tr._tags.includes(t)) && words.every(w => tr._text.includes(w));
                tr.hidden = !ok; if (ok) n++;
            });
            cnt.textContent = n + ' / ' + rows.length + ' 件';
            app.querySelectorAll('[data-tag]').forEach(b => b.classList.toggle('active', sel.has(b.dataset.tag)));
        }
    
        app.addEventListener('click', e => {
            const b = e.target.closest('[data-tag]');
            if (!b) return;
            e.preventDefault();
            const t = b.dataset.tag;
            sel.has(t) ? sel.delete(t) : sel.add(t);
            apply();
        });
        q.addEventListener('input', apply);
        app.querySelector('#clear').addEventListener('click', () => { sel.clear(); q.value = ''; apply(); });
        apply();
    })();
});
