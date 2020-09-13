#!/bin/bash

docker build -t ipython ipython

docker run -it ipython

# docker build -t miniconda3 miniconda3