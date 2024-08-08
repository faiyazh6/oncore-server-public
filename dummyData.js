const mongoose = require('mongoose');
const dotenv = require('dotenv');
const Schedule = require('./models/Schedule');
const RoiMetrics = require('./models/RoiMetrics');
const Settings = require('./models/Settings');
const TemplateSchedule = require('./models/TemplateSchedule');

dotenv.config();

const connectDB = async () => {
  try {
    await mongoose.connect(process.env.MONGO_URI, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });
    console.log('MongoDB Connected...');
  } catch (err) {
    console.error(err.message);
    process.exit(1);
  }
};

const createDummyData = async () => {
  await connectDB();

  // Clear existing data
  await Schedule.deleteMany({});
  await RoiMetrics.deleteMany({});
  await Settings.deleteMany({});
  await TemplateSchedule.deleteMany({});

  // Create dummy schedules
  const schedules = [
    {
      date: new Date(),
      patients: [
        {
          patientId: 'P001',
          readyTime: '08:00',
          actualStartTime: '08:10',
          length: 60,
          acuity: 'Medium',
          assignedChair: 'C1'
        },
        {
          patientId: 'P002',
          readyTime: '08:30',
          actualStartTime: '08:40',
          length: 90,
          acuity: 'High',
          assignedChair: 'C2'
        }
      ],
      nurses: [
        {
          nurseId: 'N001',
          assignedPatients: ['P001', 'P002'],
          startTime: '08:00',
          endTime: '16:00'
        }
      ],
      uploadedAt: new Date()
    }
  ];

  // Create dummy ROI metrics
  const roiMetrics = [
    {
      date: new Date(),
      unoptimized: {
        avgOvertimePerNurse: 30,
        avgPatientWaitTime: 20,
        avgNursesWithLunchBreak: 5,
        avgNursesWithoutOvertime: 8,
        avgOntimeClosesPerWeek: 3
      },
      optimized: {
        avgOvertimePerNurse: 10,
        avgPatientWaitTime: 10,
        avgNursesWithLunchBreak: 10,
        avgNursesWithoutOvertime: 9,
        avgOntimeClosesPerWeek: 5
      }
    }
  ];

  // Create dummy settings
  const settings = {
    numberOfChairs: 20,
    goals: {
      avgOvertimePerNurse: 10,
      avgPatientWaitTime: 15,
      avgNursesWithLunchBreak: 10,
      avgNursesWithoutOvertime: 10,
      avgOntimeClosesPerWeek: 5
    }
  };

  // Create dummy template schedules
  const templateSchedules = [
    {
      templateName: 'Weekday Template',
      day: 'Monday',
      schedule: [
        {
          time: '08:00',
          patientCounts: [
            { durationType: '1', count: 3 },
            { durationType: '2', count: 5 },
          ]
        },
        {
          time: '09:00',
          patientCounts: [
            { durationType: '1', count: 2 },
            { durationType: '3-5', count: 1 },
          ]
        }
      ]
    }
  ];

  await Schedule.insertMany(schedules);
  await RoiMetrics.insertMany(roiMetrics);
  await Settings.create(settings);
  await TemplateSchedule.insertMany(templateSchedules);

  console.log('Dummy data inserted');
  process.exit();
};

createDummyData();