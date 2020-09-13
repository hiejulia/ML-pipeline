# Docker 
https://github.com/nielsborie/ml-docker

# Dataset 
- `python3 data/download_dataset.py`


# Docker 
- Run the job image in Detached Mode `docker run -d ... /bin/sh -c "while true; do echo hello world; sleep 1; done"`
- `docker logs upbeat_easley`

# Image
- ` docker run -d -P jupyter/scipy-notebook`
    - base- notebook
    - minimal notebook 
    - scipy notebook 
    - r - notebook 
    - tensorflow 
    - pyspark
    - all spark 


# Docker-compose
- Redis
- Jupyter notebook 
- 

# Cheatsheet
- `docker run \
  -v /Users/joshuacook/src:/home/jovyan/src \
    -d -p 5000:8888 \
    jupyter/demo
273ff71c6755670e21accd197461dd4256fbeb129393d137733f36bcb5432a55`

