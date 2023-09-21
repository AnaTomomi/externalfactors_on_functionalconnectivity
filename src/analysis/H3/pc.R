library(R.matlab)
library(xlsx)
library(car)
library(zoo)

#set the variables
path = "/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/rs"
beh_path = "/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/"
save_path = "/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/H3"
strategy = "24HMP-8Phys-Spike_HPF"
atlas_name = "seitzman-set2"

# Set seed for reproducibility
set.seed(0)

# Number of subjs
n_subjects <- 30

# load the dependent variable
pc <- readMat(paste(path, strategy, paste0("parti-coeff_", strategy, "_", atlas_name, ".mat"), sep="/"))
pc <- pc$pc
num_rois <- ncol(pc)

#load the independent variables
beh <- read.xlsx(paste(beh_path, "behavioral/sub-01_day-lag1_task_movie.xlsx", sep="/"), sheetIndex = 1)
eye <- read.csv(paste(beh_path, "/mri/sub-01_day-all_device-eyetracker.csv", sep="/"))
eye$resting <- ifelse(is.na(eye$resting), 0, eye$resting) #fill in the NaNs with the median (0)

# Combine into a data frame
data <- data.frame(pc, beh, eye$resting)

# Loop through the first num_rois columns, i.e. each node in the adjacency matrix
result_df <- data.frame()
for (i in 1:num_rois) {
  col_name <- colnames(data)[i] # Extract column name
  formula_str <- paste0(col_name, " ~ total_sleep_duration + awake_time + restless_sleep + pa_mean + pa_std + na_mean + stress_mean + pain_mean + mean_respiratory_rate_brpm + min_respiratory_rate_brpm + max_respiratory_rate_brpm + median_respiratory_rate_brpm + mean_prv_rmssd_ms + min_prv_rmssd_ms + max_prv_rmssd_ms + eye.resting") # Construct the formula dynamically
  model <- lm(formula_str, data = data)
  model_summary <- summary(model)
  result_col <- data.frame(t_values = model_summary$coefficients[, "t value"], 
                          p_values = model_summary$coefficients[, "Pr(>|t|)"], 
                          r_squared = model_summary$r.squared, 
                          adj_r_squared = model_summary$adj.r.squared,
                          f_statistic = model_summary$fstatistic[1],
                          f_p_value = pf(model_summary$fstatistic[1], model_summary$fstatistic[2], model_summary$fstatistic[3], lower.tail = FALSE),
                          node = i)
  result_df <- rbind(result_df, result_col)
}
save_file = paste(save_path, paste0("parti-coeff_", strategy, "_", atlas_name, ".csv"), sep="/")
write.csv(result_df, save_file, row.names = TRUE)
