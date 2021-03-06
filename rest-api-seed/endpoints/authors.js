'use strict';
const mongoose = require('mongoose');

const Author = require('../models/author');
const parseQueryParams = require('../lib/parseQueryParams');
const convertToCsv = require('../lib/convertToCsv');


/**
 * An endpoint example that retrives some artworks and return them as json objects or as a csv file
 */
const endpoint = function(req, res) {
    const reqParams = req.query;
    // map request query params to db querying params
    const queryParams = parseQueryParams(req.query);
    // setup db query
    Author.find(queryParams.query)
        .limit(queryParams.limit)
        .lean()
        // execute db query
        .exec(function(err, doc) {
            if (err) {
                res.status(500).json(err);
                return console.error(err);
            // handle csv conversion
            } else if (queryParams.convertToCsv) {
                
            	convertToCsv(doc, function (err, csvStr) {
            		if (err) {
            			res.status(500).send(err);
            		} else {
            			console.log(csvStr);
            			res.header("Content-Disposition,attachment;filename=data.csv");
		                res.type("text/csv");
		                res.send(200, csvStr);
            		}
            	});
            } else {
                res.status(200).json(doc);
            }
        });
}

module.exports = endpoint;