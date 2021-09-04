## Data Engineering : Correlation Measure on 2018 Stock Market Dataset

The dataset contains trading data for 2182 unique stocks, on 40 unique stock exchanges. The monthly data is provided by stocks with each stock being associated with a specific stock exchange and is initially stored in the .txt format. Each file contains a trading history of a stock in a particular month and has the following schema.

- Date (Calendar Year 2018)
- Time (in CET timezone)
- Opening price (The first price within this minute)
- Highest price (The highest price within this minute)
- Lowest price (The lowest price within this minute)
- Closing price (the last price within this minute)
- Volume (Sum of the volume of all transactions within this minute)
The dataset can be downloaded from : [2018 Stock](https://www.kaggle.com/rhnfzl/stock-dataset-of-2018)

![Architecture](/img/architecture.png)
