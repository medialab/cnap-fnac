const Artwork = require('../models/artwork');


module.exports = function(cb) {
    console.log('listing years count');
    Artwork.find({$where: 'this.acquisition_year !== undefined && this.acquisition_year >=  1980 && this.acquisition_year <= 2010'})
        .lean()
        // execute db query
        .exec(function(err, doc) {
            const y = doc.reduce(function(years, d) {
                const year = d.acquisition_year;
                years[year] = years[year] === undefined ? 1 :
                            years[year] + 1;
                return years;
            }, {});

            for (var i = 2011 ; i <= 2016 ; i++) {
                y[i] = y['2010'];
            }

            const output = Object.keys(y).map(function(year) {
                return {
                    year: +year,
                    count: y[year]
                }
            });
            console.log('done');
            cb(null, y);
        });
}