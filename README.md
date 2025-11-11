# E-Commerce Delivery Data Analysis with End-to-End Data Pipeline Using Apache Airflow,ElasticSearch, and Kibana

## Repository Outline
```
    ecommerce-data-pipeline
    |
    ├── images/
    │   ├── introduction & objective.png
    │   ├── kesimpulan.png
    │   ├── plot & insights 01.png
    │   ├── plot & insights 02.png
    │   ├── plot & insights 03.png
    │   ├── plot & insights 04.png
    │   ├── plot & insights 05.png
    │   └── plot & insights 06.png
    ├── DAG_graph.png
    ├── DAG.py
    ├── data_clean.csv
    ├── data_raw.csv
    ├── data_validation_great_expectation.ipynb
    ├── README.md
    └── sql_ddl_syntax.txt
```
- **ecommerce-data-pipeline**  
    Repository github ini.

- **images**  
    Folder yang berisi foto-foto plot data beserta dengan insights dari dashboard kibana.

- **DAG_graph.png**  
    File screenshot graph DAG yang telah dibuat pada Apache Airflow.

- **DAG.py**  
    File python yang membuat DAG pada Apache Airflow. DAG ini melakukan fetch data dari PostgreSQL, cleaning data, dan simpan kepada ElasticSearch.

- **data_clean.csv**  
    File csv dataset yang telah dibersihkan dari `DAG.py`.

- **data_raw.csv**  
    File csv dataset yang belum dibersihkan dan diambil dari PostgreSQL docker.

- **sql_ddl_syntax.txt**  
    File txt berisi kode sql yang dijalankan untuk mengimport data csv ke dalam postgres container docker.

- **data_validation_great_expectation.ipynb**  
    File ipynb yang membuat peraturan/kriteria tertentu untuk validasi data menggunakan library python Great Expectations.

- **README.md**  
    File dokumentasi yang berisi mengenai overview dan penjelasan repository ini.

