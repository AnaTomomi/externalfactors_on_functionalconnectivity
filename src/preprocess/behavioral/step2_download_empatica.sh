#! user/bin/bash

cd /u/68/trianaa1/unix/Documents/rr/embraceplus/
ls
source config
~/bin/aws s3 sync ${ACCESS_URL} ${LOCAL_PATH}

