[简体中文](./readme_zh.md)

# async-map-mongo
Asynchronously calls Amap's API to obtain corresponding latitude and longitude coordinates, with API call results stored in a MongoDB database. Provides functionality to query latitude and longitude from MongoDB and export to Excel.

Open Source Code Address: [https://github.com/JieShenAI/async-map-mongo](https://github.com/JieShenAI/async-map-mongo)

## Introduction

This package enables asynchronous calls to geocoding APIs (default: Amap API; extensible to Baidu Maps and more) to fetch latitude and longitude for addresses. It automates persists geocoding results (e.g., formatted address, country, province, city, coordinates) in MongoDB for efficient data retrieval.

Amap API call interface:
https://restapi.amap.com/v3/geocode/geo?address=北京市朝阳区阜通东大街6号&output=XML&key=<user's key>

## install

```
pip install async-map-mongo
```

## Usage

The Amap API key can be stored in a .env file:

```
api_key=Amap API Key
```

Call the Amap API and save latitude and longitude information to MongoDB:
```shell
amap_insert \
--db_name map \
--collection_name amap \
--limiter_ratio 2.8 \
--address_min_length 5 \
--filename data/excel_name.xlsx \
--address_col_name address \
--address_clean true \
--max_addresses_num 1000 \
```

Collects all addresses from the "address" column, filters out addresses that do not exist in the database, and then calls Amap for the remaining addresses to obtain latitude and longitude.
- filename: Excel or CSV file;
- address_col_name: the attribute name corresponding to the address;
- limiter_ratio: API call rate limit per second;
- max_addresses_num: maximum of 1000 Amap API calls;
- address_min_length: minimum length of a valid address; addresses with a string length less than address_min_length will not call the API;

Data format stored in the database:
![](https://gitee.com/jieshenai/imags/raw/master/Typora/20250820144056211.png)

Query latitude and longitude from MongoDB based on the provided table and export to Excel:
```shell
amap_export \
--db_name map \
--collection_name amap \
--address_min_length 5 \
--filename data/excel_name.xlsx \
--address_col_name address \
--address_clean true \
--output_type csv \
--output_dir output
```

- address_clean: whether to remove text enclosed in Chinese parentheses in the address; true means remove, false means do not remove;
- output_type: The format of the exported file, which defaults to csv. Only file extensions of csv and xlsx are supported.

## API Call Extensibility

Although it supports Amap API for latitude and longitude calls by default, Baidu Maps can be used by changing the base_url parameter. For calls to other API interfaces and corresponding processing, please modify the code of AsyncMapCall.__call_api.