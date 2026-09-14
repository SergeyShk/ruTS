import threading
from collections import Counter
from importlib.metadata import version
from math import isnan

import gradio as gr
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import spacy
from matplotlib.figure import Figure

from ruts import (
    BasicStats,
    DiversityStats,
    MorphStats,
    PhonStats,
    ReadabilityStats,
    StyleStats,
    SyntaxStats,
    WordsExtractor,
)
from ruts.constants import (
    BASIC_STATS_DESC,
    DIVERSITY_STATS_DESC,
    HIGHLIGHT_LAYERS_DESC,
    MORPHOLOGY_STATS_DESC,
    PHON_STATS_DESC,
    READABILITY_STATS_DESC,
    STYLE_STATS_DESC,
    SYNTAX_STATS_DESC,
)
from ruts.style_stats import is_stopword
from ruts.visualizers import highlight, zipf

matplotlib.use("Agg")

MAX_CHARS = 20_000
ZIPF_WORDS = 100
ZIPF_MIN_WORDS = 100
POS_SHORT = {
    "NOUN": "сущ.",
    "ADJF": "прил.",
    "ADJS": "кр. прил.",
    "COMP": "компаратив",
    "VERB": "глагол",
    "INFN": "инфинитив",
    "PRTF": "причастие",
    "PRTS": "кр. прич.",
    "GRND": "деепричастие",
    "NUMR": "числит.",
    "ADVB": "наречие",
    "NPRO": "местоим.",
    "PRED": "предикатив",
    "PREP": "предлог",
    "CONJ": "союз",
    "PRCL": "частица",
    "INTJ": "междометие",
}
EXAMPLES = {
    "Сказка": (
        "Жили-были старик со старухой. У них была курочка Ряба. Снесла курочка яичко, "
        "не простое, а золотое. Дед бил, бил - не разбил. Баба била, била - не разбила. "
        "Мышка бежала, хвостиком махнула, яичко упало и разбилось. Дед плачет, баба плачет, "
        "а курочка кудахчет: не плачь, дед, не плачь, баба, я снесу вам яичко другое, "
        "не золотое, а простое."
    ),
    "Стихи": (
        "Полночной порою в болотной глуши\n"
        "Чуть слышно, бесшумно шуршат камыши.\n"
        "О чём они шепчут? О чём говорят?\n"
        "Зачем огоньки между ними горят?\n\n"
        "Мелькают, мигают - и снова их нет.\n"
        "И снова забрезжил блуждающий свет.\n"
        "Полночной порой камыши шелестят.\n"
        "В них жабы гнездятся, в них змеи свистят."
    ),
    "Новость": (
        "Администрация города утвердила программу ремонта дворов на следующий год. "
        "Согласно документу, в первую очередь будут отремонтированы проезды и детские площадки "
        "в микрорайонах, построенных до 1980 года, а заявки жителей, поданные через портал, "
        "рассматриваются в течение месяца. Расходы бюджета оцениваются в двести миллионов рублей, "
        "подрядчиков выберут по итогам открытого конкурса в марте.\n\n"
        "Программа рассчитана на три года. В первый год планируется привести в порядок сорок "
        "дворов, во второй - шестьдесят, в третий - все оставшиеся. Жители смогут следить "
        "за ходом работ на карте, которая появится на сайте администрации весной: там будут "
        "отмечены адреса, сроки и подрядчики. Как пояснили в пресс-службе, при выборе дворов "
        "учитывались возраст домов, состояние покрытия и число обращений. Депутаты городской думы "
        "поддержали программу единогласно, но попросили отчитываться о её выполнении каждый "
        "квартал, а не раз в год, как предлагала администрация."
    ),
    "Научная проза": (
        "Тезаурусы - особый класс лексикографических ресурсов, для которых характерны следующие "
        "черты: полнота значений словарного состава языка или какого-либо его сегмента; "
        "тематический, или идеографический способ упорядочения значений слов. Отличительной "
        "особенностью тезаурусов по сравнению с формальными онтологиями является выход в сферу "
        "лексических значений, установление связей не только между значениями и выражающими их "
        "словами, а также между самими значениями (регистрация различных семантических отношений "
        "внутри словаря)."
    ),
    "Канцелярит": (
        "Проект, подготовленный за неделю, был одобрен советом без обсуждения. Повышение "
        "эффективности использования бюджетных средств обсуждалось, не выходя за рамки регламента. "
        "Участники, представлявшие региональные министерства, не смогли согласовать позиции по "
        "вопросам финансирования и распределения ответственности между ведомствами, поскольку "
        "каждое из них настаивало на собственной трактовке положений соглашения. Споры стихли, "
        "в кулуарах шумно шептались и шушукались, а решение было отложено до следующего заседания."
    ),
}

