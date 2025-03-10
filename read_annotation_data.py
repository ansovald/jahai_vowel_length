from structural_analysis import classify_morpheme, get_main_syllable, classify_phone, get_cv_structure, classify_cv_structure, normalize_word

class AnnotationObject:
    def __init__(self, name, annotation_data):
        if name.endswith('.json'):
            name = name[:-5]
        self.name = name
        self.timeline = Timeline(annotation_data['timeline'])
        self.tiers = []

        self.speakers = []
        for p in annotation_data['persons']:
            if annotation_data['persons'][p]['tiers']:
                if len(annotation_data['persons'][p]['tiers']) == 8:
                    self.speakers.append(annotation_data['persons'][p]['name'])
                    self.tiers.extend(annotation_data['persons'][p]['tiers'])
                    # We exclude speakers from analysis that do not have the full set of tiers

        self.data = {
            'words' : {},
            'morphemes' : {},
            'glosses' : {},
            'phones' : {}
        }
        self.read_words_from_data(annotation_data['annotation_blocks'])

    def read_words_from_data(self, annotation_blocks):
        annotation_structure = {
            # the key to search for in the annotation_blocks, the key to store the data in the data dict,
            # the object type to create, and the parent key to link the data to
            'wd' : [ 'words', Word,  self ],
            'mb' : [ 'morphemes', Morpheme, 'words' ],
            'gl' : [ 'glosses', Gloss, 'morphemes' ],
            'ph' : [ 'phones', Phone, 'morphemes' ]
        }
        for ab in annotation_blocks:
            block = annotation_blocks[ab]
            speaker = block['who']
            for child in block['children']:
                for key in annotation_structure:
                    if child.startswith(key) and child in self.tiers:
                        sub_dict, child_class, parent_dict = annotation_structure[key]
                        for obj in block['children'][child]:
                            obj_data = block['children'][child][obj]
                            start = self.timeline.get_when(obj_data['from'])
                            end = self.timeline.get_when(obj_data['to'])
                            text = obj_data['text']
                            if parent_dict is not self:
                                parent = self.data[parent_dict][obj_data['target'][1:]]
                                self.data[sub_dict][obj] = child_class(obj, start, end, text, parent=parent)
                            else:
                                self.data[sub_dict][obj] = child_class(obj, start, end, text, parent=self, speaker=speaker)
        
        for word in self.data['words']:
            word_obj = self.data['words'][word]
            word_obj.complete_analysis()

    def __str__(self):
        return f'{self.name}'

class Timeline:
    def __init__(self, timeline_dict):
        for key in timeline_dict:
            if 'absolute' in timeline_dict[key]:
                absolute = timeline_dict[key]['absolute']
                if absolute == '00:00:00':
                    absolute = 0
                setattr(self, key, absolute)
            else:
                setattr(self, key, timeline_dict[key]['interval'])

    def get_when(self, when_id):
        if when_id.startswith('#'):
            when_id = when_id[1:]
        return getattr(self, when_id)

