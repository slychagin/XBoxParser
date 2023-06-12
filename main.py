import time
import random
from typing import Tuple, List, Union

import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

from input_data import (
    URL,
    NUMBER_OF_GAMES,
    SOURCE_FILE,
    URLS_FILE,
    GAMES_DATA_FILE,
    EXTRAS_DATA_FILE,
    HEADERS,
    load_btn_selector
)


class XboxParser:

    def __init__(self):
        self.url = URL
        self.source_file = SOURCE_FILE
        self.urls_file = URLS_FILE
        self.games_data_file = GAMES_DATA_FILE
        self.extras_data_file = EXTRAS_DATA_FILE
        self.session = requests.Session()
        self.session.headers = HEADERS
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option("detach", True)
        self.options.add_argument(f'user-agent={HEADERS["User-Agent"]}')
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=self.options
        )
        self.driver.maximize_window()

    def get_html_source(self) -> None:
        """Get html content with NUMBER_OF_GAMES and save it to the html file"""
        self.driver.get(self.url)
        wait = WebDriverWait(self.driver, 10)

        try:
            while True:
                # Check number of games and break if it is greater than NUMBER_OF_GAMES
                games_list = self.driver.find_elements(
                    By.XPATH,
                    '//*[@id="PageContent"]/div/div/div[2]/div[2]/div[1]/section/div/ol/li'
                )
                if len(games_list) >= NUMBER_OF_GAMES:
                    with open(self.source_file, 'w', encoding='utf-8') as file:
                        file.write(self.driver.page_source)
                    print('HTML source were successfully written!')
                    break

                # Wait until the download button becomes available and click it
                load_more_btn = wait.until(ec.visibility_of_element_located(
                    (By.CSS_SELECTOR, load_btn_selector))
                )
                load_more_btn.click()
                time.sleep(2)
        except Exception as e:
            print(e)
        finally:
            self.driver.close()
            self.driver.quit()

    def get_game_urls(self) -> None:
        """Get from html source file all urls"""
        with open(self.source_file, encoding='utf-8') as file:
            src = file.read()

        # Get all game cards from html file
        soup = BeautifulSoup(src, 'lxml')
        game_cards = soup.find_all(
            name='div', class_='ProductCard-module__cardWrapper___6Ls86 shadow'
        )[:NUMBER_OF_GAMES]

        # Get game urls and write it to the text file
        urls = [item.find('a').get('href') for item in game_cards]
        with open(self.urls_file, 'w', encoding='utf-8') as file:
            for url in urls:
                file.write(f'{url}\n')
        print('Links were successfully written!')

    def get_game_data(self):
        """Parse data for each game and extra games"""
        with open(self.urls_file, encoding='utf-8') as file:
            urls = [url.strip() for url in file.readlines()]
        print('Start parsing process...')

        games_data = []
        game_extras = []

        count = 1
        urls_count = len(urls)
        for url in urls:
            soup = self.get_soup(url)

            # Get title, price data and release date
            title = self.get_title(soup)
            release_date = self.release_date(soup)
            price_data = self.get_price(soup)

            games_data.append({
                'title': title,
                'price': price_data[0],
                'discount': price_data[1],
                'discount_price': price_data[2],
                'release_date': release_date
            })

            # Get data from collection games
            collection_urls = self.get_collection_urls(soup)
            if collection_urls:
                for link in collection_urls:
                    extra_soup = self.get_soup(link)
                    title = self.get_title(extra_soup)
                    price_data = self.get_price(extra_soup)
                    release_date = self.release_date(extra_soup)

                    games_data.append({
                        'title': title,
                        'price': price_data[0],
                        'discount': price_data[1],
                        'discount_price': price_data[2],
                        'release_date': release_date
                    })
                    time.sleep(0.5)

            # Get game extras
            extras = self.get_game_extras(title, soup)
            if extras:
                game_extras.extend(extras)

            time.sleep(random.randrange(1, 3))

            # Randomly sleep every 10 iteration
            if count % 10 == 0:
                time.sleep(random.randrange(2, 5))
            print(f'Processed: {count}/{urls_count}')
            count += 1

        return {'games_data': games_data, 'game_extras': game_extras}

    def get_soup(self, url) -> BeautifulSoup:
        """Send request to url and return soup"""
        try:
            response = self.session.get(url=url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            return soup
        except requests.exceptions.ConnectionError as err:
            print(err)
        except requests.exceptions.HTTPError as err:
            print(err)
        except requests.exceptions.RequestException as err:
            print(err)

    @staticmethod
    def get_title(soup_data: BeautifulSoup) -> str:
        """Get game title"""
        try:
            title = soup_data.find(
                name='h1',
                class_='typography-module__xdsH1___7oFBA ProductDetailsHeader-module__productTitle___Hce0B'
            ).text.strip()
        except Exception as e:
            # print(e)
            title = 'No title'
        return title

    def get_price(self, soup_data: BeautifulSoup) -> Tuple:
        """Get origin price, discount and price with discount"""
        try:
            price_data = soup_data.find(
                'div',
                'FadeContainers-module__fadeIn___5xlsD FadeContainers-module__widthInherit___5fuOa'
            ).find_next('div').find_all('span')

            # Check that game has price
            if price_data[0].attrs and 'Price-module' in price_data[0].attrs['class'][0]:
                original_price = price_data[0].text.strip(' USD$+')
                try:
                    discount_price = price_data[1].text.strip(' USD$+')
                    discount = self.get_discount(float(original_price), float(discount_price))
                except IndexError:
                    discount_price = '-'
                    discount = '-'
                return original_price, discount, discount_price
            else:
                original_price = 'Недоступно по отдельности'
                discount = '-'
                discount_price = '-'
                return original_price, discount, discount_price
        except Exception as e:
            # print(e)
            original_price = '-'
            discount = '-'
            discount_price = '-'
            return original_price, discount, discount_price

    @staticmethod
    def release_date(soup_data: BeautifulSoup) -> str:
        """Get release date"""
        try:
            release_date = soup_data.find(
                name='h3',
                class_='typography-module__xdsBody1___+TQLW',
                string='Дата выпуска'
            ).next_sibling.text.strip()
        except Exception as e:
            # print(e)
            release_date = '-'
        return release_date

    @staticmethod
    def get_discount(org_price: float, dsc_price: float) -> str:
        """Calculate and return discount"""
        discount = round((org_price - dsc_price) / org_price * 100)
        return f'{discount}%'

    @staticmethod
    def get_collection_urls(soup_data: BeautifulSoup) -> Union[list, None]:
        """Get url for games in collection"""
        try:
            a_tag_list = soup_data.find_all('a', string='ПЕРЕЙТИ К ИГРЕ')
            urls = [a['href'] for a in a_tag_list]
        except Exception as e:
            # print(e)
            urls = None
        return urls

    @staticmethod
    def get_game_extras(game_title: str, soup_data: BeautifulSoup) -> Union[List[dict], None]:
        """Get game extras"""
        try:
            # Get li list with extras and delete last hidden li without needed data
            extras_list = soup_data.find(
                name='section',
                attrs={'aria-label': 'Дополнения для этой игры'}
            ).find_next('ol').find_all('li')[:-1]

            # Get extras title and price
            extras = []
            for item in extras_list:
                data_extra = item.find('div', 'ProductCard-module__infoBox___M5x18')
                extra_title = data_extra.next_element.text.strip()
                try:
                    extra_price = data_extra.find(
                        'span',
                        'Price-module__boldText___vmNHu Price-module__moreText___q5KoT '
                        'ProductCard-module__price___cs1xr Price-module__listedDiscountPrice___67yG1'
                    ).text.strip(' USD$+')
                except Exception as e:
                    # print(e)
                    extra_price = data_extra.find(
                        'span',
                        'Price-module__boldText___vmNHu Price-module__moreText___q5KoT '
                        'ProductCard-module__price___cs1xr'
                    ).text.strip(' USD$+')
                extras.append({
                    'title': game_title,
                    'extra_title': extra_title,
                    'extra_price': extra_price
                })
        except Exception as e:
            # print(e)
            extras = None
        return extras

    def save_data_to_csv(self, games: List[dict], extras: List[dict]) -> None:
        """Save data to csv with pandas"""
        pd.DataFrame(games).to_csv(self.games_data_file, index=False, sep=';', encoding='utf-8-sig')
        pd.DataFrame(extras).to_csv(self.extras_data_file, index=False, sep=';', encoding='utf-8-sig')


if __name__ == '__main__':
    parser = XboxParser()

    start_time = time.perf_counter()

    parser.get_html_source()
    parser.get_game_urls()
    data = parser.get_game_data()
    parser.save_data_to_csv(data['games_data'], data['game_extras'])

    print('Data saved to file!')

    end_time = time.perf_counter()
    total_time = end_time - start_time
    print(f'{total_time:.4f} seconds')
