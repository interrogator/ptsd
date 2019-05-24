#!/usr/bin/env python3

"""
Script to make a plain text corpus of PTSD narratives,
with a little bit of metadata.
"""

import os
import time
import requests
from bs4 import BeautifulSoup
from pycookiecheat import chrome_cookies


MONTHS = dict(january=1,
              february=2,
              march=3,
              april=4,
              may=5,
              june=6,
              july=7,
              august=8,
              september=9,
              october=10,
              november=11,
              december=12)

def convert_date(original):
    """
    May 10, 2018 --> 2018-05-10
    """
    month, day, year = original.strip().replace(',', '').split()
    month = str(MONTHS[month.lower()]).zfill(2)
    return f'{year}-{month}-{day}'

def make_text(idx, root, story):
    """
    Get page containing story, make corpus file contents and retur as string
    """
    # title as it appears to reader
    title = story.a.text
    # full url for this story
    url = root + story.a['href']
    # get the html at this link
    cookies = chrome_cookies(url)
    response = requests.get(url, cookies=cookies)
    soup = BeautifulSoup(response.text, 'lxml')
    # get the box containing the story
    text = soup.find('div', {'class': 'content'})
    # extract the text from each <p>, preserving paragraph boundaries
    paras = text.find_all('p')
    full = '\n\n'.join([p.text.strip() for p in paras if p.text.strip()])
    date = convert_date(soup.find('div', {'class': 'byline'}).text.strip())
    # make metadata string, so we can search by title or date or whatever
    meta = f'<metadata url="{url}" date="{date}" title="{title}", idx="{idx}">'
    return meta + '\n' + title + '\n\n' + full


def get_last_page(base):
    """
    Get total number of pages in forum as integer
    """
    url = base + '1'
    cookies = chrome_cookies(url)
    r = requests.get(url, cookies=cookies)
    soup = BeautifulSoup(r.text, 'lxml')
    ul = soup.find('ul', {'class': 'pagination'})
    last_page = ul.find_all('li')[-2].text
    print(f'Number of pages found: {last_page}')
    return int(last_page.strip())

# urls
root = 'http://www.snapnetwork.org'
base = root + '/member_stories?page='
# how many pages does the site have in total? ~37?
num_pages = get_last_page(base)
# a sequential name for each story
story_id = 1
# where we will keep our data, in ./texts
os.makedirs('texts', exist_ok=True)

# iterate over each page, with each page listing 10 stories
for page in range(1, num_pages + 1):
    # get this particular page number, and make it into soup
    url = base + str(page)
    cookies = chrome_cookies(url)
    response = requests.get(url, cookies=cookies)
    soup = BeautifulSoup(response.text, 'lxml')
    # get the boxes containing links to each story
    stories = soup.find_all('div', {'class': 'page-excerpt'})
    # iterate over each story box, open the linked page and make .txt data
    for i, story in enumerate(stories, start=1):
        # make a unique id for each story, also used as filename
        idx = str(story_id).zfill(3)
        # progress of this script :P
        print(f'Doing {story_id}/{num_pages * 10}: {story.a.text}')
        # the hard work --- turn the html into good .txt
        formatted = make_text(idx, root, story)
        # save our result to disk
        with open(f'texts/{idx}.txt', 'w') as fo:
            fo.write(formatted.strip() + '\n')
        # increment our counter for the next story
        story_id += 1
    # be a little bit kind to our host
    time.sleep(10)

