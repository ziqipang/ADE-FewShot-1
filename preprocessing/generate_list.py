import json
import numpy as np
import argparse
import os
import random
import math


def base_generation(args):
    origin_path = os.path.join(args.root_dataset, args.origin_dataset)
    base_set_path = os.path.join(origin_path, 'base_set.json')
    img_path_path = os.path.join(origin_path, 'img_path.json')
    img_path2size_path = os.path.join(origin_path, 'img_path2size.json')
    base_list_path = os.path.join(origin_path, 'base_list.json')
    f = open(base_set_path, 'r')
    base_set = json.load(f)
    f.close()
    f = open(img_path_path, 'r')
    img_path = json.load(f)
    f.close()
    f = open(img_path2size_path, 'r')
    img_path2size = json.load(f)
    f.close()
    f = open(base_list_path, 'r')
    base_list = json.load(f)
    f.close()

    # initialize the sample list
    sample_list_train = [dict() for i in range(len(img_path))]
    for i in range(len(img_path)):
        sample_list_train[i]['fpath_img'] = img_path[i]
        sample_list_train[i]['height'], sample_list_train[i]['width'] = \
            img_path2size[img_path[i]]
        sample_list_train[i]['index'] = i
        sample_list_train[i]['anchors'] = []
    sample_list_val = [dict() for i in range(len(img_path))]
    for i in range(len(img_path)):
        sample_list_val[i]['fpath_img'] = img_path[i]
        sample_list_val[i]['height'], sample_list_val[i]['width'] = \
            img_path2size[img_path[i]]
        sample_list_val[i]['index'] = i
        sample_list_val[i]['anchors'] = []

    # get the category information to split train and val
    all_list = [[] for category in base_list]
    for obj in base_set:
        img_index = int(obj["img"])
        category = base_list.index(int(obj["obj"]))
        box = obj["box"]
        annotation = {"img": img_index, "obj": category, "box": box}
        all_list[category].append(annotation)

    random.seed(73)
    for category in range(len(base_list)):
        if all_list[category] is []:
            continue
        random.shuffle(all_list[category])

    # split into train and val
    for i in range(len(base_list)):
        length = len(all_list[i])
        if length == 0:
            continue
        for j in range(0, math.ceil(5 * length / 6)):
            img_index = all_list[i][j]['img']
            sample_list_train[img_index]['anchors'].append({'anchor': all_list[i][j]['box'], 'label': i})

        for j in range(math.ceil(5 * length / 6), length):
            img_index = all_list[i][j]['img']
            sample_list_val[img_index]['anchors'].append({'anchor': all_list[i][j]['box'], 'label': i})

    output_path = os.path.join(args.root_dataset, args.output)
    output_train = os.path.join(output_path, 'base_img_train.json')
    f = open(output_train, 'w')
    json.dump(sample_list_train, f)
    f.close()
    output_val = os.path.join(output_path, 'base_img_val.json')
    f = open(output_val, 'w')
    json.dump(sample_list_val, f)
    f.close()


def novel_generation(args):
    origin_path = os.path.join(args.root_dataset, args.origin_dataset)
    novel_set_path = os.path.join(origin_path, 'novel_set.json')
    img_path_path = os.path.join(origin_path, 'img_path.json')
    img_path2size_path = os.path.join(origin_path, 'img_path2size.json')
    novel_list_path = os.path.join(origin_path, 'novel_list.json')
    f = open(novel_set_path, 'r')
    novel_set = json.load(f)
    f.close()
    f = open(img_path_path, 'r')
    img_path = json.load(f)
    f.close()
    f = open(img_path2size_path, 'r')
    img_path2size = json.load(f)
    f.close()
    f = open(novel_list_path, 'r')
    novel_list = json.load(f)
    f.close()

    # initialize the sample list
    sample_list_train = [dict() for i in range(len(img_path))]
    for i in range(len(img_path)):
        sample_list_train[i]['fpath_img'] = img_path[i]
        sample_list_train[i]['height'], sample_list_train[i]['width'] = \
            img_path2size[img_path[i]]
        sample_list_train[i]['index'] = i
        sample_list_train[i]['anchors'] = []
    sample_list_val = [dict() for i in range(len(img_path))]
    for i in range(len(img_path)):
        sample_list_val[i]['fpath_img'] = img_path[i]
        sample_list_val[i]['height'], sample_list_val[i]['width'] = \
            img_path2size[img_path[i]]
        sample_list_val[i]['index'] = i
        sample_list_val[i]['anchors'] = []

    # get the category information to split train and val
    all_list = [[] for category in novel_list]
    for obj in novel_set:
        img_index = int(obj["img"])
        category = novel_list.index(int(obj["obj"]))
        box = obj["box"]
        annotation = {"img": img_index, "obj": category, "box": box}
        all_list[category].append(annotation)

    random.seed(73)
    for category in range(len(novel_list)):
        if all_list[category] == []:
            continue
        random.shuffle(all_list[category])

    # split into train and val
    for i in range(len(novel_list)):
        length = len(all_list[i])
        if length == 0:
            continue
        for j in range(0, args.shot):
            img_index = all_list[i][j]['img']
            sample_list_train[img_index]['anchors'].append({'anchor': all_list[i][j]['box'], 'cls_label': i})

        for j in range(args.shot, length):
            img_index = all_list[i][j]['img']
            sample_list_val[img_index]['anchors'].append({'anchor': all_list[i][j]['box'], 'cls_label': i})

    output_path = os.path.join(args.root_dataset, args.output)
    output_train = os.path.join(output_path, 'novel_img_train.json')
    f = open(output_train, 'w')
    json.dump(sample_list_train, f)
    f.close()
    output_val = os.path.join(output_path, 'novel_img_val.json')
    f = open(output_val, 'w')
    json.dump(sample_list_val, f)
    f.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-root_dataset', default='../data/ADE')
    parser.add_argument('-origin_dataset', default='ADE_Origin/')
    parser.add_argument('-part', default='Base')
    parser.add_argument('-shot', default=5)
    parser.add_argument('-img_size', default='img_path2size.json')

    args = parser.parse_args()
    setattr(args, 'output', 'ADE_' + args.part)
    if args.part == 'Base':
        base_generation(args)
    elif args.part == 'Novel':
        novel_generation(args)
