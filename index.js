var oboe = require('oboe');
var fs = require('fs');
var async = require('async');
var MongoClient = require('mongodb').MongoClient

var index = 0;

var url = 'mongodb://localhost:27017/myproject';

var authors, artworks;

function insertArtwork(artwork, db, callback) {
  // Get the documents collection

  // Insert some documents
  artworks.insert(artwork, {}, callback);
}


function insertAuthors(artwork, db, callback) {
  // Get the documents collection
  // console.log('will insert author');
  // Insert some documents
  authors.insert(artwork._source.ua.authors, {}, callback);
  // console.log('inserted authors');
}

function onNode(artwork, db, callback) {
	if (index % 100 === 0) {
		console.log('on node', index);
	}
	async.waterfall([
		function(cback1) {
			insertArtwork(artwork, db, cback1);
		},
		function(db, cback2) {
			insertAuthors(artwork, db, cback2);
		}
	], callback);
};

async.waterfall([
	function(callback) {
		MongoClient.connect(url, callback);
	},
	function(db, callback) {
		console.log('connecting');
		db.createCollection('authors', {}, callback);
  		artworks = db.collection('documents');
  		authors = db.collection('authors');
	},
	function (db ,callback) {
		console.log('starting to feed data');
		oboe(fs.createReadStream('./input/artworks-all.json'))
			.node('![*]', function(node) {
				index++;
				onNode(node, db, function(err) {
					// if (err)
					// 	console.log('err on node', err);
				});
			})
			.done(function(big){
				console.log('done');
				console.log('I am still alive ');
				callback(db);
			})
	}
], function(err, db) {
	console.log('done, err: ', err);
	db.close();
})