docker_volume_root=$(docker info 2>/dev/null |grep -i Root |awk -F ":" '{print $2}')
if [[ $? != 0 ]] || [[ -z ${docker_volume_root} ]];then
  "echo find docker root directory failed!"
  exit 1
fi

volume=$(docker volume inspect prometheus-config >/dev/null)

if [[ $? != 0 ]];then
  echo "create volume prometheus-config"
  docker volume create prometheus-config
  sudo cp prometheus-config/* ${docker_volume_root}/volumes/prometheus-config/_data/
else
  echo "volume prometheus-config already exist"
fi
