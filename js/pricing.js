/*
 * アセント社労士事務所 — サービス・料金ページ
 * 料金表そのものは HTML に書いてあり、JS が動かなくてもすべて読めます。
 * このスクリプトは「人数・給与計算の有無を選んで比べる」「給与計算の目安を出す」補助だけを行います。
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

    // --- 給与計算：対象人数から月額の目安を出す ------------------------------------
    var BASE = 12000, PER_PAYROLL = 800, PER_ATTENDANCE = 400;
    var calc = document.querySelector('[data-payroll-calc]');
    if (calc) {
        calc.hidden = false;
        var nInput = calc.querySelector('[data-payroll-n]');
        var att = calc.querySelector('[data-payroll-att]');
        var formula = calc.querySelector('[data-payroll-formula]');
        var total = calc.querySelector('[data-payroll-total]');
        var update = function () {
            var n = Math.max(1, Math.min(999, parseInt(nInput.value, 10) || 1));
            var perPerson = PER_PAYROLL + (att.checked ? PER_ATTENDANCE : 0);
            var extra = perPerson * n;
            formula.textContent = yen(BASE) + '＋' + yen(extra) + '（' + yen(perPerson) + '×' + n + '名）';
            total.textContent = '月額' + yen(BASE + extra);
        };
        nInput.addEventListener('input', update);
        att.addEventListener('change', update);
        update();
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
