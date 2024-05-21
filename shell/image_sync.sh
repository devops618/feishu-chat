#!/bin/bash

dest_image=$1
registry_name=`echo ${dest_image}| awk -F: '{print $1}'`
if [[ ${registry_name} = "preregistry" ]]; then
  image_name=`echo ${dest_image} |awk -F'preregistry:5000' '{print $2}'`
  src_image=`echo ${dest_image}| sed 's/^pre/sit/g'`
  dest_image="harbor-pre.dfiov.com.cn:5000${image_name}"
else
  src_image=`echo ${dest_image}| sed 's/^perf\|^uat\|^pro/sit/g'`
fi

docker pull ${src_image}
docker tag ${src_image} ${dest_image}
docker push ${dest_image}
