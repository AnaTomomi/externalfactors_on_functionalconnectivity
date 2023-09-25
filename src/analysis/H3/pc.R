library(R.matlab)
library(xlsx)
library(car)
library(zoo)
library(lmPerm)

#set the variables
path = "/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/rs"
beh_path = "/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/"
save_path = "/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/H3"
strategy = "24HMP-8Phys-4GSR-Spike_HPF"
atlas_name = "seitzman-set1"

# Set seed for reproducibility
set.seed(0)

# Number of subjects
n_subjects <- 30

# Set a floor value for the p-vals in case one is too small, in which case
# R will save the value as 0 and can cause problems when performing the FDR correction
# Thus. any value below the floor will be saved as the floor
floor_value <- 2.2e-15

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
names(data)[names(data) == "eye.resting"] <- "eye_resting"

# Loop through the first num_rois columns, i.e. each node in the adjacency matrix
result_df <- data.frame()
for (i in 1:num_rois) {
  col_name <- colnames(data)[i] # Extract column name
  formula_str <- paste0(col_name, " ~ total_sleep_duration + awake_time + restless_sleep + pa_mean + pa_std + na_mean + stress_mean + pain_mean + mean_respiratory_rate_brpm + min_respiratory_rate_brpm + max_respiratory_rate_brpm + median_respiratory_rate_brpm + mean_prv_rmssd_ms + min_prv_rmssd_ms + max_prv_rmssd_ms + eye_resting") # Construct the formula dynamically
  model <- lmp(as.formula(formula_str), data = data, perm="Prob", maxIter=10000, Ca=1e-09, center=FALSE)
  model_summary <- summary(model)
  
  # Manual standardization for all coefficients including the intercept
  predictors <- names(coef(model))  
  standardized_betas <- numeric(length(predictors))
  
  for (j in 1:length(standardized_betas)) {
    predictor <- predictors[j]
    if (predictor == "(Intercept)") {
      standardized_betas[j] <- coef(model)[predictor] - sum(coef(model)[-1] * colMeans(data[predictors[-1]]))
    } else {
      standardized_betas[j] <- coef(model)[predictor] * sd(data[[predictor]]) / sd(data[[col_name]])
    }
  }
  
  result_col <- data.frame(estimate = model_summary$coefficients[,"Estimate"],
                          p_values = model_summary$coefficients[, "Pr(Prob)"], 
                          r_squared = model_summary$r.squared, 
                          adj_r_squared = model_summary$adj.r.squared,
                          f_statistic = model_summary$fstatistic[1],
                          f_p_value = pf(model_summary$fstatistic[1], model_summary$fstatistic[2], model_summary$fstatistic[3], lower.tail = FALSE),
                          standardized_betas = standardized_betas,
                          node = i)
  
  result_df <- rbind(result_df, result_col)
}

if (0 %in% result_df$p_values) {
  result_df$p_values[result_df$p_values < floor_value] <- floor_value
}

save_file = paste(save_path, paste0("parti-coeff_", strategy, "_", atlas_name, ".csv"), sep="/")
write.csv(result_df, save_file, row.names = TRUE)
