import scrapy
from scrapy_splash import SplashRequest
from scrapy.utils.request import request_fingerprint


class TurboSpider(scrapy.Spider):
    name = "update_main_31_07_2023"
    allowed_domains = ["turbo.az"]
    start_urls = ["https://turbo.az/autos?page=1"]
    script = '''
         function main(splash, args)
            local success, error_message
            success, error_message = pcall(function()
                splash.private_mode_enabled = false
                url = args.url
                assert(splash:go(url))
                splash:set_viewport_full()
                splash:wait(3)  -- Add a short delay to allow dynamic content to load
            end)
            if not success then
                splash:log("Error: " .. error_message)
            end

            return {
                html = splash:html()
            }
        end
             '''

    custom_settings = {
        'CONCURRENT_REQUESTS': 8,  # Increase the number of concurrent requests
        'DOWNLOAD_DELAY': 2,  # Add a download delay between requests to avoid overwhelming the server
        'AUTOTHROTTLE_ENABLED': True,  # Enable AutoThrottle to automatically adjust request rate
    }

    def parse(self, response):
        yield from self.parse_pagination(response)

    def parse_pagination(self, response):
        # Extract car links from the current page
        hrefs = response.xpath('/html/body/div[4]/div[3]/div[2]/div/div/div/div/a[1]/@href').getall()
        for href in hrefs:
            yield SplashRequest(
                url=response.urljoin(href),
                callback=self.parse_car_details,
                endpoint='execute',
                args={'lua_source': self.script, 'timeout': 60},
                headers={'X-Crawlera-Fingerprint': request_fingerprint(response.request)},
                meta={'href': href},
            )

        # Follow pagination links and recursively parse each page
        pagination_links = response.xpath('//nav[@class="pagination"]/span[@class="page"]/a/@href').getall()
        for link in pagination_links:
            yield SplashRequest(
                url=response.urljoin(link),
                callback=self.parse_pagination,
                endpoint='execute',
                args={'lua_source': self.script, 'timeout': 60},
                headers={'X-Crawlera-Fingerprint': request_fingerprint(response.request)},
            )

    def parse_car_details(self, response):
        href = response.request.meta['href']

        # Define default values in case XPath selectors don't match any elements
        default_value = None

        try:
            # Extract car details using more efficient and specific XPath expressions
            car_details = {
                'href': href,
                'id': response.xpath('//div[@class="product-actions__id"]/text()').get(),
                'phone': response.xpath(
                    '//div[@class="product-phones__list"]/a[@class="product-phones__list-i"]/text()').getall(),
                'product_title': response.xpath('//h1[@class="product-title"]/text()').get(),
                'short_description': response.xpath('//h1[@class="product-title"]/span[@class="nobr"]/text()').getall(),
                'update_date': response.xpath(
                    '(//section[contains(@class, "product-section--without-border-top")]/ul[@class="product-statistics"]/li/span[@class="product-statistics__i-text"]/text())[1]').get(),
                'views_count': response.xpath(
                    '(//section[contains(@class, "product-section--without-border-top")]/ul[@class="product-statistics"]/li/span[@class="product-statistics__i-text"]/text())[2]').get(),
                'owner_name': response.xpath(
                    '//div[contains(@class, "product-owner__info")]/div[@class="product-owner__info-name"]/text()').get(),
                'owner_region': response.xpath(
                    '//div[contains(@class, "product-owner__info")]/div[@class="product-owner__info-region"]/text()').get(),
                'city': response.xpath(
                    '/html/body/div[4]/div[3]/div[3]/div[2]/div/main/section[3]/div/div[1]/div[1]/span/text()').get(),
                'brand': response.xpath(
                    '/html/body/div[4]/div[3]/div[3]/div[2]/div/main/section[3]/div/div[1]/div[2]/span/a/text()').get(),
                'model': response.xpath(
                    '/html/body/div[4]/div[3]/div[3]/div[2]/div/main/section[3]/div/div[1]/div[3]/span/a/text()').get(),
                'year': response.xpath(
                    '/html/body/div[4]/div[3]/div[3]/div[2]/div/main/section[3]/div/div[1]/div[4]/span/a/text()').get(),
                'body_type': response.xpath(
                    '/html/body/div[4]/div[3]/div[3]/div[2]/div/main/section[3]/div/div[1]/div[5]/span/text()').get(),
                'color': response.xpath(
                    '/html/body/div[4]/div[3]/div[3]/div[2]/div/main/section[3]/div/div[1]/div[6]/span/text()').get(),
                'engine': response.xpath(
                    '/html/body/div[4]/div[3]/div[3]/div[2]/div/main/section[3]/div/div[1]/div[7]/span/text()').get(),
                'mileage': response.xpath(
                    '/html/body/div[4]/div[3]/div[3]/div[2]/div/main/section[3]/div/div[1]/div[8]/span/text()').get(),
                'transmission': response.xpath(
                    '/html/body/div[4]/div[3]/div[3]/div[2]/div/main/section[3]/div/div[2]/div[1]/span/text()').get(),
                'drive_train': response.xpath(
                    '/html/body/div[4]/div[3]/div[3]/div[2]/div/main/section[3]/div/div[2]/div[2]/span/text()').get(),
                'is_new': response.xpath(
                    '/html/body/div[4]/div[3]/div[3]/div[2]/div/main/section[3]/div/div[2]/div[3]/span/text()').get(),
                'number_of_seats': response.xpath(
                    '/html/body/div[4]/div[3]/div[3]/div[2]/div/main/section[3]/div/div[2]/div[4]/span/span/text()').get(),
                'number_of_prior_owners': response.xpath(
                    '/html/body/div[4]/div[3]/div[3]/div[2]/div/main/section[3]/div/div[2]/div[5]/span/span/text()').get(),
                'condition': response.xpath(
                    '/html/body/div[4]/div[3]/div[3]/div[2]/div/main/section[3]/div/div[2]/div[6]/span/text()').get(),
                'market': response.xpath(
                    '/html/body/div[4]/div[3]/div[3]/div[2]/div/main/section[3]/div/div[2]/div[7]/span/text()').get(),
            }

            yield car_details

        except Exception as e:
            # Log the error and yield an item with default values
            self.logger.error(f"Error parsing details for URL: {response.url}. Error: {repr(e)}")
            yield {
                'href': href,
                'id': default_value,
                'owner_phone': default_value,
                'product_title': default_value,
                'update_date': default_value,
                'views_count': default_value,
                'owner_name': default_value,
                'owner_region': default_value,
                'city': default_value,
                'brand': default_value,
                'model': default_value,
                'year': default_value,
                'body_type': default_value,
                'color': default_value,
                'engine': default_value,
                'mileage': default_value,
                'transmission': default_value,
                'drive_train': default_value,
                'is_new': default_value,
                'number_of_seats': default_value,
                'number_of_prior_owners': default_value,
                'condition': default_value,
                'market': default_value
            }
