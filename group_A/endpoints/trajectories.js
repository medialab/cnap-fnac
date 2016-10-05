'use strict';
const mongoose = require('mongoose');

const Artwork = require('../models/artwork');
const parseQueryParams = require('../lib/parseQueryParams');
const convertToCsv = require('../lib/convertToCsv');


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
                    creation_date: d.creation_date,
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
                            // console.log(country);
                        }
                        if (expo.match(/([\d]{4})/)) {
                            const date = +expo.match(/([\d]{4})/)[0];
                            return date;
                            /*return {
                                date: date,
                                country: country,
                                countryFr: countryFr
                            };*/
                        }
                        
                        return undefined//  {};
                    }).filter(function(expo) {
                        return expo !== undefined;
                    });
                        
                }
                if (d.transfert) {
                    if (d.transfert.match(/([\d]{4})/)) {
                        d.transfertRaw = d.transfert;
                        d.transfert = +d.transfert.match(/([\d]{4})/)[0];
                    } else d.transfert = undefined;
                }

                if (d.dernierDepot) {
                    if (d.dernierDepot.match(/([\d]{4})/)) {
                        d.dernierDepot = +d.dernierDepot.match(/([\d]{4})/)[0];
                    } else d.dernierDepot = undefined;
                }

                const steps = [];
                if (d.acquisition !== undefined) {
                    steps.push({
                        step: 'acquisition',
                        year: d.acquisition
                    });
                }
                if (d.transfert !== undefined) {
                    steps.push({
                        step: 'transfert',
                        year: d.transfert,
                        transfertRaw: d.transfertRaw
                    });
                }

                if (d.dernierDepot !== undefined) {
                    steps.push({
                        step: 'dépot',
                        year: d.dernierDepot
                    });
                }
                
                var nbExpos = 0;
                if (d.expositions.length) {
                    nbExpos ++;
                    d.expositions.forEach(function(expo){
                        steps.push({
                            step: 'exposition',
                            year: expo
                        })
                    })
                }
                d.nbExpos = nbExpos;

                const order = steps.sort(function(a, b) {
                    if (a.year > b.year) {
                        return 1;
                    } else return -1;
                });

                const final = order.slice();
                while (final[0].step !== 'acquisition' &&
                        final.length > 1) {
                    final.shift();
                }
                /*
                if (final[0].step === 'acquisition') {
                    final.unshift({step: ''});
                }
                if (final[1].step === 'acquisition') {
                    final.unshift({step: ''});
                }
                if (final[2].step === 'acquisition') {
                    final.unshift({step: ''});
                }
                if (final[3].step === 'acquisition') {
                    final.unshift({step: ''});
                }
                if (final[4].step === 'acquisition') {
                    final.unshift({step: ''});
                }
                if (final[5].step === 'acquisition') {
                    final.unshift({step: ''});
                }
                */

                let objet = {};

                objet.acquisition_year = d.acquisition_year;
                objet.acquisition_mode = d.acquisition_mode;
                objet.creation_date = d.creation_date;
                objet.domain = d.domain;

                let acquisitionStep;
                final.some(function(step, stepI) {
                    if (step.step === 'acquisition')  {
                        acquisitionStep = stepI;
                        return true;
                    }
                });

                // console.log('calculating adn from ', acquisitionStep);
                // calc adn
                objet.adn_complet = final.slice(acquisitionStep).reduce(function(adn, step) {
                    switch(step.step) {
                        case 'acquisition':
                            adn += 'A';
                        break;
                        case 'exposition':
                            adn += 'E';
                        break;
                        case 'dépot':
                            adn += 'D';
                        break;
                        case 'transfert':
                            adn += 'T';
                        break;
                        default:
                        break;
                    }
                    return adn;
                }, '');

                objet.adn_simplifie = objet.adn_complet.replace(/[E]+/g, 'E');
                objet = final.reduce(function(obj, step, i) {
                    obj['étape ' + (i+1)] = step.step;
                    return obj;
                }, objet);


                objet.probaExpoAns = d.expositions.length/30;
                objet.probaEvtsAns = final.length/30;
                objet.natioArtiste = d.nationality_artist;
                if (objet.natioArtiste) {
                    objet.artisteDom = objet.natioArtiste.indexOf('français') === 0 ? 'français': 'étranger';
                }
                return objet;
            });

            console.log('done');

            if (err) {
                res.status(500).json(err);
                return console.error(err);
            // handle csv conversion
            } else if (queryParams.convertToCsv) {
                let fields = [];
                for (var i = 1 ; i <= 20 ; i++) {
                    fields.push('étape ' + i);
                }
                fields = fields.concat([
                    'acquisition_year',
                    'acquisition_mode',
                    'creation_date',
                    'domain',
                    'adn_complet',
                    'adn_simplifie',
                    'nbExpos',
                    'probaExpoAns',
                    'probaEvtsAns',
                    'artisteDom',
                    'natioArtiste'
                ]);
                let csvStr = fields.join(',') + '\n';
                documents.forEach(function(document) {
                    csvStr += fields.map(function(field) {
                        return document[field];
                    }).join(',') + '\n';
                });
                console.log('csv done');
                res.header("Content-Disposition,attachment;filename=data.csv");
                res.type("text/csv");
                res.status(200).send(csvStr);
            } else {
                console.log('returning');
                res.status(200).json(documents);
            }
        });
}

module.exports = endpoint;
