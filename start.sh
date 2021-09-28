docker run --net=host -it --rm --entrypoint bash -v ~/.kube:/root/.kube -v prometheus-config:/consulProme/prometheus-config -v /tmp/host-files:/files harbor.tiduyun.com/qujun/consulprome:v1
