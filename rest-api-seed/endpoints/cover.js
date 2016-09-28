'use strict';
const mongoose = require('mongoose');
const async = require('async');

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
    let Collection;
    if (req.params.collection === 'media') {
        Collection = require('../models/media');
    } else if (req.params.collection === 'author') {
        Collection = require('../models/author');
    } else  {
        Collection = require('../models/artwork');
    }

    async.waterfall([
        function(numberCb) {
            Collection.count().exec(numberCb)
        },
        function(totalNumber, coverageCb) {
            Collection.find(queryParams.query)
            .limit(100)
            // execute db query
            .exec(function(err, doc) {
                if (err) {
                    coverageCb(err);
                    // handle csv conversion
                } else {
                    let dict = {};
                    let dictLength = 0;
                    // storing all possible values with 100 first items
                    doc.forEach(function(d) {
                        Object.keys(d._doc)
                        .forEach(function(key, index) {
                            if (dict[key] === undefined) {
                                dict[key] = typeof d._doc[key] === 'object' ? 
                                    Array.isArray(d._doc[key]) ?
                                        'array'
                                        : 'object'
                                : typeof d._doc[key];
                                dictLength ++;
                            }
                        });
                    });
                    const coverage = [];
                    let dictCovered = 0;
                    async.mapSeries(Object.keys(dict), async.ensureAsync(function(key, keyCb) {
                        const propInfo = {
                            key: key,
                            valueType: dict[key]
                        };
                        console.log('processing coverage for key ', key, ' of type ', dict[key]);
                        switch (dict[key]) {

                            case 'string':
                                const expression = 'this.' + key + ' !== undefined && this.' + key + '.length > 0';
                                return Collection.count()
                                .$where(expression)
                                .exec(function (err, count) {
                                    if (err) {
                                        return console.log('error: ', err);
                                    }
                                    console.log('done for ', dictCovered, '/', dictLength , ': ', ', count is ', count);
                                    propInfo.numberCovered = count
                                    propInfo.proportionCovered = count/totalNumber;
                                    propInfo.percentageCovered = parseInt(count/totalNumber * 100);
                                    dictCovered++;
                                    keyCb(null, propInfo);
                                });

                            case 'array':

                                return Collection.count({
                                    [key] : { $exists: true, $not: {$size: 0} }
                                })
                                .exec(function (err, count) {
                                    if (err) {
                                        return console.log('error: ', err);
                                    }
                                    console.log('done for ', dictCovered, '/', dictLength , ': ', key, ', count is ', count);
                                    propInfo.numberCovered = count
                                    propInfo.proportionCovered = count/totalNumber;
                                    propInfo.percentageCovered = parseInt(count/totalNumber * 100);
                                    dictCovered++;
                                    keyCb(null, propInfo);
                                });


                            default:
                                return Collection.count({
                                    [key] : {$ne: null}
                                })
                                .exec(function (err, count) {
                                    if (err) {
                                        return console.log('error: ', err);
                                    }
                                    console.log('done for ', dictCovered, '/', dictLength , ': ', key, ', count is ', count);
                                    propInfo.numberCovered = count;
                                    propInfo.proportionCovered = count/totalNumber;
                                    propInfo.percentageCovered = parseInt(count/totalNumber * 100);
                                    dictCovered++;
                                    keyCb(null, propInfo);
                                });
                        }
                    }), coverageCb)
                }
            });
        }/*,
        function (propInfos, distinctCb) {

        }*/
    ], function (err, results) {
        console.log('done processing');
        if (err) {
            return res.status(500).json(err);
        } else if (queryParams.convertToCsv) {
            convertToCsv(results, function (err, csvStr) {
                    if (err) {
                        res.status(500).send(err);
                    } else {
                        console.log('ready to render to csv');
                        res.header("Content-Disposition,attachment;filename=data.csv");
                        res.type("text/csv");
                        res.send(200, csvStr);
                    }
                });
        } else res.status(200).json(results);
    });
}

module.exports = endpoint;
