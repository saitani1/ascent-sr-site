/*
 * アセント社労士事務所 — トップページの動き
 * JSが動かない環境でも、すべての内容は読める状態で表示されます。
 */
(function () {
    'use strict';

    var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var header = document.getElementById('site-header');

    // --- Mobile menu --------------------------------------------------------
    var menuBtn = document.getElementById('mobile-menu-btn');
    var menu = document.getElementById('mobile-menu');

    function setMenu(open) {
        menu.classList.toggle('is-open', open);
        header.classList.toggle('menu-open', open);
        menuBtn.setAttribute('aria-expanded', String(open));
        menu.setAttribute('aria-hidden', String(!open));
        document.body.style.overflow = open ? 'hidden' : '';
    }
    menuBtn.addEventListener('click', function () {
        setMenu(!menu.classList.contains('is-open'));
    });
    menu.addEventListener('click', function (e) {
        if (e.target.closest('a')) setMenu(false);
    });
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && menu.classList.contains('is-open')) {
            setMenu(false);
            menuBtn.focus();
        }
    });

    // --- Count-up -------------------------------------------------------------
    function countUp(el) {
        var target = parseInt(el.getAttribute('data-count'), 10);
        if (reduceMotion || !target || target < 10) return;
        var start = null;
        var dur = 1400;
        function frame(t) {
            if (!start) start = t;
            var p = Math.min((t - start) / dur, 1);
            var eased = 1 - Math.pow(1 - p, 3);
            el.textContent = Math.round(target * eased).toLocaleString('ja-JP');
            if (p < 1) requestAnimationFrame(frame);
        }
        el.textContent = '0';
        requestAnimationFrame(frame);
    }

    // --- Reveal on scroll ----------------------------------------------------
    var revealEls = document.querySelectorAll('[data-reveal]');
    if ('IntersectionObserver' in window && !reduceMotion) {
        var io = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                var el = entry.target;
                el.classList.add('is-in');
                el.querySelectorAll('[data-count]').forEach(countUp);
                io.unobserve(el);
            });
        }, { rootMargin: '0px 0px -10% 0px', threshold: 0.08 });
        revealEls.forEach(function (el) { io.observe(el); });
    } else {
        revealEls.forEach(function (el) { el.classList.add('is-in'); });
    }

    // --- Self check: 「なんとなく不安」チェック --------------------------------
    var checks = document.querySelectorAll('#self-check input');
    var countEl = document.getElementById('check-count');
    var msgEl = document.getElementById('check-msg');
    var messages = [
        'ひとつでも当てはまれば、早めの整理がおすすめです。',
        '小さな迷いのうちに、判断基準を決めておきましょう。',
        '迷いが重なり始めています。5分診断で優先順位を整理しませんか。',
        '利益を削る前に、一度まとめて整理するのがおすすめです。'
    ];
    function updateChecks() {
        var n = 0;
        checks.forEach(function (c) { if (c.checked) n++; });
        countEl.textContent = n;
        msgEl.textContent = messages[n === 0 ? 0 : n === 1 ? 1 : n <= 3 ? 2 : 3];
    }
    checks.forEach(function (c) { c.addEventListener('change', updateChecks); });

    // --- Blog rail ----------------------------------------------------------
    var rail = document.getElementById('rail');
    if (rail) {
        var slides = rail.querySelectorAll('.swiper-slide');
        var prev = document.getElementById('rail-prev');
        var next = document.getElementById('rail-next');
        var cur = document.getElementById('rail-current');
        var total = document.getElementById('rail-total');
        var bar = document.getElementById('rail-bar');
        var pad = function (n) { return n < 10 ? '0' + n : String(n); };
        total.textContent = pad(slides.length);

        var railLeft = function () {
            return rail.getBoundingClientRect().left + parseFloat(getComputedStyle(rail).paddingLeft);
        };
        var currentIndex = function () {
            var left = railLeft();
            var best = 0;
            var bestDist = Infinity;
            slides.forEach(function (s, i) {
                var d = Math.abs(s.getBoundingClientRect().left - left);
                if (d < bestDist) { bestDist = d; best = i; }
            });
            return best;
        };
        var update = function () {
            var max = rail.scrollWidth - rail.clientWidth;
            var i = rail.scrollLeft >= max - 4 ? slides.length - 1 : currentIndex();
            cur.textContent = pad(i + 1);
            prev.disabled = rail.scrollLeft <= 4;
            next.disabled = rail.scrollLeft >= max - 4;
            var w = Math.max(rail.clientWidth / rail.scrollWidth, 0.1);
            bar.style.width = (w * 100) + '%';
            bar.style.left = (max > 0 ? (rail.scrollLeft / max) * (1 - w) * 100 : 0) + '%';
        };
        var go = function (dir) {
            var i = Math.max(0, Math.min(slides.length - 1, currentIndex() + dir));
            rail.scrollBy({ left: slides[i].getBoundingClientRect().left - railLeft(), behavior: reduceMotion ? 'auto' : 'smooth' });
        };

        prev.addEventListener('click', function () { go(-1); });
        next.addEventListener('click', function () { go(1); });
        rail.addEventListener('scroll', function () { window.requestAnimationFrame(update); }, { passive: true });
        window.addEventListener('resize', update);
        update();

        // マウスでのドラッグ送り（タッチはブラウザ標準のスワイプに任せる）
        var dragging = false, moved = false, startX = 0, startLeft = 0;
        rail.addEventListener('pointerdown', function (e) {
            if (e.pointerType !== 'mouse' || e.button !== 0) return;
            dragging = true; moved = false;
            startX = e.clientX; startLeft = rail.scrollLeft;
            rail.style.scrollSnapType = 'none';
        });
        window.addEventListener('pointermove', function (e) {
            if (!dragging) return;
            var dx = e.clientX - startX;
            if (Math.abs(dx) > 5) moved = true;
            rail.scrollLeft = startLeft - dx;
        });
        window.addEventListener('pointerup', function () {
            if (!dragging) return;
            dragging = false;
            rail.style.scrollSnapType = '';
        });
        rail.addEventListener('click', function (e) {
            if (moved) { e.preventDefault(); e.stopPropagation(); moved = false; }
        }, true);
        rail.addEventListener('dragstart', function (e) { e.preventDefault(); });
    }

    // --- Contact: 付箋 → 本文へ -------------------------------------------------
    var textarea = document.getElementById('message');
    var PREFIX = 'ご相談テーマ：';
    document.querySelectorAll('.tag').forEach(function (tag) {
        tag.addEventListener('click', function () {
            tag.setAttribute('aria-pressed', String(tag.getAttribute('aria-pressed') !== 'true'));
            var chosen = [];
            document.querySelectorAll('.tag[aria-pressed="true"]').forEach(function (t) {
                chosen.push(t.textContent.trim());
            });
            var lines = textarea.value.split('\n');
            if (lines[0].indexOf(PREFIX) === 0) lines.shift();
            textarea.value = (chosen.length ? PREFIX + chosen.join('／') + '\n' : '') + lines.join('\n');
        });
    });

    // --- Mobile dock: ヒーローを過ぎたら出し、フォームが見えたら隠す ---------------
    var dock = document.getElementById('dock');
    var hero = document.getElementById('home');
    var contact = document.getElementById('contact-form-anchor');
    if (dock && 'IntersectionObserver' in window) {
        var pastHero = false, atContact = false;
        var sync = function () { dock.classList.toggle('is-shown', pastHero && !atContact); };
        new IntersectionObserver(function (e) { pastHero = !e[0].isIntersecting; sync(); }).observe(hero);
        new IntersectionObserver(function (e) { atContact = e[0].isIntersecting; sync(); }).observe(contact);
    }

    // --- Video: 動きを減らす設定ではユーザー操作に任せる ------------------------------
    var video = document.getElementById('labor-journey-video');
    if (video && reduceMotion) {
        video.autoplay = false;
        video.pause();
    }
})();
