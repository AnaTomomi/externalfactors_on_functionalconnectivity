# Quality data check up

Once all data has been preprocessed, it is important to visualize and inspect their quality per souce. The following list has all the scripts designed for visualization of the quality of data. There is no special order in which they need to be run. 

- `plot_quality_all_main.py PATH SAVEPATH': plots the heatmap of the % of data collected. It plots all sources. It also marks every Sunday during the data collection period, to ease visual inspection. This is a general plot, it will show data completeness and its patterns, but it will not show details on each source. 
- `plot_behavioral_quality.py PATH SAVEPATH': plots a detailed missing data patterns on the behavioral sources, i.e. smartphone ESM, smartring sleep and activity patterns, smartwatch heart rate, heart rate variability, and breathing rate. It also includes other smartphone sensors and GPS-based location data which is not used in this analysis. All data that is plotted here has been aggregated already. 
- `plot_cognitive_quality.py PATH SAVEPATH': plots details on missing data patterns on the cognitive scores, i.e. PVT and n-back tests. 

