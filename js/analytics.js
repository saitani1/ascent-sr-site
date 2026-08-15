/*
 * アセント社労士事務所 — 計測
 *
 * 目的: profile.html を読んだ人が、実際にお問い合わせまで進んだかを追う。
 *
 * 使い方:
 *   1. GA4 プロパティを作成し、測定ID（G- から始まる文字列）を取得する
 *   2. 下の ASCENT_GA_ID を差し替える
 *   3. 差し替えるまで、このスクリプトは外部への送信を一切行わない
 *
 * 注意: 測定IDを設定すると Google へのデータ送信が始まります。
 *       プライバシーポリシーの掲載を先に済ませてください。
 */

var ASCENT_GA_ID = 'G-XXXXXXXXXX';

(function () {
    'use strict';

    // 測定ID未設定のあいだは何も送らない（配線だけ通しておくための安全弁）
    if (!ASCENT_GA_ID || ASCENT_GA_ID.indexOf('XXXX') !== -1) {
        return;
    }

    var tag = document.createElement('script');
    tag.async = true;
    tag.src = 'https://www.googletagmanager.com/gtag/js?id=' + ASCENT_GA_ID;
    document.head.appendChild(tag);

    window.dataLayer = window.dataLayer || [];
    function gtag() { window.dataLayer.push(arguments); }
    window.gtag = gtag;

    gtag('js', new Date());
    gtag('config', ASCENT_GA_ID);

    var ORIGIN_KEY = 'ascent_cta_origin';

    function pageName() {
        var f = location.pathname.split('/').pop();
        return f ? f.replace(/\.html$/, '') : 'index';
    }

    // CTAがページのどこにあるかを、囲っている要素から判定する
    function ctaLocation(el) {
        if (el.closest('header')) return 'header';
        if (el.closest('footer')) return 'footer';
        var section = el.closest('section');
        if (section && section.id) return section.id;
        return 'body';
    }

    function ctaKind(href) {
        if (href.indexOf('tel:') === 0) return 'tel';
        if (href.indexOf('contact-form-anchor') !== -1) return 'contact';
        if (href.indexOf('#services') !== -1) return 'services';
        return 'other';
    }

    // --- 1. CTAクリック ---------------------------------------------------
    document.addEventListener('click', function (e) {
        var a = e.target.closest('a[href]');
        if (!a) return;

        var href = a.getAttribute('href') || '';
        var kind = ctaKind(href);
        if (kind === 'other') return;

        var from = pageName();

        gtag('event', 'cta_click', {
            cta_kind: kind,                                  // contact / tel / services
            cta_location: ctaLocation(a),                    // header / footer / セクションid
            cta_label: (a.innerText || '').trim().slice(0, 40),
            from_page: from
        });

        // 問い合わせ導線に入った出発点を覚えておく。
        // フォームは index.html にあるため、ページをまたいで引き継ぐ必要がある。
        if (kind === 'contact') {
            try { sessionStorage.setItem(ORIGIN_KEY, from); } catch (err) { /* 無視 */ }
        }
    }, true);

    // --- 2. フォーム送信 ---------------------------------------------------
    // Formspree への通常POSTなので、送信後は外部ドメインへ遷移する。
    // 遷移前にこのイベントを飛ばすことが、送信を観測できる唯一の機会。
    var form = document.querySelector('form.contact-form');
    if (form) {
        form.addEventListener('submit', function () {
            var origin = '';
            try { origin = sessionStorage.getItem(ORIGIN_KEY) || 'direct'; } catch (err) { origin = 'unknown'; }

            gtag('event', 'contact_submit', {
                cta_origin: origin,                          // profile / index / direct
                transport_type: 'beacon'
            });

            try { sessionStorage.removeItem(ORIGIN_KEY); } catch (err) { /* 無視 */ }
        });
    }

    // --- 3. 読了深度（profile.html のみ） ----------------------------------
    // 「ワークライフハーモニーを奥に置く」判断が正しかったかを検証するための計測。
    // 奥まで読まれていなければ、置き場所を見直す材料になる。
    if (pageName() === 'profile') {
        var marks = [25, 50, 75, 100];
        var sent = {};

        var onScroll = function () {
            var doc = document.documentElement;
            var scrollable = doc.scrollHeight - window.innerHeight;
            if (scrollable <= 0) return;

            var pct = (window.scrollY / scrollable) * 100;

            for (var i = 0; i < marks.length; i++) {
                var m = marks[i];
                if (pct >= m && !sent[m]) {
                    sent[m] = true;
                    gtag('event', 'scroll_depth', { percent: m, page: 'profile' });
                }
            }

            if (sent[100]) {
                window.removeEventListener('scroll', onScroll);
            }
        };

        window.addEventListener('scroll', onScroll, { passive: true });
    }
})();
