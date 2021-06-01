# -*- coding: utf-8 -*-
import scrapy
# Any additional imports (items, libraries,..)
from artworks.items import ArtworksItem
import logging

logger = logging.getLogger('trialScrappyLogger')


class TrialSpider(scrapy.Spider):
    name = 'trial'
    start_urls = ['http://pstrial-2019-12-16.toscrape.com/browse/summertime']  # put your start urls here

    def start_requests(self):
        url = "http://pstrial-a-2018-10-19.toscrape.com/browse/"

        yield scrapy.http.FormRequest(url=url,
                                      method='GET',
                                      callback=self.parse_browse)

    def parse(self, response):
        # Put your logic to process artworks directory
        print(response.body)
        filename = '/home/pro/Documents/quotes2.txt'
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log(f'Saved file {filename}')

    def parse_browse(self, response):
        # First, check the category summertime <div> and his subsections
        summertime_div = response.xpath('//*[@id="subcats"]/div[5]')
        for item in summertime_div.css('li'):
            url_summertime_subitems = response.urljoin(item.css('a').attrib['href']) + '?page=0'

            yield scrapy.http.FormRequest(url=url_summertime_subitems,
                                          method='GET',
                                          callback=self.parse_categorie,
                                          meta={
                                              'page': 0,
                                              'categorie': url_summertime_subitems.split('/')[-1].split('?')[0]
                                          })

        # Now, check in the in_sunsh <a> link
        in_sunsh_a = response.xpath('//*[@id="subcats"]/div[3]/a')
        if in_sunsh_a.attrib['href']:
            url_in_sunsh = response.urljoin(in_sunsh_a.attrib['href']) + '?page=0'

            yield scrapy.http.FormRequest(url=url_in_sunsh,
                                          method='GET',
                                          callback=self.parse_categorie,
                                          meta={
                                              'page': 0,
                                              'categorie': 'in_sunsh'
                                          })

    def parse_categorie(self, response):
        for item in response.xpath('//*[@id="body"]/div[2]').css('a'):
            url_item = response.urljoin(item.css('a').attrib['href'])

            yield scrapy.http.FormRequest(url=url_item,
                                          method='GET',
                                          callback=self.parse_item,
                                          meta={
                                              'page': response.meta["page"],
                                              'categorie': response.meta["categorie"]
                                          })

        if 'Next' in response.text:
            url_next_page = f'{response.url.split("=")[0]}={response.meta["page"] + 1}'

            yield scrapy.http.FormRequest(url=url_next_page,
                                          method='GET',
                                          callback=self.parse_categorie,
                                          dont_filter=True,
                                          meta={
                                              'page': response.meta["page"] + 1,
                                              'categorie': response.meta["categorie"]
                                          })

    def parse_item(self, response):
        list_artist = []
        return_object = ArtworksItem()

        if response.xpath('//*[@id="content"]/h2').get():
            if 'Artist' in response.xpath('//*[@id="content"]/h2').get():
                for artist in response.xpath('//*[@id="content"]/h2').get().split('Artist: ')[1:]:
                    list_artist.append(artist.split('<')[0].split(';')[0])

        if response.xpath('//*[@id="content"]/dl/dd[3]').get():
            if 'cm' in response.xpath('//*[@id="content"]/dl/dd[3]').get():
                size = response.xpath('//*[@id="content"]/dl/dd[3]').get().split('(')[1].split(' cm')[0]
                if len(size.split('x')) == 2:
                    height, width = size.split('x')
                else:
                    try:
                        height, width, depth = size.split('x')
                    except:
                        logger.warning("Size not found!")

                return_object["height"] = float(height.strip())
                return_object["width"] = float(width.strip())

        return_object["url"] = response.url
        return_object["artist"] = list_artist
        return_object["title"] = response.css('h1').get().split('>')[1].split('<')[0].strip()
        return_object["image"] = 'http://pstrial-a-2018-10-19.toscrape.com' + response.css('img').attrib['src']
        return_object["categories"] = [response.meta['categorie']]

        if response.xpath('//*[@id="content"]/div/p').get():
            return_object["description"] = response.xpath('//*[@id="content"]/div/p').get().split('>')[1].split('<')[0]

        yield return_object