const Tabletop = require('tabletop');

const key = '10vhd3bun8-dtGo7S2XuXyW3GWMIYrfwYbQTUlw3UhrA';

module.exports = function(dataset, cb) {
  Tabletop.init({
    key: key,
    callback: function(queries) {
      console.log(queries.content.elements);
      return cb(null, dataset);
    }
  })
}