nlp = spacy.load("ru_core_news_sm", exclude=["ner"])
plot_lock = threading.Lock()


def format_value(value: float | int) -> str:
    if isinstance(value, float):
        return "-" if isnan(value) else f"{value:.2f}"
    return str(value)


def stats_table(stats: dict[str, float], desc: dict[str, str]) -> pd.DataFrame:
    rows = [(desc[key], format_value(stats[key])) for key in desc if key in stats]
    return pd.DataFrame(rows, columns=["Метрика", "Значение"])


def format_reading_time(minutes: float) -> str:
    if minutes < 1:
        return "меньше минуты"
    total = round(minutes)
    if total < 60:
        return f"{total} мин"
    return f"{total // 60} ч {total % 60} мин"


def readability_summary(rs: ReadabilityStats) -> str:
    return (
        f"### {rs.describe_grade()}\n\n"
        f"Сводный класс по семи формулам - **{rs.consensus_grade:.1f}**, "
        f"индекс удобочитаемости Флеша - **{rs.flesch_reading_easy:.0f}**, "
        f"время чтения - **{format_reading_time(rs.reading_time)}**."
    )


def morph_tables(ms: MorphStats) -> tuple[pd.DataFrame, pd.DataFrame]:
    stats = ms.get_stats(filter_none=True)
    pos = sorted(stats["pos"].items(), key=lambda item: -item[1])
    pos_table = pd.DataFrame(
        [(POS_SHORT.get(tag, tag), count) for tag, count in pos], columns=["Часть речи", "Слов"]
    )
    rows = []
    for category, counts in stats.items():
        if category == "pos":
            continue
        desc = MORPHOLOGY_STATS_DESC[category]
        for value, count in sorted(counts.items(), key=lambda item: -item[1]):
            rows.append((desc["name"], desc["values"].get(value, value), count))
    return pos_table, pd.DataFrame(rows, columns=["Признак", "Значение", "Слов"])


def zipf_plot(words: tuple[str, ...]) -> Figure:
    counter = Counter(word for word in words if not is_stopword(word))
    with plot_lock:
        fig = plt.figure(figsize=(7, 4.5))
        zipf(
            counter,
            num_words=min(ZIPF_WORDS, len(counter)),
            num_labels=6,
            show_theory=True,
            alpha=1.1,
        )
        fig.tight_layout()
        plt.close(fig)
    return fig


def render_highlight(doc, layers: list[str]) -> str:
    return highlight(doc, layers=layers).to_html()


def analyze(text: str, layers: list[str]):
    text = text.strip()[:MAX_CHARS]
    if not text:
        raise gr.Error("Вставьте текст для разбора")
    doc = nlp(text)
    try:
        bs = BasicStats(doc)
        rs = ReadabilityStats(doc)
        ds = DiversityStats(doc)
        ms = MorphStats(doc)
        ss = StyleStats(doc)
        ps = PhonStats(doc)
        xs = SyntaxStats(doc)
    except ValueError as error:
        raise gr.Error(str(error)) from error
    words = WordsExtractor(use_lexemes=True, lowercase=True, filter_nums=True).extract(text)
    pos_table, morph_table = morph_tables(ms)
    basic = {key: value for key, value in bs.get_stats().items() if key in BASIC_STATS_DESC}
    enough_words = bs.n_words >= ZIPF_MIN_WORDS
    return (
        doc,
        render_highlight(doc, layers),
        readability_summary(rs),
        stats_table(rs.get_stats(), READABILITY_STATS_DESC),
        stats_table(ds.get_stats(), DIVERSITY_STATS_DESC),
        pos_table,
        morph_table,
        stats_table(xs.get_stats(), SYNTAX_STATS_DESC),
        stats_table(ss.get_stats(), STYLE_STATS_DESC),
        stats_table(ps.get_stats(), PHON_STATS_DESC),
        stats_table(basic, BASIC_STATS_DESC),
        gr.Plot(value=zipf_plot(words) if enough_words else None, visible=enough_words),
        gr.Markdown(visible=not enough_words),
    )


