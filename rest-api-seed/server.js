'use strict';

const config = require('./config.json');
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const compression = require('compression');
const bodyParser = require('body-parser');

const port = process.env.PORT || 3005;

const app = express();

module.exports = app;

function listen () {
  if (app.get('env') === 'test') return;
  app.listen(port);
  console.log('Express app started on port ' + port);
}

function connect () {
  var options = { server: { socketOptions: { keepAlive: 1 } } };
  console.log('connected to mongoose on ', config.mongoUrl);
  return mongoose.connect(config.mongoUrl, options).connection;
}

connect()
  .on('error', console.log)
  .on('disconnected', connect)
  .once('open', listen);

app.use(compression({
	threshold: 512
}));

app.use(cors());

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

/*****
ROUTES
*****/

require('./endpoints/');