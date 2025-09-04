####  **LEGAL DISCLAIMER**

_Neither this package nor the author, tomathon, are affiliated with or endorsed by Google. The inclusion of Google trademark(s), if any, upon this webpage is solely to identify Google contributors, goods, or services, and not for commercial purposes._


-----


## ***ABOUT***

#### `gcloudy` is a wrapper for Google's GCP Python package(s) that aims to make interacting with GCP and its services more intuitive, especially for new GCP users. In doing so, it adheres to ***pandas-like*** syntax for function/method calls.

#### The `gcloudy` package is not meant to be a replacement for GCP power-users, but rather an alternative for GCP users who are interested in using Python in GCP to interact with certain GCP services, especially BigQuery.

#### The **gcloudy** package is built on top of canonical Google Python packages(s) without any alteration to Google's base code.

#### **Documentation can be found** [here](https://tomathon.dev/articles/gcloudy)


-----


## ***QUICKSTART***

#### **gcloudy** is installed using pip with the command:

`$ pip install gcloudy`

#### Once installed, the main **BigQuery** class can be imported from the main **GoogleCloud** module with:

`from gcloudy.GoogleCloud import BigQuery`

#### The `bq` object is initialized using your GCP Project:

`bq = BigQuery(project_id = "gcp-project-name")`

#### To initialize using a specific service account key, pass the full key path to your `key.json`:

```
bq = BigQuery(
    project_id = "gcp-project-name",
    service_acct_key_path = "/full/path/to/your/service/account/key.json"
)
```


-----


## ***COMMON METHODS***

#### **NOTE**: See [docs](https://tomathon.dev/articles/gcloudy) for full documentation

### -----------


## `bq.read_bigquery`
### _Read an existing BigQuery table into a DataFrame_

#### `read_bigquery(bq_dataset_dot_table = None, date_cols = [], preview_top = None, to_verbose = True)`

- **bq_dataset_dot_table** : the "dataset-name.table-name" path of the existing BigQuery table
- **date_cols** : [optional] column(s) passed inside a list that should be parsed as dates
- **preview_top** : [optional] only read in the top ***N*** rows
- **to_verbose** : should info be printed? defaults to **True**
- **use_polars** : should a `polars` DataFrame be returned instead of a `pandas` DataFrame? Defaults to **False**

### EX:

```
my_table = bq.read_bigquery("my_bq_dataset.my_bq_table")
my_table = bq.read_bigquery("my_bq_dataset.my_bq_table", date_cols = ['date'])
my_table = bq.read_bigquery("my_bq_dataset.my_bq_table", use_polars = True)
```


### -----------


## `bq.read_custom_query`
### _Read in a custom BigQuery SQL query into a DataFrame_

#### `read_custom_query(custom_query, to_verbose = True)`

- **custom_query** : the custom BigQuery SQL query that will produce a table to be read into a DataFrame
- **to_verbose** : should info be printed? defaults to **True**
- **use_polars** : should a `polars` DataFrame be returned instead of a `pandas` DataFrame? Defaults to **False**

### EX:

```
my_custom_table = bq.read_custom_query("""
    SELECT
        date,
        sales,
        products
    FROM
        my_bq_project_id.my_bq_dataset.my_bq_table
    WHERE
        sales_month = 'June'
""")
```


### -----------


## `bq.write_bigquery`
### _Write a DataFrame to a BigQuery table_

#### `write_bigquery(df, bq_dataset_dot_table = None, use_schema = None, append_to_existing = False, to_verbose = True)`

- **df** : the DataFrame to be written to a BigQuery table
- **bq_dataset_dot_table** : the "dataset-name.table-name" path of the existing BigQuery table
- **use_schema** : [optional] a custom schema for the BigQuery table. **NOTE**: see **bq.guess_schema** below
- **append_to_existing** : should the DataFrame be appended to an existing BigQuery table? defaults to **False** (create new / overwrite)
- **to_verbose** : should info be printed? defaults to **True**

### EX:

```
bq.write_bigquery(my_data, "my_bq_dataset.my_data")
bq.write_bigquery(my_data, "my_bq_dataset.my_data", append_to_existing = True)
```


### -----------


## `bq.send_query`
### _Send a custom SQL query to BigQuery. Process is carried out within BigQuery. Nothing is returned_

#### _send_query(que, to_verbose = True)_

- **que** : the custom SQL query to be sent and carried out within BigQuery
- **to_verbose** : should info be printed? defaults to **True**

### EX:

```
bq.send_query("""
    CREATE TABLE my_bq_project_id.my_bq_dataset.my_new_bq_table AS 
    (
        SELECT
            date,
            sales,
            products
        FROM
            my_bq_project_id.my_bq_dataset.my_bq_table
        WHERE
            sales_month = 'June'
    )
""")
```

### -----------
