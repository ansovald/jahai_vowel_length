import matplotlib.pyplot as plt
import numpy as np

def xsampa_to_unicode(xsampa):
    xsampa = xsampa.replace('1', 'ɨ')
    xsampa = xsampa.replace('a~', 'ã')
    xsampa = xsampa.replace('a', 'a')
    xsampa = xsampa.replace('E~', 'ẽ')
    xsampa = xsampa.replace('E', 'ɛ')
    xsampa = xsampa.replace('i~', 'ĩ')
    xsampa = xsampa.replace('i', 'i')
    xsampa = xsampa.replace('O', 'ɔ')
    xsampa = xsampa.replace('o', 'o')
    xsampa = xsampa.replace('u~', 'ũ')
    xsampa = xsampa.replace('u', 'u')
    xsampa = xsampa.replace('@~', 'õ')
    xsampa = xsampa.replace('@', 'ə')
    return xsampa

def plot_vowel_durations(vowel_durations, name, axis_label, save_format='png', figsize=(6.4,4.8)):
    x_vowels = list(vowel_durations.keys())
    # replace the xsampa vowels with unicode characters
    u_vowels = [xsampa_to_unicode(v) for v in x_vowels]

    # Make a boxplot with the vowel durations
    plt.figure(figsize=figsize)
    x = np.arange(len(vowel_durations))
    y = [vowel_durations[v]['data'] for v in vowel_durations if v]
    plt.boxplot(y, showfliers=False, showmeans=True)
    plt.xticks(x+1, u_vowels)

    # Label the medians
    for i in range(len(x)):
        plt.text(x[i]+1, vowel_durations[x_vowels[i]]['median'], f'{int(vowel_durations[x_vowels[i]]["median"])}', ha='center', va='bottom', fontsize='small')
    # Label the means, round to one digit
    for i in range(len(x)):
        plt.text(x[i]+1, vowel_durations[x_vowels[i]]['mean'], f'{np.round(vowel_durations[x_vowels[i]]["mean"], 1)}', ha='center', va='bottom', fontsize='small', color='tab:red')

    # Add a line for the total median
    plt.axhline(vowel_durations['all']['median'], color='g', linestyle='--')
    # Label it on the right margin
    plt.text(len(x)+1, vowel_durations['all']['median'], f'{int(vowel_durations["all"]["median"])}', ha='right', va='center', color='g')

    plt.ylabel(f'vowel durations in ms\n{axis_label}')
    plt.savefig(f'fig/{name}_duration.{save_format}', format=save_format)
    plt.clf()

    # Remove 'all' from u_vowels and vowel_durations
    u_vowels = u_vowels[:-1]
    total_vowel_count = vowel_durations['all']['count']
    vowel_durations = {v: vowel_durations[v] for v in vowel_durations if v != 'all'}

    # Plot the number of vowels
    x = np.arange(len(vowel_durations))
    y = [vowel_durations[v]['count'] for v in vowel_durations]
    plt.bar(x, y)
    plt.xticks(x, u_vowels)
    # Label the bars with their values
    for i in range(len(x)):
        plt.text(x[i], y[i], f'{y[i]}', ha='center', va='bottom')
    plt.ylabel(f'vowel occurrence count\n{axis_label} (total: {total_vowel_count})')
    plt.savefig(f'fig/{name}_occurrences.{save_format}', format=save_format)

    plt.close()

def plot_data_row(data, name, plot_label, save_format='png'):
    for key in data:
        print(f'{key}: {data[key]}')
    x_ticks = list(data.keys())
    x = np.arange(len(x_ticks))
    plt.figure(figsize=(6.4,4.8))
    y = [data[key]['data'] for key in data]
    plt.boxplot(y, showfliers=False, showmeans=True)
    # label the medians
    for i in range(len(x)):
        plt.text(x[i]+1, data[x_ticks[i]]['median'], f'{int(data[x_ticks[i]]["median"])}', ha='center', va='bottom', fontsize='small')
    # label the means, round to one digit
    for i in range(len(x)):
        plt.text(x[i]+1, data[x_ticks[i]]['mean'], f'{np.round(data[x_ticks[i]]["mean"], 1)}', ha='center', va='bottom', fontsize='small', color='tab:red')
    plt.xticks(x+1, x_ticks)
    plt.ylabel(plot_label)
    plt.savefig(f'fig/{name}_duration.{save_format}', format=save_format)
    plt.close()

    # plot the occurrence counts
    print(data)
    counts = {}
    for key in data:
        if key == 'main syllable':
            continue
        counts[key] = len(data[key]['data'])
    total_count = sum(counts.values())
    print(counts, total_count)

    plt.figure(figsize=(6.4,4.8))
    x = np.arange(len(counts))
    plt.bar(x, counts.values())
    plt.xticks(x, counts.keys())
    # label the bars with their values
    for i in range(len(x)):
        plt.text(x[i], counts[x_ticks[i]], f'{counts[x_ticks[i]]}', ha='center', va='bottom')
    plt.ylabel(f'distribution of minor syllable types in disyllabic words (total: {total_count})')
    plt.savefig(f'fig/{name}_occurrences.{save_format}', format=save_format)
    plt.close()
