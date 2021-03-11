import re

import scrapy

from scrapy.loader import ItemLoader

from ..items import BancatransilvaniaroItem
from itemloaders.processors import TakeFirst


class BancatransilvaniaroSpider(scrapy.Spider):
	name = 'bancatransilvaniaro'
	start_urls = ['https://www.bancatransilvania.ro/bt-social-media-newsroom/?page/1/']

	def parse(self, response):
		post_links = response.xpath('//div[@class="news"]')
		for post in post_links:
			url = post.xpath('./figure/a/@href').get()
			date = post.xpath('./h6/span[@class="text-gray"]/text()').get()
			print(date)

			yield response.follow(url, self.parse_post, cb_kwargs={'date': date})

		next_page = response.xpath('//div[@class="pagination"]/ul/li/a/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//h1//text()|//div[@class="news-wrapper"]//h2//text()').get()
		description = response.xpath('//div[@class="col-xs-12 forTooltip"]//text()[normalize-space() and not(ancestor::h1 | ancestor::script)]|//div[@class="news-wrapper"]//text()[normalize-space() and not(ancestor::h2 | ancestor::script | ancestor::span[@class="com"])]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=BancatransilvaniaroItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
