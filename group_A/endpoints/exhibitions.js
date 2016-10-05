'use strict';
const mongoose = require('mongoose');
const async = require('async');

const Artwork = require('../models/artwork');
const parseQueryParams = require('../lib/parseQueryParams');
const convertToCsv = require('../lib/convertToCsv');
const listYearsCount = require('../lib/listYearsCount');


function transformDoc(doc) {
    console.log(doc);
    return doc;
}

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
                .find({$where: 'this.acquisition_year !== undefined && this.acquisition_year >=  1980 && this.acquisition_year <= 2010'})
                // .limit(queryParams.limit)
                // execute db query
                .exec(function(err, doc) {
                    // const doc = inputDocs;
                    console.log('ready');
                    const documents = doc.map(function(d) {
                        const exhibitions = d.exhibitions_history;
                        const dernierDepot = d.localisation_if_deposit;
                        const acquisition = d.acquisition_year;
                        const transfert = d.localization_if_external;
                        const natio = d.authors_nationality;
                        return {
                            acquisition: acquisition,
                            transfert: transfert,
                            dernierDepot : dernierDepot,
                            expositions: Array.isArray(exhibitions) ? exhibitions : [],
                            domain: d.domain.replace(/,/g, '-'),
                            acquisition_year: d.acquisition_year,
                            acquisition_mode: d.acquisition_mode.replace(/,/g, '-'),
                            creation_date: d.date_creation,
                            id: d._id,
                            nationality_artist: natio
                        }
                    }).map(function(d, i) {
                        if (i % 1000 === 0) {
                            console.log(i);
                        }
                        if (Array.isArray(d.expositions) && d.expositions.length > 0) {
                            d.expositions = d.expositions.map(function(expo) {
                                var country,countryFr;
                                const expression = expo.indexOf(':') > -1 ?
                                    expo.split(':')[1].split(',')[0]
                                    : expo.split(':')[0].split(',')[0];
                                const address = expression.match(/([\w-']+) ?\(([\w]+)\)/i);
                                if (address) {
                                    var country = address[2];
                                    if (country) {
                                        countryFr = country.trim().toLowerCase().indexOf('fran') === 0 ? 'en France': 'à l\'étranger';
                                    }
                                }
                                // console.log(expo);
                                if (expo.match(/([\d]{4})/)) {
                                    var date = +expo.match(/([\d]{4})/)[0];
                                    if (date) {
                                        date = (date >= 1980  && date <= 2016) ?
                                                date: undefined;
                                    }
                                    return {
                                        text: expo,
                                        dateExpo: date,
                                        expoCountry: country,
                                        expoCountrySimpl: countryFr
                                    };
                                }
                                return undefined;
                            }).filter(function(expo) {
                                return expo !== undefined;
                            });
                        }
                        
                        var totalExpos = d.expositions.length;


                        return d.expositions.sort(function(a, b) {
                            if (a.year > b.year) {
                                return 1;
                            } else return -1;
                        }).map(function(datum) {
                            if (datum.dateExpo) {
                                datum.weight = 1/yearsCount[datum.dateExpo];
                            }
                            datum.domain = d.domain;
                            datum.acquisition_year = d.acquisition_year;
                            datum.acquisition_mode = d.acquisition_mode;
                            datum.id = d.id;
                            datum.creation_date = d.creation_date;
                            datum.nationality_artist = d.nationality_artist;
                            if (datum.nationality_artist) {
                                datum.artistFr = d.nationality_artist.toLowerCase().trim().indexOf('fran') === 0 ? 'français': 'étranger';
                            }
                            if (datum.artistFr && datum.expoCountrySimpl) {
                                if (datum.artistFr === 'français' && datum.expoCountrySimpl === 'à l\'étranger') {
                                    datum.mouvement = 'export';
                                }
                                if (datum.artistFr === 'étranger' && datum.expoCountrySimpl === 'en France') {
                                    datum.mouvement = 'import';
                                }
                                if (datum.artistFr === 'français' && datum.expoCountrySimpl === 'en France') {
                                    datum.mouvement = 'domestique';
                                }
                                if (datum.artistFr === 'étranger' && datum.expoCountrySimpl === 'à l\'étranger') {
                                    datum.mouvement = 'étranger';
                                }
                            }

                            return datum;
                        });
                    }).reduce(function(total, expositions) {
                        return total.concat(expositions);
                    }, [])

                    console.log('done');

                    cb(null, documents);
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