## Problem Background
Jumlah pelanggan e-commerce semakin bertambah banyak seiring berjalannya perkembangan teknologi dan ini menjadi tantangan bagi banyak perusahaan e-commerce. Kepuasan pelanggan terhadap perusahaan e-commerce tidak terbatas oleh produknya saja, tetapi juga pengirimannya. Menurut sebuah [artikel](https://www.thescxchange.com/articles/8106-survey-70-of-e-commerce-shoppers-say-their-goods-were-shipped-late-without-any-excuse), sebanyak 70% pelanggan mengalami keterlambatan pengiriman dan 35% keterlambatan tersebut tidak disertai dengan alasan keterlambatan. Lalu setelah mengalami keterlambatan itu, 90% pelanggan menyatakan kemungkinan besar tidak akan membeli lagi dari perusahaan tersebut dan sebanyak 29% menyatakan terdorong untuk meninggalkan ulasan yang buruk.

## Project Output
Output dari project ini adalah program DAG untuk melakukan otomasi fetching, cleaning, dan penyimpanan data kepada elastic search pada Apache Airflow, program validasi data menggunakan Great Expectations untuk melakukan validasi data, dan dashboard analisa data pada kibana menggunakan data yang telah diterima oleh Elastic Search.

## Data
[URL Dataset](https://www.kaggle.com/datasets/prachi13/customer-analytics/data)

Dataset ini diambil dari Kaggle dengan tautan di atas. Terdapat 10999 baris data pengiriman dan 12 kolom. Kolom tersebut adalah:
| No. | Nama Kolom            | Penjelasan                                                                                                                                                          |
|-----|-----------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 1   | ID                    | ID dari pengiriman.                                                                                                                                                 |
| 2   | Warehouse_block       | Warehouse/gudang asal paket dikirim. Direpresentasikan dalam alfabet A,B,C,D,F.                                                                                     |
| 3   | Mode_of_shipment      | Metode pengiriman yang digunakan yaitu "Flight", "Ship", dan "Road".                                                                                                |
| 4   | Customer_care_calls   | Berapa kali pelanggan menelpon untuk menanyakan mengenai pengirimannya.                                                                                             |
| 5   | Customer_rating       | Rating yang diberikan oleh pelanggan dari 1 hingga 5, 1 adalah rating terendah/terburuk, dan 5 adalah rating tertinggi/terbaik.                                     |
| 6   | Cost_of_the_Product   | Harga dari produk dalam US dollar.                                                                                                                                  |
| 7   | Prior_purchases       | Berapa kali pelanggan tersebut sudah pernah membeli dari perusahaan ini.                                                                                            |
| 8   | Product_importance    | Pengkategorian pengiriman dalam 3 kategori yaitu "low", "medium", dan "high".                                                                                       |
| 9   | Gender                | Jenis kelamin pelanggan yaitu "Male" dan "Female".                                                                                                                  |
| 10  | Discount_offered      | Diskon yang ditawarkan dari produk tersebut.                                                                                                                        |
| 11  | Weight_in_gms         | Berat dari produk tersebut dalam gram.                                                                                                                              |
| 12  | Reached.on.Time_Y.N   | Indikator apakah pengiriman dikirim tepat waktu atau terlambat. 1 mengindikasikan pengiriman **terlambat**, sedangkan 0 mengindikasikan pengiriman **tepat waktu**. |


## Method
Project ini dilakukan dengan cara menyimpan dataset dari kaggle kepada PostgreSQL docker terlebih dahulu, di mana docker container ini mensimulasikan server. Lalu menggunakan program DAG Apache Airflow, program akan mengakses dataset dari PostgreSQL docker, lalu melakukan data cleaning, dan menyimpan data hasil cleaning tersebut kepada Elastic Search milik docker juga. Kemudian data dari elastic search itu akan diterima oleh kibana untuk dapat divisualisasikan dalam dashboard.

Beberapa hal yang harus diperhatikan ketika menjalankan program ini adalah:
1. Konfigurasi variable `conn_string` pada fungsi `fetchData()` di program `DAG.py`. Sesuaikan nama database, host, port, username, dan password sesuai dengan pengaturan postgres yang telah dikonfigurasi pada file docker.
2. Konfigurasi variable `es` milik elastic search pada fungsi `loadData()` di program `DAG.py`. Sesuaikan URL dengan host name dan port sesuai dengan pengaturan Elastic Search yang telah dikonfigurasi pada file docker.
3. Jika akan mengimport data melalui csv kepada PostgreSQL milik docker, ada 2 cara yang dapat dilakukan. Cara pertama adalah melakukan import melalui CLI PostgreSQL yang disambungkan kepada server postgres docker dan mengambil file dari komputer lokal (yang menjalankan CLI), sedangkan cara kedua mengcopy file pada komputer lokal (yang menjalankan CLI) kepada container docker postgres dan PostgreSQL akan mengimport dari file container postgres:  

    **Cara pertama:**  
    1. Buka command prompt dan jalankan perintah ini. Sesuaikan perintah di ini sesuai konfigurasi docker postgres dan .env, menggunaakn port, user, dan nama database yang sesuai agar dapat berhasil dijalankan.  
    ```
    psql -h localhost -p 5434 -U airflow -d airflow
    ```
    2. Setelah berhasil dijalankan, kini command prompt sudah tersambung dengan server PostgreSQL milik docker container.
    3. Jalankan kode SQL `-- method 1` yang ada pada `sql_ddl_syntax.txt`, sesuaikan nama tabel, isi kolom dari tabel, serta path untuk file csv yang akan di copy.
    
    **Cara kedua:**  
    1. Buka command prompt dan jalankan perintah di bawah ini. Perintah ini mengcopy file pada komputer lokal (yang menjalankan command prompt) kepada docker container. Sesuaikan path untuk file csv yang akan dicopy. Perintah dibawah ini akan mengcopy file csv pada path yang diberikan kepada container postgres docker pada directory `/tmp/data.csv` (csv dicopy dengan nama data.csv pada folder tmp).   
    ```
    docker cp "\your\data_raw\file\path" postgres:/tmp/data.csv
    ```
    2. Koneksikan pgAdmin dengan server postgres dari docker container. Gunakan host, port, user, dan password sesuai konfigurasi file docker postgres dan .env.
    3. Setelah berhasil terkoneksi dengan server postgres docker, jalankan kode SQL `-- method 2` pada `sql_ddl_syntax.txt`. Sesuaikan juga nama tabel dan isi kolom dari tabel, jika directory copy berbeda dengan perintah yang diberikan di atas, sesuaikan juga dengan directory copy yang telah dilakukan.

## Stacks
Project ini menggunakan bahasa pemrograman Python untuk membuat DAG serta data validation. Library Python yang digunakan adalah pandas, airflow, elasticsearch, dan great_expectations. Tools lainnya yang digunakan adalah PostgreSQL, Docker, Apache Airflow, Elastic Search, dan Kibana.

## Reference
- [Dataset](https://www.kaggle.com/datasets/rabieelkharoua/alzheimers-disease-dataset/data)
