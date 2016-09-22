# cnap-fnac

**usage**

1. copy `config.sh.example` to `config.sh` and update values
2. `bash download_all_data.sh` download data from api into json files
3. `mongod --dbpath ./db`
4. `npm install` get dependencies
5. `node dataToMongo.js` insert data into a mango database