def rerender(doc, layers: list[str]) -> str:
    if doc is None:
        return ""
    return render_highlight(doc, layers)


HEADER = """
# ruTS - статистики русского текста

Вставьте текст и получите удобочитаемость, лексическое разнообразие, морфологический и синтаксический
профиль, SEO-метрики стиля, фоностатистики и подсветку фрагментов, из которых складываются эти числа.
[GitHub](https://github.com/SergeyShk/ruTS) · [Документация](https://sergeyshk.github.io/ruTS/) ·
[PyPI](https://pypi.org/project/ruts/)
"""
FOOTER = (
    f"ruts {version('ruts')} · spaCy {spacy.__version__} · ru_core_news_sm {nlp.meta['version']}"
)
CSS = """
.ruts-highlight { font-size: 1.05em; }
.stats { --font-mono: var(--font); }
"""

with gr.Blocks(title="ruTS") as demo:
    gr.Markdown(HEADER)
    doc_state = gr.State()
    highlight_output = gr.HTML(label="Подсветка", container=True, padding=True, render=False)
    summary_output = gr.Markdown(render=False)
    tables = {
        name: gr.Dataframe(interactive=False, elem_classes="stats", render=False)
        for name in ("readability", "diversity", "morph", "syntax", "style", "phon", "basic")
    }
    pos_output = gr.BarPlot(
        x="Часть речи",
        y="Слов",
        sort="-y",
        x_label_angle=-30,
        height=300,
        container=False,
        render=False,
    )
    zipf_output = gr.Plot(label="Закон Ципфа", show_label=False, render=False)
    zipf_note = gr.Markdown(
        f"*График закона Ципфа строится для текстов от {ZIPF_MIN_WORDS} слов.*",
        visible=False,
        render=False,
    )
    outputs = [
        doc_state,
        highlight_output,
        summary_output,
        tables["readability"],
        tables["diversity"],
        pos_output,
        tables["morph"],
        tables["syntax"],
        tables["style"],
        tables["phon"],
        tables["basic"],
        zipf_output,
        zipf_note,
    ]

    with gr.Row():
        with gr.Column(scale=3):
            text_input = gr.Textbox(
                lines=9,
                max_lines=20,
                max_length=MAX_CHARS,
                label="Текст",
                placeholder=f"Вставьте текст на русском языке, до {MAX_CHARS:,} символов".replace(
                    ",", " "
                ),
            )
            gr.Examples(
                examples=[[text] for text in EXAMPLES.values()],
                example_labels=list(EXAMPLES),
                inputs=[text_input],
                outputs=outputs,
                fn=lambda text: analyze(text, list(HIGHLIGHT_LAYERS_DESC)),
                run_on_click=True,
                cache_examples=False,
                label="Примеры",
            )
        with gr.Column(scale=1):
            layers_input = gr.CheckboxGroup(
                choices=[(name, key) for key, name in HIGHLIGHT_LAYERS_DESC.items()],
                value=list(HIGHLIGHT_LAYERS_DESC),
                label="Слои подсветки",
            )
            analyze_button = gr.Button("Разобрать", variant="primary")
    with gr.Row():
        with gr.Column():
            highlight_output.render()
            zipf_output.render()
            zipf_note.render()
        with gr.Column():
            summary_output.render()
            with gr.Tabs():
                with gr.Tab("Читаемость"):
                    tables["readability"].render()
                with gr.Tab("Лексика"):
                    tables["diversity"].render()
                with gr.Tab("Морфология"):
                    pos_output.render()
                    tables["morph"].render()
                with gr.Tab("Синтаксис"):
                    tables["syntax"].render()
                with gr.Tab("Стиль"):
                    tables["style"].render()
                with gr.Tab("Фоника"):
                    tables["phon"].render()
                with gr.Tab("Базовые"):
                    tables["basic"].render()
    gr.Markdown(FOOTER)

    demo.load(
        lambda: (EXAMPLES["Новость"], *analyze(EXAMPLES["Новость"], list(HIGHLIGHT_LAYERS_DESC))),
        outputs=[text_input, *outputs],
    )
    analyze_button.click(analyze, inputs=[text_input, layers_input], outputs=outputs)
    text_input.submit(analyze, inputs=[text_input, layers_input], outputs=outputs)
    layers_input.change(rerender, inputs=[doc_state, layers_input], outputs=[highlight_output])

if __name__ == "__main__":
    demo.launch(css=CSS)
