#Set the variables
path = "/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/mri/conn_matrix/nback"
beh_path = "/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/"
save_path = "/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/results/H2"

#Get the parameters that were passed on from the command line
args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 2) {
  stop("You must provide strategy and atlas_name as arguments")
}
strategy <- args[1]
atlas_name <- args[2]

#Check that the packages we need are installed
pkg_list <- c("R.matlab", "xlsx", "lmPerm")

# Function to check, install and load packages
load_package <- function(pkg){
  if (!requireNamespace(pkg, quietly = TRUE)) {
    install.packages(pkg, repos = "https://cloud.r-project.org/")
  }
  library(pkg, character.only = TRUE)
}
sapply(pkg_list, load_package) # Apply the function to each package in the list

# Set seed for reproducibility
set.seed(0)

# Number of subjs
n_subjects <- 30

# load the dependent variable
eff <- readMat(paste(path, strategy, paste0("global-eff_", strategy, "_", atlas_name, ".mat"), sep = "/"))
eff <- eff$eff

#load the independent variables
beh <- read.xlsx(paste(beh_path, "behavioral/sub-01_day-lag1_task_pvt.xlsx", sep="/"), sheetIndex = 1)

# Combine into a data frame
data <- data.frame(eff, beh)

# Fit the linear model
formula_str <- eff ~ total_sleep_duration + awake_time + restless_sleep + steps + inactive_time
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


