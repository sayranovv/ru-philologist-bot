from typing import Dict, List, Tuple

import pymorphy3

POS_MAP = {
    'NOUN': 'существительное',
    'ADJF': 'прилагательное',
    'ADJS': 'прилагательное',
    'COMP': 'комп',
    'VERB': 'глагол',
    'INFN': 'инфинитив',
    'PRTF': 'причастие',
    'PRTS': 'причастие',
    'GRND': 'деепричастие',
    'NUMR': 'число',
    'ADVB': 'наречие',
    'NPRO': 'местоимение',
    'PRED': 'предк',
    'PREP': 'предлог',
    'CONJ': 'союз',
    'PART': 'часть',
    'INTJ': 'междометие',
}

GRAMMEME_MAP = {
    'NOUN': 'СУЩ',
    'ADJF': 'ПРИЛ',
    'ADJS': 'ПРИЛ',
    'COMP': 'КОМП',
    'VERB': 'ГЛАГ',
    'INFN': 'ИНФИНИТИВ',
    'PRTF': 'ПРИЧАСТИЕ',
    'PRTS': 'ПРИЧАСТИЕ',
    'GRND': 'ДЕЕПРИЧАСТИЕ',
    'NUMR': 'ЧИСЛ',
    'ADVB': 'НАРЕЧ',
    'NPRO': 'МЕСТ',
    'PRED': 'ПРЕДК',
    'PREP': 'ПРЕДЛ',
    'CONJ': 'СОЮЗ',
    'PART': 'ЧАСТ',
    'INTJ': 'МЕЖД',
    'inan': 'НЕОДУШ',
    'anim': 'ОДУШ',
    'femn': 'ЖЕН',
    'masc': 'МУЖ',
    'neut': 'СР',
    'sing': 'ЕД',
    'plur': 'МН',
    'nomn': 'ИМ',
    'gent': 'РОД',
    'datv': 'ДАТ',
    'accs': 'ВИН',
    'ablt': 'ТВОР',
    'loct': 'ПРЕДЛ',
}

morph = pymorphy3.MorphAnalyzer()


def map_grammemes(grammemes_set):
    return [GRAMMEME_MAP.get(g, g) for g in sorted(grammemes_set)]


async def analyze_word(word: str) -> Dict[str, str]:
    parsed = morph.parse(word)[0]

    grammemes = parsed.tag.grammemes if hasattr(parsed.tag, 'grammemes') else set()
    mapped_grammemes = map_grammemes(grammemes)
    grammeme_str = ', '.join(mapped_grammemes) if mapped_grammemes else 'н/д'

    pos = POS_MAP.get(str(parsed.tag.POS)) if hasattr(parsed.tag, 'POS') else 'СУЩ'

    return {
        'word': word,
        'normal_form': parsed.normal_form,
        'pos': pos,
        'grammemes': grammeme_str,
    }


async def get_word_variations(word: str) -> Dict[str, List[str]]:
    parsed = morph.parse(word)[0]
    normal_form = parsed.normal_form

    variations = {
        'nominative': [],
        'genitive': [],
        'dative': [],
        'accusative': [],
        'instrumental': [],
        'prepositional': [],
    }

    case_mapping = {
        'nomn': 'nominative',
        'gent': 'genitive',
        'datv': 'dative',
        'accs': 'accusative',
        'ablt': 'instrumental',
        'loct': 'prepositional',
    }

    base_parsed = morph.parse(normal_form)[0]
    for case_short, case_long in case_mapping.items():
        try:
            inflected = base_parsed.inflect({case_short})
            if inflected:
                variations[case_long].append(inflected.word)
        except Exception:
            pass

    return variations


async def lemmatize_text(text: str) -> List[Tuple[str, str]]:
    words = text.split()
    lemmatized = []

    for word in words:
        parsed = morph.parse(word)[0]
        lemmatized.append((word, parsed.normal_form))

    return lemmatized


async def extract_pos(text: str) -> Dict[str, List[str]]:
    words = text.split()
    pos_dict: Dict[str, List[str]] = {}

    for word in words:
        parsed = morph.parse(word)[0]
        pos = str(parsed.tag.POS)

        if pos not in pos_dict:
            pos_dict[pos] = []
        pos_dict[pos].append(word)

    return pos_dict
