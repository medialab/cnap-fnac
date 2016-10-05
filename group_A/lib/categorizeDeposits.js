const Tabletop = require('tabletop');
const depotsCatKey = '1cERZAzmbMZYr7Yge8Fm8zO4KV2-A29fDIjgByBKUYpc';

module.exports = function(dataset, cb) {
	
	console.log('going to ask for deposits categories');
    Tabletop.init( { 
    	key: depotsCatKey,
           callback: function(categories, tabletop) {
           	// console.log('got response');
           	const keys = {};
           	const output = dataset.map(function(datum) {
           		if (datum.localisation_if_deposit) {
           			categories.some(function(category) {
           				if (datum.localisation_if_deposit.toLowerCase().indexOf(category.Si.toLowerCase()) > -1) {
           					datum.localisation_if_deposit_category = category.Alors.trim();
           					return true;
           				}
           			});
           		}

           		if (datum.localisation_if_deposit && datum.localisation_if_deposit_category === undefined) {
           			keys[datum.localisation_if_deposit] = keys[datum.localisation_if_deposit] === undefined ? 1 : keys[datum.localisation_if_deposit]+1;
           		}
           		return datum;
           	});
           	var count = 0;
           	Object.keys(keys).sort(function(a, b) {
           		if (keys[a] > keys[b]) {
           			return 1;
           		} else return -1;
           	})
           	console.log('calling back');
           	cb(null, dataset);
			},
           simpleSheet: true 
    });
}