const mongoose = require('mongoose');

const NotificationSchema = new mongoose.Schema({
  notification_name: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    required: true,
  },
  person_id: {
    type: Number,
    required: true,
  },
  importance: {
    type: String,
    required: true,
  },
  time: {
    type: Date,
    required: true,
  },
  icon: {
    type: String,
    required: true,
  },
  active: {
    type: Boolean,
    default: true,
  },
});

module.exports = mongoose.model('Notification', NotificationSchema);