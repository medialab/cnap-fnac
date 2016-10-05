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
    console.log('rendering acquisitions');
    const reqParams = req.query;
    // map request query params to db querying params
    const queryParams = parseQueryParams(req.query);
    // setup db query
    Artwork.find(queryParams.query)
        .find({$where: 'this.acquisition_year !== undefined && this.acquisition_year >=  1980 && this.acquisition_year <= 2010'})
        .lean()
        // execute db query
        .exec(function(err, doc) {
            const y = doc.reduce(function(years, d) {
                const year = d.acquisition_year;
                years[year] = years[year] === undefined ? 1 :
                            years[year] + 1;
                return years;
            }, {});

            const output = Object.keys(y).map(function(year) {
                return {
                    year: +year,
                    count: y[year]
                }
            })

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
}

module.exports = endpoint;
