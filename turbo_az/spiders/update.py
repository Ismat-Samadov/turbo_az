import time
import warnings
import hashlib
import scrapy
from scrapy_splash import SplashRequest
from twisted.internet.error import TimeoutError as GlobalTimeoutError

# Disable deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)


class TurboSpider(scrapy.Spider):
    name = "update"
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
            end)
            if not success then
                splash:log("Error: " .. error_message)
            end

            return {
                html = splash:html()
            }
        end
             '''

    def request_fingerprint(self, request):
        """Generate a fingerprint for a request."""
        fp = hashlib.sha1()
        fp.update(request.method.encode())
        fp.update(request.url.encode())
        if request.body:
            fp.update(request.body)
        return fp.hexdigest()

    def start_requests(self):
        yield SplashRequest(
            url='https://turbo.az/autos?page=1',
            callback=self.parse_pagination,
            endpoint='execute',
            args={'lua_source': self.script}
        )

    def retry_request(self, request):
        # Delay before retrying (e.g., 5 seconds)
        delay = 5
        time.sleep(delay)
        return request.copy()

    def handle_error(self, failure):
        if failure.check(GlobalTimeoutError):
            # Retry the request
            request = failure.request
            return self.retry_request(request)
        else:
            # Log other errors
            self.logger.error(repr(failure))

    def parse_pagination(self, response):
        # Extract car links from the current page
        hrefs = response.xpath('/html/body/div[4]/div[3]/div[2]/div/div/div/div/a[1]/@href').getall()
        for href in hrefs:
            req_fp = self.request_fingerprint(response.request)

            yield SplashRequest(
                url=response.urljoin(href),
                callback=self.parse_car_details,
                endpoint='execute',
                args={'lua_source': self.script, 'timeout': 60},
                headers={'X-Crawlera-Fingerprint': req_fp},
                meta={'href': href},
            )

        # Follow pagination links and recursively parse each page
        pagination_links = response.xpath('//nav[@class="pagination"]/span[@class="page"]/a/@href').getall()
        for link in pagination_links:
            req_fp = self.request_fingerprint(response.request)

            yield SplashRequest(
                url=response.urljoin(link),
                callback=self.parse_pagination,
                endpoint='execute',
                args={'lua_source': self.script, 'timeout': 60},
                headers={'X-Crawlera-Fingerprint': req_fp},
            )

    def parse_car_details(self, response):
        href = response.request.meta['href']

        # Define default values in case XPath selectors don't match any elements
        default_value = None

        try:
            id = response.xpath('//div[@class="product-actions__id"]/text()').get()
            phone = response.xpath(
                '//div[@class="product-phones__list"]/a[@class="product-phones__list-i"]/text()').getall()
            product_title = response.xpath('//h1[@class="product-title"]/text()').get()
            short_description = response.xpath('//h1[@class="product-title"]/span[@class="nobr"]/text()').getall()
            update_date = response.xpath(
                '(//section[contains(@class, "product-section--without-border-top")]/ul[@class="product-statistics"]/li/span[@class="product-statistics__i-text"]/text())[1]').get()
            views_count = response.xpath(
                '(//section[contains(@class, "product-section--without-border-top")]/ul[@class="product-statistics"]/li/span[@class="product-statistics__i-text"]/text())[2]').get()
            owner_name = response.xpath(
                '//div[contains(@class, "product-owner__info")]/div[@class="product-owner__info-name"]/text()').get()
            owner_region = response.xpath(
                '//div[contains(@class, "product-owner__info")]/div[@class="product-owner__info-region"]/text()').get()
            city = response.xpath(
                '/html/body/div[4]/div[3]/div[3]/div[2]/div/main/section[3]/div/div[1]/div[1]/span/text()').get()
            brand = response.xpath(
                '/html/body/div[4]/div[3]/div[3]/div[2]/div/main/section[3]/div/div[1]/div[2]/span/a/text()').get()
            model = response.xpath(
                '/html/body/div[4]/div[3]/div[3]/div[2]/div/main/section[3]/div/div[1]/div[3]/span/a/text()').get()
            year = response.xpath(
                '/html/body/div[4]/div[3]/div[3]/div[2]/div/main/section[3]/div/div[1]/div[4]/span/a/text()').get()
            body_type = response.xpath(
                '/html/body/div[4]/div[3]/div[3]/div[2]/div/main/section[3]/div/div[1]/div[5]/span/text()').get()
            color = response.xpath(
                '/html/body/div[4]/div[3]/div[3]/div[2]/div/main/section[3]/div/div[1]/div[6]/span/text()').get()
            engine = response.xpath(
                '/html/body/div[4]/div[3]/div[3]/div[2]/div/main/section[3]/div/div[1]/div[7]/span/text()').get()
            mileage = response.xpath(
                '/html/body/div[4]/div[3]/div[3]/div[2]/div/main/section[3]/div/div[1]/div[8]/span/text()').get()
            transmission = response.xpath(
                '/html/body/div[4]/div[3]/div[3]/div[2]/div/main/section[3]/div/div[2]/div[1]/span/text()').get()
            drive_train = response.xpath(
                '/html/body/div[4]/div[3]/div[3]/div[2]/div/main/section[3]/div/div[2]/div[2]/span/text()').get()
            is_new = response.xpath(
                '/html/body/div[4]/div[3]/div[3]/div[2]/div/main/section[3]/div/div[2]/div[3]/span/text()').get()
            number_of_seats = response.xpath(
                '/html/body/div[4]/div[3]/div[3]/div[2]/div/main/section[3]/div/div[2]/div[4]/span/span/text()').get()
            number_of_prior_owners = response.xpath(
                '/html/body/div[4]/div[3]/div[3]/div[2]/div/main/section[3]/div/div[2]/div[5]/span/span/text()').get()
            condition = response.xpath(
                '/html/body/div[4]/div[3]/div[3]/div[2]/div/main/section[3]/div/div[2]/div[6]/span/text()').get()
            market = response.xpath(
                '/html/body/div[4]/div[3]/div[3]/div[2]/div/main/section[3]/div/div[2]/div[7]/span/text()').get()
            yield {
                'href': href,
                'id': id,
                'short_description': short_description,
                'product_title': product_title,
                'update_date': update_date,
                'views_count': views_count,
                'owner_phone': phone,
                'owner_name': owner_name,
                'owner_region': owner_region,
                'city': city,
                'brand': brand,
                'model': model,
                'year': year,
                'body_type': body_type,
                'color': color,
                'engine': engine,
                'mileage': mileage,
                'transmission': transmission,
                'drive_train': drive_train,
                'is_new': is_new,
                'number_of_seats': number_of_seats,
                'number_of_prior_owners': number_of_prior_owners,
                'condition': condition,
                'market': market
            }

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
