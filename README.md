# Kwork projects parser

---

![1.png](assets/1.png)
![2.png](assets/2.png)
![3.png](assets/3.png)
![4.png](assets/4.png)
![5.png](assets/5.png)
![6.png](assets/6.png)
![7.png](assets/7.png)
![8.png](assets/8.png)
![9.png](assets/9.png)
![10.png](assets/10.png)

---

## Deployment

```text
git clone https://github.com/coolworld2049/<project_name>.git
```

```text
cd src/<project_name>;
cp .env.example .env;
nano .env
```

```text
cd deployment
bash cli.sh install
```

deployment/cli.sh

  ```text
  Usage: cli.sh [OPTION]
  Options:
    install           Bring up containers using Docker Compose
    delete            Remove containers, images
    --help            Display this help message
  
  ```