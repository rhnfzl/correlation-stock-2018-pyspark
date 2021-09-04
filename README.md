## Data Engineering : Correlation Measure on 2018 Stock Market Dataset


### Goal

To find high multiple correlations of size , i.e., correlations between the vectors, that are over a threshold, or set it as an input parameter of the code.

As correlation measures, you should consider (at least) the following two:

- [Total correlation](https://en.wikipedia.org/wiki/Total_correlation)
- [Pearson correlation](https://en.wikipedia.org/wiki/Pearson_correlation_coefficient), where the vectors of the two sides are computed by linear combinations (e.g., averaged). For e.g, consider the multiple correlation of vectors representing bank1 and bank2, with the vector representing tech1.

Also, define an aggregation function. The functionality of the aggregation function is (possibly) to reduce the number of input time series.

Specifically:

- Design and build an architecture that takes your dataset(s), a correlation function, and an appropriate aggregation function as inputs and discovers sets with a high multiple correlation coefficient (over a threshold). The value of is context-dependent and relies on the dataset and correlation/aggregation algorithm used. Set a value that produces about ten results. The code should not evaluate solutions that include multiple instances of a vector in the input parameters (e.g., in both in1 and in2).

- Combine the two correlation functions mentioned before with two relevant aggregation functions and test the code using these.

#### Overview

Spark platform has been used for processing the big data and calculating the different aspects of the correlation measures. The data pre-processing is explained, followed by the description of system architecture and the parallel processing. Theoretical complexity and experimental performance have been analyzed followed by the meaningful insights.

![Architecture](/img/architecture.png)

#### Dataset

The dataset contains trading data for 2182 unique stocks, on 40 unique stock exchanges. The monthly data is provided by stocks with each stock being associated with a specific stock exchange and is initially stored in the .txt format. Each file contains a trading history of a stock in a particular month and has the following schema.

- Date (Calendar Year 2018)
- Time (in CET timezone)
- Opening price (The first price within this minute)
- Highest price (The highest price within this minute)
- Lowest price (The lowest price within this minute)
- Closing price (the last price within this minute)
- Volume (Sum of the volume of all transactions within this minute)
The dataset can be downloaded from : [2018 Stock](https://www.kaggle.com/rhnfzl/stock-dataset-of-2018)


**Data Prepossessing**

The data originating from different stock exchanges or different stocks within one stock exchange may differ in the frequency of updates, the number of missing values over time and is tied to the working hours of the corresponding stock exchange. To align the data for further analysis, the following steps were taken.

- Yearly data : Monthly text files by stocks were combined into yearly files. Few stock exchanges, as well as several individual stocks, for which the trading data was not available for all of the 12 months, were excluded.
 
- Frequency of updates. Studying the frequency of updates revealed that the vast majority of the stocks have a 1-minute frequency of updates, defined as the most frequent time interval between two subsequent entries. Therefore all the less frequently updated stocks were excluded as well.
 
- Clustering. The stock exchanges were split into 4 clusters based on their working hours in CET: Asian, European, American and Common cluster with the latter cluster including stock exchanges that cannot be attributed to a specific timezone, such as forex, or can be attributed to more than one. European cluster (14 stock exchanges) was chosen to be the focus of the analysis.

- Data incompleteness. The analysis showed that although having the needed 1-minute frequency of updates, many stocks have a substantial number of missing values during the working hours, therefore such stocks, specifically those having less than 1000 entries per month (∼ 50 one-minute entries per working day), were also excluded, thereby leaving 540 stocks traded on 14 European stock exchanges to proceed with.

- Aggregating. The data was aggregated by resampling to 1-hour frequency, using mean as the aggregation function. Timestamp label of a specific hour was tied to the right end of the 1-hour averaging interval.

- Finalizing the dataset. In order to deal with the increased computational complexity of the task, a subset of 450 vectors was created by, firstly, choosing 225 stocks on 2 European stock exchanges: London Stock Exchange and Xetra, secondly, taking 2 columns per stock (Close price, Volume) and further, taking only the data for the Q1 of 2018. Finally, the null values were dropped, as the timestamps of the 2 selected stock exchanges were matching well for all stocks (almost no data loss), and the dataset was rounded to 4 decimals to reduce the resulting file size. The rounding precision parameter was chosen such that the rounding effect on the output of correla- tions calculation is negligible. Then, the dataset was transposed before saving for convenience of processing in Spark.

**Correlation**

- Pearson’s correlation is a measure of linear dependence, assigning a value between −1 and 1, where 0 indicates no correlation, 1 is a perfect positive correlation and −1 is a perfect negative correlation. The formula is as follows.

![equation](https://latex.codecogs.com/gif.latex?r_{xy}=\dfrac&space;{\sum&space;^{n}_{i=1}\left(&space;x_{i}-\overline&space;{x}\right)&space;\left(&space;y_{i}-\overline&space;{y}\right)&space;}{\sqrt&space;{\sum&space;^{n}_{i=1}\left(&space;x_{i}-\overline&space;{x}\right)&space;^{2}}\sqrt&space;{\sum&space;^{n}_{i=1}\left(&space;y_{i}-\overline&space;{y}\right)&space;^{2}}})

![x](https://latex.codecogs.com/gif.latex?\overline{x}) : Average value of x, 
![xi](https://latex.codecogs.com/gif.latex?x_{i}) : value of x at time i, 
![n](https://latex.codecogs.com/gif.latex?n) : The size of the sample, 
 
 
Since we need to calculate multiple correlations and, particularly, correlations of 3 vectors, Pearson's correlation for this setting was defined as PearsonCorr{aggfunc(A), aggfunc(B, C)}, where A, B, C denote the 3 distinct vectors and aggfunc is an aggregation function that ouputs one vector. Moreover, for each set of 3 vectors, 3 correlations are calculated, corresponding to each possible pair of vectors to be aggregated as one of the arguments of the Pearson's correlation function.


- Total Correlation is one of the generalizations of mutual information for multiple variables and is defined as the amount of information carried by each individual variable in addition to their joint entropy. Total correlation is always non-negative and it can be zero only if the variables are completely independent. It can be calculated as shown below:

![equation](https://latex.codecogs.com/gif.latex?C\left(&space;X_{1},X_{2},\ldots&space;,X_{n}\right)&space;=\left[&space;\sum&space;_{i=1}H\left(&space;X_{i}\right)&space;\right]&space;-&space;H\left(&space;X_{1},X_{2},\ldots&space;,X_{n}\right))

![H_x](https://latex.codecogs.com/gif.latex?H\left(&space;X_{i}\right) :  Information entropy of variable ![X_i](https://latex.codecogs.com/gif.latex?X_{i}). 


