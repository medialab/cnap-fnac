'use strict';
const mongoose = require('mongoose');
const async = require('async');
const Tabletop = require('tabletop');

const Artwork = require('../models/artwork');
const parseQueryParams = require('../lib/parseQueryParams');
const convertToCsv = require('../lib/convertToCsv');

const categorize = require('../lib/categorize');
const key = '10vhd3bun8-dtGo7S2XuXyW3GWMIYrfwYbQTUlw3UhrA'



/**
 * An endpoint example that retrives some artworks and return them as json objects or as a csv file
 */
module.exports = function(req, res) {
    const reqParams = req.query;
    const queryParams = parseQueryParams(req.query);

    Tabletop.init({
        key: key,
        simpleSheet: true,
        callback: function(queries) {
            async.map(
                queries,
                function(item, cb) {
                    const rgx = item.regex.split(' | ').join('|');
                    const query = {'$regex': new RegExp(rgx, 'i')};
                    if (!!item.exclude) {
                        query['$not'] = new RegExp(item.exclude.split(' | ').join('|'), 'i');
                    }

                    Artwork
                        .find({
                            'domain_description_mst': query,
                            'acquisition_year': {'$gt': +queryParams.year || 1945}
                        })
                        .limit(queryParams.limit || 1000)
                        .lean()
                        .exec(function(err, doc) {
                            if (err) {
                                console.log(err);
                                cb(err, null);
                            } else {
                                // Add material category as a new field.
                                doc.material = item.category.toLowerCase();
                                cb(null, doc);
                            }
                        })
                },
                function(err, results) {
                    if (err) {
                        res.status(500).json(err);
                    } else if (queryParams.convertToCsv) {
                        convertToCsv(results[0], function (err, csvStr) {
                            if (err) {
                                res.status(500).send(err);
                            } else {
                                res.header("Content-Disposition,attachment;filename=data.csv");
                                res.type("text/csv");
                                res.send(200, csvStr);
                            }
                        });
                    } else {
                        res.status(200).json(results);
                    }
                }
            )
        }
    });
}
