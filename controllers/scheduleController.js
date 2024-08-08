const Schedule = require('../models/Schedule');
const Settings = require('../models/Settings');
const connectDB = require('../config/db');
const ExcelJS = require('exceljs');
const { execFile } = require('child_process');
const dotenv = require('dotenv');

dotenv.config();
const uri = process.env.MONGO_URI;

exports.uploadSchedule = async (req, res) => {
  try {
    const file = req.file;
    const { date } = req.body;

    if (!file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    let patients = [];
    let nurses = [];

    if (file.mimetype.includes('spreadsheetml')) {
      const workbook = new ExcelJS.Workbook();
      await workbook.xlsx.load(file.buffer);

      const patientsSheet = workbook.getWorksheet(1);
      const nursesSheet = workbook.getWorksheet(2);

      patients = [];
      nurses = [];
      chairs = [];

      const convertExcelTimeToMinutes = (excelTime) => {
        const date = new Date(excelTime);
        const hours = date.getUTCHours();
        const minutes = date.getUTCMinutes();
        const minAfterMidnight = (hours * 60) + minutes;
        return minAfterMidnight;
      };

      patientsSheet.eachRow((row, rowNumber) => {
        if (rowNumber === 1) return; // Skip header row
        patients.push({
          patientId: Number(row.getCell('A').value),
          patientMRN: Number(row.getCell('B').value),
          patientName: row.getCell('C').value,
          readyTime: convertExcelTimeToMinutes(row.getCell('D').value),
          dueTime: convertExcelTimeToMinutes(row.getCell('F').value),
          actualStartTime: -1,
          length: Number(row.getCell('E').value),
          acuity: Number(row.getCell('G').value),
          assignedChair: -1,
          assignedNurse: -1
        });
      });

      nursesSheet.eachRow((row, rowNumber) => {
        if (rowNumber === 1) return; // Skip header row
        nurses.push({
          nurseId: Number(row.getCell('A').value), // Assuming Nurse is the identifier
          nurseName: row.getCell('B').value,
          nurseEmail: row.getCell('C').value,
          assignedPatients: [], // Placeholder, as not provided
          startTime: convertExcelTimeToMinutes(row.getCell('D').value),
          endTime: convertExcelTimeToMinutes(row.getCell('E').value)
        });
      });
    } else {
      return res.status(400).json({ error: 'Invalid file format' });
    }

    // Validate required fields
    for (const patient of patients) {
      if (patient.patientId == null || patient.patientMRN == null || patient.patientName == null || patient.readyTime == null || patient.dueTime == null || patient.length == null || patient.acuity == null) {
        return res.status(400).json({ error: 'Patient data is missing required fields' });
      }
    }

    for (const nurse of nurses) {
      if (nurse.nurseId == null || nurse.nurseName == null || nurse.nurseEmail == null || nurse.startTime == null || nurse.endTime == null) {
        return res.status(400).json({ error: 'Nurse data is missing required fields' });
      }
    }

    /*const newSchedule = new Schedule({
      date,
      patients,
      nurses,
      chairs,
      uploadedAt: date,
    });

    await newSchedule.save();
    console.log(newSchedule)*/

    const settings = await loadSettings();
    console.log('Loaded settings:', settings);

    await runOptimization(date, patients, nurses, chairs, settings);

    console.log('Finished Optimization!');

    res.status(200).json({ message: 'Schedule uploaded successfully' });

  } catch (error) {
    console.error('Error uploading schedule:', error);
    res.status(500).json({ error: 'Server error' });
  }
};

const loadSettings = async () => {
  try {
    const settings = await Settings.findOne(); // Adjust the query as necessary
    if (!settings) {
      throw new Error('Settings not found');
    }
    return settings;
  } catch (error) {
    console.error('Error loading settings:', error);
    throw error;
  }
};

exports.lockSchedule = async (req, res) => {
  try {
    const db = await connectDB();
    const { date } = req.body;

    console.log('Locking schedule for date:', date); // Debugging line

    // Check if the schedule exists
    const schedule = await db.collection('schedules').findOne({ date });
    if (!schedule) {
      console.log(`No schedule found for date: ${date}`);
      return res.status(404).json({ message: 'Schedule not found' });
    }

    console.log('Schedule found:', schedule); // Debugging line

    if (schedule.locked) {
      console.log(`Schedule for date ${date} is already locked`);
      return res.status(200).json({ message: 'Schedule already locked' });
    }

    const result = await db.collection('schedules').updateOne(
      { date },
      { $set: { locked: true } }
    );

    console.log('Update result:', result); // Debugging line

    if (result.modifiedCount > 0) {
      console.log(`Schedule for date ${date} locked successfully`);
      res.status(200).json({ message: 'Schedule locked successfully' });
    } else {
      console.log(`Failed to lock schedule for date: ${date}`);
      res.status(500).json({ message: 'Failed to lock schedule' });
    }
  } catch (error) {
    console.error('Error locking schedule:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
};

exports.unlockSchedule = async (req, res) => {
  try {
    const db = await connectDB();
    const { date } = req.body;

    console.log('Unlocking schedule for date:', date); // Debugging line

    // Check if the schedule exists
    const schedule = await db.collection('schedules').findOne({ date });
    if (!schedule) {
      console.log(`No schedule found for date: ${date}`);
      return res.status(404).json({ message: 'Schedule not found' });
    }

    console.log('Schedule found:', schedule); // Debugging line

    if (!schedule.locked) {
      console.log(`Schedule for date ${date} is already unlocked`);
      return res.status(200).json({ message: 'Schedule already unlocked' });
    }

    const result = await db.collection('schedules').updateOne(
      { date },
      { $set: { locked: false } }
    );

    console.log('Update result:', result); // Debugging line

    if (result.modifiedCount > 0) {
      console.log(`Schedule for date ${date} unlocked successfully`);
      res.status(200).json({ message: 'Schedule unlocked successfully' });
    } else {
      console.log(`Failed to unlock schedule for date: ${date}`);
      res.status(500).json({ message: 'Failed to unlock schedule' });
    }
  } catch (error) {
    console.error('Error unlocking schedule:', error);
    res.status(500).json({ message: 'Internal server error' });
  }
};

exports.getLockStatus = async (req, res) => {
  try {
    const schedule = await Schedule.findOne({ date: req.query.date });
    if (schedule) {
      res.status(200).json({ isLocked: schedule.locked });
    } else {
      res.status(404).json({ isLocked: false });
    }
  } catch (error) {
    res.status(500).json({ message: 'Error fetching lock status' });
  }
};

const runOptimization = async (date, patients, nurses, chairs, settings) => {
  const inputs = JSON.stringify({ uri, date, patients, nurses, chairs, settings });
  const scriptPath = './python/run_python.sh';

  console.log("Running Python Script!");

  execFile(scriptPath, [inputs], (error, stdout, stderr) => {
    if (error) {
      console.error(`Error executing Python script: ${error.message}`);
    }
    if (stderr) {
      console.error(`Python script stderr: ${stderr}`);
    }
    console.log(`Python script stdout: ${stdout}`);
  });
};

// Analyze Schedule
exports.analyzeSchedule = async (req, res) => {
  try {
    const db = await connectDB();
    const { date } = req.query;
    const schedule = await db.collection('schedules').findOne({ date });

    if (!schedule) {
      return res.status(404).json({ errorMessage: 'No analysis found for the specified date' });
    }

    const patients = schedule.patients;
    const nurses = schedule.nurses;
    const chairs = schedule.chairs;
    const actualUtilization = schedule.actualUtilization;
    const scheduledUtilization = schedule.scheduledUtilization;
    const totalAppointments = patients.length;
    const settings = await loadSettings();
    const numberOfChairs = settings.numberOfChairs;
    const numberOfNurses = nurses.length;
    const acuityMix = schedule.acuityMix;

    const hourlyColors = actualUtilization.map((actual) => {
      const scheduled = scheduledUtilization.find(s => s.time === actual.time);
      let color = '#FFFFFF'; // Default color if no condition matches

      if (scheduled) {
          const actualValue = actual.value;
          const scheduledValue = scheduled.value;

          if (scheduledValue < actualValue) {
              color = '#FFEE57'; // Scheduled is under 2+ of the actual
          } else if (scheduledValue === actualValue) {
              color = '#C7C7C7'; // Scheduled is the same as actual
          } else if (scheduledValue >= actualValue + 1 && scheduledValue <= actualValue + 2) {
              color = '#FFB24E'; // Scheduled is over the actual by 1-2
          } else if (scheduledValue > actualValue + 2) {
              color = '#FF6564'; // Scheduled is well over
          }
      }

      return { time: actual.time, color: color };
    });

    // Placeholder for analysis logic
    const analysisResults = {
      overallScore: 65, // TODO: FIX IN THE FUTURE - this is placeholder
      allocatedAppointments: totalAppointments,
      numberOfNurses: numberOfNurses,
      nursingOverTimeScore: 80,// TODO: FIX IN THE FUTURE - this is placeholder
      middayOverloadScore: 30,// TODO: FIX IN THE FUTURE - this is placeholder
      patientWaitTimeScore: 70,// TODO: FIX IN THE FUTURE - this is placeholder
      numberOfChairs: numberOfChairs,
      acuityMix: acuityMix,
      templateExpectedPatients: actualUtilization,
      actualPatients: scheduledUtilization,
      hourlyColors: hourlyColors
    };

    res.status(200).json({ payload: analysisResults, errorMessage: "" });
  } catch (error) {
    console.error('Error in analyzeSchedule:', error.message);
    res.status(500).json({ errorMessage: 'Server error' });
  }
};

// Get Schedules
exports.optimizeSchedule = async (req, res) => {
  try {
    const db = await connectDB();

    const { date, nurseId, patientId } = req.query;
    console.log('Date query parameter:', date); 
    console.log('Nurse ID query parameter:', nurseId); 
    console.log('Patient ID query parameter:', patientId); 

    const schedule = await db.collection('schedules').findOne({ date });

    if (!schedule) {
      return res.status(404).json({ errorMessage: 'No analysis found for the specified date' });
    }

    let patients = schedule.patients;
    let nurses = schedule.nurses;
    const chairs = schedule.chairs;
    const utilization = schedule.actualUtilization;
    const score = 90; 
    const totalAppointments = patients.length;
    const settings = await loadSettings();
    const numberOfChairs = settings.numberOfChairs;
    const numberOfNurses = nurses.length;
    const acuityMix = schedule.acuityMix;

    if (nurseId !== undefined) {
      nurses = nurses.filter(nurse => nurse.nurseId == nurseId);
    }

    if (patientId !== undefined) {
      patients = patients.filter(patient => patient.patientId == patientId);
    }

    const response = {
      date: date,
      newPatientSchedule: patients,
      nurseSchedule: nurses,
      chairSchedule: chairs,
      utilizationCurve: utilization,
      newScore: score,
      totalAppointments: totalAppointments,
      numberOfChairs: numberOfChairs,
      numberOfNurses: nurses.length,
      acuityMix: acuityMix,
      locked: schedule.locked // Add the locked status
    };

    res.status(200).json({ payload: response, errorMessage: "" });
  } catch (error) {
    console.error('Error in getSchedules:', error.message);
    res.status(500).json({ errorMessage: 'Server error' });
  }
};

exports.getNurseData = async (req, res) => {
  try {
    const db = await connectDB();
    const { nurseId } = req.params;

    const schedule = await db.collection('schedules').findOne({ "nurses.nurseId": parseInt(nurseId, 10) });

    if (!schedule) {
      return res.status(404).json({ errorMessage: 'No nurse found with the specified ID' });
    }

    const nurse = schedule.nurses.find(n => n.nurseId === parseInt(nurseId, 10));

    if (!nurse) {
      return res.status(404).json({ errorMessage: 'Nurse not found' });
    }

    // Fetch patient details
    const assignedPatients = schedule.patients.filter(patient => nurse.assignedPatients.includes(patient.patientId));

    // Fetch chair assignments for the assigned patients
    const chairAssignments = schedule.chairs.map(chair => {
      return {
        chairId: chair.chairId,
        assignedPatients: chair.assignedPatients.filter(patientId => nurse.assignedPatients.includes(patientId))
      };
    }).filter(chair => chair.assignedPatients.length > 0);

    res.status(200).json({ ...nurse, assignedPatients, chairAssignments });
  } catch (error) {
    console.error('Error fetching nurse data:', error.message);
    res.status(500).json({ errorMessage: 'Server error' });
  }
};

// Fetch Chair Data by ID
exports.getChairData = async (req, res) => {
  try {
    const db = await connectDB();
    const { chairId } = req.params;

    const schedule = await db.collection('schedules').findOne({ "chairs.chairId": parseInt(chairId, 10) });

    if (!schedule) {
      return res.status(404).json({ errorMessage: 'No chair found with the specified ID' });
    }

    const chair = schedule.chairs.find(c => c.chairId === parseInt(chairId, 10));

    if (!chair) {
      return res.status(404).json({ errorMessage: 'Chair not found' });
    }

    // Fetch assigned patients for the chair
    const assignedPatients = chair.assignedPatients.map(patientId => {
      return schedule.patients.find(p => p.patientId === patientId);
    });

    res.status(200).json({
      chair,
      assignedPatients
    });
  } catch (error) {
    console.error('Error fetching chair data:', error.message);
    res.status(500).json({ errorMessage: 'Server error' });
  }
};

// Fetch Patient Data by ID
exports.getPatientData = async (req, res) => {
  try {
    const db = await connectDB();
    const { patientId } = req.params;

    const schedule = await db.collection('schedules').findOne({ "patients.patientId": parseInt(patientId, 10) });

    if (!schedule) {
      return res.status(404).json({ errorMessage: 'No patient found with the specified ID' });
    }

    const patient = schedule.patients.find(p => p.patientId === parseInt(patientId, 10));

    if (!patient) {
      return res.status(404).json({ errorMessage: 'Patient not found' });
    }

    res.status(200).json(patient);
  } catch (error) {
    console.error('Error fetching patient data:', error.message);
    res.status(500).json({ errorMessage: 'Server error' });
  }
};