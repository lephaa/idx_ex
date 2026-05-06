WEEK 7 DESC:

listing_main.py:
The IQR method was applied to ClosePrice, LivingArea, and DaysOnMarket to identify extreme values. Outliers were flagged rather than removed to preserve raw data. A filtered dataset was created excluding flagged records. After filtering, median ClosePrice decreased from $855,000 to $825,000, indicating that high-value outliers were inflating central tendency measures. DaysOnMarket also decreased slightly, reflecting the removal of long-tail listings. Overall, filtering improved dataset reliability while maintaining data integrity.

sold_main.py:
The IQR method identified a higher proportion of outliers in the sold dataset compared to listings, particularly in ClosePrice and DaysOnMarket. This reflects the greater variability in completed transactions, including distressed and luxury sales. After filtering, median ClosePrice decreased from $820,000 to $785,000, indicating that high-value transactions were inflating price metrics. Median DaysOnMarket decreased from 19 to 16 days, showing that long-duration listings were skewing market timing analysis. Overall, the filtered dataset provides a more accurate representation of typical market conditions.
