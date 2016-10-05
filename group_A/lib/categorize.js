const Tabletop = require('tabletop');
const depotsCatKey = '1cERZAzmbMZYr7Yge8Fm8zO4KV2-A29fDIjgByBKUYpc';

module.exports = function(dataset, cb) {
	const cities = {};
	var cleanAddress, city, country;
	// console.log('begining to process dates');
	// var totalEtapes = 0;
	console.log('go addresses');
	dataset.forEach(function(datum) {
		if (Array.isArray(datum.exhibitions_history)) {
			datum.exhibitions_history.forEach(function(e) {
				// console.log(e);
				// console.log('----');
				const expression = e.indexOf(':') > -1 ?
					e.split(':')[1].split(',')[0]
					: e.split(':')[0].split(',')[0];
				const address = expression.match(/([\w-']+) ?\(([\w]+)\)/i);
				if (address) {
					console.log(address);
					cleanAddress = address[0];
					city = address[1];
					cities[city] = cities[city] === undefined ? 1 : cities[city] + 1;
				}
			});
		}
	});
	console.log('done');
	cb(dataset);
		/*
		
		if (datum.localisation_if_deposit !== undefined &&
			datum.localisation_if_deposit.length > 0) {
			totalEtapes ++;
			const loc = datum.localisation_if_deposit.split(':')[1].trim();
			const address1 = loc.match(/([\w-']+) ?\(([\w]+)\)/i);
			if (address1) {
				cleanAddress = loc.trim();
				city = address1[2];
				cities[city] = cities[city] === undefined ? 1 : cities[city] + 1;
			}
		}
		

		if (datum.localization_if_external !== undefined &&
			datum.localization_if_external.length > 0) {
			totalEtapes ++;
			var parts = datum.localization_if_external.split(':');
			parts = parts.length > 1 ? parts[1] : parts[0];
			parts = parts.trim();
			
			const address2 = parts.match(/([\w-']+) ?\(([\w]+)\)/i);
			if (address2) {
				cleanAddress = parts;
				city = address2[2];
				cities[city] = cities[city] === undefined ? 1 : cities[city] + 1;
			}
		}
	});
	console.log('done');
	var total = 0;
	Object.keys(cities).sort(function(a, b) {
		if (cities[a] > cities[b]) {
			return 1;
		} else return -1;
	}).forEach(function(key) {
		total += cities[key];
		console.log(key, cities[key]);
	});
	console.log('Total des villes différentes à localiser', Object.keys(cities).length);

	console.log('Total des lieux trouvés / étapes : ', total, '/', totalEtapes);

	cb(dataset);
	*/
	/*console.log('going to ask');
    Tabletop.init( { 
    	key: depotsCatKey,
           callback: function(categories, tabletop) {
           	// console.log('got response');
           	const keys = {};
           	const output = dataset.map(function(datum) {
           		if (datum.localisation_if_deposit) {
           			categories.some(function(category) {
           				if (datum.localisation_if_deposit.toLowerCase().indexOf(category.Si.toLowerCase()) > -1) {
           					datum.localisation_if_deposit_category = category.Alors;
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
           	cb(dataset);
			},
           simpleSheet: true 
    });
    */
}