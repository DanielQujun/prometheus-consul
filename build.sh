cp /usr/bin/kubectl ./

docker build --network=host -t harbor.tiduyun.com/qujun/consulprome:v1 .

docker push harbor.tiduyun.com/qujun/consulprome:v1

rm -rf ./kubectl
