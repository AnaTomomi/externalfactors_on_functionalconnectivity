library(R.matlab)
library(xlsx)
library(car)
library(lmPerm)
library(boot)

#set the variables
path = "/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/rs"
beh_path = "/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/"
save_path = "/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/H3"
strategy = "24HMP-8Phys-4GSR-Spike_HPF"
atlas_name = "seitzman-set1"

# Set seed for reproducibility
set.seed(0)

# Number of subjs
n_subjects <- 30

# load the dependent variable
eff <- readMat(paste(path, strategy, paste0("global-eff_", strategy, "_", atlas_name, ".mat"), sep = "/"))
eff <- eff$eff

#load the independent variables
beh <- read.xlsx(paste(beh_path, "behavioral/sub-01_day-lag1_task_movie.xlsx", sep="/"), sheetIndex = 1)
eye <- read.csv(paste(beh_path, "/mri/sub-01_day-all_device-eyetracker.csv", sep="/"))
eye$resting <- ifelse(is.na(eye$resting), 0, eye$resting) #fill in the NaNs with the median (0)

# Combine into a data frame
data <- data.frame(eff, beh, eye$resting)

# Fit the linear model
formula_str <- eff ~ total_sleep_duration + awake_time + restless_sleep + pa_mean + pa_std + na_mean + stress_mean + pain_mean + mean_respiratory_rate_brpm + min_respiratory_rate_brpm + max_respiratory_rate_brpm + median_respiratory_rate_brpm + mean_prv_rmssd_ms + min_prv_rmssd_ms + max_prv_rmssd_ms + eye.resting
model <- lmp(formula_str, data = data, perm="Prob", maxIter=10000, Ca=1e-09, center=FALSE)
model_summary <- summary(model)

# Manual standardization for all coefficients including the intercept
predictors <- names(coef(model))  
standardized_betas <- numeric(length(predictors))

for (i in 1:length(standardized_betas)) {
  predictor <- predictors[i]
  if (predictor == "(Intercept)") {
    standardized_betas[i] <- coef(model)[predictor] - sum(coef(model)[-1] * colMeans(data[predictors[-1]]))
  } else {
    standardized_betas[i] <- coef(model)[predictor] * sd(data[[predictor]]) / sd(data$eff)
  }
}

# Extracting values
result_df <- data.frame(estimate = model_summary$coefficients[,"Estimate"],
                        p_values = model_summary$coefficients[, "Pr(Prob)"], 
                        r_squared = model_summary$r.squared, 
                        adj_r_squared = model_summary$adj.r.squared,
                        f_statistic = model_summary$fstatistic[1],
                        f_p_value = pf(model_summary$fstatistic[1], model_summary$fstatistic[2], model_summary$fstatistic[3], lower.tail = FALSE),
                        standardized_betas = standardized_betas
                        )

save_file = paste(save_path, paste0("global-eff_", strategy, "_", atlas_name, ".csv"), sep="/")
write.csv(result_df, save_file, row.names = TRUE)


