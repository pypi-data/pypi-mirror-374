# ConLAi CIFAR10

## How to start
The following command will run one server and two clients and start learning.  

```shell
# Run 
python run.py ./conf/dsgd_cifar10_mobilenet.yaml
```

## Config file and Python script

### Config file
This example uses the following configuration file:
```yaml
# PoC mode settings
poc:
  # Data settings for CIFAR10
  data_cache_dir: "./.data_cache"
  partition_method: "hetero"
  partition_alpha: 100.
  random_seed: 42

  # Number of clients to launch
  worker_num: 2
```

### About run.py
#### 1. Prepare datasets and run clients
Splitting the CIFAR10 dataset for clients:
```python
server_path = "localhost:9200"
batch_size = 100
inner_loop = 20

poc_args = ConLPoCArguments.from_yml(args.config_path)

train_data = datasets.CIFAR10(root=poc_args.data_cache_dir, train=True, download=True, transform=ToTensor())
valid_data = datasets.CIFAR10(root=poc_args.data_cache_dir, train=False, download=True, transform=ToTensor())
# Split the CIFAR10 dataset for each client
fed_datasets = FedDatasetsClassification(poc_args, train_data, valid_data, batch_size, inner_loop, class_num=10)
```

and, run each client in multiple processes. 
```python
clients = []
for client_id in range(poc_args.worker_num):
    client = Process(target=run_client, args=(client_id,
                                              fed_datasets.fed_dataset(client_id)["train"],
                                              fed_datasets.fed_dataset(client_id)["valid"],
                                              "cuda"))
    client.start()
    clients.append(client)

for client in clients:
    client.join()
```

#### 2. Optimizer setting
Configure the Optimizer to communicate with the server:
```python
server_path = "localhost:9200"

# Preliminary: Optimizer can be anything
org_optimizer = torch.optim.SGD(filter(lambda p: p.requires_grad, model.parameters()), lr=0.01)
optimizer = DSgd(server_path, org_optimizer, model.parameters(), inner_loop=inner_loop)
```

#### 3. Start Training
Start training using the same procedure as normal PyTorch training.
