import datetime as dt
import psycopg2 as db
from elasticsearch import Elasticsearch
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import pandas as pd
import re

def fetchData():
    '''
    Fungsi ini dibuat untuk melakukan pengambilan data dari postgresql milik docker. Agar docker container
    dapat berkomunikasi dengan postgresql container tersebut sendiri maka digunakan host localhost dan post 5432 
    (port sesuai dengan apa yang telah dikonfigurasikan pada file docker). Nama database tempat data disimpan adalah 
    "airflow", lalu koneksi dengan server postgresql ini dapat diakses menggunakan user yang sudah tertulis
    dalam file .env milik docker. Pada kasus ini user yang digunakan adalah airflow dengan password yang sama.
    Fungsi akan mulai dengan melakukan koneksi kepada postgresql sesuai penjabaran di atas, lalu mengambil
    data dari table_m3, tabel di mana data berada dan diurutkan berdasarkan ID. Kemudian data tersebut akan
    disimpan ke dalam variable df dan disave menjadi file csv bernama "data_raw.csv". Kemudian
    koneksi kepada postgresql juga akan ditutup.
    '''

    print(f'{"-"*30}fetchData{"-"*30}') 
    conn_string="dbname='airflow' host='postgres' user='airflow' password='airflow' port='5432'"
    conn=db.connect(conn_string)

    df=pd.read_sql('select * from table_m3 order by "ID"', conn)

    df.to_csv('data_raw.csv', index=False)

    conn.close()
    print('Postgresql connection closed.')

    print(f'Data successfully fetched from postgresql')
    print('_'*60)


def cleanData():
    '''
    Fungsi ini adalah fungsi yang melakukan data cleaning dari file csv "data_raw.csv",
    yang merupakan data hasil fetch dari postgresql pada fungsi fetchData. Data cleaning dimulai dengan 
    mengakses file csv data_raw tersebut, lalu menghapus data duplikat. Kemudian dilakukan normalisasi nama
    kolom dengan cara mengubahnya menjadi format snake_case (huruf kecil dan dipisah dengan underscore _).
    Kemudian dilakukan juga handling missing value dengan cara mengisi missing value dengan rata-rata kolom
    tersebut jika tipe data merupakan int atau float, dan menggunakan modus dari kolom tersebut jika tipe data
    bukan int atau float. Kemudian dataframe yang telah dilakukan data cleaning akan disimpan ke dalam file csv
    data_clean bernama "data_clean.csv".
    '''

    print(f'{"-"*30}cleanData{"-"*30}')

    df=pd.read_csv('data_raw.csv')
    

    # hapus data duplikat
    df.drop_duplicates(inplace=True)
    df.reset_index(inplace=True, drop=True)


    # ganti nama kolom menjadi format snake_case
    col_cleaned = []
    for col in df.columns:
        clean_col = col.lower().strip().replace(' ', '_').replace('.', '_')
        clean_col = re.sub(r'[^a-z0-9_]', '', clean_col)
        col_cleaned.append(clean_col)

    df.columns = col_cleaned


    # handling missing value
    for i in df.columns:
        ## untuk kolom dengan tipe data integer atau float isi missing value dengan mean
        if 'int' in str(df[i].dtype) or 'float' in str(df[i].dtype):
            df[i] = df[i].fillna(int(df[i].mean()))
        ## untuk kolom dengan tipe data selain int dan float isi missing value dengan mode
        else:
            df[i] = df[i].fillna(df[i].mode()[0])
    

    # export dataframe yang sudah di clean menjadi 'P2M3_wesley_hakim_data_clean.csv'
    df.to_csv('data_clean.csv', index=False)

    print(f'Data has been cleaned and saved as data_clean csv')
    print('_'*60)

