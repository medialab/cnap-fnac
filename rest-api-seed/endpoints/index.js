const app = require('../server');

app.get('/cover/:collection?', require('./cover'));
app.get('/artworks', require('./artworks'));
app.get('/authors', require('./authors'));
app.get('/trajectories', require('./trajectories'));

