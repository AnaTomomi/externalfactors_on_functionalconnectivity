library(R.matlab)
library(xlsx)
library(car)
library(zoo)

# Set seed for reproducibility
set.seed(0)

# Number of subjs
n_subjects <- 30

# load the dependent variable
pc <- readMat("/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/rs/24HMP-8Phys-Spike_HPF/parti-coeff_24HMP-8Phys-Spike_HPF_seitzman-set1.mat")
pc <- pc$pc

#load the independent variables
beh <- read.xlsx("/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/behavioral/sub-01_day-lag1_task_movie.xlsx", sheetIndex = 1)
eye <- read.csv("/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/sub-01_day-all_device-eyetracker.csv")
eye$resting <- na.aggregate(eye$resting, FUN = mean) #fill in the NaNs with the mean

# Combine into a data frame
data <- data.frame(pc, beh, eye$resting)

# Loop through the first 293 columns, i.e. each node in the adjacency matrix
for (i in 1:293) {
  col_name <- colnames(data)[i] # Extract column name
  formula_str <- paste0(col_name, " ~ total_sleep_duration + awake_time + restless_sleep + pa_mean + pa_std + na_mean + stress_mean + pain_mean + mean_respiratory_rate_brpm + min_respiratory_rate_brpm + max_respiratory_rate_brpm + median_respiratory_rate_brpm + mean_prv_rmssd_ms + min_prv_rmssd_ms + max_prv_rmssd_ms + eye.resting") # Construct the formula dynamically
  model <- lm(formula_str, data = data)
  model_summary <- summary(model)
  result_df <- data.frame(t_values = model_summary$coefficients[, "t value"], 
                          p_values = model_summary$coefficients[, "Pr(>|t|)"], 
                          r_squared = model_summary$r.squared, 
                          adj_r_squared = model_summary$adj.r.squared,
                          f_statistic = model_summary$fstatistic[1],
                          f_p_value = pf(model_summary$fstatistic[1], model_summary$fstatistic[2], model_summary$fstatistic[3], lower.tail = FALSE))
  
  write.csv(result_df, paste0("/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/H3/parti-coeff_24HMP-8Phys-Spike_HPF_seitzman-set1_node-", i, ".csv"), row.names = TRUE)
  
}

