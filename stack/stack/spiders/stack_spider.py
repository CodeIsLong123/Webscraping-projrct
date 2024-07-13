import scrapy






### Just a small script to get a hang of scrapy, this script scrapes the questions from the stackoverflow page
### Next i want to make a script that scrapes medium articles and integrate them into my notion page
### For this i need to use Selenium as well, to log into my medium account and scrape the articles

class QuestionsScraperSpider(scrapy.Spider):
    name = 'stack'
    start_urls = ['https://stackoverflow.com/questions?tab=unanswered&page=1']
    host_url = 'https://stackoverflow.com'
    
    
    
    ### scrapes a single page, but can be modified to scrape multiple pages 
    

    def parse(self, response):
        selector = '#questions .s-post-summary'
        for stackoverflow_item in response.css(selector):
            name = '.s-post-summary--content-title a::text'
            url = '.s-post-summary--content-title a::attr(href)'
            
            yield {
                'name': stackoverflow_item.css(name).extract_first(),
                'url': self.host_url+stackoverflow_item.css(url).extract_first(),
                }
            
            
    