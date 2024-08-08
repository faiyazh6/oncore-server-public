const mongoose = require('mongoose');

const RoiMetricsSchema = new mongoose.Schema({
  date: { type: String, required: true },
  unoptimized: {
    avgOvertimePerNurse: { type: Number, required: true },
    avgPatientWaitTime: { type: Number, required: true },
    avgNursesWithLunchBreak: { type: Number, required: true },
    avgNursesWithoutOvertime: { type: Number, required: true },
    avgOntimeClosesPerWeek: { type: Number, required: true }
  },
  optimized: {
    avgOvertimePerNurse: { type: Number, required: true },
    avgPatientWaitTime: { type: Number, required: true },
    avgNursesWithLunchBreak: { type: Number, required: true },
    avgNursesWithoutOvertime: { type: Number, required: true },
    avgOntimeClosesPerWeek: { type: Number, required: true }
  }
});

module.exports = mongoose.model('RoiMetrics', RoiMetricsSchema);