const mongoose = require('mongoose');

const SettingsSchema = new mongoose.Schema({
  numberOfChairs: { type: Number, required: true },
  patientNurseRatio: { type: Number, required: true },
  openTime: { type: String, required: true },
  closeTime: { type: String, required: true },
  breakStartTime: { type: String, required: true },
  breakEndTime: { type: String, required: true },
  breakDuration: { type: Number, required: true },
  goals: {
    avgOvertimePerNurse: { type: Number, required: true },
    avgPatientWaitTime: { type: Number, required: true },
    avgNursesWithLunchBreak: { type: Number, required: true },
    avgNursesWithoutOvertime: { type: Number, required: true },
    avgOntimeClosesPerWeek: { type: Number, required: true }
  }
});

module.exports = mongoose.model('Settings', SettingsSchema);