class Word:
    def __init__(self, word_id, start, end, text, parent, speaker=None):
        if speaker is not None:
            self.speaker = speaker
        self.word_id = word_id
        self.start = int(start)
        self.end = int(end)
        self.text = normalize_word(text)
        self.parent = parent
        self.children = []
        self.exclude_from_analysis = False
        self.main_syllable = ''
        self.word_type = ''
        self.structure = ''
        self.phon_structure = ''
        self.syll_count = 0
        if text[0] == '<' and text[-1] == '>':
            # print(f'Excluding {text} from analysis')
            self.exclude_from_analysis = True

    def __str__(self):
        return f'{self.text} ({self.morphological_analysis()})'

    def morphological_analysis(self):
        return ''.join([c.text for c in self.children])

    def children_string(self):
        return ', '.join([str(c) for c in self.children])

    def duration(self):
        return self.end - self.start

    def get_morph_cv_structure(self):
        if not self.structure:
            if self.exclude_from_analysis:
                self.structure = 'invalid'
            structure = ''
            for c in self.children:
                if type(c) == Morpheme:
                    if c.cv_structure == 'invalid':
                        self.exclude_from_analysis = True
                        return 'invalid'
                    structure += c.cv_structure
            self.structure = structure
        return self.structure

    def get_phon_cv_structure(self):
        if not self.phon_structure:
            self.complete_analysis()
        return self.phon_structure

    def prefixed(self):
        if len(self.children) > 1:
            return True
        return False

    def add_child(self, child):
        self.children.append(child)
        # Sort by child.start
        self.children.sort(key=lambda x: x.start)

    def get_vowel_durations(self):
        vowel_durations = []
        for c in self.children:
            if type(c) == Morpheme:
                vowel_durations.extend(c.get_vowel_durations())
        return vowel_durations

    def get_vowel_count(self):
        vowel_count = 0
        for c in self.children:
            if type(c) == Morpheme:
                vowel_count += c.vowel_count()
        return vowel_count

    def get_phones(self):
        phones = []
        for c in self.children:
            if type(c) == Morpheme:
                phones.extend(c.get_phones())
        return phones

    def get_head_morpheme(self):
        return self.children[-1]

    def get_glosses(self):
        glosses = []
        for c in self.children:
            if type(c) == Morpheme:
                morph_string = c.text
                for ch in c.children:
                    if type(ch) == Gloss:
                        morph_string += f' {ch.text}'
                glosses.append(morph_string)
        return glosses

    def set_main_syllable(self, main_syllable):
        self.main_syllable = main_syllable
        if self.main_syllable == 'invalid':
            self.exclude_from_analysis = True

    def complete_analysis(self):
        if self.exclude_from_analysis:
            return 'invalid'
        structure = ''
        for c in self.children:
            if type(c) == Morpheme:
                structure += c.cv_structure
        word_type, structure = classify_cv_structure(structure)
        self.word_type = word_type
        self.phon_structure = structure
        self.syll_count = len(structure.split('.'))
        if self.syll_count != self.get_vowel_count():
            self.exclude_from_analysis = True

class SubWord(Word):
    def __init__(self, word_id, start, end, text, parent):
        super().__init__(word_id, start, end, text, parent)
        parent.add_child(self)

    def __str__(self):
        return f'{self.text} ({self.duration()}ms)'

    def duration(self):
        return self.end - self.start

class Morpheme(SubWord):
    def __init__(self, word_id, start, end, text, parent):
        super().__init__(word_id, start, end, text, parent)
        self.phones = []
        self.vowels = []
        self.gloss = None
        self.word = parent
        self.morph_type = classify_morpheme(self.text)
        self.main_syllable = get_main_syllable(self.text)
        self.cv_structure = get_cv_structure(self.text)
        if self.end == parent.end and not parent.exclude_from_analysis:
            parent.set_main_syllable(self.main_syllable)

    def add_vowel(self, vowel):
        self.vowels.append(vowel)
        # Sort the vowels by 'start'
        self.vowels.sort(key=lambda x: x['start'])

    def add_phone(self, phone):
        self.phones.append(phone)
        # Sort the phones by 'start'
        self.phones.sort(key=lambda x: x.start)

    def print_vowels(self):
        for v in self.vowels:
            print(f'{v["phone"]} {v["duration"]}', end='; ')
        print()

    def get_vowel_durations(self):
        return [(v['phone'], v['duration']) for v in self.vowels]

    def get_phones(self):
        return [p.text for p in self.phones]
    
    def vowel_count(self):
        return len(self.vowels)

class Gloss(SubWord):
    def __init__(self, word_id, start, end, text, parent):
        super().__init__(word_id, start, end, text, parent)
        parent.gloss = self.text
        self.word = parent.word

        if text.endswith('NAME'):
            self.word.exclude_from_analysis = True

class Phone(SubWord):
    def __init__(self, word_id, start, end, text, parent):
        super().__init__(word_id, start, end, text, parent)
        parent.add_phone(self)
        self.classification = classify_phone(text)
        if self.classification == 'V':
            parent.add_vowel({ 'phone': self.text, 'start': self.start, 'duration': self.duration() })
