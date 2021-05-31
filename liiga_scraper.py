from bs4 import BeautifulSoup
from urllib.parse import urlparse
import pandas as pd
import requests


class LiigaScraper():
    """
    Used to fetch data from Liiga's website at liiga.fi.
    One can either provide the url from which to fetch the data
    or a filename for a prefetched html file. If both are provided
    then the url type is prioritised.

    After instantiating the class with either of the above methods,
    the data retrieval can be performed with LiigaScraper.getStats.
    This method returns the retrieved data as a pandas DataFrame
    and also stores it in the variable LiigaScraper.df for later retrieval.
    """
    def __init__(self, url=None, file=None):
        self.soup = None

        # Container for the DataFrame for the site associated to this instance
        self.df = None

        # The year the data is for
        self.year = -1

        # The type of data in the page: regular series stats, player stats,
        # game results
        self.type = None

        # Series type currently only 'runkosarja' is supported, this is the
        # regular season
        self.series = None

        if not(url is None):
            self._loadFromUrl(url)
            self._parseSoup()
        elif not(file is None):
            self._loadFromFile(file)
            self._parseSoup()

    def _loadFromUrl(self, url):
        o = urlparse(url)
        if o.query:
            raise ValueError('Invalid URL.')
        html_data = requests.get(url)
        self.soup = BeautifulSoup(html_data.text, 'html.parser')

    def _loadFromFile(self, file):
        self.soup = BeautifulSoup(open(file, 'r'), 'html.parser')

    def _parseSoup(self):
        if self.soup is None:
            raise ValueError('Cannot parse empty soup.')

        url = self.soup.find('meta',
                             property='og:url')['content']
        o = urlparse(url)
        p = o.path.strip('/').split('/')

        if p[1] == 'tilastot':
            self.year = p[2].split('-')[0]
            self.series = p[3]
            type_dic = {'joukkueet': 'series', 'pelaajat': 'players'}
            self.type = type_dic[p[4]]
        elif p[1] == 'ottelut':
            self.year = p[2].split('-')[0]
            self.series = p[3]
            self.type = 'games'
        else:
            raise ValueError('Invalid html data.')

    def getStats(self):
        if self.type == 'series':
            self.df = self._getSeriesStats()
        elif self.type == 'players':
            self.df = self._getPlayersStats()
        elif self.type == 'games':
            self.df = self._getGames()

        return self.df

    def _getPlayersStats(self):
        players_table = self.soup.find('table', id='stats')
        players_rows = players_table.find_all('tr')
        colnames_row = players_rows[0].find_all('td', title=True)
        colnames = []
        for c in colnames_row:
            colnames.append(c['title'])

        colnames = ['Nimi', 'Joukkue'] + colnames
        players_stats = []
        for row in players_rows[1:]:
            stats = []
            for val in row.find_all('td'):
                stats.append(val.get_text().strip())

            players_stats.append(stats[1:])  # the first column is just the index

        df = pd.DataFrame(players_stats, columns=colnames)
        df['Vuosi'] = self.year

        return df

    def _getSeriesStats(self):
        series_table = self.soup.find('table',
                                      attrs={'class': 'team-table'})
        series_rows = series_table.find_all('tr')
        colnames_row = series_rows[0].find_all('td', title=True)
        colnames = []
        for c in colnames_row:
            colnames.append(c['title'])

        col_trans = {'Ottelut': 'Matches', 'Voitot': 'Wins', 'Tasapelit':
                     'Draws', 'Häviöt': 'Losses', 'Tehdyt maalit': 'Goals',
                     'Päästetyt maalit': 'ConcededGoals', 'Lisäpisteet':
                     'OvertimeWins', 'Jatkoaikavoitot': 'OvertimeWins',
                     'Pisteet': 'Points',
                     'Pisteitä per ottelu': 'PointsPerGame',
                     'Ylivoimaprosentti': 'PP', 'Alivoimaprosentti': 'PK'}

        colnames = ['Rank', 'Team'] + [col_trans[s] for s in colnames]
        team_stats = []
        for row in series_rows[1:]:
            stats = []
            for val in row.find_all('td'):
                # val.string is not good here because there could be other tags
                # inside the <td>
                stats.append(val.get_text().strip())

            team_stats.append(stats)

        df = pd.DataFrame(team_stats, columns=colnames)
        df['Year'] = self.year
        df['Series'] = self.series

        return df

    def _getGames(self):
        games_table = self.soup.find('table', id='games')

        games_rows = games_table.find_all('tr')

        colnames = ['Index', 'Time', 'Home', 'Away', 'HG', 'AG']
        game_stats = []
        for row in games_rows[1:]:
            stats = []
            cells = row.find_all('td')
            # Index
            stats.append(cells[0].get_text())
            # Time
            stats.append(row['data-time'])
            # Home
            stats.append(cells[3].get_text().split()[0])
            # Away
            stats.append(cells[3].get_text().split()[2])
            # Home Goals
            stats.append(cells[5].get_text().split()[0])
            # Away Goals
            stats.append(cells[5].get_text().split()[2])

            game_stats.append(stats)

        df = pd.DataFrame(game_stats, columns=colnames)
        df.set_index('Index', drop=True, inplace=True)
        df['Year'] = self.year
        df['Series'] = self.series

        return df
