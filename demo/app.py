import threading
from collections import Counter
from functools import lru_cache
from importlib.metadata import version
from io import BytesIO
from math import isnan

import gradio as gr
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import spacy
from PIL import Image
from spacy.tokens import Doc

from ruts import (
    BasicStats,
    CohesionStats,
    DiversityStats,
    LexicalStats,
    MorphStats,
    PhonStats,
    ReadabilityStats,
    StyleStats,
    SyntaxStats,
    WordsExtractor,
)
from ruts.constants import (
    BASIC_STATS_DESC,
    COHESION_STATS_DESC,
    DIVERSITY_STATS_DESC,
    HIGHLIGHT_DEFAULT_LAYERS,
    HIGHLIGHT_LAYER_GROUPS,
    HIGHLIGHT_LAYERS_DESC,
    LEXICAL_STATS_DESC,
    MORPHOLOGY_STATS_DESC,
    PHON_STATS_DESC,
    READABILITY_STATS_DESC,
    STYLE_STATS_DESC,
    SYNTAX_STATS_DESC,
)
from ruts.datasets import FreqDict
from ruts.style_stats import is_stopword
from ruts.visualizers import highlight, zipf

matplotlib.use("Agg")

MAX_CHARS = 20_000
ZIPF_WORDS = 100
ZIPF_MIN_WORDS = 100
POS_SHORT = {
    "NOUN": "сущ.",
    "PROPN": "имя собств.",
    "ADJ": "прил.",
    "ADV": "наречие",
    "VERB": "глагол",
    "AUX": "вспом. глагол",
    "PRON": "местоим.",
    "DET": "местоим. прил.",
    "NUM": "числит.",
    "ADP": "предлог",
    "CCONJ": "соч. союз",
    "SCONJ": "подч. союз",
    "PART": "частица",
    "INTJ": "междометие",
    "PUNCT": "знак",
    "SYM": "символ",
    "X": "прочее",
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
        "Чуть слышно, бесшумно, шуршат камыши.\n\n"
        "О чём они шепчут? О чём говорят?\n"
        "Зачем огоньки между ними горят?\n\n"
        "Мелькают, мигают - и снова их нет.\n"
        "И снова забрезжил блуждающий свет.\n\n"
        "Полночной порой камыши шелестят.\n"
        "В них жабы гнездятся, в них змеи свистят.\n\n"
        "В болоте дрожит умирающий лик.\n"
        "То месяц багровый печально поник.\n\n"
        "И тиной запахло. И сырость ползёт.\n"
        "Трясина заманит, сожмёт, засосёт.\n\n"
        "«Кого? Для чего? - камыши говорят, -\n"
        "Зачем огоньки между нами горят?»\n\n"
        "Но месяц печальный безмолвно поник.\n"
        "Не знает. Склоняет всё ниже свой лик.\n\n"
        "И, вздох повторяя погибшей души,\n"
        "Тоскливо, бесшумно, шуршат камыши.\n\n"
        "* * *\n\n"
        "Вечер. Взморье. Вздохи ветра.\n"
        "Величавый возглас волн.\n"
        "Близко буря. В берег бьётся\n"
        "Чуждый чарам чёрный чёлн.\n\n"
        "Чуждый чистым чарам счастья,\n"
        "Чёлн томленья, чёлн тревог,\n"
        "Бросил берег, бьётся с бурей,\n"
        "Ищет светлых снов чертог.\n\n"
        "Мчится взморьем, мчится морем,\n"
        "Отдаваясь воле волн.\n"
        "Месяц матовый взирает,\n"
        "Месяц горький полон грусти.\n\n"
        "Умер вечер. Ночь чернеет.\n"
        "Ропщет море. Мрак растёт.\n"
        "Чёлн томленья тьмой охвачен.\n"
        "Буря воет в бездне вод."
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
        "внутри словаря).\n\n"
        "Построение тезауруса предполагает выделение понятий предметной области, установление "
        "между ними отношений синонимии, гипонимии и ассоциации, а также сопоставление каждому "
        "понятию множества текстовых входов - слов и словосочетаний, которыми оно выражается "
        "в текстах. Полученная структура используется для расширения запросов в информационном "
        "поиске, автоматической рубрикации документов и разрешения лексической многозначности, "
        "поскольку позволяет соотносить разные формулировки с одним и тем же значением."
    ),
    "Канцелярит": (
        "Проект, подготовленный за неделю, был одобрен советом без обсуждения. Повышение "
        "эффективности использования бюджетных средств обсуждалось, не выходя за рамки регламента. "
        "Участники, представлявшие региональные министерства, не смогли согласовать позиции по "
        "вопросам финансирования и распределения ответственности между ведомствами, поскольку "
        "каждое из них настаивало на собственной трактовке положений соглашения. Споры стихли, "
        "в кулуарах шумно шептались и шушукались, а решение было отложено до следующего заседания.\n\n"
        "По итогам заседания было принято решение о необходимости проведения дополнительных "
        "консультаций с участием представителей заинтересованных ведомств в целях выработки "
        "согласованной позиции по вопросу распределения полномочий. Ответственность за организацию "
        "консультаций и подготовку соответствующего протокола была возложена на секретариат, "
        "которым должен быть обеспечен учёт замечаний, поступивших в ходе обсуждения."
    ),
}

