'use strict';
/**
 * Simple module for mapping url request db params to mongoose db request params
 */
module.exports = function(queryParams) {
	// set default limit for retried objects
    let limit = 1000;
    let convertToCsv = false;
    // bootstrap empty query object
    const query = {};
    // feed query object with req.query params
    Object.keys(queryParams).forEach(function(key) {
        if (queryParams[key] !== undefined) {
        	switch(key) {
        		case 'limit':
        			limit = +queryParams[key];
        			break;
        		case 'csv':
        			convertToCsv = true;
        			break;
        		default:
        			query[key] = queryParams[key];
        			break;
        	}
        }
    });
    return {
    	convertToCsv,
    	query,
    	limit,
    }
}