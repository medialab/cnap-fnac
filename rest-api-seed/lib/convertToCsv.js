const jsoncsv = require('json-csv')

module.exports = function(docs, callback, inputFields) {
	const fields = [];
	console.log('convert to csv', fields);
	if (fields === undefined || fields.length === 0) {
		// quick and dirty columns making
		var i = 0;
		console.log('determining fields');
		while (i < 1000) {
			Object.keys(docs[i]).forEach(function(key) {
				const field = fields.find(function(f) {
					return f.name === key;
				});
				if (field === undefined) {
					fields.push({
			            name: key,
			            label: key
			        });
				}
		    });
			i++;
		}
		console.log('done');
	} else {
		fields = inputFields;
	}
    jsoncsv.csvBuffered(docs, {fields: fields}, callback);
}