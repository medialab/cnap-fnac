var oboe = require('oboe');
var fs = require('fs');
var async = require('async');
var MongoClient = require('mongodb').MongoClient;
var filesystem = require('fs');

var index = 0; // control index
var url = 'mongodb://localhost:27017/myproject';

var duplicate_count = 0;
//var objectsToProcess = []; // list of json objects to process

var AUTHOR_COLLECTION = 'Author';
var ARTWORK_COLLECTION = 'Artwork';
var MEDIA_COLLECTION = 'Media';

var jsonList = filesystem.readdirSync('./data_cleaned');

/**
 * Format and insert an artwork's array of media objects in media mongo collection
 */
function insertMedias(artwork, db, callback) {
    var medias = artwork._source.ua.medias;
    async.mapSeries(medias, function(media, mediaCb) {
        db.collection(MEDIA_COLLECTION).updateOne({_id: media._id}, {
            $set: media,
            $addToSet: {artworks: artwork._id}
        }, {
            upsert: true
        }).then(function(err, res) {
            // not catching errors because possible dupkeys that we don't care about
            mediaCb(null);
        });
    }, function(err) {
        callback(err);
    });
}

/**
 * Format and insert an artwork's array of authors objects in authors mongo collection
 */
function insertAuthors(artwork, db, callback) {
   // console.log(artwork);
    var authors = artwork._source.ua.authors;
   // console.log('a');
    async.mapSeries(authors, function(author, authorCb) {
        db.collection(AUTHOR_COLLECTION).updateOne({_id: author._id}, {
            $set: author,
            $addToSet: {artworks: artwork._id}
        }, {
            upsert: true
        }).then(function(err, res) {
            // not catching errors because possible dupkeys that we don't care about
            authorCb(null);
        });
    }, function(err) {
        callback(err);
    });
}

/**
 * Format and insert artwork object in artworks mongo collection
 */
function insertArtwork(artwork, db, callback) {
    // un-nest artwork main information
    var artworkSimplified = artwork._source.ua.artwork;
    // store medias as an array of ids instead of complete objects
    artworkSimplified.medias = artwork._source.ua.medias ? 
        artwork._source.ua.medias
        .map(function(media) {
            return media._id;
        })
        : [];
    // store authors as an array of ids instead of complete objects
    artworkSimplified.authors = artwork._source.ua.authors ? 
        artwork._source.ua.authors
        .map(function(author) {
            return author._id;
        })
        : [];
    // keep top-level native artwork id
    artworkSimplified._id = artwork._id;
    db.collection(ARTWORK_COLLECTION).insert(artworkSimplified, function(err){
    	// not catching errors because possible dupkeys that we don't care about
    	if (err != null) {
    		duplicate_count++;
    	}
    	callback(null);
    });
}

/**
 * Populate db with a native artwork data
 */
function populateDbWithArtwork(artwork, db, callback) {
    var local_index = ++index;
    if (local_index % 10000 === 0) {
        console.log('populating db with artwork n°%s', local_index);
        stalked = 1;
    }
    // chaining the two insert operations
    async.waterfall([
        function(cback1) {
            insertAuthors(artwork, db, cback1);
        },
        function(cback2) {
            insertMedias(artwork, db, cback2);
        },
        function(cback3) {
            insertArtwork(artwork, db, cback3);
        },
    ], function(err) {
        if (local_index % 10000 === 0) {
            console.log('done populating with artwork n°%s', local_index);
        }
        callback(err, artwork);
    });
}

/**
 * Main function
 */
function dataToMongo() {
    async.waterfall(
    [
        // connect to mongo
        function(callback) {
            console.log('connecting to db');
            MongoClient.connect(url, callback);
        },
        function(db, callback) {
        	//db_co = db;
            // chaining the two collections creation operations
            async.waterfall([
                function(cback1) {
                    console.log('creating Media collection');
                    db.createCollection(MEDIA_COLLECTION, {}, cback1);
                },
                function(col, cback2) {
                    console.log('creating Author collection');
                    db.createCollection(AUTHOR_COLLECTION, {}, cback2);
                },
                function(col, cback3) {
                    console.log('creating Artwork collection');
                    db.createCollection(ARTWORK_COLLECTION, {}, cback3);
                }
            ], function(err, collection) {
                console.log('collections (re) created, errors: ', err);
                callback(err, db);
            });
        },
        function(db, callback) {
            console.log('cleaning collections');
            var medias = db.collection(MEDIA_COLLECTION);
            // clear previous documents
            medias.removeMany();
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
            //Make something with split files
            async.eachLimit(jsonList, 2,
            	function(file, nestedCallback) {
            		var smallTab = []
            		console.log('parsing '+file);
            		oboe(fs.createReadStream('./data_cleaned/'+file))
                	.node('![*]',
                	function(node) {
                	    smallTab.push(node);
                	}
                	).done(
                	function(results) {
                	    //console.log(smallTab.length);
                	    async.eachLimit(smallTab, 4,
                		    function(node, nodeCallback) {
                		        populateDbWithArtwork(node, db, nodeCallback);
                		    },
                		    function(err) {
                		        console.log(file+' errors: '+err);
                		    	console.log('done '+file);
                		    	nestedCallback(err);
                		    }
                		);
                	}
            		);
            	},
         		function(err){
         	   		console.log('Global errors: '+err);
            		console.log('done with streaming json');
            		callback(null, db);
            	}
            );
        }
    ], function(err, db) {
    	console.log(duplicate_count+' duplicates found');
        console.log('done with everything, closing db');
        db.close();
    });
}

dataToMongo();
