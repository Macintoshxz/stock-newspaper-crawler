# -*- coding: utf-8 -*-
# !/usr/bin/python
################################### PART0 DESCRIPTION #################################
# Filename: class_crawl_securities_newspaper.py
# Description: Crawl data from "四大证券报精华_163,
#              http://money.163.com/special/0025262F/sidbk.html
#              And then show result of crawler in the command.
#              Four Securities newspaper:
#              [1]China Securities Journal(zgzqb)
#              [2]Securities Daily(zqrb)
#              [3]Shanghai Securities News(shzqb)
#              [4]Securities Times(zqsb)

# Author: Shuai Yuan
# E-mail: ysh329@sina.com
# Create: 2015-7-22 17:03:18
# Last:
__author__ = 'yuens'
################################### PART1 IMPORT ######################################
import urllib2
import re
from bs4 import BeautifulSoup
import logging
import time

################################### PART2 CLASS && FUNCTION ###########################
class CrawlSecuritiesNewspapers(object):
    def __init__(self):
        self.start = time.clock()

        logging.basicConfig(level = logging.DEBUG,
                  format = '%(asctime)s  %(filename)19s[line:%(lineno)3d]  %(levelname)5s  %(message)s',
                  datefmt = '%y-%m-%d %H:%M:%S',
                  filename = 'class_crawl_securities_newspaper.log',
                  filemode = 'a')
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s  %(filename)19s[line:%(lineno)3d]  %(levelname)5s  %(message)s')
        console.setFormatter(formatter)

        logging.getLogger('').addHandler(console)
        logging.info("[CrawlSecuritiesNewspapers][__init__]START.")

    def __del__(self):
        logging.info("[CrawlSecuritiesNewspapers][__del__]END.")

    def get_index_pages_links_list(self):
        logging.info("[CrawlSecuritiesNewspapers][get_index_pages_links_list]")
        pages_links_list = ["http://www.ccstock.cn/meiribidu/sidazhengquanbaotoutiao/index_p1.html", \
                           "http://www.ccstock.cn/meiribidu/sidazhengquanbaotoutiao/index_p2.html"]
        return pages_links_list



    def get_cur_page_essays_links_list(self, cur_page_link):
        logging.info("[CrawlSecuritiesNewspapers][get_cur_page_essays_links_list]")
        cur_page_essays_links_list = []

        try:
            request = urllib2.Request(cur_page_link)
            response = urllib2.urlopen(request, timeout=5)
            web_text = response.read()
            soup = BeautifulSoup(web_text)
        except:
            logging.error("[CrawlSecuritiesNewspapers][get_cur_page_essays_links_list]Retrying......")
            self.get_cur_page_essays_links_list(cur_page_link)
            return

        essays_title_with_link_label_list = soup.find("div", 'listMain').findAll('a')

        '''
        print "essays_title_with_link_label_list:", essays_title_with_link_label_list
        print "len(essays_title_with_link_label_list)", len(essays_title_with_link_label_list)
        '''
        for cur_page_essay_idx in range(len(essays_title_with_link_label_list) - 2):
            cur_labeled_essay_title_bs = essays_title_with_link_label_list[cur_page_essay_idx]
            cur_labeled_essay_title_str = str(cur_labeled_essay_title_bs)
            cur_page_essay_link = re.compile('href="(.*?)" title').findall(cur_labeled_essay_title_str)[0]
            cur_page_essays_links_list.append(cur_page_essay_link)

        return cur_page_essays_links_list



    def get_all_pages_essays_links_list(self):
        logging.info("[CrawlSecuritiesNewspapers][get_all_pages_essays_links_list]")
        all_essays_links_list = []
        all_index_pages_link_list = self.get_index_pages_links_list()
        #print "all_index_pages_link_list:", all_index_pages_link_list

        for page_idx in range(len(all_index_pages_link_list)):
            #print "page_idx:", page_idx
            cur_page_link = all_index_pages_link_list[page_idx]
            cur_page_essays_link_list = self.get_cur_page_essays_links_list(cur_page_link = cur_page_link)
            #cur_page_essalen(essays_title_with_link_label_list)ys_link_list = self.get_list_without_blank(cur_page_essays_link_list)
            '''
            print "type(cur_page_essays_link_list):", type(cur_page_essays_link_list)
            print "cur_page_essays_link_list:", cur_page_essays_link_list
            print "len(cur_page_essays_link_list):", len(cur_page_essays_link_list)
            '''
            if cur_page_essays_link_list != None:
                all_essays_links_list.append(cur_page_essays_link_list)

        all_essays_links_list = sum(all_essays_links_list, [])
        '''
        print "all_essays_links_list:", all_essays_links_list
        print "len(all_essays_links_list):", len(all_essays_links_list)
        '''
        return all_essays_links_list

    # Get information of current essay's page,
    # Information includes: newspaper_name, title, content, date, link, detailed_link
    def get_cur_essay_page_information_tuple(self, cur_page_link):
        logging.info("[CrawlSecuritiesNewspapers][get_cur_essay_page_information_tuple]Analysing cur_page_link:", cur_page_link)

        try:
            request = urllib2.Request(cur_page_link)
            response = urllib2.urlopen(request, timeout=5)
            web_text = response.read()
        except:
            logging.error("[CrawlSecuritiesNewspapers][get_cur_essay_page_information_tuple]Retrying......")
            self.get_cur_essay_page_information_tuple(cur_page_link)
            return

        soup = BeautifulSoup(web_text)

        try:
            raw_date_str = str(soup.find("div", 'sub_bt').find("span"))
            date = re.compile('更新时间： (.*) ').findall(raw_date_str)[0]
        except:
            logging.error("[CrawlSecuritiesNewspapers][get_cur_essay_page_information_tuple]Get date from another method.")
            essay_title = soup.find("div", 'bt').find('h1').string
            date = re.compile('(.*)').find(essay_title)

        news_content_bs = soup.find(id="newscontent")

        try:
            part1_zqrb_str = re.compile('【证券日报】(.*?)【中国证券报】').findall(str(news_content_bs))[0]
            part1_zqrb_titles_list = self.get_cur_newspaper_title_list(cur_newspaper_part_str = part1_zqrb_str)
            part1_zqrb_links_list = self.get_cur_newspaper_link_list(cur_newspaper_part_str = part1_zqrb_str)
            part1_zqrb_content_list =  self.get_cur_newspaper_content_list(cur_newspaper_part_str = part1_zqrb_str)
        except:
            logging.error("[CrawlSecuritiesNewspapers][get_cur_essay_page_information_tuple]Fail in attaining Part1 newspaper's data(zqrb).")
            part1_zqrb_titles_list = []
            part1_zqrb_links_list = []
            part1_zqrb_content_list = []
        finally:
            part1 = (part1_zqrb_titles_list, part1_zqrb_content_list, date, cur_page_link, part1_zqrb_links_list)
        '''
        print part1_zqrb_str
        print
        for i in part1_zqrb_titles_list: print "|"+i+'|'
        print
        for i in part1_zqrb_links_list: print "|"+i+'|'
        print
        for i in part1_zqrb_content_list: print "|"+i+'|'
        '''

        try:
            part2_zgzqb_str = re.compile('【中国证券报】(.*?)【上海证券报】').findall(str(news_content_bs))[0]
            part2_zgzqb_titles_list = self.get_cur_newspaper_title_list(cur_newspaper_part_str = part2_zgzqb_str)
            part2_zgzqb_links_list = self.get_cur_newspaper_link_list(cur_newspaper_part_str = part2_zgzqb_str)
            part2_zgzqb_content_list = self.get_cur_newspaper_content_list(cur_newspaper_part_str = part2_zgzqb_str)
        except:
            logging.error("[CrawlSecuritiesNewspapers][get_cur_essay_page_information_tuple]Fail in attaining Part2 newspaper's data(zgzqb).")
            part2_zgzqb_titles_list = []
            part2_zgzqb_links_list = []
            part2_zgzqb_content_list = []
        finally:
            part2 = (part2_zgzqb_titles_list, part2_zgzqb_content_list, date, cur_page_link, part2_zgzqb_links_list)

        try:
            part3_shzqb_str = re.compile('【上海证券报】(.*?)【证券时报】').findall(str(news_content_bs))[0]
            part3_shzqb_titles_list = self.get_cur_newspaper_title_list(cur_newspaper_part_str = part3_shzqb_str)
            part3_shzqb_links_list = self.get_cur_newspaper_link_list(cur_newspaper_part_str = part3_shzqb_str)
            part3_shzqb_content_list = self.get_cur_newspaper_content_list(cur_newspaper_part_str = part3_shzqb_str)
        except:
            logging.error("[CrawlSecuritiesNewspapers][get_cur_essay_page_information_tuple]Fail in attaining Part3 newspaper's data(shzqb).")
            part3_shzqb_titles_list = []
            part3_shzqb_links_list = []
            part3_shzqb_content_list = []
        finally:
            part3 = (part3_shzqb_titles_list, part3_shzqb_content_list, date, cur_page_link, part3_shzqb_links_list)

        try:
            part4_zqsb_str = re.compile('【证券时报】(.*</p>)').findall(str(news_content_bs))[0]
            part4_zqsb_titles_list = self.get_cur_newspaper_title_list(cur_newspaper_part_str = part4_zqsb_str)
            part4_zqsb_links_list = self.get_cur_newspaper_link_list(cur_newspaper_part_str = part4_zqsb_str)
            part4_zqsb_content_list = self.get_cur_newspaper_content_list(cur_newspaper_part_str = part4_zqsb_str)
        except:
            logging.error("[CrawlSecuritiesNewspapers][get_cur_essay_page_information_tuple]Fail in attaining Part2 newspaper's data(zqsb).")
            part4_zqsb_titles_list = []
            part4_zqsb_links_list = []
            part4_zqsb_content_list = []
        finally:
            part4 = (part4_zqsb_titles_list, part4_zqsb_content_list, date, cur_page_link, part4_zqsb_links_list)

        return part1, part2, part3, part4


    def get_cur_newspaper_title_list(self, cur_newspaper_part_str):
        logging.info("[CrawlSecuritiesNewspapers][get_cur_newspaper_title_list]")
        try:
            cur_newspaper_title_list = re.compile('<strong>(.*?)</strong>').findall(cur_newspaper_part_str)
            cur_newspaper_title_list = map(lambda title: self.get_unlabeled_list_or_string(str_or_list = title), cur_newspaper_title_list)
            cur_newspaper_title_list = map(lambda title: unicode(title, 'utf8').strip().encode('utf8'), cur_newspaper_title_list)
            cur_newspaper_title_list = self.get_list_without_blank(list_with_blank = cur_newspaper_title_list)
        except:
            logging.error("[CrawlSecuritiesNewspapers][get_cur_newspaper_title_list]Fail in attaining current (Part) newspaper title list.")
            print "cur_newspaper_str can't match title's pattern and return a blank list."
            cur_newspaper_title_list = []
        return cur_newspaper_title_list



    def get_cur_newspaper_content_list(self, cur_newspaper_part_str):
        logging.info("[CrawlSecuritiesNewspapers][get_cur_newspaper_content_list]")
        try:
            cur_newspaper_content_list = re.compile('</strong>.*?</p><p>(.*?)</p>').findall(cur_newspaper_part_str)
            cur_newspaper_content_list = map(lambda content: self.get_unlabeled_list_or_string(str_or_list = content), cur_newspaper_content_list)
            cur_newspaper_content_list = map(lambda content: unicode(content, 'utf8').strip().encode('utf8'), cur_newspaper_content_list)
            cur_newspaper_content_list = self.get_list_without_blank(list_with_blank = cur_newspaper_content_list)
        except:
            logging.error("[CrawlSecuritiesNewspapers][get_cur_newspaper_content_list]cur_newspaper_str can't match content's pattern and return a blank list.")
            cur_newspaper_content_list = []
        return cur_newspaper_content_list



    def get_cur_newspaper_link_list(self, cur_newspaper_part_str):
        logging.info("[CrawlSecuritiesNewspapers][get_cur_newspaper_link_list]")
        try:
            cur_newspaper_link_list = re.compile('href="(.*?\.html)"').findall(cur_newspaper_part_str)
        except:
            logging.error("[CrawlSecuritiesNewspapers][get_cur_newspaper_link_list]Fail in attaining current newspaper title link's list.")
            cur_newspaper_link_list = []
        return cur_newspaper_link_list



    def get_unlabeled_list_or_string(self, str_or_list):
        logging.info("[CrawlSecuritiesNewspapers][get_unlabeled_list_or_string]preparing clean label(s) of string or list variable.")

        if type(str_or_list) == str:
            unlabeled_str = re.sub('<[^>]+>','',str_or_list)
            return unlabeled_str
        elif type(str_or_list) == list:
            unlabeled_list = []
            for idx in range(len(str_or_list)):
                cur_str_in_list = str_or_list[idx]
                unlabeled_list.append(re.sub('<[^>]+>','',cur_str_in_list))
            return unlabeled_list
        else:
            print "variable of input's type is wrong and return a blank string."
            return ""



    def get_list_without_blank(self, list_with_blank):
        logging.info("[CrawlSecuritiesNewspapers][get_list_without_blank]")
        new_list = []
        for element_idx in range(len(list_with_blank)):
            cur_element = list_with_blank[element_idx]
            if cur_element == [] or cur_element == "" or cur_element == [""]:
                continue
            else:
                new_list.append(cur_element)
        return new_list



