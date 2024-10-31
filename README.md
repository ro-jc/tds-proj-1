# tds-proj-1

Submission for Tools in Data Science Course - Project 1

- The data was scraped using the Github REST API, filtering users by location:Mumbai and followers:>50. The data was cleaned up and saved in json format as well as in the required csv files using the csv writer. All this is done in `get_data.py`.
- 27.9% of all repositories were created over the weekend and this is close to $\frac{2}{7} \approx 28.6\% \implies $ on average, developers in Mumbai seem to be just as active as during the weekends as weekdays and the weekend repos perform marginally better (6.3 vs 4.7 average stars)
- Work on side-projects you enjoy in your free time - it is likely that one of those will get higher stars and that is significantly positively correlated with higher followers. Also, keep your bio between 5 and 15 words - those seem to have the highest followers
