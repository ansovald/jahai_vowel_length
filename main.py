from analyse_data import read_all_data, build_word_list, main_syllable_counts, filter_main_syllables
from mean_vowel_length import vowel_durations, read_vowel_durations
from plot_vowel_stats import plot_vowel_durations, compare_plot

def students_t_test(data1, data2):
    from scipy.stats import ttest_ind
    import numpy as np
    print(f'mean1: {np.mean(data1)}, mean2: {np.mean(data2)}')
    t, p = ttest_ind(data1, data2)
    return t, p

if __name__ == '__main__':
    annotation_objects = read_all_data()
    word_list = build_word_list(annotation_objects)

    criteria_list = [
        {'word_type': 'monosyllabic', 'syllable_structure': 'all'},
        {'word_type': 'sesquisyllabic', 'syllable_structure': 'all'},
        {'word_type': 'disyllabic', 'syllable_structure': 'all'},
        # {'word_type': 'trisyllabic', 'syllable_structure': 'all'},
    ]
    for criteria in criteria_list:
        vowel_durations(word_list, criteria)

    from mean_vowel_length import all_vowel_durations
    all_vowels_durations = all_vowel_durations(word_list)

    vowel_durations = read_vowel_durations()
    for key in vowel_durations:
        print(f'{key}: {vowel_durations[key]}')
        plot_vowel_durations(vowel_durations[key]['data'], name=key, axis_label=vowel_durations[key]['plot_label'], save_format='eps')

    save_format = 'png'
    vowel_durations = read_vowel_durations()

    disyllabic_data_keys = {
        'disyllabic_CC.CVC_S1' : 'CC',
        'disyllabic_CV.CVC_S1' : 'CV',
        'disyllabic_CVC.CVC_S1' : 'CVC',
        'disyllabic_CVC_S2' : 'main syllable'
    }
    from mean_vowel_length import extract_data_rows
    from plot_vowel_stats import plot_data_row
    disyllabic_data = extract_data_rows(vowel_durations, disyllabic_data_keys)
    plot_data_row(disyllabic_data, plot_label='vowel duration for syllable types in disyllabic words (in ms)', name='disyllabic_1S', save_format=save_format)


    sesquisyllabic_data_keys = {
        'sesquisyllabic_C.CVC_S1': 'C',
        'sesquisyllabic_C.CVC_S2': 'main syllable',
    }
    sesquisyllabic_data = extract_data_rows(vowel_durations, sesquisyllabic_data_keys)
    plot_data_row(sesquisyllabic_data, plot_label='vowel duration for syllable types in sesquisyllabic words (in ms)', name='sesquisyllabic_1S', save_format=save_format)

    main_syllable_keys = {
        'sesquisyllabic_C.CVC_S2': 'sesquisyllabic',
        'disyllabic_CVC_S2': 'disyllabic',
        'monosyllabic_CVC_S1': 'monosyllabic',
    }

    main_syllable_data = extract_data_rows(vowel_durations, main_syllable_keys)
    plot_data_row(main_syllable_data, plot_label='vowel duration of main syllables in different word types (in ms)', name='main_syllable', save_format=save_format)

    from scipy.stats import ttest_ind

    # Test independence of data rows
    data1 = disyllabic_data['CC']['data']
    data2 = disyllabic_data['CV']['data']
    data3 = disyllabic_data['CVC']['data']
    data4 = disyllabic_data['main syllable']['data']
    print('CC vs CV')
    t, p = students_t_test(data1, data2)
    print(f'\tt: {t}, p: {p}')
    print('CC vs CVC')
    t, p = students_t_test(data1, data3)
    print(f'\tt: {t}, p: {p}')
    print('CV vs CVC')
    t, p = students_t_test(data2, data3)
    print(f'\tt: {t}, p: {p}')
    print('CVC vs main syllable')
    t, p = students_t_test(data3, data4)
    print(f'\tt: {t}, p: {p}')
    print('CV vs main syllable')
    t, p = students_t_test(data2, data4)
    print(f'\tt: {t}, p: {p}')

    print('\n SESQUISYLLABIC')
    data5 = sesquisyllabic_data['C']['data']
    data6 = sesquisyllabic_data['main syllable']['data']
    print('C vs main syllable')
    t, p = students_t_test(data5, data6)
    print(f'\tt: {t}, p: {p}')

    print('\n MAIN SYLLABLE')
    data7 = main_syllable_data['sesquisyllabic']['data']
    data8 = main_syllable_data['disyllabic']['data']
    data9 = main_syllable_data['monosyllabic']['data']
    print('sesquisyllabic vs disyllabic')
    t, p = students_t_test(data7, data8)
    print(f'\tt: {t}, p: {p}')
    print('sesquisyllabic vs monosyllabic')
    t, p = students_t_test(data7, data9)
    print(f'\tt: {t}, p: {p}')
    print('disyllabic vs monosyllabic')
    t, p = students_t_test(data8, data9)
    print(f'\tt: {t}, p: {p}')

    print('\nsesquisyllabic C vs disyllabic CC')
    data10 = sesquisyllabic_data['C']['data']
    data11 = disyllabic_data['CC']['data']
    t, p = students_t_test(data10, data11)
    print(f'\tt: {t}, p: {p}')