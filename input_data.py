URL = 'https://www.xbox.com/ru-RU/browse/games'
NUMBER_OF_GAMES = 500

SOURCE_FILE = 'files/source_page.html'
URLS_FILE = 'files/urls.txt'
HEADERS = {
    'Accept': '*/*',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,es;q=0.6',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 '
                  'Safari/537.36 '
}

load_btn_selector = '#PageContent > div > div > div.BrowsePage-module__filtersAndProductGrid___rAq1z > ' \
                    'div.BrowsePage-module__productGridAndLoadMore___1ZN4F > ' \
                    'div.BrowsePage-module__loadMoreRow___sx0qx > ' \
                    'button.commonStyles-module__basicButton___go-bX.Button-module__basicBorderRadius___TaX9J.Button' \
                    '-module__defaultBase___c7wIT.Button-module__buttonBase___olICK.Button' \
                    '-module__textNoUnderline___kHdUB.Button-module__typeBrand___MMuct.Button-module__sizeMedium___T' \
                    '\+8s\+.Button-module__overlayModeSolid___v6EcO '
