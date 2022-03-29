import scrapy
import re
from scrapy.http import HtmlResponse
import json
from instagramparser.items import InstagramparserItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    inst_login = 'Onliskill_udm'
    inst_pwd = '#PWD_INSTAGRAM_BROWSER:10:1648392075:AUBQABtefr2ZVlLc0/yxBnVw9Glsofk9ShF8E2S2SL0OB4gYujOha+qIQicrECEhUWx3kG6gX+Lvhsx4jFSbN6Vnl6zyJa0jFyBEu2EyNnSNm7X01TrWW/vPC/VX5mUqFoomBIByAc5m8jIfWCdH'
    parse_user = 'techskills_2022'

    def parse(self, response: HtmlResponse):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.login,
            formdata={'username': self.inst_login,
                      'enc_password': self.inst_pwd},
            headers={'X-CSRFToken': csrf}
        )

    def login(self, response: HtmlResponse):
        j_body = response.json()
        if j_body['authenticated']:
            yield response.follow(f'/{self.parse_user}', callback=self.followers_parse, cb_kwargs={'username': self.parse_user})

    def followers_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        url = f"https://i.instagram.com/api/v1/friendships/{user_id}/followers/?count=12&search_surface=follow_list_page"
        yield response.follow(
            url,
            callback=self.followers_parse_next_page,
            headers={'User-Agent': 'Instagram 105.0.0.11.118'},
            cb_kwargs={'username': username,
                       'user_id': user_id})

    def followers_parse_next_page(self, response: HtmlResponse, username, user_id):
        j_data = response.json()
        max_id = j_data.get('next_max_id')
        if j_data['next_max_id']:
            url = f"https://i.instagram.com/api/v1/friendships/{user_id}/followers/?count=12&{max_id}&search_surface=follow_list_page"
            yield response.follow(
                url,
                callback=self.subscribers_parse_next,
                headers={'User-Agent': 'Instagram 105.0.0.11.118'},
                cb_kwargs={'username': username,
                           'user_id': user_id})

        users = j_data.get('users')
        for user in users:
            item = InstagramparserItem(
                user_name=user.get('Object').get('username'),
                user_id=user.get('Object').get('pk'),
                photo=user.get('Object').get('profile_pic_url'),
                user_data=user.get('Object')
            )
            yield item

    def fetch_csrf_token(self, text):
        """ Get csrf-token for auth """
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        try:
            matched = re.search(
                '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
            ).group()
            return json.loads(matched).get('id')
        except:
            return re.findall('\"id\":\"\\d+\"', text)[-1].split('"')[-2]
