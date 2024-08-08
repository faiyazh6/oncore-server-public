const mongoose = require('mongoose');

const ScheduleSchema = new mongoose.Schema({
  date: { type: String, required: true },
  patients: [
    {
      patientId: { type: Number, required: true },
      patientMRN: { type: Number, required: true },
      patientName: { type: String, required: true },
      readyTime: { type: Number, required: true },
      dueTime: { type: Number, required: true },
      actualStartTime: { type: Number, required: true },
      length: { type: Number, required: true },
      acuity: { type: Number, required: true },
      assignedChair: { type: Number, required: true },
      assignedNurse: { type: Number, required: true }
    }
  ],
  nurses: [
    {
      nurseId: { type: Number, required: true },
      nurseName: { type: String, required: true },
      nurseEmail: { type: String, required: true },
      assignedPatients: [Number],
      startTime: { type: Number, required: true },
      endTime: { type: Number, required: true }
    }
  ],
  chairs: [
    {
      chairId: { type: Number, required: true },
      assignedPatients: [Number],
    }
  ],
  actualUtilization: [
    {
      time: { type: Number, required: true },
      patientCount: { type: Number, required: true }
    }
  ],
  naiveUtilization: [
    {
      time: { type: Number, required: true },
      patientCount: { type: Number, required: true }
    }
  ],
  scheduledUtilization: [
    {
      time: { type: Number, required: true },
      patientCount: { type: Number, required: true }
    }
  ],
  uploadedAt: { type: String, required: true }
});

module.exports = mongoose.model('Schedule', ScheduleSchema);