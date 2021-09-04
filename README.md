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
 
 
Since it need to calculate multiple correlations and, particularly, correlations of 3 vectors, Pearson's correlation for this setting was defined as PearsonCorr{aggfunc1(A), aggfunc1(B, C)}, where A, B, C denote the 3 distinct vectors and aggfunc1 is an aggregation function that ouputs one vector. Moreover, for each set of 3 vectors, 3 correlations are calculated, corresponding to each possible pair of vectors to be aggregated as one of the arguments of the Pearson's correlation function.


- Total Correlation is one of the generalizations of mutual information for multiple variables and is defined as the amount of information carried by each individual variable in addition to their joint entropy. Total correlation is always non-negative and it can be zero only if the variables are completely independent. It can be calculated as shown below:

![equation](https://latex.codecogs.com/gif.latex?C\left(&space;X_{1},X_{2},\ldots&space;,X_{n}\right)&space;=\left[&space;\sum&space;_{i=1}H\left(&space;X_{i}\right)&space;\right]&space;-&space;H\left(&space;X_{1},X_{2},\ldots&space;,X_{n}\right))

![H_x](https://latex.codecogs.com/gif.latex?H\left(&space;X_{i}\right)) :  Information entropy of variable ![X_i](https://latex.codecogs.com/gif.latex?X_{i}). 


The Total correlation was defined as TotalCorr{aggfunc2(A, B, C)}, where A, B, C denote the 3 distinct vectors and aggfunc2(vectorsList) is an aggregation function that ouputs a list of vectors.

**Aggregation**

Two types of aggregation functions were used: 
(1) One that aggregates a list of vectors into one vector (used for Pearson's correlation) i.e Average aggregation function takes a list of vectors of the same length and outputs an average vector.
(2) Second that aggregates a list of vectors into a list of vectors (used for Total correlation). i.e Identity Aggregation takes a list of vectors of the same length and outputs the same list of vectors.

**System Architecture**

Two approaches for calculation of multiple correlations were investigated. First approach is based on constructing a Cartesian product and the second approach, uses an auxiliary index structure that indexes all the combinations of 3 vectors. Both approaches are described with more details and Pyspark pseudocode below.

- Approach 1
```
combinations = vectors.cartesian(vectors).cartesian(vectors).
                   filter(lambda triplet:
                       vectorname1 < vectorname2 < vectorname3)
```
where the inequality sign above denotes alphabetical order ("A" < "B" < "C"). This way, only unique combinations of distinct vectors are left. However, as expected, the scalability of this approach turned out to be worse than that of the second approach since selecting only unique combinations by vector name resulted in very unbalanced partitions and thus in worse performance. Therefore, it was abandon for it's further development.

- Approach 2

Initially, the text file is parsed and transformed into a Spark DataFrame, having the following format:


|                name|             values|idx|
|--------------------|-------------------|---|
|London_AAL_Close_....|15.4492,15.4539...|  1|
|London_AAL_Volume....|8212.3051,5014.3..|  2|

I. Auxiliary index structure : The idea is to generate key-value pairs, 3 pairs with the same key for each unique non-trivial combination of vectors such that these pairs are subsequently passed to reducers, which accumulate the lists of vectors to be further passed to correlation functions. The keys used to generate key-value pairs can be organized in a 3-D abstract table (cube) as shown in the picture below for a small example (N=7). The indices of unique combinations are displayed as solid cubes. This structure is not materialized, though its configuration is used to calculate the needed keys for each vector.

![Architecture](/img/index_cube.png)

II. Generating key-value pairs : The idea of producing key-value pairs is implemented as a generator function in Python, taking 3 arguments: $N$, number of vectors; $idx$, the index of a particular vector among all vectors; $[vector]$, a list containing the only element - the vector itself. This generator is then passed to the flatMap transformation applied to the RDD associated with the DataFrame mentioned above.
```
keyValPairs = 
    vectors_df.rdd.flatMap(lambda tuple:
      keyValPairs_generator(N, idx, [vector]))
```

Further, the RDD containing all generated key-value pairs is repartitioned (with the number of partitions equal to the number of available workers) based on the key value to ensure parallelism and then cached. It is worth noting that as $value$ is the (list with the) vector itself, not its name, it induces a certain memory overhead while caching, but this is easily managed both on a single machine and using a cluster.

 III. Reduce by key : Subsequently, reduceByKey transformation is invoked (reduction: list concatenation). As each key is associated with exactly 3 generated key-value pairs by design, that results in a list of 3 vectors for each key after reduction. Finally, the list of vectors is passed to the aggregation and correlation functions to produce the output.
 
For Pearson's correlation, there is an additional step after reduceByKey to produce 3 permutations of a given combination, accounting for the 3 possible pairs of vectors to be aggregated (averaged):
```
correlations = 
  keyValPairs.reduceByKey(lambda a, b: a + b)
  ###generate 3 permutations for Pearson###
    .map(lambda vectors: (
            v1.name, 
            v2.name+"_aggwith_"+v3.name, 
            PCorr(agg1([v1]), agg1([v2, v3]))))
```
For Total correlation the list is directly passed to the aggregation and correlation functions:
```
correlations = 
  keyValPairs.reduceByKey(lambda a, b: a + b)
    .map(lambda vectors: (
            v1.name, v2.name, v3.name, 
            TCorr(agg2([v1, v2, v3]))))
```


**Distribution of Computation**

Code were execued both in local computation, on a single machine using logical cores as independent workers (16 cores), as well as setup of a cluster in Microsoft Azure (with 3 worker nodes and the overall number of cores equal to 24) to compare the performance and the way workload is distributed. In both approaches described in the previous section, parallelism in computation were used.


- In Aproach 1 unbalanced distribution of the workload were observed, primarily due to filtering of the set of combinations of the vectors (triplets) aimed at avoiding repeated (redundant) computation. More evidently than in the case of pairwise comparison, few overloaded partitions served as a bottleneck for computation, even though the cores of one machine could quickly switch between partitions (vectors set persists in memory). Therefore, it was decided not to develop this approach further.

- Approach 2 differs in the way the workload is distributed since repartitioning is explicitly invoked after producing key-value pairs: that is essential because the intention is for the pairs with the same key to occur in the same partition. A reasonable decision is to set the number of partitions after flatMap, thereby the number of reducers, equal to the number of available cores (16 locally and 24 for the cluster). In this case, the workload is perfectly balanced. Furthermore, in order to optimize our architecture and to avoid redundant computation, precomputation of several statistics for the vectors before passing them to the key-value pairs generator (see pseudocode example below) were performed.  Particularly, the number of the elements, sum of the elements, sum of their squares and entropy for each vector, and appended these values at the end of the vector. Accordingly, the correlation and aggregation functions were adjusted to make use of the precomputed statistics.

```
keyValPairs = 
    vectors_df.rdd.map(lambda tuple:
      (name, precompute_stats(vector), idx))
                  .flatMap(...)
```

### You can watch the demo of the project here :

<a href="https://youtu.be/dnfvP0mbC5A?t=11" target="_blank"><img src="https://img.youtube.com/vi/dnfvP0mbC5A/3.jpg"
alt="IMAGE ALT TEXT HERE" width="240" height="180" border="10" /></a>


### Contributer Credits

- [Kartik B Bhargav](https://github.com/bhargavkartik)
- [Rehan Fazal](https://github.com/rhnfzl)
- [Sukanya Patra](https://github.com/sukanyapatra1997)
- [Stepan Veretennikov](https://github.com/stepanveret)
