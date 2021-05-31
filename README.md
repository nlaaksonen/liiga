# Who should've won Liiga in 2019--2020?

> Please note that this project is work in progress.

In this series of notebooks our plan is to use historical data of
the Finnish ice hockey league Liiga to build a model to predict the winner of
the playoff stage based on regular season statistics. We will then use
the final model to "decide" who should've won Liiga in the 2019 season, when
the playoffs had to be cancelled due to COVID-19.

We rely almost solely on statistics from the official Liiga website, which
we'll scrape and process in the first notebook (see also [liiga_scraper.py](liiga_scraper.py)
and [scrape_data.py](scrape_data.py) for a helper class responsible for
the data retrieval). The process to build the model is divided into the following notebooks:

1. [Data cleanup and feature engineering](preprocessing.ipynb)
2. Exploratory analysis *(under construction)*
3. Modelling *(under construction)*
