http_file_storage
===


## Getting started
Get yourself a copy and create virtual enviroment by pasting the following lines into your terminal:


``` 
git clone https://github.com/kirpastuhov/http_file_storage.git
cd http_file_storage
python3 -m venv venv
source venv/bin/activate
```

Install all requirments

```
pip3 install -r requirments.txt
```

You can start file server with:
```
python3 server.py
```

Storage supports **download**, **delete**, and **upload** methods

### Download
```
localhost:8080/api/download/YOUR_FILE_HASH
```
### Delete
```
localhost:8080/api/delete/YOUR_FILE_HASH
```
### Upload
```
curl -X POST -d @test.txt 'localhost:8080/api/upload'
```
