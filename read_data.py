import os
import json
from bs4 import BeautifulSoup
import bs4

DORECO_DATA_DIR = 'doreco_jeha1242_extended_v1.3'

def read_xml_file(file_name):
    file = os.path.join(DORECO_DATA_DIR, file_name)
    print(f'Reading {file}...')
    with open(file, 'r') as f:
        data = f.read()
        data = BeautifulSoup(data, 'xml')

        tier_list = {}
        tiers = {}
        tier_description = data.find_all('note', {'type': 'TEMPLATE_DESC'})
        for t_d in tier_description:
            t_d.find_all('note')
            for t in t_d:
                if type(t) == bs4.element.Tag:
                    tier_id = t.attrs['xml:id']
                    tier_list[tier_id] = {}
                    for n in t.find_all('note'):
                        tier_list[tier_id][n.attrs['type']] = n.text
                        if n.attrs['type'] == 'code':
                            tiers[n.text] = []
        # for t in tier_list:
        #     print(f'\t{t}: {tier_list[t]}')
        # print(tiers)

        persons = {}
        person_list = data.find_all('listPerson')
        for pl in person_list:
            for p in pl.find_all('person'):
                person_id = p.attrs['xml:id']
                pers_name = p.find('persName')
                persons[person_id] = {'name': pers_name.text, 'tiers': []}
                for a in p.find_all('alt'):
                    persons[person_id]['tiers'].append(a['type'])

        # for p in persons:
        #     print(f'{p}: {persons[p]}')

        timeline = {}
        when_list = data.find_all('when')
        for w in when_list:
            when_id = w.attrs['xml:id']
            timeline[when_id] = {}
            for a in w.attrs:
                if a != 'xml:id':
                    timeline[when_id][a] = w.attrs[a]

        # for i, t in enumerate(timeline):
        #     print(f'{t}: {timeline[t]}')
        #     if i == 10:
        #         break

        annotation_blocks = {}
        annotation_block_list = data.find_all('annotationBlock')
        for ab in annotation_block_list:
            ab_id = ab.attrs['xml:id']
            annotation_blocks[ab_id] = {}
            for a in ab.attrs:
                if a != 'xml:id':
                    annotation_blocks[ab_id][a] = ab.attrs[a]
            seg = ab.find('seg')
            annotation_blocks[ab_id]['seg'] = seg.text
            # print(f'{ab_id}: {annotation_blocks[ab_id]}')
            annotation_blocks[ab_id]['children'] = {}
            span_groups = ab.find_all('spanGrp')
            for sg in span_groups:
                sg_type = sg['type']
                span_group = {}
                spans = sg.find_all('span')
                for s in spans:
                    span_id = s.attrs['xml:id']
                    span = {}
                    for a in s.attrs:
                        if a != 'xml:id':
                            span[a] = s.attrs[a]
                    span['text'] = s.text
                    span_group[span_id] = span
                annotation_blocks[ab_id]['children'][sg_type] = span_group

    data = {'tiers': tier_list, 'persons': persons, 'timeline': timeline, 'annotation_blocks': annotation_blocks}
    return data

def save_json(data, file_name):
    if not file_name.endswith('.json'):
        if file_name.endswith('.xml'):
            file_name = file_name.split('.')[0] + '.json'
        else:
            file_name = file_name + '.json'
    out_file = os.path.join(DORECO_DATA_DIR, file_name)
    # Save the data to a json file
    with open(out_file, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f'Data saved to {out_file}')

def out_file_name(file_name):
    return file_name.split('.')[0] + '.json'

def get_xml_files(directory=DORECO_DATA_DIR):
    files = os.listdir(directory)
    xml_files = [f for f in files if f.endswith('.xml')]
    return xml_files

def xml_to_json(directory=DORECO_DATA_DIR):
    xml_files = get_xml_files(directory)
    for xml_file in xml_files:
        data = read_xml_file(xml_file)
        save_json(data, out_file_name(xml_file))

def get_json_files(directory=DORECO_DATA_DIR):
    files = os.listdir(directory)
    json_files = [f for f in files if f.endswith('.json') if f.startswith('doreco')]
    return json_files

def read_json(file_name):
    file = os.path.join(DORECO_DATA_DIR, file_name)
    print(f'Reading {file}...')
    with open(file, 'r') as f:
        data = json.load(f)
    return data
