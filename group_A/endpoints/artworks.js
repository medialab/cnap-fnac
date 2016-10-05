'use strict';
const mongoose = require('mongoose');

const Artwork = require('../models/artwork');
const parseQueryParams = require('../lib/parseQueryParams');
const convertToCsv = require('../lib/convertToCsv');

const categorize = require('../lib/categorize');


/**
 * An endpoint example that retrives some artworks and return them as json objects or as a csv file
 */
const endpoint = function(req, res) {
    const reqParams = req.query;
    // map request query params to db querying params
    const queryParams = parseQueryParams(req.query);
    // setup db query
    Artwork.find(queryParams.query)
        .limit(1000)
        // .limit(queryParams.limit)
        .lean()
        // execute db query
        .exec(function(err, doc) {
            categorize(doc, function(output) {
                console.log('got output', output.length);
                if (err) {
                    res.status(500).json(err);
                    return console.error(err);
                // handle csv conversion
                } else if (queryParams.convertToCsv) {
                    
                    convertToCsv(output, function (err, csvStr) {
                        if (err) {
                            res.status(500).send(err);
                        } else {
                            // console.log(csvStr);
                            res.header("Content-Disposition,attachment;filename=data.csv");
                            res.type("text/csv");
                            res.send(200, csvStr);
                        }
                    });
                } else {
                    console.log('returning');
                    res.status(200).json(output);
                }
            });
        });
}

module.exports = endpoint;
