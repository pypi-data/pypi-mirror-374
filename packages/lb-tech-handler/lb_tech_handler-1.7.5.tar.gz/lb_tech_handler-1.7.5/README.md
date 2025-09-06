

## 📝 Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Deployment](#deployment)
- [Usage](#usage)
- [Built Using](#built_using)
- [TODO](../TODO.md)
- [Contributing](../CONTRIBUTING.md)
- [Authors](#authors)
- [Acknowledgments](#acknowledgement)
## 🧐 About <a name = "about"></a>

Write about 1-2 paragraphs describing the purpose of your project.

## 🏁 Getting Started <a name = "getting_started"></a>

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See [deployment](#deployment) for notes on how to deploy the project on a live system.

### Setting Up the Module

Set the Envirornment Varibles

Create a file called `.env` in the root directory

```
LB_DB_HOST_NAME_OR_IP = 192.168.1.1
LB_DB_USER_NAME = USER1
LB_DB_PASSWORD = ABCDEF
LB_DB_PORT = 5432
LB_DB_DATABASE_NAME = DBNAME
```

Install the Module

```
pip install lb_tech_handler
```

if already installed then upgrade

```
pip install --upgrade lb_tech_handler
```

End with an example of getting some data out of the system or using it for a little demo.


## Overall Functions In each Modules

### Api Handler
The `api_handler` sub-module handles various operations.

[- **`authenticated_tracked_external_api`**](#authenticated_tracked_external_api)

[- **`authenticated_tracked_internal_api`**](#authenticated_tracked_internal_api)

[- **`authenticated_untracked_external_api`**](#authenticated_untracked_external_api)

[- **`authenticated_untracked_internal_api`**](#authenticated_untracked_internal_api)

[- **`create_redis_client`**](#create_redis_client)

[- **`debug_api_response`**](#debug_api_response)

[- **`debug_drf_response`**](#debug_drf_response)

[- **`download_file_in_chunk_by_url`**](#download_file_in_chunk_by_url)

[- **`execute_query_and_return_result`**](#execute_query_and_return_result)

[- **`get_user_token_from_redis`**](#get_user_token_from_redis)

[- **`get_values_from_token`**](#get_values_from_token)

[- **`log_api_request`**](#log_api_request)

[- **`log_drf_request`**](#log_drf_request)

[- **`proccess_django_api`**](#proccess_django_api)

[- **`set_lb_auth_user_token_to_redis`**](#set_lb_auth_user_token_to_redis)

[- **`test_api`**](#test_api)

[- **`throttle_api_call`**](#throttle_api_call)

[- **`unauthenticated_tracked_external_api`**](#unauthenticated_tracked_external_api)

[- **`unauthenticated_tracked_internal_api`**](#unauthenticated_tracked_internal_api)

[- **`unauthenticated_untracked_external_api`**](#unauthenticated_untracked_external_api)

[- **`unauthenticated_untracked_internal_api`**](#unauthenticated_untracked_internal_api)

[- **`under_development_api`**](#under_development_api)

[- **`validate_token`**](#validate_token)

### Common Methods
The `common_methods` sub-module handles various operations.

[- **`display_indented_text`**](#display_indented_text)

[- **`download_file_in_chunk_by_url`**](#download_file_in_chunk_by_url)

[- **`timed_execution`**](#timed_execution)

### Db Handler
The `db_handler` sub-module handles various operations.

[- **`execute_query`**](#execute_query)

[- **`execute_query_and_return_result`**](#execute_query_and_return_result)

[- **`execute_transaction`**](#execute_transaction)

[- **`execute_transaction_with_multiprocessing`**](#execute_transaction_with_multiprocessing)

[- **`get_connection_from_pool`**](#get_connection_from_pool)

[- **`get_dataframe_from_list_of_queries`**](#get_dataframe_from_list_of_queries)

[- **`get_dataframe_from_query`**](#get_dataframe_from_query)

[- **`is_free_connection_in_pool`**](#is_free_connection_in_pool)

[- **`load_dotenv`**](#load_dotenv)

[- **`put_connection_in_pool`**](#put_connection_in_pool)

[- **`test_async_query`**](#test_async_query)

[- **`test_excution_multi_query`**](#test_excution_multi_query)

[- **`timed_execution`**](#timed_execution)

### Documentation Handler
The `documentation_handler` sub-module handles various operations.

No functions available.

### Excel Handler
The `excel_handler` sub-module handles various operations.

[- **`read_excel_file`**](#read_excel_file)

### File Handler
The `file_handler` sub-module handles various operations.

[- **`delete_file`**](#delete_file)

[- **`generate_barcode`**](#generate_barcode)

[- **`generate_qr_code`**](#generate_qr_code)

[- **`get_file_extension`**](#get_file_extension)

[- **`get_file_name`**](#get_file_name)

[- **`get_file_name_without_extension`**](#get_file_name_without_extension)

[- **`get_file_size`**](#get_file_size)

[- **`get_number_of_pages_of_pdf`**](#get_number_of_pages_of_pdf)

[- **`rename_pdf_file_with_page_number`**](#rename_pdf_file_with_page_number)

### Notification Handler
The `notification_handler` sub-module handles various operations.

[- **`load_dotenv`**](#load_dotenv)

[- **`send_teams_notification`**](#send_teams_notification)

### Os Handler
The `os_handler` sub-module handles various operations.

[- **`get_all_env_variables`**](#get_all_env_variables)

[- **`get_cpu_count`**](#get_cpu_count)

[- **`get_env_variable`**](#get_env_variable)

[- **`set_env_variable`**](#set_env_variable)

### Report Templates
The `report_templates` sub-module handles various operations.

No functions available.

### Sharepoint Handler
The `sharepoint_handler` sub-module handles various operations.

[- **`display_indented_text`**](#display_indented_text)

[- **`download_file_in_chunk_by_url`**](#download_file_in_chunk_by_url)

[- **`generate_fernet_decryption_key`**](#generate_fernet_decryption_key)

[- **`load_dotenv`**](#load_dotenv)

[- **`lru_cache`**](#lru_cache)

[- **`quote`**](#quote)

### Test
The `test` sub-module handles various operations.

No functions available.

###   Init  
The `__init__` sub-module handles various operations.

No functions available.

## Function Defination

### Api Handler
The `api_handler` sub-module handles various operations.

- ### **`authenticated_tracked_external_api`**: 

        Decorator for authenticated, tracked external APIs.
        Requires user token and logs API calls into the database.
        
        Args:
            view_func: The view function to be wrapped.
        
        Returns:
            Response from the view function if token is valid; otherwise, a 401 or 403 error.
- ### **`authenticated_tracked_internal_api`**: 

        Decorator for authenticated, tracked internal APIs.
        Validates user token, origin against ALLOWED_DOMAINS, and logs API calls into the database.
        
        Args:
            view_func: The view function to be wrapped.
        
        Returns:
            Response from the view function if validation passes; otherwise, a 401 or 403 error.
- ### **`authenticated_untracked_external_api`**: 

        Decorator for authenticated, untracked external APIs.
        Requires user token for access but does not log the API call into the database.
        
        Args:
            view_func: The view function to be wrapped.
        
        Returns:
            Response from the view function if token is valid; otherwise, a 401 or 403 error.
- ### **`authenticated_untracked_internal_api`**: 

        Decorator for authenticated, untracked internal APIs.
        Validates user token and origin against ALLOWED_DOMAINS.
        
        Args:
            view_func: The view function to be wrapped.
        
        Returns:
            Response from the view function if validation passes; otherwise, a 401 or 403 error.
- ### **`create_redis_client`**: 

        No description available
- ### **`debug_api_response`**: 

        Debug an API response by collecting useful details and returning them as a structured dictionary.
        
        Args:
            api_response (requests.Response): The API response object to debug.
        
        Returns:
            dict: A dictionary containing API debugging information.
- ### **`debug_drf_response`**: 

        No description available
- ### **`download_file_in_chunk_by_url`**: 

        No description available
- ### **`execute_query_and_return_result`**: 

        _summary_
        
        Args:
            query (str): _description_
            vars (dict, optional): _description_. Defaults to {}.
        
        Raises:
            Exception: _description_
        
        Returns:
            list: _description_
- ### **`get_user_token_from_redis`**: 

        No description available
- ### **`get_values_from_token`**: 

        Extracts email and expiration timestamp from the provided access token.
        
        Args:
            access_token (str): The access token from which details are extracted.
- ### **`log_api_request`**: 

        No description available
- ### **`log_drf_request`**: 

        No description available
- ### **`proccess_django_api`**: 

        No description available
- ### **`set_lb_auth_user_token_to_redis`**: 

        No description available
- ### **`test_api`**: 

        No description available
- ### **`throttle_api_call`**: 

        This is a decorator use to slow down API calls.
        SLowing down API calls by throttling to prevent overloading the server.
        
        Example:
            @throttle_api_call(minimum_api_wait_time_in_seconds=3,maximum_api_wait_time_in_seconds=5)
            def test_api():
                response = requests.get("https://api.learnbasics.fun/testing?name=test")
        
            @throttle_api_call
            def test_api():
                response = requests.get("https://api.learnbasics.fun/testing?name=test")
        
        Args:
            minimum_api_wait_time_in_seconds (int, optional): _description_. Defaults to 3.
            maximum_api_wait_time_in_seconds (int, optional): _description_. Defaults to 5.
- ### **`unauthenticated_tracked_external_api`**: 

        Decorator for unauthenticated, tracked external APIs.
        Logs API calls into the database.
        
        Args:
            view_func: The view function to be wrapped.
        
        Returns:
            Response from the view function.
- ### **`unauthenticated_tracked_internal_api`**: 

        Decorator for unauthenticated, tracked internal APIs.
        Validates the origin against ALLOWED_DOMAINS and logs API calls into the database.
        
        Args:
            view_func: The view function to be wrapped.
        
        Returns:
            Response from the view function if origin is allowed; otherwise, a 403 error.
- ### **`unauthenticated_untracked_external_api`**: 

        Decorator for unauthenticated, untracked external APIs.
        This API does not require authentication and is not logged into the database.
        
        Args:
            view_func: The view function to be wrapped.
        
        Returns:
            Response from the view function.
- ### **`unauthenticated_untracked_internal_api`**: 

        Decorator for unauthenticated, untracked internal APIs.
        Validates the origin against ALLOWED_DOMAINS.
        
        Args:
            view_func: The view function to be wrapped.
        
        Returns:
            Response from the view function if origin is allowed; otherwise, a 403 error.
- ### **`under_development_api`**: 

        Decorator for APIs under development.
        Allows access only from TESTING_HOST.
        
        Args:
            view_func: The view function to be wrapped.
        
        Returns:
            Response from the view function if host is in TESTING_HOST; otherwise, a 403 error.
- ### **`validate_token`**: 

        Validates the token's email and expiration timestamp.
        
        Args:
            mail (str): The email extracted from the token.
            exp (int): The expiration timestamp from the token.
### Common Methods
The `common_methods` sub-module handles various operations.

- ### **`display_indented_text`**: 

        No description available
- ### **`download_file_in_chunk_by_url`**: 

        No description available
- ### **`timed_execution`**: 

        This is a decorator to time the execution time of a function
        
        Example:
            @timed_execution
            def test_api():
                response = requests.get("https://api.learnbasics.fun/testing?name=test")
        
        Args:
            func (_type_): Function to be timed
### Db Handler
The `db_handler` sub-module handles various operations.

- ### **`execute_query`**: 

        _summary_
        
        Args:
            query (str): _description_
            vars (dict, optional): _description_. Defaults to {}.
        
        Raises:
            Exception: _description_
- ### **`execute_query_and_return_result`**: 

        _summary_
        
        Args:
            query (str): _description_
            vars (dict, optional): _description_. Defaults to {}.
        
        Raises:
            Exception: _description_
        
        Returns:
            list: _description_
- ### **`execute_transaction`**: 

        Executes a list of queries
        
        Input Format:
        
            [
                {
                    'query':query,
                    'vars':{
                        "key1":"value1",
                        "key2":"value2"
                    }
                },
                {
                    'query':query2,
                    'vars':{
                        "key1":"value1",
                        "key2":"value4"
                    }
                }
            ]
        
        
        Args:
        --------
            query (str): query
            vars (dict, optional): _description_. Defaults to {}.
        
        Returns:
        ---------
            is_transaction_successful: bool
- ### **`execute_transaction_with_multiprocessing`**: 

        This is a function to execute a list of queries in parallel using multiprocessing
        Use this when you have a list of queries and want to execute them in parallel
        
        Args:
        
        - list_of_queries (list[dict]):
        
        Input Format:
        
                [
                    {
                        'query':query,
                        'vars':{
                            "key1":"value1",
                            "key2":"value2"
                        }
                    },
                    {
                        'query':query2,
                        'vars':{
                            "key1":"value1",
                            "key2":"value2"
                        }
                    }
                ]
        
        - MAX_PROCESS (int, optional): Maximum number of processes to use.
            - Defaults to CPU_COUNT.
        
        Returns:
            bool: _description_
- ### **`get_connection_from_pool`**: 

        No description available
- ### **`get_dataframe_from_list_of_queries`**: 

        returns the query as pandas dataframe from database
        
        Input Format:
            [
                {
                    'query':query,
                    'vars':{
                        "key1":"value1",
                        "key2":"value2"
                    }
                },
                {
                    'query':query2,
                    'vars':{
                        "key1":"value1",
                        "key2":"value2"
                    }
                }
            ]
        
        Args:
        --------
            query (str): query
        
        Returns:
        ---------
            data: pandas dataframe from query
- ### **`get_dataframe_from_query`**: 

        _summary_
        
        Args:
            query (str): _description_
            vars (dict, optional): _description_. Defaults to {}.
        
        Returns:
            _type_: _description_
- ### **`is_free_connection_in_pool`**: 

        No description available
- ### **`load_dotenv`**: 

        Parse a .env file and then load all the variables found as environment variables.
        
        Parameters:
            dotenv_path: Absolute or relative path to .env file.
            stream: Text stream (such as `io.StringIO`) with .env content, used if
                `dotenv_path` is `None`.
            verbose: Whether to output a warning the .env file is missing.
            override: Whether to override the system environment variables with the variables
                from the `.env` file.
            encoding: Encoding to be used to read the file.
        Returns:
            Bool: True if at least one environment variable is set else False
        
        If both `dotenv_path` and `stream` are `None`, `find_dotenv()` is used to find the
        .env file with it's default parameters. If you need to change the default parameters
        of `find_dotenv()`, you can explicitly call `find_dotenv()` and pass the result
        to this function as `dotenv_path`.
- ### **`put_connection_in_pool`**: 

        No description available
- ### **`test_async_query`**: 

        No description available
- ### **`test_excution_multi_query`**: 

        No description available
- ### **`timed_execution`**: 

        This is a decorator to time the execution time of a function
        
        Example:
            @timed_execution
            def test_api():
                response = requests.get("https://api.learnbasics.fun/testing?name=test")
        
        Args:
            func (_type_): Function to be timed
### Documentation Handler
The `documentation_handler` sub-module handles various operations.

No functions available.

### Excel Handler
The `excel_handler` sub-module handles various operations.

- ### **`read_excel_file`**: 

        Read an Excel file and return a pandas DataFrame.
        
        Args:
            file_path (str): The path to the Excel file.
            sheet_name (str): The name of the sheet to read. Defaults to "Sheet1".
        
        Returns:
            pd.DataFrame: A pandas DataFrame containing the data from the Excel file.
### File Handler
The `file_handler` sub-module handles various operations.

- ### **`delete_file`**: 

        Function to delete file
        
        Args:
            file_path (str): Path of the file
- ### **`generate_barcode`**: 

        Function to generate a barcode
        
        Args:
            value (_type_): Value of the barcode
            path (_type_): Path to save the barcode
            barcode_value_to_be_printed (bool, optional): Wether to print the value of barocde at bottom. Defaults to False.
        
        Raises:
            Exception: _description_
        
        Returns:
            str: Barcode path
- ### **`generate_qr_code`**: 

        Function to generate a QR code.
        
        Args:
            value (str): The data or text to encode in the QR code.
            path (str): The file path where the generated QR code image will be saved.
        
            config (dict, optional): Configuration for QR code generation. Defaults to {}.
        
            General Configuration:
                version (int, optional): Controls the size of the QR Code (1 is the smallest, 40 is the largest). Defaults to 1.
                error_correction (int, optional): Level of error correction. Defaults to 1 (Low).
        
                        - 1: Low (7% of codewords can be restored).
        
                        - 2: Medium (15% of codewords can be restored).
        
                        - 3: High (25% of codewords can be restored).
        
                        - 4: Very High (30% of codewords can be restored).
        
            Display Configuration:
                box_size (int, optional): The size of each box in the QR code grid. Defaults to 10.
                border (int, optional): The width of the border (minimum is 4). Defaults to 4.
                fit (bool, optional): Whether to adjust the QR Code size to fit the data. Defaults to True.
        
            Color Configuration:
                fill_color (str, optional): The color of the QR code. Defaults to "black".
                back_color (str, optional): The background color of the QR code. Defaults to "white".
        
        
            Example:
                config = {
                    "version": 1,
                    "error_correction": 2,
                    "box_size": 10,
                    "border": 4,
                    "fit": True,
                    "fill_color": "blue",
                    "back_color": "yellow"
                }
        
        Returns:
            str: The file path where the QR code image was saved.
- ### **`get_file_extension`**: 

        Function to get file extension
        
        Args:
            file_path (str): Path of the file
        
        Returns:
            str: Extension of the file
- ### **`get_file_name`**: 

        Function to get file name wwithout the folder structure.
        
        Args:
            file_path (str): Path of the file
        
        Returns:
            str: Name of the file
- ### **`get_file_name_without_extension`**: 

        Function to get file name wwithout the folder structure.
        
        Args:
            file_path (str): Path of the file
        
        Returns:
            str: Name of the file
- ### **`get_file_size`**: 

        Function to get file size
        
        Args:
            file_path (str): Path of the file
        
        Returns:
            int: Size of the file in bytes
- ### **`get_number_of_pages_of_pdf`**: 

        Function to get number of pages
        
        Args:
            file_path (str): _description_
        
        Returns:
            int: Number of pages
- ### **`rename_pdf_file_with_page_number`**: 

        Function to rename a PDF file with page number
        
        Args:
            file_path (str): Path of the file
            add_page_name_at_start (bool, optional): If True, the page number will be added at the start of the file name else at the end. Defaults to True.
            keep_original_file_name (bool, optional): If True, the original file name will be kept else deleted. Defaults to False.
        
        Returns:
            str: Path of the new file
### Notification Handler
The `notification_handler` sub-module handles various operations.

- ### **`load_dotenv`**: 

        Parse a .env file and then load all the variables found as environment variables.
        
        Parameters:
            dotenv_path: Absolute or relative path to .env file.
            stream: Text stream (such as `io.StringIO`) with .env content, used if
                `dotenv_path` is `None`.
            verbose: Whether to output a warning the .env file is missing.
            override: Whether to override the system environment variables with the variables
                from the `.env` file.
            encoding: Encoding to be used to read the file.
        Returns:
            Bool: True if at least one environment variable is set else False
        
        If both `dotenv_path` and `stream` are `None`, `find_dotenv()` is used to find the
        .env file with it's default parameters. If you need to change the default parameters
        of `find_dotenv()`, you can explicitly call `find_dotenv()` and pass the result
        to this function as `dotenv_path`.
- ### **`send_teams_notification`**: 

        No description available
### Os Handler
The `os_handler` sub-module handles various operations.

- ### **`get_all_env_variables`**: 

        Function to get all env variables
        
        Returns:
            dict: _description_
- ### **`get_cpu_count`**: 

        Function to get cpu count
        
        Returns:
            int: Number of cpus
- ### **`get_env_variable`**: 

        Function to get env variable
        
        Args:
            key (str): _description_
        
        Returns:
            str: _description_
- ### **`set_env_variable`**: 

        Function to set env variable
        
        Args:
            key (str): _description_
            value (str): _description_
### Report Templates
The `report_templates` sub-module handles various operations.

No functions available.

### Sharepoint Handler
The `sharepoint_handler` sub-module handles various operations.

- ### **`display_indented_text`**: 

        No description available
- ### **`download_file_in_chunk_by_url`**: 

        No description available
- ### **`generate_fernet_decryption_key`**: 

        No description available
- ### **`load_dotenv`**: 

        Parse a .env file and then load all the variables found as environment variables.
        
        Parameters:
            dotenv_path: Absolute or relative path to .env file.
            stream: Text stream (such as `io.StringIO`) with .env content, used if
                `dotenv_path` is `None`.
            verbose: Whether to output a warning the .env file is missing.
            override: Whether to override the system environment variables with the variables
                from the `.env` file.
            encoding: Encoding to be used to read the file.
        Returns:
            Bool: True if at least one environment variable is set else False
        
        If both `dotenv_path` and `stream` are `None`, `find_dotenv()` is used to find the
        .env file with it's default parameters. If you need to change the default parameters
        of `find_dotenv()`, you can explicitly call `find_dotenv()` and pass the result
        to this function as `dotenv_path`.
- ### **`lru_cache`**: 

        Least-recently-used cache decorator.
        
        If *maxsize* is set to None, the LRU features are disabled and the cache
        can grow without bound.
        
        If *typed* is True, arguments of different types will be cached separately.
        For example, f(3.0) and f(3) will be treated as distinct calls with
        distinct results.
        
        Arguments to the cached function must be hashable.
        
        View the cache statistics named tuple (hits, misses, maxsize, currsize)
        with f.cache_info().  Clear the cache and statistics with f.cache_clear().
        Access the underlying function with f.__wrapped__.
        
        See:  https://en.wikipedia.org/wiki/Cache_replacement_policies#Least_recently_used_(LRU)
- ### **`quote`**: 

        quote('abc def') -> 'abc%20def'
        
        Each part of a URL, e.g. the path info, the query, etc., has a
        different set of reserved characters that must be quoted. The
        quote function offers a cautious (not minimal) way to quote a
        string for most of these parts.
        
        RFC 3986 Uniform Resource Identifier (URI): Generic Syntax lists
        the following (un)reserved characters.
        
        unreserved    = ALPHA / DIGIT / "-" / "." / "_" / "~"
        reserved      = gen-delims / sub-delims
        gen-delims    = ":" / "/" / "?" / "#" / "[" / "]" / "@"
        sub-delims    = "!" / "$" / "&" / "'" / "(" / ")"
                      / "*" / "+" / "," / ";" / "="
        
        Each of the reserved characters is reserved in some component of a URL,
        but not necessarily in all of them.
        
        The quote function %-escapes all characters that are neither in the
        unreserved chars ("always safe") nor the additional chars set via the
        safe arg.
        
        The default for the safe arg is '/'. The character is reserved, but in
        typical usage the quote function is being called on a path where the
        existing slash characters are to be preserved.
        
        Python 3.7 updates from using RFC 2396 to RFC 3986 to quote URL strings.
        Now, "~" is included in the set of unreserved characters.
        
        string and safe may be either str or bytes objects. encoding and errors
        must not be specified if string is a bytes object.
        
        The optional encoding and errors parameters specify how to deal with
        non-ASCII characters, as accepted by the str.encode method.
        By default, encoding='utf-8' (characters are encoded with UTF-8), and
        errors='strict' (unsupported characters raise a UnicodeEncodeError).
### Test
The `test` sub-module handles various operations.

No functions available.

###   Init  
The `__init__` sub-module handles various operations.

No functions available.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Add notes about how to use the system.

## 🚀 Deployment <a name = "deployment"></a>

Add additional notes about how to deploy this on a live system.

## ⛏️ Built Using <a name = "built_using"></a>

- [MongoDB](https://www.mongodb.com/) - Database
- [Express](https://expressjs.com/) - Server Framework
- [VueJs](https://vuejs.org/) - Web Framework
- [NodeJs](https://nodejs.org/en/) - Server Environment

## ✍️ Authors <a name = "authors"></a>

- [@kylelobo](https://github.com/kylelobo) - Idea & Initial work

See also the list of [contributors](https://github.com/kylelobo/The-Documentation-Compendium/contributors) who participated in this project.

## 🎉 Acknowledgements <a name = "acknowledgement"></a>

- Hat tip to anyone whose code was used
- Inspiration
- References
