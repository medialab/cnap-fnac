'use strict';
const mongoose = require('mongoose');
const async = require('async');

const Artwork = require('../models/artwork');
const parseQueryParams = require('../lib/parseQueryParams');
const convertToCsv = require('../lib/convertToCsv');
const listYearsCount = require('../lib/listYearsCount');
const categorizeDeposits = require('../lib/categorizeDeposits');


/**
 * An endpoint example that retrives some artworks and return them as json objects or as a csv file
 */
const endpoint = function(req, res) {
    const data = [];
    let i = 0;
    const reqParams = req.query;
    // map request query params to db querying params
    const queryParams = parseQueryParams(req.query);
    // setup db query
    const mongoQuery = {};
    console.log('query params:', queryParams);
    if (queryParams.query.from && queryParams.query.to) {
        mongoQuery.$where = 'this.acquisition_year !== undefined && this.acquisition_year >=  ' + queryParams.query.from + ' && this.acquisition_year <= ' + queryParams.query.to;
        console.log('queryParams', mongoQuery);
    }
    async.waterfall([
        listYearsCount,
        function(yearsCount, cb) {
            console.log(yearsCount);
            Artwork.find(mongoQuery)
                .lean()
                .find({$where: 'this.acquisition_year !== undefined && this.acquisition_year >=  1980 && this.acquisition_year <= 2016'})
                // .limit(queryParams.limit)
                // execute db query
                .exec(function(err, doc) {
                    categorizeDeposits(doc, function(err, categories) {
                        const documents = doc.map(function(work) {
                            if (work.localisation_if_deposit) {
                                if (work.localisation_if_deposit.match(/([\d]{4})/)) {
                                    work.localisation_if_deposit_year = +work.localisation_if_deposit.match(/([\d]{4})/)[0];
                                } else work.localisation_if_deposit_year = undefined;
                            }

                            if (work.localisation_if_deposit_year) {
                                work.weight = 1/yearsCount[work.localisation_if_deposit_year];
                            }
                            work.deposit_year = work.localisation_if_deposit_year > 1980 ? work.localisation_if_deposit_year : undefined;
                            return {
                                'deposit_year': work.deposit_year,
                                'deposit_loc': work.localisation_if_deposit,
                                'deposit_category': work.localisation_if_deposit_category,
                                'weight': work.weight
                            } 
                        }).filter(function(obj) { return obj.deposit_loc !== undefined});
                        console.log(documents);
                        cb(null, documents);
                    });
                });
        }
    ], function (err, documents) {
        if (err) {
                        res.status(500).json(err);
                        return console.error(err);
                    // handle csv conversion
                    } else if (queryParams.convertToCsv) {
                        convertToCsv(documents, function (err, csvStr) {
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
                        res.status(200).json(documents);
                    }
    });
}

module.exports = endpoint;
