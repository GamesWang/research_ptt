#!/bin/usr/env python
#-*- coding:utf-8 -*-

from module_config import *
from os import path
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import jieba
import numpy as np
from PIL import Image
from collections import Counter
import functools
from util import *

def loadTotalStatistic(inputFileName):
    loadStopWords()
    # Read the whole text.
    text_tuple_list = []
    with open(inputFileName, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            split_line = line.strip().split(' ')
            if len(split_line) < 2:
                print('Length < 2: ' + split_line[0])
                continue
            key = split_line[0]
            value = split_line[1]
            if key not in stopwords_list:
                text_tuple_list.append((key, int(float(value))))
    return text_tuple_list

def ouput_word_cloud_by_frequency(frequency_list=None, outputFileName='word_cloud.png', maskFile=None, font_path='../resource/fonts/simhei.ttf', background_color='white', max_words=2000):
    pic_mask = np.array(Image.open(maskFile))
    wc = WordCloud(font_path=font_path, background_color=background_color, max_words=max_words, mask=pic_mask)
    wc.fit_words(frequency_list)
    wc.to_file(outputFileName)

def ouput_word_cloud_by_text(text=None, outputFileName='word_cloud.png', maskFile=None, font_path='../resource/fonts/simhei.ttf', background_color='white', max_words=2000):
    pic_mask = np.array(Image.open(maskFile))
    wc = WordCloud(font_path=font_path, background_color=background_color, max_words=max_words, mask=pic_mask)
    wc.generate(text)
    wc.to_file(outputFileName)


# worcloud setting
# class wordcloud.WordCloud(font_path=None, 
#                             width=400, 
#                             height=200, 
#                             margin=5, 
#                             ranks_only=False, 
#                             prefer_horizontal=0.9,
#                             mask=None, 
#                             scale=1, 
#                             color_func=<function random_color_func at 0x2b8b422a31b8>, 
#                             max_words=200, 
#                             stopwords=None,
#                             random_state=None, 
#                             background_color='black', 
#                             max_font_size=None)

def main():

    MAX_WORDS = 1500
    ouput_word_cloud_by_frequency(loadTotalStatistic('./outputs/gossip_top_occurence.txt'), maskFile='../resource/pic/taiwan.jpg',max_words=MAX_WORDS, outputFileName='gossip_word_taiwan_'+str(MAX_WORDS) + '.png')
    # ouput_word_cloud_by_text(maskFile=,outputFileName=,text=)


if __name__ == '__main__':
    main()
    exit(0)