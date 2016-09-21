var oboe = require('oboe');
var fs = require('fs');
var async = require('async');
var MongoClient = require('mongodb').MongoClient

var index = 0; // control index
var url = 'mongodb://localhost:27017/myproject';
var objectsToProcess = []; // list of json objects to process

var AUTHOR_COLLECTION = 'Author';
var ARTWORK_COLLECTION = 'Artwork';

/**
 * Format and insert an artwork's array of authors objects in authors mongo collection
 */
function insertAuthors(artwork, db, callback) {
    var authors = artwork._source.ua.authors;
    db.collection(AUTHOR_COLLECTION).insert(authors,  function(err) {
    	// not catching errors because possible dupkeys that we don't care about
    	callback(null);
    });
}

/**
 * Format and insert artwork object in artworks mongo collection
 */
function insertArtwork(artwork, db, callback) {
    var artworkSimplified = artwork._source.ua;
    artworkSimplified._id = artwork._id;
    db.collection(ARTWORK_COLLECTION).insert(artworkSimplified, function(err){
    	// not catching errors because possible dupkeys that we don't care about
    	callback(null);
    });
}

/**
 * Populate db with a native artwork data
 */
function populateDbWithArtwork(artwork, db, callback) {
    index++;
    if (index % 10000 === 0) {
        console.log('populating db with artwork n°%s', index);
    }
    // chaining the two insert operations
    async.waterfall([
        function(cback1) {
            insertArtwork(artwork, db, cback1);
        },
        function(cback2) {
            insertAuthors(artwork, db, cback2);
        }
    ], function(err) {
        if (index % 10000 === 0) {
            console.log('done populating with artwork n°%s', index);
        }
        callback(err, artwork);
    });
}

/**
 * Main function
 */
function dataToMongo() {
    async.waterfall([
        // connect to mongo
        function(callback) {
            console.log('connecting to db');
            MongoClient.connect(url, callback);
        },
        function(db, callback) {
            // chaining the two collections creation operations
            async.waterfall([
                function(cback1) {
                    console.log('creating authors collections');
                    db.createCollection(AUTHOR_COLLECTION, {}, cback1);
                },
                function(col, cback2) {
                    console.log('creating artworks collections');
                    db.createCollection(ARTWORK_COLLECTION, {}, cback2);
                }
            ], function(err, collection) {
                console.log('collections (re) created, errors: ', err);
                callback(err, db);
            });
        },
        function(db, callback) {
            console.log('cleaning collections');
            var authors = db.collection(AUTHOR_COLLECTION);
            // clear previous documents
            authors.removeMany();
            var artworks = db.collection(ARTWORK_COLLECTION);
            // clear previous documents
            artworks.removeMany();
            callback(null, db);
        },
        function(db, callback) {
            console.log('starting to parse data in json');
            oboe(fs.createReadStream('./data/artworks-all.json'))
                .node('![*]', function(node) {
                    index++;
                    objectsToProcess.push(node);
                    if (index % 10000 === 0) {
                        console.log('done parsing node n°%s', index);
                    }
                })
                .done(function(results) {
                    index = 0;
                    console.log('done with streaming json');
                    callback(null, db);
                });
        },
        function(db, callback) {
            console.log('starting populating the mongo base with %s artwork objects', objectsToProcess.length);
            async.mapSeries(objectsToProcess, function(node, nodeCallback) {
                populateDbWithArtwork(node, db, nodeCallback);
            }, function(errors) {
                console.log('done populating with all objects');
                callback(errors, db);
            })
        }
    ], function(err, db) {
        console.log('done with everything, closing db');
        db.close();
    });
}

dataToMongo();
