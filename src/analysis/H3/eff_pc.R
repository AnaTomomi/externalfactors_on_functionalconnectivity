library(R.matlab)
library(xlsx)
library(car)

#set the variables
path = "/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/rs"
beh_path = "/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/"
save_path = "/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/H3"
strategy = "24HMP-8Phys-4GSR-Spike_HPF"
atlas_name = "seitzman-set2"

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
model <- lm(eff ~ total_sleep_duration + awake_time + restless_sleep + pa_mean + pa_std + na_mean + stress_mean + pain_mean + mean_respiratory_rate_brpm + min_respiratory_rate_brpm + max_respiratory_rate_brpm + median_respiratory_rate_brpm + mean_prv_rmssd_ms + min_prv_rmssd_ms + max_prv_rmssd_ms + eye.resting, data = data)
summary(model)

# Extracting values
model_summary <- summary(model)
result_df <- data.frame(t_values = model_summary$coefficients[, "t value"], 
                        p_values = model_summary$coefficients[, "Pr(>|t|)"], 
                        r_squared = model_summary$r.squared, 
                        adj_r_squared = model_summary$adj.r.squared,
                        f_statistic = model_summary$fstatistic[1],
                        f_p_value = pf(model_summary$fstatistic[1], model_summary$fstatistic[2], model_summary$fstatistic[3], lower.tail = FALSE))

save_file = paste(save_path, paste0("global-eff_", strategy, "_", atlas_name, ".csv"), sep="/")
write.csv(result_df, save_file, row.names = TRUE)

#sanity checks
hist(model$residuals, main = "Histogram of Residuals", xlab = "Residuals")
qqnorm(model$residuals)
qqline(model$residuals)
vif(model) #colinearity

# Calculate residuals
residuals <- residuals(model)

# Create a scatterplot of max_respiratory_rate_brpm vs. residuals
library(ggplot2)
ggplot(data, aes(x = max_respiratory_rate_brpm, y = residuals)) +
  geom_point() +
  geom_hline(yintercept = 0, color = "red", linetype = "dashed") +
  labs(x = "max_respiratory_rate_brpm", y = "Residuals") +
  ggtitle("Scatterplot of max_respiratory_rate_brpm vs. Residuals")

# Create a scatterplot of the data
ggplot(data, aes(x = max_respiratory_rate_brpm, y = eff)) +
  geom_point() +  # Add the scatterplot points
  geom_smooth(method = "lm", se = FALSE, color = "blue") +  # Add the regression line
  labs(x = "max_respiratory_rate_brpm", y = "global efficiency", title = "global efficiency")

# removing variables with high collinearity
model <- lm(eff ~ total_sleep_duration + awake_time + restless_sleep + pa_mean + pa_std + stress_mean + pain_mean + mean_respiratory_rate_brpm + min_respiratory_rate_brpm + max_respiratory_rate_brpm + mean_prv_rmssd_ms + max_prv_rmssd_ms + eye.resting, data = data)
summary(model)

model <- lm(eff ~ total_sleep_duration + awake_time + restless_sleep + pa_mean  + stress_mean + pain_mean + mean_respiratory_rate_brpm + mean_prv_rmssd_ms + eye.resting, data = data)
summary(model)
