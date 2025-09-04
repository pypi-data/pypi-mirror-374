# Python SDK for Data Intelligence solution


## Documentation
<https://scod.hpedev.io/>


## Installation

To install the `pydi-client` package, follow these steps:

1. Ensure you have Python 3.11.2 installed on your system.
2. Clone the repository or navigate to the directory containing the `pyproject.toml` file.
3. Install the package using `pip`:

    ```bash
    pip install pydi-client
    ```

4. Verify the installation by running:

    ```bash
    pip list | grep pydi-client
    ```

**For detailed steps refer to the documentation**

## Usage

The `pydi-client` package provides a `DIClient` class that allows you to interact with the Data Intelligence SDK. Below are the steps to use its methods. For admin operation use DIAdminClient class:

### Importing the DIClient

Start by importing the `DIClient` class:

```python
from pydi_client.di_client import DIClient
```

### Initializing the Client

Create an instance of the `DIClient`:

```python
client = DIClient(uri="https://your-api-endpoint.com")
```

### Using DIClient Methods

Here are some common methods you can use:

#### Example: Get collection

```python
response = client.get_collection(name="<collection name>")
print(response)
```

#### Example: get collections

```python
response = client.get_all_collections()
print(response)
```

#### Example: similarity search on collection

```python
result = client.similarity_search(query="Which Hercule Poirot book is the best",
                                collection_name="agatha_christie_books",
                                top_k=50,
                                access_key="acesskey***",
                                secret_key="secretkey***",
                                search_parameters={"metric": "cosine", "ef_search": "100"})
print(result)
```

## Community

Please file any issues, questions or feature requests you may have [here](https://scod.hpedev.io/) (do not use this facility for support inquiries of your HPE storage product)

## Contributing

We value all feedback and contributions. If you find any issues or want to contribute, please feel free to open an issue or file a PR. More details in [CONTRIBUTING.md](CONTRIBUTING.md)

## License

This is open source software licensed using the Apache 2.0. Please see [LICENSE](LICENSE) for details.