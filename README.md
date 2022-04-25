# PPT-Chain
Just anathor simple implementation of blockchain.

Notes can be found [here](https://rodrous.notion.site/Block-chain-929a6b9f93a643338c7675183d7d821f).

## How to run
1. First install dependencies using `pip`
    
 ```
    pip install -r requirements.txt --no-cache-dir
 ```

2. Since its built on Fast-Api, you can just run
    
```
    uvicorn server:app
```

3. Or use Docker compose
   
 ```
    docker-compose up -d
```

> If building through docker compose, port 8080 will be opened on localmachine

### How to make it work?
*Endpoints at /docs*

1. Register your node [can be skipped]
2. Mine
