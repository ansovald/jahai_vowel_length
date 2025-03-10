import unicodedata

VOWELS = ['a', 'e', 'i', 'o', 'u', 'ɛ', 'ɨ', 'ə', 'ɔ']
# For some reason, COMBINING GREEK PERISPOMENI appears at least once in place of COMBINING TILDE
COMBINING_TILDE = ['\u0303', '\u0342']

X_SAMPA_VOWELS = ['a', 'e', 'i', 'o', 'u', 'E', '1', '@', 'O']

def normalize_word(word):
    # Normalize the word to NFD form
    word = unicodedata.normalize('NFD', word)
    # Replace COMBINING GREEK PERISPOMENI with COMBINING TILDE
    replace_dict = { '\u0342' : '\u0303' }
    for k, v in replace_dict.items():
        word = word.replace(k, v)
    return word

def classify_phone(phone):
    if phone[0] in X_SAMPA_VOWELS:
        return 'V'
    return 'C'

def get_cv_structure(word):
    # Returns the structured word and the syllable structure
    # word = normalize_word(word)
    structure = ''
    for letter in word:
        if letter in VOWELS:
            structure += 'V'
        elif letter == '-' or letter == '=' or letter == '_':
            structure += '='
        elif letter == '<' or letter == '>':
            structure += letter
        elif letter in ['*', '<', '>']:
            return 'invalid'
        elif letter in COMBINING_TILDE:
            continue
            # Add COMBINING TILDE to the last vowel in decomposed_word
            # decomposed_word[-1] += '\u0303'
        else:
            structure += 'C'
            # decomposed_word.append(letter)
        if structure[-3:] == 'CVC' and len(structure) > 3:
            structure = structure[:-3] + '.CVC'
        if len(structure) > 6 and structure[-3:] != 'CVC':
            return 'invalid'
    return structure #, decomposed_word

def classify_morpheme(morpheme):
    if morpheme[0] == '=':
        if morpheme[-1] == '=':
            return 'infix'
        return 'prefix'
    return 'main'

def get_main_syllable(morpheme):
    # Returns the main syllable of a morpheme
    decomposed_morpheme = []
    for letter in morpheme:
        if letter in VOWELS:
            decomposed_morpheme.append(letter)
        elif letter in COMBINING_TILDE:
            # Add COMBINING TILDE to the last vowel in decomposed_word
            decomposed_morpheme[-1] += '\u0303'
        else:
            decomposed_morpheme.append(letter)
    return ''.join(decomposed_morpheme[-3:]) if len(decomposed_morpheme) > 2 else 'invalid'

def classify_cv_structure(cv_structure):
    # print(f'\t\tcv_structure: {cv_structure}')
    # Replace 'CV=C=' with 'CVC.', since in this case the second prefix isn't a syllable on its own
    cv_structure = cv_structure.replace('CV=C=', 'CVC.')
    cv_structure = cv_structure.replace('CV=C.', 'CVC.')
    # Same goes for 'C=C.'
    cv_structure = cv_structure.replace('C=C.', 'CC.')
    # Replace '=' with '.'
    cv_structure = cv_structure.replace('=', '.')
    # If '-', '_', '<', or '>' is present, the structure is invalid
    if '-' in cv_structure or '_' in cv_structure or '<' in cv_structure or '>' in cv_structure:
        print(f'\n\n\nInvalid cv_structure: {cv_structure}\n\n\n')
        return 'invalid', 'invalid'
    if not cv_structure.endswith('CVC'):
        return 'invalid', 'invalid'
    syllables = cv_structure.split('.')
    syll_types = ''     # will be a list of `h` for half and `f` for full syllables
    for s in syllables:
        if s == 'C':
            syll_types += 'h'
        elif s == 'CV' or s == 'CC' or s == 'CVC':
            syll_types += 'f'
        else:
            # print(f'Syllable {s} not recognized')
            return 'invalid', 'invalid'
    if syll_types == 'f':
        return 'monosyllabic', cv_structure
    elif syll_types == 'hf':
        return 'sesquisyllabic', cv_structure
    elif syll_types == 'ff':
        return 'disyllabic', cv_structure
    elif syll_types == 'fff' or syll_types == 'hff':
        return 'trisyllabic', cv_structure
    return 'unclear', cv_structure
