'''
wikipediaParser module

returns JSON structured object of categories and sub-categories
'''

from bs4 import BeautifulSoup
import requests as r
import pprint as pp
import pandas as pd

import os, sys
import time
import json

class WikipediaParser():
    ''' Class for extracting wikipedia category trees, implements a depth-first search tree'''
    
    
    def __init__(self):
        self.base_url = 'https://en.m.wikipedia.org'
        

    def getSoup(self, category):
        ''' Hits web endpoint, returns soup of page '''

        time.sleep(0.5)
        resp = r.get(self.base_url + category)

        if resp.status_code == 200:
            return BeautifulSoup(resp.text)

        else:
            print(resp.status_code)
            return {}
    

    def parseSubcategory(self, section, parent):
        ''' Parses a subcategory entry'''

        node_title = section.find("a").get_text()
        node_href = section.find("a").get("href")
        node = node_href.split("/wiki/Category:")[1]

        links = section.find("span", {"dir" : "ltr"}).get("title").replace('and ','').split('Contains ')[1].split(', ')
        n_subcategories = [x for x in links if 'subcategories' in x]
        n_pages = [x for x in links if 'pages' in x]
        n_files = [x for x in links if 'files' in x]

        return {
            "node": node,
            "parent": parent,
            "node_href": node_href,
            "node_title": node_title,

            "links": links,
            "n_files": n_files,
            "n_pages": n_pages,
            "n_subcategories": n_subcategories
        }


    def parseSoup(self, soup, parent, parsed_page = [], max_depth = 0):
        print(parent)
        print(len(parsed_page))

        # depth-first search tree across sub-categories
        for subcategory in soup.find_all("div", {"class" : "CategoryTreeSection"}):


            parsed_subcategory = self.parseSubcategory(subcategory, parent)
            parsed_page.append(parsed_subcategory)


            # make recursive call, and extract subcategory
            if len(parsed_subcategory['n_subcategories']) > 0 and int(parsed_subcategory['n_subcategories'][0][0]) > 0 and max_depth < 3:
                max_depth += 1

                sub_soup = self.getSoup(
                    parsed_subcategory['node_href']
                )

                parsed_page+= self.parseSoup(
                    sub_soup,
                    parsed_subcategory['node'],
                    parsed_page,
                    max_depth
                )
            

        max_depth = 0
        return parsed_page
