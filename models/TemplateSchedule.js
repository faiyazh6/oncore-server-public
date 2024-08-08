const mongoose = require('mongoose');

const TemplateScheduleSchema = new mongoose.Schema({
  templateName: { type: String, required: true },
  schedule: [
    {
      time: { type: String, required: true },  // e.g., "08:00"
      patientCounts: [  // Array of patient counts per duration type
        {
          durationType: { type: String, required: true },  // e.g., "1", "2", "3-5", "6-8"
          count: { type: Number, required: true }
        }
      ]
    }
  ]
});

module.exports = mongoose.model('TemplateSchedule', TemplateScheduleSchema);