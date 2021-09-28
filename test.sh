# list service from consul
python3 main.py  --job node-exporter

# add service
python3 main.py --o add_service --job node-exporter --ip 192.168.0.192 --port 9100

# del service
python3 main.py --o del_service --job node-exporter --ip 192.168.0.192 --port 9100

# del node
python3 main.py --o del_node  --ip 192.168.0.192

# add prometheus job
python3 main.py --o add_job --job xx-ff

# delete prometheus job
python3 main.py --o del_job --job xx-bb

python3 main.py --o del_job --job xx-ff

