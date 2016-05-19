# gsTiles

gsTiles is an open source library for creating gsTiles.

It aims to be:

1. Well Organized

2. Well Documented

3. Well Tested

To use this library add the path to this directory to your PYTHONPATH
or install with setup.py

## Install

gsTiles currently requires py2cairo.  The python 2.x bindings which are included with cario.
This cannot be installed with pip.  cairocffi should be investigated as an alternative. Initial tests with cairocffi shows a significant reduction in performance.

## Introduction

This project takes a shapefile and creates an sqlite database containing raster tiles (gsTiles). Tiles containing more then 256 regions are stored a integer rasters (Type C), where each cell in the raster contains the interger offset of the region from the shapefile.  Tiles with 2 to 256 regions are stored as fragments of a PNG files (Type D).  Tiles with 1 region are stored as the id of the regions (Type B). Blank tiles are flagged as such and contain no data (Type A).

A secondary project (jsRender) generates PNG map tiles by mapping the region offsets to colors. Because the original vectors have already been rasterized, this process is very fast.  
