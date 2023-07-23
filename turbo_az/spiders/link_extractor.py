# import scrapy
# from scrapy_splash import SplashRequest
#
#
# class LinkExtractorSpider(scrapy.Spider):
#     name = "link_extractor"
#     allowed_domains = ["turbo.az"]
#     start_urls = ["https://turbo.az/autos?page=1"]
#     script = '''
#         function main(splash,args)
#           splash.private_mode_enabled=false
#           url=args.url
#           assert(splash:go(url))
#           splash:set_viewport_full()
#           return {
#             png=splash:png(),
#             html=splash:html()
#             }
#         end
#     '''
#
#     def start_requests(self):
#         yield SplashRequest(url='https://turbo.az/autos?page=1',
#                             callback=self.parse,
#                             endpoint='execute',
#                             args={'lua_source': self.script}
#                             )
#
#     def parse(self, response):
#         hrefs = response.xpath('/html/body/div[4]/div[3]/div[2]/div/div/div/div/a[1]/@href').getall()
#         for href in hrefs:
#             yield {
#                 "href": href
#             }
import scrapy
from scrapy_splash import SplashRequest


class LinkExtractorSpider(scrapy.Spider):
    name = "link_extractor"
    allowed_domains = ["turbo.az"]
    start_urls = ["https://turbo.az/autos?page=1"]
    script = '''
        function main(splash, args)
            splash.private_mode_enabled = false
            url = args.url
            assert(splash:go(url))
            splash:set_viewport_full()
            return {
                png = splash:png(),
                html = splash:html()
            }
        end   
    '''

    def start_requests(self):
        yield SplashRequest(
            url='https://turbo.az/autos?page=1',
            callback=self.parse,
            endpoint='execute',
            args={'lua_source': self.script}
        )

    def parse(self, response):
        # Extract car links from the current page
        hrefs = response.xpath('/html/body/div[4]/div[3]/div[2]/div/div/div/div/a[1]/@href').getall()
        for href in hrefs:
            yield {
                "href": href
            }

        # Follow pagination links and recursively parse each page
        pagination_links = response.xpath('//nav[@class="pagination"]/span[@class="page"]/a/@href').getall()
        for link in pagination_links:
            yield SplashRequest(
                url=response.urljoin(link),
                callback=self.parse,
                endpoint='execute',
                args={'lua_source': self.script}
            )
