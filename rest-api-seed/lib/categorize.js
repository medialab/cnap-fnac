const Tabletop = require('tabletop');
const depotsCatKey = '1cERZAzmbMZYr7Yge8Fm8zO4KV2-A29fDIjgByBKUYpc';

module.exports = function(dataset, cb) {
    Tabletop.init( { key: depotsCatKey,
                   callback: function(categories, tabletop) {
                   	const output = dataset.map(function(datum) {
                   		if (datum.localisation_if_deposit) {
                   			categories.some(function(category) {
                   				if (datum.localisation_if_deposit.indexOf(category.Si) > -1) {
                   					datum.localisation_if_deposit_category = category.Alors;
                   					console.log(datum.localisation_if_deposit_category);
                   					return true;
                   				}
                   			})
                   		}
                   		return datum;
                   	});
                   	cb(null, dataset);
					},
                   simpleSheet: true } )
}