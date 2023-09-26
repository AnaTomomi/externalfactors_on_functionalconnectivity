library(R.matlab)
library(xlsx)
library(car)
library(readxl)
library(zoo)
library(lmPerm)
library(boot)

#set the variables
path = "/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/rs"
result_path <- '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/H3'
beh_path = "/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/"
save_path = "/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/H3"
strategy = "24HMP-8Phys-Spike_HPF"
atlas_name = "seitzman-set2"
measure = 'parti-coeff'#'reg-links'

# Set seed for reproducibility
set.seed(0)

# Number of subjects
n_subjects <- 30

# Load the B&H corrected data
file_path <- paste0(result_path, "/", measure, "_", strategy, "_", atlas_name, "_BHcorrected.xlsx")
file <- read_excel(file_path)

#Load the data to modify
save_file = paste(save_path, paste0(measure,"_", strategy, "_", atlas_name, ".csv"), sep="/")
result_2mod_file <- read.csv(save_file)

#get the col_number (i) for which we need to compute the confidence intervals
non_zero_rows <- apply(file[,-1], 1, function(row) any(row != 0))
to_compute <- file$node[non_zero_rows]

# load the dependent variable
pc <- readMat(paste(path, strategy, paste0(measure,"_", strategy, "_", atlas_name, ".mat"), sep="/"))
if (measure == 'parti-coeff') {
  pc <- pc$pc
} else if (measure == 'reg-links') {
  pc <- pc$links
}

#load the independent variables
beh <- read.xlsx(paste(beh_path, "behavioral/sub-01_day-lag1_task_movie.xlsx", sep="/"), sheetIndex = 1)
eye <- read.csv(paste(beh_path, "/mri/sub-01_day-all_device-eyetracker.csv", sep="/"))
eye$resting <- ifelse(is.na(eye$resting), 0, eye$resting) #fill in the NaNs with the median (0)

# Combine into a data frame
data <- data.frame(pc, beh, eye$resting)
names(data)[names(data) == "eye.resting"] <- "eye_resting"

#Standardize the data
data <- as.data.frame(lapply(data, scale))

#Define a function for bootstraping (confidence intervals)
boot_fn <- function(data, indices) {
  sample_data <- data[indices, ] 
  model_boot <- lmp(as.formula(formula_str), data = sample_data, perm="Prob", maxIter=10000, Ca=1e-09, center=FALSE)
  return(unlist(coef(model_boot)))
}

for (i in to_compute) {
  col_name <- colnames(data)[i] # Extract column name
  formula_str <- paste0(col_name, " ~ total_sleep_duration + awake_time + restless_sleep + pa_mean + pa_std + na_mean + stress_mean + pain_mean + mean_respiratory_rate_brpm + min_respiratory_rate_brpm + max_respiratory_rate_brpm + median_respiratory_rate_brpm + mean_prv_rmssd_ms + min_prv_rmssd_ms + max_prv_rmssd_ms + eye_resting") # Construct the formula dynamically
  
  model <- lmp(as.formula(formula_str), data = data, perm="Prob", maxIter=10000, Ca=1e-09, center=FALSE)
  model_summary <- summary(model)
  
  confidence_int <- boot(data=data, statistic=boot_fn, R=1000)
  all_conf_intervals <- lapply(1:length(coef(model)), function(idx) {
    conf_intervals <- boot.ci(confidence_int, type="bca", index=idx)
    return(conf_intervals$bca)
  })
  CI_lower <- sapply(all_conf_intervals, function(ci) ci[4])
  CI_upper <- sapply(all_conf_intervals, function(ci) ci[5])
  
  #include this info in the results file
  row_to_update <- which(result_2mod_file$node == i)
  result_2mod_file[row_to_update, "CI_lower"] <- CI_lower
  result_2mod_file[row_to_update, "CI_upper"] <- CI_upper
}

#write.csv(result_2mod_file, save_file, row.names = TRUE)
