#libraries
library(xlsx)
library(car)
library(lmPerm)
library(dplyr)

#set the paths
pvt_path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/cognitive/sub-01_day-all_device-presentation_test-pvt.csv'
nback_path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/cognitive/sub-01_day-all_device-presentation_test-nback.csv'
behav_path = '/m/cs/scratch/networks-pm/effects_externalfactors_on_functionalconnectivity/data/behavioral/sub-01_day-all_device-oura.csv'

#read the files
pvt = read.csv(pvt_path)
nback = read.csv(nback_path)
behav = read.csv(behav_path)

#convert the dates to the right format
behav = behav[,c("date","total_sleep_duration","sleep_efficiency", "sleep_latency", "Steps", "Inactive.Time")]

#compute nback accuracy
nback$accuracy1 = nback$right_1/(nback$right_1+nback$wrong_1+nback$miss_1)
nback$accuracy2 = nback$right_2/(nback$right_2+nback$wrong_2+nback$miss_2)

#Fill NA values with the mean (as stated in the report)
numeric_columns <- sapply(behav, is.numeric)
column_means <- sapply(behav[, numeric_columns], function(x) mean(x, na.rm = TRUE))
behav_filled <- behav  # Copy original data frame
behav_filled[, numeric_columns] <- data.frame(lapply(seq_along(column_means), function(i) {
  column_data <- behav[, names(column_means)[i]]
  is_na <- is.na(column_data)
  column_data[is_na] <- column_means[i]
  return(column_data)
}))

# fit the PVT model
data = data.frame(pvt, behav_filled)
names(data)[names(data) == "Inactive.Time"] <- "inactive_time"
pvt_model = lmp(mean_1_RT ~ total_sleep_duration + sleep_efficiency + sleep_latency, data=data, perm="Prob", maxIter=10000, Ca=1e-09, center=FALSE)
summary(pvt_model)

#Fit models for n-back
data = data.frame(nback, behav_filled)
names(data)[names(data) == "Inactive.Time"] <- "inactive_time"
data <- data %>% mutate(across(c(Steps, inactive_time), lag)) #set the lag for activity values

nback_model1 = lmp(accuracy1 ~ total_sleep_duration + sleep_efficiency + sleep_latency + Steps + inactive_time, data=data, perm="Prob", maxIter=10000, Ca=1e-09, center=FALSE)
summary(nback_model1)

nback_model2 = lmp(accuracy2 ~ total_sleep_duration + sleep_efficiency + sleep_latency + Steps + inactive_time, data=data, perm="Prob", maxIter=10000, Ca=1e-09, center=FALSE)
summary(nback_model1)
