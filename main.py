
import os

import asyncio
import aiohttp
from fake_useragent import UserAgent
from pypasser import reCaptchaV3
from bs4 import BeautifulSoup

from bot import send_message_to_group


class UnauthorizedError(Exception):
    pass
  

# global variables
headers = {
    'user-agent': UserAgent().random,
}

reCaptcha_anchor = 'https://www.recaptcha.net/recaptcha/api2/anchor?ar=1&k=6LcCR2cUAAAAANS1Gpq_mDIJ2pQuJphsSQaUEuc9&co=aHR0cHM6Ly93d3cudGVzbWFuaWFuLmNvbTo0NDM.&hl=en&v=vpEprwpCoBMgy-fvZET0Mz6L&size=invisible&cb=9doekayh7f9o'


# get data
async def fetch_and_parse(session, page: int, count_of_pages: int, list_of_articles: list):
    url = f'https://www.tesmanian.com/blogs/tesmanian-blog?page={page}'
    async with session.get(url) as response:
        soup = BeautifulSoup(await response.text(), 'lxml')
        links = soup.find_all('a', class_='blog-post-card__figure')
        for link in links:
            title = link.find('img').get('alt')
            link_of_article = f'https://www.tesmanian.com/' + link.get('href')
            list_of_articles.append({'title': title, 'link': link_of_article})


async def login(session):
    reCaptcha_response = reCaptchaV3(reCaptcha_anchor)
    login_data = {
        'form_type': 'customer_login',
        'utf8': '✓',
        'checkout_url': '/account',
        'customer[email]': os.environ.get('EMAIL_TESLA'),
        'customer[password]': os.environ.get('PASSWORD_TESLA'),
        'return_url': '/account',
        'recaptcha-v3-token': f'{reCaptcha_response}',
    }
    login_header = {
        'upgrade-insecure-requests': '1',
        'origin': 'https://www.tesmanian.com',
        'referer': 'https://www.tesmanian.com/',
        'content-type': 'application/x-www-form-urlencoded'
    }
    async with session.post('https://www.tesmanian.com/account/login', data=login_data, headers=login_header) as resp:
        soup = BeautifulSoup(await resp.text(), 'lxml')
        wrappers = soup.find_all('div', class_='empty-state__icon-wrapper')
        if len(wrappers) != 2:
            raise UnauthorizedError('UnauthorizedError')


async def main():
    async with aiohttp.ClientSession(headers=headers) as session:
        await login(session)
        while True:
            list_of_articles = []
            first_page = await session.get('https://www.tesmanian.com/blogs/tesmanian-blog?page=1')
            soup = BeautifulSoup(await first_page.text(), 'lxml')
            count_of_pages = int(soup.find('span', class_='pagination__current').text.split()[-1])

            tasks = [asyncio.create_task(fetch_and_parse(session, page, count_of_pages, list_of_articles)) for page in range(1, count_of_pages + 1)]

            await asyncio.gather(*tasks)
            await send_message_to_group(list_of_articles)
            await asyncio.sleep(15)


if __name__ == '__main__':
    asyncio.run(main())