DEFAULT_LAYERS = list(HIGHLIGHT_DEFAULT_LAYERS)
DEFAULT_GROUP_LAYERS = [
    [layer for layer in group if layer in HIGHLIGHT_DEFAULT_LAYERS]
    for group in HIGHLIGHT_LAYER_GROUPS.values()
]
nlp = spacy.load("ru_core_news_sm", exclude=["ner", "lemmatizer"])
freq_dict = FreqDict()
if not freq_dict.filepath:
    try:
        freq_dict.download()
    except (RuntimeError, OSError) as error:
        print(f"Частотный словарь недоступен: {error}")
plot_lock = threading.Lock()


@lru_cache(maxsize=32)
def parse(text: str) -> Doc:
    return nlp(text)


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


def lexical_table(ls: LexicalStats) -> pd.DataFrame:
    if freq_dict.filepath:
        return stats_table(ls.get_stats(), LEXICAL_STATS_DESC)
    bands = {
        key: getattr(ls, key)
        for key in LEXICAL_STATS_DESC
        if key.startswith(("p_top", "p_beyond"))
    }
    bands["lexical_density"] = ls.lexical_density
    return stats_table(bands, LEXICAL_STATS_DESC)


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


def zipf_image(words: tuple[str, ...]) -> Image.Image:
    counter = Counter(word for word in words if not is_stopword(word))
    buffer = BytesIO()
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
        fig.savefig(buffer, format="png", dpi=150)
        plt.close(fig)
    buffer.seek(0)
    return Image.open(buffer)


def render_highlight(text: str, layers: list[str]) -> str:
    return highlight(parse(text), layers=layers).to_html()


def compute(text: str, layers: list[str]) -> dict:
    text = text.strip()[:MAX_CHARS]
    if not text:
        raise ValueError("Вставьте текст для разбора")
    doc = parse(text)
    bs = BasicStats(doc)
    rs = ReadabilityStats(doc)
    ds = DiversityStats(doc)
    ms = MorphStats(doc)
    ss = StyleStats(doc)
    ps = PhonStats(doc)
    xs = SyntaxStats(doc)
    cs = CohesionStats(doc)
    ls = LexicalStats(doc, freq_dict=freq_dict)
    words = WordsExtractor(use_lexemes=True, lowercase=True, filter_nums=True).extract(text)
    pos_table, morph_table = morph_tables(ms)
    basic = {key: value for key, value in bs.get_stats().items() if key in BASIC_STATS_DESC}
    enough_words = bs.n_words >= ZIPF_MIN_WORDS
    return {
        "text": text,
        "highlight": highlight(doc, layers=layers).to_html(),
        "summary": readability_summary(rs),
        "readability": stats_table(rs.get_stats(), READABILITY_STATS_DESC),
        "diversity": stats_table(ds.get_stats(), DIVERSITY_STATS_DESC),
        "pos": pos_table,
        "morph": morph_table,
        "syntax": stats_table(xs.get_stats(), SYNTAX_STATS_DESC),
        "cohesion": stats_table(cs.get_stats(), COHESION_STATS_DESC),
        "lexical": lexical_table(ls),
        "style": stats_table(ss.get_stats(), STYLE_STATS_DESC),
        "phon": stats_table(ps.get_stats(), PHON_STATS_DESC),
        "basic": stats_table(basic, BASIC_STATS_DESC),
        "zipf": zipf_image(words) if enough_words else None,
        "enough_words": enough_words,
    }


