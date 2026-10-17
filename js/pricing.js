/*
 * アセント社労士事務所 — サービス・料金ページ
 * 料金表そのものは HTML に書いてあり、JS が動かなくてもすべて読めます。
 * このスクリプトは「人数・給与計算の有無を選んで比べる」補助だけを行います。
 *
 * 料金を変更するときは、HTML の表と下の PLAN_PRICES の両方を直してください。
 */
(function () {
    'use strict';

    var yen = function (n) { return n.toLocaleString('ja-JP') + '円'; };

    // --- 顧問プラン：社会保険の加入人数で3プランの月額を比べる ---------------------
    // b1:1～5名 b2:6～10名 b3:11～20名 b4:21～30名 b5:31～50名 b6:51～75名 b7:76名以上（null＝個別見積り）
    var PLAN_PRICES = {
        consult:   { b1: 16000, b2: 20000, b3: 24000, b4: 32000, b5: 40000, b6: null,  b7: null },
        procedure: { b1: 24000, b2: 28000, b3: 36000, b4: 44000, b5: 56000, b6: 72000, b7: null },
        partner:   { b1: 40000, b2: 40000, b3: 48000, b4: 56000, b5: 72000, b6: null,  b7: null }
    };
    var BAND_LABEL = { b1: '1～5名', b2: '6～10名', b3: '11～20名', b4: '21～30名', b5: '31～50名', b6: '51～75名', b7: '76名以上' };

    // 給与計算ありの月額＝顧問料＋給与計算の基本料金（別途 1名800円）。② ③ だけが選べる
    var PAYROLL_BASE = 12000;
    var PAYROLL_PLANS = ['procedure', 'partner'];

    var picker = document.querySelector('[data-headcount]');
    var advisor = document.getElementById('labor-advisor');
    if (picker) {
        picker.hidden = false;
        document.querySelectorAll('.plan__variant').forEach(function (v) { v.hidden = false; });

        var apply = function () {
            var band = picker.querySelector('input[name="band"]:checked').value;
            var withPayroll = picker.querySelector('input[name="payroll"]:checked').value === 'yes';
            advisor.classList.toggle('payroll-on', withPayroll);
            document.querySelectorAll('[data-set-payroll]').forEach(function (btn) {
                btn.setAttribute('aria-pressed', String((btn.getAttribute('data-set-payroll') === 'yes') === withPayroll));
            });
            document.querySelectorAll('[data-plan]').forEach(function (plan) {
                var key = plan.getAttribute('data-plan');
                var price = PLAN_PRICES[key][band];
                var addPayroll = withPayroll && PAYROLL_PLANS.indexOf(key) !== -1;
                var out = plan.querySelector('[data-plan-price]');
                if (price === null) {
                    out.textContent = '個別見積り';
                } else if (addPayroll) {
                    out.innerHTML = yen(price + PAYROLL_BASE) + '<small class="plan__plus">＋給与計算 1名800円</small>';
                } else {
                    out.textContent = yen(price);
                }
                plan.querySelector('[data-plan-band]').textContent = '（' + BAND_LABEL[band] + 'の場合）';
                plan.querySelectorAll('tr[data-bands]').forEach(function (tr) {
                    tr.classList.toggle('is-on', tr.getAttribute('data-bands').split(' ').indexOf(band) !== -1);
                });
            });
        };
        picker.addEventListener('change', apply);
        // カード内の「給与計算なし／あり」ボタンは、上の条件と連動させる
        document.querySelectorAll('[data-set-payroll]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                picker.querySelector('input[name="payroll"][value="' + btn.getAttribute('data-set-payroll') + '"]').checked = true;
                apply();
            });
        });
        apply();
    }

    // --- ヒーロー：用紙と料金早見表が順に現れ、金額が数え上がる ------------------------
    // 動きを減らす設定・JS なしのときは静止した完成形のまま
    var heroEl = document.querySelector('.pr-hero');
    if (heroEl && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        heroEl.classList.add('hm');
        requestAnimationFrame(function () { heroEl.classList.add('is-play'); });
        heroEl.querySelectorAll('[data-count]').forEach(function (el, i) {
            var to = Number(el.getAttribute('data-count'));
            var finalText = el.textContent;
            setTimeout(function () {
                var start = null;
                var step = function (ts) {
                    if (start === null) start = ts;
                    var p = Math.min((ts - start) / 900, 1);
                    el.textContent = p < 1 ? Math.round(to * (1 - Math.pow(1 - p, 3))).toLocaleString('ja-JP') : finalText;
                    if (p < 1) requestAnimationFrame(step);
                };
                requestAnimationFrame(step);
            }, 1100 + i * 250);
        });
    }

    // --- 積み上げ式：画面に入ったら層を順に積み上げる（「もう一度見る」で再生し直せる） ---
    var stackEl = document.querySelector('[data-stack]');
    if (stackEl && 'IntersectionObserver' in window && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        stackEl.classList.add('sm');
        var replay = stackEl.querySelector('[data-stack-replay]');
        var playStack = function () {
            stackEl.classList.remove('is-play');
            void stackEl.offsetWidth;
            stackEl.classList.add('is-play');
        };
        var stackIo = new IntersectionObserver(function (e) {
            if (!e[0].isIntersecting) return;
            playStack();
            stackIo.disconnect();
        }, { threshold: 0.35 });
        stackIo.observe(stackEl);
        if (replay) {
            replay.hidden = false;
            replay.addEventListener('click', playStack);
        }
    }

    // --- スマホ：ヒーローを過ぎたら相談ボタンを出す ---------------------------------
    var dock = document.getElementById('pr-dock');
    var hero = document.querySelector('.pr-hero');
    var contact = document.getElementById('contact');
    if (dock && hero && 'IntersectionObserver' in window) {
        var pastHero = false, atContact = false;
        var sync = function () { dock.classList.toggle('is-shown', pastHero && !atContact); };
        new IntersectionObserver(function (e) { pastHero = !e[0].isIntersecting; sync(); }).observe(hero);
        new IntersectionObserver(function (e) { atContact = e[0].isIntersecting; sync(); }).observe(contact);
    }
})();
