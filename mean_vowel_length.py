import numpy as np
import json

VOWEL_ORDER = ['i', '1', 'u', 'e', '@', 'o', 'E', 'a', 'O', 'i~', 'u~', '@~', 'E~', 'a~', 'all']

def sort_by_vowel_order(vowel_dict):
    sorted_vowel_dict = {}
    for v in VOWEL_ORDER:
        if v in vowel_dict:
            sorted_vowel_dict[v] = vowel_dict[v]
    return sorted_vowel_dict

def sort_list_by_vowel_order(vowel_list):
    sorted_vowel_list = []
    for v in VOWEL_ORDER:
        if v in vowel_list:
            sorted_vowel_list.append(v)
    return sorted_vowel_list

def all_vowel_durations(word_list):
    vowel_durations = {
        'all' : {
            'description': 'vowel durations for all words',
            'plot_label': 'all words',
            'data': {}
        }
    }
    for w in word_list:
        v_d = w.get_vowel_durations()
        for i, (v, d) in enumerate(v_d):
            if v not in vowel_durations['all']['data']:
                vowel_durations['all']['data'][v] = []
            vowel_durations['all']['data'][v].append(d)

    # analyze the vowel durations
    vowel_durations['all']['data'] = analyze_vowel_durations(vowel_durations['all']['data'])
    # Sort the vowel durations by VOWEL_ORDER
    vowel_durations['all']['data'] = sort_by_vowel_order(vowel_durations['all']['data'])
    save_vowel_durations(vowel_durations)
    return vowel_durations

def vowel_durations(word_list, criteria=None):
    if not criteria:
        criteria = {
            'word_type': 'disyllabic',
            'syllable_structure': 'all',
        }
    print(f"Calculating vowel durations for {criteria["word_type"]} words with syllable structure '{criteria["syllable_structure"]}'.")
    vowel_durations = {}
    for w in word_list:
        if w.word_type == criteria['word_type'] or criteria['word_type'] == 'all':
            if criteria['syllable_structure'] == 'all' or w.get_phon_cv_structure() in criteria['syllable_structure']:
                v_d = w.get_vowel_durations()
                for i, (v, d) in enumerate(v_d):
                    main_key = f'{criteria['word_type']}_{w.get_phon_cv_structure()}_S{i+1}'
                    if main_key not in vowel_durations:
                        vowel_durations[main_key] = {
                            'description': f"syllable #{i+1} of {criteria["word_type"]} words with structure '{w.get_phon_cv_structure()}'",
                            'plot_label': f"({criteria["word_type"]} {w.get_phon_cv_structure()})",
                            'data': {}
                        }
                        if not criteria["word_type"] == 'monosyllabic':
                            vowel_durations[main_key]['plot_label'] = f'{i+1}. syllable ' + vowel_durations[main_key]['plot_label']
                    if v not in vowel_durations[main_key]['data']:
                        vowel_durations[main_key]['data'][v] = []
                    vowel_durations[main_key]['data'][v].append(d)
                    if criteria['word_type'] in ['sesquisyllabic', 'disyllabic', 'trisyllabic'] and i == 1:
                        secondary_key = f'{criteria['word_type']}_CVC_S2'
                        if secondary_key not in vowel_durations:
                            vowel_durations[secondary_key] = {
                                'description': f"syllable #2 of {criteria["word_type"]} words with structure 'CVC'",
                                'plot_label': f"({criteria["word_type"]} CVC)",
                                'data': {}
                            }
                        if v not in vowel_durations[secondary_key]['data']:
                            vowel_durations[secondary_key]['data'][v] = []
                        vowel_durations[secondary_key]['data'][v].append(d)


    for s in vowel_durations:
        vowel_durations[s]['data'] = sort_by_vowel_order(vowel_durations[s]['data'])
        print(f'analyzing {s}...')
        vowel_durations[s]['data'] = analyze_vowel_durations(vowel_durations[s]['data'])
    # for key in vowel_durations:
    #     print(key)
    #     print(f'\t{vowel_durations[key]["description"]}')
    #     for v in vowel_durations[key]['data']:
    #         print(f'\t\t{v}: {vowel_durations[key]["data"][v]}')

    save_vowel_durations(vowel_durations)
    return vowel_durations

def analyze_vowel_durations(vowel_durations, min_count=10):
    # Input is a dictionary, where the keys are vowels and the values are lists of vowel durations
    # Output is a dictionary, where the keys are vowels and the values are dictionaries with the keys:
    # 'mean', 'standard_deviation', 'count', and 'data'
    # Additional key is 'all', which contains the same information for all vowels (minus the 'data' key)
    temp_vowel_durations = {}
    for v in vowel_durations:
        duration_data = np.array(vowel_durations[v])
        duration_data = reject_outliers(duration_data)
        count = len(duration_data)
        if count < min_count:
            print(f'\t{v} has {count} < {min_count} data points. Skipping.')
            continue
        mean = np.mean(duration_data)
        median = np.median(duration_data)
        std = np.std(duration_data)
        # make duration data a list of integers
        duration_data = [int(d) for d in duration_data]
        temp_vowel_durations[v] = {
            'median': float(np.round(median, 1)),
            'mean': float(np.round(mean, 1)),
            'standard_deviation': float(np.round(std, 1)),
            'count': count,
            'data': duration_data
        }
    # Calculate the mean for all vowels
    all_data = np.array([d for v in vowel_durations for d in vowel_durations[v]])
    all_data = reject_outliers(all_data)
    all_mean = np.mean(all_data)
    all_median = np.median(all_data)
    all_std = np.std(all_data)
    all_count = len(all_data)
    # convert all data to list of int
    all_data = [int(d) for d in all_data]
    temp_vowel_durations['all'] = {
        'median': all_median,
        'mean': all_mean,
        'standard_deviation': all_std,
        'count': all_count,
        'data': all_data
    }
    return temp_vowel_durations

def save_vowel_durations(vowel_durations, name='vowel_duration_data.json', append=True):
    if append:
        try:
            with open(name, 'r') as f:
                data = json.load(f)
                data.update(vowel_durations)
        except FileNotFoundError:
            print(f'File {name} not found. Creating new file.')
            data = vowel_durations
    else:
        data = vowel_durations
    with open(name, 'w') as f:
        json.dump(data, f)

def read_vowel_durations(name='vowel_duration_data.json'):
    with open(name, 'r') as f:
        data = json.load(f)
    return data

def extract_data_rows(vowel_durations, keys):
    data_rows = {}
    for key in keys:
        data_rows[keys[key]] = {'description': vowel_durations[key]['description'], 'plot_label': vowel_durations[key]['plot_label']}
        data_rows[keys[key]]['median'] = vowel_durations[key]['data']['all']['median']
        data_rows[keys[key]]['mean'] = vowel_durations[key]['data']['all']['mean']
        data_rows[keys[key]]['data'] = vowel_durations[key]['data']['all']['data']
        print(f'mean of {keys[key]}: {data_rows[keys[key]]["mean"]}')
    return data_rows

def reject_outliers(data, m = 2.):
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d/mdev if mdev else np.zeros(len(d))
    return data[s<m]
