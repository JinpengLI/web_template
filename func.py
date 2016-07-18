# -*- coding: utf-8 -*-
"""
Created on Sat Jan 18 12:52:17 2014

@author: jinpeng
"""
import re
import os

def read_url(url):
    return open(url, "r").read()

class KeyWordsPage(object):
    def __init__(self, page_source, key_words):
        self.page_source = page_source
        self.key_words = key_words


class AroundContent(object):
    def __init__(self, left, right):
        self.left = left
        self.right = right


def get_around_one_keyword_pattern(one_page_source,
                                   key_word,
                                   min_around_len):
    """
    Example
    -------
    one_page_source = "1111ddd2222edde3333"
    min_around_len = 2
    key_word = "dd"
    get_around_one_keyword_pattern(one_page_source, key_word, min_around_len)
    """
    around_contents = []
    pattern = "(.{%d})%s(.{%d})" % (min_around_len,
                                    re.escape(key_word),
                                    min_around_len)
    res_set = re.findall(pattern, one_page_source, re.DOTALL)
    for res in res_set:
        left = res[0]
        right = res[1]
        around_content = AroundContent(left, right)
        around_contents.append(around_content)
    return around_contents


def get_around_keyword_pattern(one_page_source,
                               key_words,
                               min_around_len):
    """
    Example
    -------
    one_page_source = "1111ddd2222eeee3333"
    min_around_len = 2
    key_words = ["11", "22", "33"]
    around_contents_2d = get_around_keyword_pattern(one_page_source,
                                                    key_words,
                                                    min_around_len)
    """
    around_contents_2d = []
    for key_word in key_words:
        around_contents = get_around_one_keyword_pattern(one_page_source,
                                                         key_word,
                                                         min_around_len)
        around_contents_2d.append(around_contents)
    return around_contents_2d


def get_keywords_from_around_contents(one_page_source, around_contents):
    """
    Example
    -------
    one_page_source = "1111ddd2222eeee3333"
    min_around_len = 2
    key_words = ["ddd", "eeee"]
    for around_len in xrange(10):
        ac_2d = get_around_keyword_pattern(one_page_source,
                                           key_words,
                                           around_len)
        tmp_ac = [i[0] for i in ac_2d]
        key_words2 = get_keywords_from_around_contents(one_page_source, tmp_ac)
        print "====================="
        print "around_len=", around_len
        print "key_words=", key_words
        print "key_words2=", key_words2
        if key_words2 == key_words:
            break
    """
    key_words = []
    for around_content in around_contents:
        if around_content != "":
            pattern = "%s(.*)%s" % (re.escape(around_content.left),
                                            re.escape(around_content.right))
            # print "pattern=", pattern
            res = re.findall(pattern, one_page_source, re.DOTALL)
            if not res:
                key_words.append("")
            else:
                key_words.append(res[0])
        else:
            key_words.append("")
    return key_words


def sub_train_key_word_partterns(key_words_pages, i_key_word):
    """
    Example
    -------
    key_words_pages = []
    page_source = "1111 ddd 2222 eeee 3333"
    key_words = ["ddd", "eeee"]
    key_words_pages.append(KeyWordsPage(page_source, key_words))
    page_source = "1111 ii 2222 ggg 3333"
    key_words = ["ii", "ggg"]
    key_words_pages.append(KeyWordsPage(page_source, key_words))
    page_source = "1111 kkk 2222 iii 3333"
    key_words = ["kkk", "iii"]
    key_words_pages.append(KeyWordsPage(page_source, key_words))
    res0 = sub_train_key_word_partterns(key_words_pages, 0)
    res1 = sub_train_key_word_partterns(key_words_pages, 1)
    """
    first_key_words_page = key_words_pages[0]
    around_content = None
    max_min_around_len = min([30,
                              int(len(first_key_words_page.page_source) / 4)])
    for min_around_len in xrange(5, max_min_around_len):
        ac_list = get_around_one_keyword_pattern(
                             first_key_words_page.page_source,
                             first_key_words_page.key_words[i_key_word],
                             min_around_len)
        for ac in ac_list:
            is_fit_for_all_pages = True
            for key_words_page in key_words_pages:
                one_page_source = key_words_page.page_source
                key_word = key_words_page.key_words[i_key_word]
                key_words2 = get_keywords_from_around_contents(one_page_source,
                                                               [ac])
                if key_word != key_words2[0]:
                    is_fit_for_all_pages = False
                    break
            if is_fit_for_all_pages:
                around_content = ac
                return around_content
    return around_content


def train_key_word_partterns(key_words_pages):
    """
    Example
    -------
    key_words_pages = []
    page_source = "1111 ddd 2222 eeee 3333"
    key_words = ["ddd", "eeee"]
    key_words_pages.append(KeyWordsPage(page_source, key_words))
    page_source = "1111 ii 2222 ggg 3333"
    key_words = ["ii", "ggg"]
    key_words_pages.append(KeyWordsPage(page_source, key_words))
    page_source = "1111 kkk 2222 iii 3333"
    key_words = ["kkk", "iii"]
    key_words_pages.append(KeyWordsPage(page_source, key_words))
    around_contents = train_key_word_partterns(key_words_pages)
    """
    num_key_words = len(key_words_pages[0].key_words)
    for key_words_page in key_words_pages:
        if num_key_words != len(key_words_page.key_words):
            raise ValueError("Not same number of key words")
    around_contents = []
    for i in xrange(num_key_words):
        print "start to analyse ", i, " keyword..."
        around_content = sub_train_key_word_partterns(key_words_pages, i)
        if around_content:
            around_contents.append(around_content)
        else:
            around_contents.append("")
    return around_contents


if __name__ == "__main__":

    cur_dir = os.path.dirname(os.path.realpath(__file__))
    path_product1 = os.path.join(cur_dir, "sample_page", "product1.html")
    path_product2 = os.path.join(cur_dir, "sample_page", "product2.html")
    path_product3 = os.path.join(cur_dir, "sample_page", "product3.html")

    text1 = read_url(path_product1)
    text2 = read_url(path_product2)
    text3 = read_url(path_product3)

    ## define your cralwer by two pages
    key_words_pages = []
    page_source = text1
    key_words = ["115", "15", "46"]
    key_words_pages.append(KeyWordsPage(page_source, key_words))
    page_source = text2
    key_words = ["32", "55", "17"]
    key_words_pages.append(KeyWordsPage(page_source, key_words))
    acs = train_key_word_partterns(key_words_pages)
    ## end of defining the crawler

    ## you will get key words ['88', '7', '8']
    print get_keywords_from_around_contents(text3, acs)
    