initial_link = "http://stock.jrj.com.cn/list/stockbktt.shtml"
test = CrawlSecuritiesNewspapers()

all_essays_links_list = test.get_all_pages_essays_links_list()
print "all_essays_links_list:", all_essays_links_list
print "len(all_essays_links_list):", len(all_essays_links_list)
for essay_idx in range(len(all_essays_links_list)):
    essay_link = all_essays_links_list[essay_idx]
    print "[%3d]essay_link:" % essay_idx + essay_link
    part1, part2, part3, part4 = test.get_cur_essay_page_information_tuple(cur_page_link = essay_link)
    if part1[0] == []: print "part1 data lost."
    if part2[0] == []: print "part2 data lost."
    if part3[0] == []: print "part3 data lost."
    if part4[0] == []: print "part4 data lost."


'''
part1, part2, part3, part4 = test.get_cur_essay_page_information_tuple(cur_page_link="http://www.ccstock.cn/meiribidu/sidazhengquanbaotoutiao/2015-07-17/A1437088835539.html")
print "part1:", part1
print "part2:", part2
print "part3:", part3
print "part4:", part4
'''

#test.get_cur_essay_page_information_tuple(cur_page_link="http://www.ccstock.cn/meiribidu/sidazhengquanbaotoutiao/2015-07-17/A1437088835539.html")
