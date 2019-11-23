#!/usr/bin/env python
# -*- coding:utf-8 -*-


import Levenshtein
from conf.search_params_define import SIMILARITY_THRESHOLD

def get_similar_bool(a: str, b: str) -> bool:
    if not a or not b:
        return False
    if Levenshtein.ratio(a, b) > SIMILARITY_THRESHOLD:
        return True
    else:
        return False


if __name__ == '__main__':
    res = get_similar_bool('qtalk后端裙','qtalk后端群')
    print(type(res))
# 根据网上的调研 Levenshtein 的效果更好
# from difflib import SequenceMatcher

# def get_similar(a, b):
#     return SequenceMatcher(None, a, b).ratio()


