library("R.matlab")
library("xlsx")
library("lmPerm")
library("car")

path = "/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/pvt"
beh_path = "/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/"

strategy <- "24HMP-8Phys-Spike_HPF"
atlas_name <- "seitzman-set1"
thres <- "thr-10"

set.seed(0)
n_subjects <- 30

eff <- readMat(paste(path, strategy, paste0("global-eff_", strategy, "_", atlas_name, "_", thres, ".mat"), sep = "/"))
eff <- eff$eff

# Let's start with sleep variables only
beh <- read.xlsx(paste(beh_path, "behavioral/sub-01_day-lag1_task_pvt.xlsx", sep="/"), sheetIndex = 1)
data <- data.frame(eff, beh)

i=1
col_name <- colnames(data)[i] # Extract column name
formula_str <- paste0(col_name, " ~ total_sleep_duration + awake_time + restless_sleep + sleep_latency + sleep_efficiency + steps + inactive_time") # Construct the formula dynamically
model <- lmp(as.formula(formula_str), data = data, perm="Prob", maxIter=10000, Ca=1e-09, center=FALSE)
vif(model)

# sleep efficiency is too high (91.43), so we discard it
formula_str <- paste0(col_name, " ~ total_sleep_duration + awake_time + restless_sleep + sleep_latency + steps + inactive_time") # Construct the formula dynamically
model <- lmp(as.formula(formula_str), data = data, perm="Prob", maxIter=10000, Ca=1e-09, center=FALSE)
vif(model)

# all variables are now VIF<5, but sleep latency and awake time are highly correlated (rho>0.7)
rho <- cor(data$awake_time, data$sleep_latency, method = "spearman")

# Conclusion #1: total sleep time, awake time, and restless sleep are selected. 

#Now let's start with the other variables
path = "/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/rs"
eff <- readMat(paste(path, strategy, paste0("global-eff_", strategy, "_", atlas_name, "_", thres, ".mat"), sep = "/"))
eff <- eff$eff

beh <- read.xlsx(paste(beh_path, "behavioral/sub-01_day-lag1_task_movie.xlsx", sep="/"), sheetIndex = 1)
data <- data.frame(eff, beh)

i=1
col_name <- colnames(data)[i] # Extract column name
formula_str <- paste0(col_name, " ~ total_sleep_duration + awake_time + restless_sleep + pa_mean + pa_median + pa_min + pa_max + pa_std + na_mean + na_median + na_min + na_max + na_std + stress_mean + stress_median + stress_min + stress_max + stress_std + pain_mean + pain_median + pain_min + pain_max + pain_std + mean_respiratory_rate_brpm + min_respiratory_rate_brpm + max_respiratory_rate_brpm + median_respiratory_rate_brpm + std_respiratory_rate_brpm + mean_prv_rmssd_ms + min_prv_rmssd_ms + max_prv_rmssd_ms + median_prv_rmssd_ms + std_prv_rmssd_ms") # Construct the formula dynamically
model <- lmp(as.formula(formula_str), data = data, perm="Prob", maxIter=10000, Ca=1e-09, center=FALSE)
vif(model)

#At this level even it's too much for R, let's take some variables from the formula (those with high rho)
rho <- cor(data$pa_mean, data$pa_median, method = "spearman") #rho=0.79
rho <- cor(data$pa_mean, data$pa_min, method = "spearman") #rho=0.702
rho <- cor(data$na_mean, data$na_max, method = "spearman") #rho=0.93
rho <- cor(data$na_mean, data$na_std, method = "spearman") #rho=0.93
rho <- cor(data$stress_mean, data$stress_max, method = "spearman") #rho=0.95
rho <- cor(data$stress_mean, data$stress_std, method = "spearman") #rho=0.96
rho <- cor(data$pain_mean, data$pain_max, method = "spearman") #rho=1
rho <- cor(data$pain_mean, data$pain_std, method = "spearman") #rho=1
rho <- cor(data$mean_respiratory_rate_brpm, data$median_respiratory_rate_brpm, method = "spearman") #rho=0.78
rho <- cor(data$mean_prv_rmssd_ms, data$median_prv_rmssd_ms, method = "spearman") #rho=0.94
rho <- cor(data$max_prv_rmssd_ms, data$std_prv_rmssd_ms, method = "spearman") #rho=0.80

#plus na_min and stress_min have no variance, the formula we can start with is:
formula_str <- paste0(col_name, " ~ total_sleep_duration + awake_time + restless_sleep + pa_mean + pa_max + pa_std + na_mean + stress_mean + stress_median + pain_mean + pain_median + pain_min + mean_respiratory_rate_brpm + min_respiratory_rate_brpm + max_respiratory_rate_brpm + std_respiratory_rate_brpm + mean_prv_rmssd_ms + min_prv_rmssd_ms + max_prv_rmssd_ms ") # Construct the formula dynamically
model <- lmp(as.formula(formula_str), data = data, perm="Prob", maxIter=10000, Ca=1e-09, center=FALSE)
vif(model)

#still alliased variables. So, let's discard more variables based on their correlation coefficient
formula_str <- paste0(col_name, " ~ total_sleep_duration + awake_time + restless_sleep + pa_mean + pa_std + na_mean + stress_mean + pain_mean + mean_respiratory_rate_brpm + min_respiratory_rate_brpm + max_respiratory_rate_brpm + std_respiratory_rate_brpm + mean_prv_rmssd_ms + min_prv_rmssd_ms + max_prv_rmssd_ms ") # Construct the formula dynamically
model <- lmp(as.formula(formula_str), data = data, perm="Prob", maxIter=10000, Ca=1e-09, center=FALSE)
vif(model)

#Still remove the variables with VIF>5
formula_str <- paste0(col_name, " ~ total_sleep_duration + awake_time + restless_sleep + pa_mean + pa_std + na_mean + stress_mean + pain_mean + mean_respiratory_rate_brpm + min_respiratory_rate_brpm + max_respiratory_rate_brpm + mean_prv_rmssd_ms + min_prv_rmssd_ms + max_prv_rmssd_ms ") # Construct the formula dynamically
model <- lmp(as.formula(formula_str), data = data, perm="Prob", maxIter=10000, Ca=1e-09, center=FALSE)
vif(model)
