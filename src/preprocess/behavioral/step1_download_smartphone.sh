#! user/bin/bash


start=$1
end=$2

export session_id=cookies

module load anaconda/2020-04-tf2

logfiles=(/m/cs/archive/networks-pm/behavioral/smartphone/*.csv.partial)

if [[ -f ${logfiles[0]} ]]; then
  echo 'deleting partial files'
  rm /m/cs/archive/networks-pm/behavioral/smartphone/*.csv.partial
fi

python3 /m/cs/scratch/networks-pm/software/koota-server/kdata/bin/download_sync.py --group https://koota.cs.aalto.fi/group/precisionmapping2020 AwareApplicationNotifications /m/cs/archive/networks-pm/behavioral/smartphone/ --format=csv --start=$start --end=$end

python3 /m/cs/scratch/networks-pm/software/koota-server/kdata/bin/download_sync.py --group https://koota.cs.aalto.fi/group/precisionmapping2020 AwareBattery /m/cs/archive/networks-pm/behavioral/smartphone/ --format=csv --start=$start --end=$end

python3 /m/cs/scratch/networks-pm/software/koota-server/kdata/bin/download_sync.py --group https://koota.cs.aalto.fi/group/precisionmapping2020 AwareCalls /m/cs/archive/networks-pm/behavioral/smartphone/ --format=csv --start=$start --end=$end

python3 /m/cs/scratch/networks-pm/software/koota-server/kdata/bin/download_sync.py --group https://koota.cs.aalto.fi/group/precisionmapping2020 AwareESM /m/cs/archive/networks-pm/behavioral/smartphone/ --format=csv --start=$start --end=$end

python3 /m/cs/scratch/networks-pm/software/koota-server/kdata/bin/download_sync.py --group https://koota.cs.aalto.fi/group/precisionmapping2020 AwareLocation /m/cs/archive/networks-pm/behavioral/smartphone/ --format=csv --start=$start --end=$end

python3 /m/cs/scratch/networks-pm/software/koota-server/kdata/bin/download_sync.py --group https://koota.cs.aalto.fi/group/precisionmapping2020 AwareMessages /m/cs/archive/networks-pm/behavioral/smartphone/ --format=csv --start=$start --end=$end

python3 /m/cs/scratch/networks-pm/software/koota-server/kdata/bin/download_sync.py --group https://koota.cs.aalto.fi/group/precisionmapping2020 AwareScreen /m/cs/archive/networks-pm/behavioral/smartphone/ --format=csv --start=$start --end=$end
