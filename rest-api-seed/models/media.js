const mongoose = require('mongoose');

const mediaSchema = mongoose.Schema({
});

module.exports = mongoose.model('Media', mediaSchema, 'Media');