const mongoose = require('mongoose');

const artworkSchema = mongoose.Schema({
	authors: [{type: mongoose.Schema.Types.ObjectId, ref: 'Author'}]
});

module.exports = mongoose.model('Artwork', artworkSchema, 'Artwork');