from read_annotation_data import AnnotationObject
from read_data import get_json_files, read_json

def read_all_data():
    json_files = get_json_files()
    annotation_objects = []
    for j_f in json_files:
        annotation_data = read_json(j_f)
        has_mb = False
        for tier in annotation_data['tiers']:
            for key in annotation_data['tiers'][tier]:
                if annotation_data['tiers'][tier][key] == 'mb':
                    has_mb = True
                    break
        if not has_mb:
            print('No morpheme tier found in annotation data. Skipping.')
            continue
        annotation_objects.append(AnnotationObject(j_f, annotation_data))
    return annotation_objects

def build_word_list(annotation_objects):
    word_list = []
    exclude_count = 0
    for a_o in annotation_objects:
        for word in a_o.data['words']:
            w = a_o.data['words'][word]
            if not w.exclude_from_analysis:
                word_list.append(w)
            else:
                exclude_count += 1

    print(f'Excluded {exclude_count} words from analysis.')
    return word_list

def main_syllable_counts(word_list):
    main_syllable_counts = {}
    for word in word_list:
        if not word.main_syllable in main_syllable_counts:
            main_syllable_counts[word.main_syllable] = {
                'count': 0,
                'syllable_types': {
                    'monosyllabic': {'count': 0, 'words': []},
                    'sesquisyllabic': {'count': 0, 'words': []},
                    'disyllabic': {'count': 0, 'words': []},
                    'trisyllabic': {'count': 0, 'words': []}
                }
            }
        main_syllable_counts[word.main_syllable]['count'] += 1
        if not word.word_type in main_syllable_counts[word.main_syllable]['syllable_types']:
            main_syllable_counts[word.main_syllable]['syllable_types'][word.word_type] = {'count': 0, 'words': []}
        main_syllable_counts[word.main_syllable]['syllable_types'][word.word_type]['count'] += 1
        main_syllable_counts[word.main_syllable]['syllable_types'][word.word_type]['words'].append(word)
    # sort main_syllable_counts by count
    main_syllable_counts = dict(sorted(main_syllable_counts.items(), key=lambda item: item[1]['count'], reverse=True))
    return main_syllable_counts

def filter_main_syllables(main_syllable_count_dict, min_count=10):
    filtered_dict = {}
    for main_syllable in main_syllable_count_dict:
        syllable_type_counts = main_syllable_count_dict[main_syllable]['syllable_types']
        if syllable_type_counts['sesquisyllabic']['count'] > min_count or syllable_type_counts['disyllabic']['count'] > min_count:
            filtered_dict[main_syllable] = main_syllable_count_dict[main_syllable]
    return filtered_dict
