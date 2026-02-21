"""
Hungarian and Multilingual AutoMod Support
Contains Hungarian-specific content filtering and language-aware moderation
"""

# Common Hungarian bad words and profanity
HUNGARIAN_BAD_WORDS = [
    # Common insults and swear words
    'kurva', 'kibaszott', 'faszt', 'picsog', 'szar', 'geci',
    'segg', 'buzi', 'teljesen hülye', 'hülye', 'idióta',
    'fasz', 'barom', 'szaros', 'gecis', 'retkes',
    'rohadt', 'anyád', 'szarkozik', 'apád'
    'rohadeknak', 'tehetetlen', 'szemét', 'idióta',
    'hülye', 'balfasz', 'balfék', 'agyhalott',
    'pofád', 'pofádat', 'büdös', 'büdös élet',
    'szopás', 'szopd', 'szopd', 'szopjam',
    'baszd', 'baszd meg', 'baszd meg', 'bassza',
    'bassza meg', 'basszad', 'basszad meg',
    'picsába', 'picsád', 'picsádat', 'kurvára', 'kurvát',
    'rohadék', 'rohadékot','hülyének', 'hülyét',
    'idiótának', 'idiótát', 'balfasznak', 'balféket',
    'agyhalottnak', 'agyhalottat', 'büdösnek'
    
    # Variations and slang
    'kurva anyad', 'anyad kurva', 'szegenyek',
    'szemet', 'szemelyetelen', 'szegenynek',
]

# English bad words (common profanity)
ENGLISH_BAD_WORDS = [
    'shit', 'fuck', 'ass', 'asshole', 'bitch', 'dick',
    'cock', 'pussy', 'damn', 'damned', 'hell', 'crap',
    'bastard', 'piss', 'motherfucker', 'wtf', 'stfu',
    'nigga', 'nigger', 'faggot', 'retard'
]

# Language-specific configurations
LANGUAGE_FILTERS = {
    'hu': {
        'name': 'Hungarian',
        'bad_words': HUNGARIAN_BAD_WORDS,
        'caps_threshold': 0.7,
        'spam_timeout': 5
    },
    'en': {
        'name': 'English',
        'bad_words': ENGLISH_BAD_WORDS,
        'caps_threshold': 0.7,
        'spam_timeout': 5
     },   
}

def get_bad_words_for_language(language_code):
    """Get bad words list for a specific language"""
    if language_code in LANGUAGE_FILTERS:
        return LANGUAGE_FILTERS[language_code]['bad_words']
    return ENGLISH_BAD_WORDS

def merge_bad_words(language_code, custom_bad_words):
    """Merge language-specific bad words with custom ones"""
    base_words = get_bad_words_for_language(language_code)
    if custom_bad_words:
        return list(set(base_words + custom_bad_words))
    return base_words

def detect_language(text):
    """Simple language detection based on text characteristics"""
    text_lower = text.lower()
    
    # Hungarian specific characters
    hungarian_chars = ['á', 'é', 'í', 'ó', 'ö', 'ő', 'ú', 'ü', 'ű']
    hungarian_count = sum(1 for char in text_lower if char in hungarian_chars)
    
    # Determine dominant language
    if hungarian_count > hungarian_count > 0:
        return 'hu'
    elif hungarian_count > 0:
        return 'hu'
    else:
        return 'en'

def has_bad_words(text, language='en', custom_bad_words=None):
    """Check if text contains bad words for a given language"""
    bad_words = merge_bad_words(language, custom_bad_words)
    text_lower = text.lower()
    
    for word in bad_words:
        # Check for exact word match and word boundary variations
        if word in text_lower:
            return True, word
    
    return False, None
