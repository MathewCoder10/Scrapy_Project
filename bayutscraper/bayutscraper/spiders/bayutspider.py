import scrapy

class BayutSpider(scrapy.Spider):
    name = 'bayut'
    start_urls = ['https://www.bayut.com/to-rent/property/dubai/']

    def parse(self, response):
        base_url = 'https://www.bayut.com'

        for property_item in response.xpath('//article[contains(@class, "fbc619bc") and contains(@class, "058bd30f")]'):
            property_url = property_item.xpath('.//a/@href').get()
            full_url = property_url if property_url.startswith('http') else base_url + property_url

            if full_url:
                yield response.follow(full_url, callback=self.parse_property_details)

        next_page = response.xpath('//a[@title="Next"]/@href').get()
        if next_page:
            next_page_url = next_page if next_page.startswith('http') else base_url + next_page
            yield response.follow(next_page_url, callback=self.parse)

    def parse_property_details(self, response):

        breadcrumb_items = response.xpath('//div[@aria-label="Breadcrumb"]//span[@aria-label="Link name"]/text()').getall()
        breadcrumbs = " > ".join(breadcrumb_items[:-1]) if breadcrumb_items else None

        amenities = response.xpath('//div[contains(@class, "_91c991df")]//span[contains(@class, "_7181e5ac")]/text()').getall()
        amenities = [amenity.strip() for amenity in amenities] if amenities else None

        bedrooms = self.extract_digits(response.xpath('//span[@aria-label="Beds"]//span[contains(@class, "_140e6903")]/text()').get())
        bathrooms = self.extract_digits(response.xpath('//span[@aria-label="Baths"]//span[contains(@class, "_140e6903")]/text()').get())
        size = response.xpath('//span[@aria-label="Area"]//span[contains(@class, "_140e6903")]//span/text()').get()

        property_details = {
            'property_id': response.xpath('//span[@aria-label="Reference"]/text()').get(),
            'purpose': response.xpath('//span[@aria-label="Purpose"]/text()').get(),
            'type': response.xpath('//span[@aria-label="Type"]/text()').get(),
            'added_on': response.xpath('//span[@aria-label="Reactivated date"]/text()').get(),
            'furnishing': response.xpath('//span[@aria-label="Furnishing"]/text()').get(),
            'price': {
                'currency': response.xpath('//span[@aria-label="Currency"]/text()').get(),
                'amount': response.xpath('//span[@aria-label="Price"]/text()').get(),
            },
            'location': response.xpath('//div[@aria-label="Property header"]/text()').get(),
            'bed_bath_size': {
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'size': size
            },
            'permit_number': response.xpath('//li[div[contains(text(),"Permit Number")]]/span/text()').get(),
            'agent_name': response.xpath('//span[@aria-label="Agent name"]/text() | //span[contains(@class, "_64aa14db")]//a/text()').get(),
            'primary_image_url': response.xpath('//div[contains(@class, "345bbb7c")]//picture//img/@src').get(),
            'breadcrumbs': breadcrumbs,
            'amenities': amenities,
            'description': ' '.join(response.xpath('//div[@aria-label="Property description"]//text()').getall()).strip(),
            'property_image_urls': response.xpath('//picture//img/@src').getall(),
        }

        yield property_details

    def extract_digits(self, text):
        if text:
            digits = ''.join(filter(str.isdigit, text))
            return int(digits) if digits else None
        return None
