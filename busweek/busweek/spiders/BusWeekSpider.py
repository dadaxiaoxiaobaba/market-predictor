# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 10:51:09 2016

@author: brian
"""
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from busweek.items import BusweekItem

'''
Using a CrawlSpider here so I can provide rules
It's convenient since it automatically grabs the links on the start_urls
page and will parse only the ones defined in the rule using regex
'''
class BusWeekSpider(CrawlSpider):
    name = "busweek"
    allowed_domains = ["businessweek.com"]
    start_urls = ["http://www.businessweek.com/archive/news.html"]
    
    #I only want data for 2014 since this is just an exploratory project
    #and I have little doubt there will be anything better than a coinflip
    #chance of finding something
    rules = (
                Rule(LinkExtractor(allow=('www\.businessweek\.com\/archive\/2014-\d\d\/news\.html')),
                     callback='parse_day_tabs'),)

#    def parse_item(self, response):
#        for href in response.xpath('//ul[@class = "link_list months"]/li/ul/li/a/@href'):
#            url = href.extract()
#            yield scrapy.Request(url, callback=self.parse_month_links)
'''
The spider will first dive into each month for 2014. Then it'll dive into each
tab, then it'll dive into each article and parse out the stuff I want.
'''
    #divining into the tabs that represent days, although they're tagged
    #under the class 'weeks'
    def parse_day_tabs(self, response):
        for href in response.xpath('//ul[@class="weeks"]/li/a/@href'):
            url = href.extract()
            yield scrapy.Request(url, callback=self.parse_month_links)
            
    #Getting all the links under the archive class. These will be the articles themselves
    def parse_month_links(self, response):
        for href in response.xpath('//ul[@class = "archive"]/li/h1/a/@href'):
            url = href.extract()
            yield scrapy.Request(url, callback=self.parse_articles)
    
    #Grabbing the data from the articles. This is where I could probably customize, esp
    #for the versio where I'm using just keywords. But maybe it's better to grab everything
    #once, and never have to do it again since it'll be stored in the jason        
    def parse_articles(self, response):
        item = BusweekItem();
        item['date'] = response.xpath('//meta[@name = "pub_date"]/@content').extract()
        item['body'] = response.xpath('//div[@id = "article_body"]/p/text()').extract()
        item['keywords'] = response.xpath('//meta[@name = "keywords"]/@content').extract()
        item['title'] = response.xpath('//title/text()').extract()
        yield item
