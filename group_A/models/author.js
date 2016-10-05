const mongoose = require('mongoose');

const authorSchema = mongoose.Schema({
});

module.exports = mongoose.model('Author', authorSchema, 'Author');