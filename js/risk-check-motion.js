/*
 * サービス・料金ページ — 特別メニュー「実務同行型 労務点検」の動き
 * 内容はすべて HTML に書いてあり、JS が動かない／動きを減らす設定のときは静止した完成形で表示されます。
 * このスクリプトは、画面に入った要素に .is-play を付けて CSS のアニメーションを始め、価格を数え上げるだけです。
 */
(function () {
    'use strict';

    var section = document.getElementById('risk-check');
    if (!section) return;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    if (!('IntersectionObserver' in window)) return;

    section.classList.add('rc-motion');

    // 価格を 0 から数え上げる（最後は必ず HTML に書いた金額で止める）
    var countUp = function (el) {
        var to = Number(el.getAttribute('data-to'));
        var finalText = el.textContent;
        var start = null, DURATION = 1400;
        var step = function (ts) {
            if (start === null) start = ts;
            var p = Math.min((ts - start) / DURATION, 1);
            var eased = 1 - Math.pow(1 - p, 3);
            el.textContent = p < 1 ? (Math.round(to * eased / 1000) * 1000).toLocaleString('ja-JP') : finalText;
            if (p < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
    };

    var play = function (el) {
        el.classList.add('is-play');
        var count = el.querySelector('.rc-count');
        if (count) setTimeout(function () { countUp(count); }, 500);
    };

    var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
            if (!e.isIntersecting) return;
            play(e.target);
            io.unobserve(e.target);
        });
    }, { threshold: 0.3 });
    section.querySelectorAll('[data-rc]').forEach(function (el) { io.observe(el); });
})();
