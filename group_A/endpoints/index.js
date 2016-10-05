const app = require('../server');

app.get('/cover/:collection?', require('./cover'));
app.get('/artworks', require('./artworks'));
app.get('/exhibitions', require('./exhibitions'));
app.get('/authors', require('./authors'));
app.get('/trajectories', require('./trajectories'));

app.get('/acquisitions', require('./acquisitions'));
app.get('/deposits', require('./deposits'));