def analyze(text: str, *groups: list[str]):
    try:
        result = compute(text, [layer for group in groups for layer in group])
    except ValueError as error:
        raise gr.Error(str(error)) from error
    return (
        result["text"],
        result["highlight"],
        result["summary"],
        result["readability"],
        result["diversity"],
        result["pos"],
        result["morph"],
        result["syntax"],
        result["cohesion"],
        result["lexical"],
        result["style"],
        result["phon"],
        result["basic"],
        gr.Image(value=result["zipf"], visible=result["enough_words"]),
        gr.Markdown(visible=not result["enough_words"]),
    )


def rerender(text: str | None, *groups: list[str]) -> str:
    if not text:
        return ""
    return render_highlight(text, [layer for group in groups for layer in group])


HEADER = """
# ruTS - статистики русского текста

Вставьте текст и получите удобочитаемость, лексическое разнообразие, морфологический и синтаксический
профиль, связность, частотность слов, SEO-метрики стиля, фоностатистики и подсветку фрагментов, из которых складываются эти числа.
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

INITIAL = compute(EXAMPLES["Новость"], DEFAULT_LAYERS)

with gr.Blocks(title="ruTS") as demo:
    gr.Markdown(HEADER)
    text_state = gr.State(INITIAL["text"])
    highlight_output = gr.HTML(
        INITIAL["highlight"], label="Подсветка", container=True, padding=True, render=False
    )
    summary_output = gr.Markdown(INITIAL["summary"], render=False)
    tables = {
        name: gr.Dataframe(INITIAL[name], interactive=False, elem_classes="stats", render=False)
        for name in (
            "readability",
            "diversity",
            "morph",
            "syntax",
            "cohesion",
            "lexical",
            "style",
            "phon",
            "basic",
        )
    }
    pos_output = gr.BarPlot(
        INITIAL["pos"],
        x="Часть речи",
        y="Слов",
        sort="-y",
        x_label_angle=-30,
        height=300,
        container=False,
        render=False,
    )
    zipf_output = gr.Image(
        INITIAL["zipf"],
        label="Закон Ципфа",
        show_label=False,
        interactive=False,
        visible=INITIAL["enough_words"],
        render=False,
    )
    zipf_note = gr.Markdown(
        f"*График закона Ципфа строится для текстов от {ZIPF_MIN_WORDS} слов.*",
        visible=not INITIAL["enough_words"],
        render=False,
    )
    outputs = [
        text_state,
        highlight_output,
        summary_output,
        tables["readability"],
        tables["diversity"],
        pos_output,
        tables["morph"],
        tables["syntax"],
        tables["cohesion"],
        tables["lexical"],
        tables["style"],
        tables["phon"],
        tables["basic"],
        zipf_output,
        zipf_note,
    ]

    with gr.Row():
        with gr.Column(scale=3):
            text_input = gr.Textbox(
                INITIAL["text"],
                lines=9,
                max_lines=20,
                max_length=MAX_CHARS,
                label="Текст",
                placeholder=f"Вставьте текст на русском языке, до {MAX_CHARS:,} символов".replace(
                    ",", " "
                ),
            )
        with gr.Column(scale=1):
            layer_inputs = [
                gr.CheckboxGroup(
                    choices=[(HIGHLIGHT_LAYERS_DESC[layer], layer) for layer in group],
                    value=[layer for layer in group if layer in HIGHLIGHT_DEFAULT_LAYERS],
                    label=f"Подсветка: {name.lower()}",
                )
                for name, group in HIGHLIGHT_LAYER_GROUPS.items()
            ]
            analyze_button = gr.Button("Разобрать", variant="primary")
    gr.Examples(
        examples=[[text, *DEFAULT_GROUP_LAYERS] for text in EXAMPLES.values()],
        example_labels=list(EXAMPLES),
        inputs=[text_input, *layer_inputs],
        outputs=outputs,
        fn=analyze,
        run_on_click=True,
        cache_examples=False,
        label="Примеры",
    )
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
                with gr.Tab("Связность"):
                    tables["cohesion"].render()
                with gr.Tab("Частотность"):
                    tables["lexical"].render()
                with gr.Tab("Стиль"):
                    tables["style"].render()
                with gr.Tab("Фоника"):
                    tables["phon"].render()
                with gr.Tab("Базовые"):
                    tables["basic"].render()
    gr.Markdown(FOOTER)

    analyze_button.click(analyze, inputs=[text_input, *layer_inputs], outputs=outputs)
    text_input.submit(analyze, inputs=[text_input, *layer_inputs], outputs=outputs)
    for layer_input in layer_inputs:
        layer_input.change(
            rerender, inputs=[text_state, *layer_inputs], outputs=[highlight_output]
        )

if __name__ == "__main__":
    demo.launch(css=CSS)
