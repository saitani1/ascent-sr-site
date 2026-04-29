document.addEventListener("DOMContentLoaded", () => {
    const questions = [
        "採用して3か月以内に辞める人が、一定数いますか。",
        "人が辞めたあと、原因を整理する前に「また採ればよい」で回してしまうことが多いですか。",
        "定着しない理由を、労務や職場運営の観点から十分に整理できていませんか。",
        "社会保険や扶養の判断が、担当者や店長によって少しずつ違うことがありますか。",
        "着替え時間・開店準備・休憩中の電話対応など、「これは勤務時間に入るの？」と迷う場面がある。",
        "採用時に、勤務条件や社会保険加入について十分に説明できていないと感じますか。",
        "店長や責任者が、注意や指導をためらう場面がありますか。",
        "「指導」と「ハラスメント」の線引きが、現場で共有されていないと感じますか。",
        "勤務態度不良や問題行動への対応が、その場しのぎになりやすいですか。",
        "休職・復職・雇い止めなどの対応基準が、あいまいだと感じますか。",
        "労基署や年金事務所から連絡が来たときに、何を確認すればいいかすぐには整理できませんか。",
        "就業規則や雇用契約書が、今の現場実態に合っていないと感じますか。"
    ];

    const results = [
        {
            min: 0,
            max: 5,
            type: "安定運営タイプ",
            heading: "労務の土台は、比較的安定しています。",
            copy: [
                "現時点では、大きな乱れは起きにくい状態です。採用、社会保険判断、現場対応の基準が、一定程度そろっている可能性があります。",
                "ただし、サービス業は人の入れ替わりや制度変更で崩れやすい業種です。今のうちに、判断基準の明文化や定期点検をしておくことで、採用費やトラブル対応費のブレをさらに抑えやすくなります。"
            ],
            state: ["大きな問題は起きていない。", "属人的な判断が一部残っている可能性はある。", "今後の拡大時に崩れないよう、先回りして整える段階です。"],
            action: ["社会保険・雇用条件の説明ルールを見直す。", "店長向けの指導基準を明文化する。", "就業規則や雇用契約書が現場実態に合っているか確認する。"],
            cta: "無料チェックリストを受け取る"
        },
        {
            min: 6,
            max: 11,
            type: "見直し優先タイプ",
            heading: "小さな迷いが、コスト増につながり始めている可能性があります。",
            copy: [
                "現場運営は回っていても、一部の判断が属人化しているかもしれません。その状態を放置すると、シフト修正、説明ミス、店長判断のばらつきなど、小さなコストが積み上がりやすくなります。",
                "今の段階で整理しておけば、採用やトラブルにかかる余計なコストを抑えやすくなります。"
            ],
            state: ["大きな事故はない。", "現場の負担や手戻りが少しずつ増えている。", "担当者や店長によって対応に差がある。"],
            action: ["社会保険判断とシフト運用のルールを整理する。", "採用時説明の内容をそろえる。", "ハラスメントと指導の基準を共有する。"],
            cta: "結果レポートを受け取る"
        },
        {
            min: 12,
            max: 17,
            type: "コスト流出注意タイプ",
            heading: "労務の迷いが、利益の不安定さにつながっている可能性があります。",
            copy: [
                "採用やトラブル対応に関するコストが、見えないまま増えている可能性があります。店長が判断に迷う。社会保険や勤務条件の説明がぶれる。問題対応が後手に回る。",
                "こうした状態が続くと、売上が安定していても利益が残りにくくなります。場当たり的に対処するより、優先順位をつけて整えた方が、改善は早くなります。"
            ],
            state: ["人が辞めるたびに採用負担が増える。", "シフトや保険の判断が後追いになる。", "トラブル対応に時間を取られる。", "現場責任者が疲弊しやすい。"],
            action: ["離職や採用のやり直しが起きる原因を整理する。", "休職・雇い止め・指導のルールを明文化する。", "優先順位をつけて運用改善を始める。"],
            cta: "無料相談で優先順位を整理する"
        },
        {
            min: 18,
            max: 24,
            type: "早期改善推奨タイプ",
            heading: "利益を守るために、早めの見直しをおすすめします。",
            copy: [
                "労務判断のあいまいさが、採用・定着・トラブル対応に大きく影響している可能性があります。この状態では、売上が安定していても、利益が安定しにくくなります。",
                "採用費がかさむ。トラブル対応で本来業務が止まる。現場責任者の負担が重くなる。そうした状態が続く前に、一度全体を整理した方が改善は早いです。"
            ],
            state: ["場当たり対応が続いている。", "判断基準が人によって違う。", "問題が起きるたびに個別対応している。", "利益を削るコストが見えにくくなっている。"],
            action: ["まず全体の課題を整理する。", "どこで採用費やトラブル対応費が膨らんでいるか確認する。", "優先順位を決めて、制度と運用をセットで見直す。"],
            cta: "無料相談を予約する"
        }
    ];

    const root = document.querySelector("[data-diagnosis]");
    if (!root) return;

    const form = root.querySelector("[data-question-form]");
    const questionText = root.querySelector("[data-question-text]");
    const stepLabel = root.querySelector("[data-step-label]");
    const remaining = root.querySelector("[data-remaining]");
    const progressBar = root.querySelector("[data-progress-bar]");
    const prevButton = root.querySelector("[data-prev]");
    const nextButton = root.querySelector("[data-next]");
    const resultPanel = root.querySelector("[data-result]");
    const resultScore = root.querySelector("[data-result-score]");
    const resultTitle = root.querySelector("[data-result-title]");
    const resultHeading = root.querySelector("[data-result-heading]");
    const resultCopy = root.querySelector("[data-result-copy]");
    const resultState = root.querySelector("[data-result-state]");
    const resultAction = root.querySelector("[data-result-action]");
    const resultCta = root.querySelector("[data-result-cta]");
    const hiddenResult = document.querySelector("[data-hidden-result]");
    const resultDisplay = document.querySelector("[data-result-display]");

    let current = 0;
    const answers = new Array(questions.length).fill(null);

    const renderQuestion = () => {
        questionText.textContent = questions[current];
        stepLabel.textContent = `STEP ${current + 1} / ${questions.length}`;
        const left = questions.length - current - 1;
        remaining.textContent = left === 0 ? "最後の質問です" : `あと${left}問です`;
        progressBar.style.width = `${(current / questions.length) * 100}%`;
        prevButton.disabled = current === 0;
        nextButton.textContent = current === questions.length - 1 ? "結果を見る" : "次へ";
        form.querySelectorAll("input[name='answer']").forEach((input) => {
            input.checked = answers[current] === Number(input.value);
        });
    };

    const selectedAnswer = () => {
        const checked = form.querySelector("input[name='answer']:checked");
        return checked ? Number(checked.value) : null;
    };

    const fillList = (element, items) => {
        element.innerHTML = "";
        items.forEach((item) => {
            const li = document.createElement("li");
            li.textContent = item;
            element.appendChild(li);
        });
    };

    const showResult = () => {
        const score = answers.reduce((total, value) => total + Number(value || 0), 0);
        const result = results.find((item) => score >= item.min && score <= item.max);

        resultScore.textContent = `${score}点 / 24点`;
        resultTitle.textContent = result.type;
        resultHeading.textContent = result.heading;
        resultCopy.innerHTML = result.copy.map((paragraph) => `<p>${paragraph}</p>`).join("");
        fillList(resultState, result.state);
        fillList(resultAction, result.action);
        resultCta.textContent = result.cta;
        if (hiddenResult) hiddenResult.value = `${result.type}（${score}点 / 24点）`;
        if (resultDisplay) resultDisplay.value = `${result.type}（${score}点 / 24点）`;

        form.hidden = true;
        resultPanel.hidden = false;
        progressBar.style.width = "100%";
        stepLabel.textContent = "RESULT";
        remaining.textContent = "診断結果を表示しています";
        resultPanel.scrollIntoView({ behavior: "smooth", block: "start" });
    };

    form.addEventListener("submit", (event) => {
        event.preventDefault();
        const answer = selectedAnswer();
        if (answer === null) {
            form.querySelector(".answer-grid").animate(
                [{ transform: "translateX(0)" }, { transform: "translateX(8px)" }, { transform: "translateX(0)" }],
                { duration: 180 }
            );
            return;
        }

        answers[current] = answer;
        if (current < questions.length - 1) {
            current += 1;
            renderQuestion();
            return;
        }

        showResult();
    });

    prevButton.addEventListener("click", () => {
        if (current === 0) return;
        current -= 1;
        renderQuestion();
    });

    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
        anchor.addEventListener("click", (event) => {
            const target = document.querySelector(anchor.getAttribute("href"));
            if (!target) return;
            event.preventDefault();
            target.scrollIntoView({ behavior: "smooth", block: "start" });
        });
    });

    renderQuestion();
});
