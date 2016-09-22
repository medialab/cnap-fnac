# cnap-fnac

**usage**

1. copy `config.sh.example` to `config.sh` and update values
2. `mkdir data` creates data directory
3. `bash download_all_data.sh` download data from api into json files
4. `mkdir data;mongod --dbpath ./db`
5. `npm install` get dependencies 
6. `node dataToMongo.js` insert data into a mango database