def loadData():
    '''
    Fungsi ini adalah fungsi yang meload data yang telah dibersihkan dari fungsi cleanData yaitu 
    file "data_clean.csv" ke pada elastic search. Di mulai dengan membuat objek koneksi dengan
    Elasticsearch pada localhost port 9200 dan menyimpan data_clean csv sebagai dataframe. Lalu setiap baris
    dari dataframe tersebut akan diiterasi, di mana setiap baris akan diubah menjadi format json, dan disimpan
    ke index fromcleanedcsv (index pada elasticsearch seperti table pada postgresql) dengan isi data doc dan id i
    (i akan mengiterasi sepanjang dataframe).
    '''

    print(f'{"-"*30}loadData{"-"*30}')

    es = Elasticsearch('http://elasticsearch:9200')
    df=pd.read_csv('data_clean.csv')
    for i,r in df.iterrows():
        doc=r.to_json()
        res=es.index(index="fromcleanedcsv", doc_type="doc", body=doc, id=i)
        print(res)

    print(f'Data has been loaded to elastic search')
    print('_'*60)


'''
default_args berisi parameter default yang akan diikuti node/task dari DAG. Di sini telah didefinisikan
bahwa owner dari DAG ini adalah wesley, dan penjadwalan automasi DAG akan dimulai pada tanggal 1 November 2024
pada pukul 9. Kemudian karena airflow menggunakan timezone yang berbeda dari Indonesia (UTC +0), maka akan dikurangi
7 jam agar startdate yang disetting menggunakan WIB (UTC +7) menjadi UTC +0. Lalu dikonfigurasi jika terjadi kegagalan
DAG akan melakukan pengulangan sekali saja dan pengulangan dilakukan 5 menit setelah kegagalan.
'''
default_args = {
    'owner': 'wesley',
    'start_date': dt.datetime(2024, 11, 1, 9, 0, 0) - dt.timedelta(hours=7),
    'retries': 1,
    'retry_delay': dt.timedelta(minutes=5),
}


'''
Lalu baris kode di bawah adalah kode yang mendefinisikan nama dari DAG yaitu "FetchCleaningDAG" dan DAG
ini menggunakan default parameter yang telah ditulis di atas. Lalu penjadwalan automasi DAG juga ditetapkan
pada kode ini dimana penjadwalan ditetapkan menggunakan cronjob "10-30/10 2 * * 6" yang berarti setiap hari Sabtu
pada pukul 2 dari menit ke 10 hingga 30, kelipatan 10 (langkah setiap 10 menit) akan dilakukan task DAG ini. Perlu 
Diingat bahwa timezone yang digunakan oleh airflow adalah UTC +0 maka dalam UTC +7 cronjob ini sebenarnay sama dengan 
"10-30/10 9 * * 6" karena jam 9 dikurangi dengan 7 jam menjadi 2 yang berarti "10-30/10 2 * * 6". Lalu
setiap node/task yang akan dilakukan juga didefinisikan dalam with DAG di mana terdapat 3 node yaitu:
- fetch_data : didefinisikan sebagai python operator dengan id "fetch" dan akan menjalankan fungsi fetchData 
- clean_data : didefinisikan sebagai python operator dengan id "clean" dan akan menjalankan fungsi cleanData
- load_data  : didefinisikan sebagai python operator dengan id "load" dan akan menjalankan fungsi loadData
'''
with DAG('FetchCleaningDAG',
         default_args=default_args,
         schedule_interval="10-30/10 2 * * 6",
         ) as dag:

    fetch_data = PythonOperator(task_id='fetch',
                                 python_callable=fetchData)
    
    clean_data = PythonOperator(task_id='clean',
                                 python_callable=cleanData)

    load_data = PythonOperator(task_id='load',
                                 python_callable=loadData)


'''
Lalu urutan dari task dari DAG ditentukan seperti di bawah, yang berarti task memiliki urutan sebagai berikut:
1. fetch_data : Menjalankan fungsi fetchData, yang mengambil data dari postgresql docker dan menyimpannya sebagai csv data_raw 
2. clean_data : Menjalankan fungsi cleanData, yang mengambil data dari data_raw csv dan membersihkan data dan simpan sebagai csv data_clean
3. load_data  : Menjalankan fungsi loadData, yang mengambil data dari data_clean dan menyimpannya kepada elasticsearch
'''
fetch_data >> clean_data >> load_data
