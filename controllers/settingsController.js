const connectDB = require('../config/db');

exports.getSettings = async (req, res) => {
  try {
    const db = await connectDB();
    const settings = await db.collection('settings').findOne();

    if (!settings) {
      return res.status(404).json({ errorMessage: 'No settings found' });
    }

    res.status(200).json({ payload: settings, errorMessage: "" });
  } catch (error) {
    console.error('Error in getSettings:', error.message);
    res.status(500).json({ errorMessage: 'Server error' });
  }
};

exports.updateSettings = async (req, res) => {
  try {
    const db = await connectDB();

    const { 
      numberOfChairs, 
      goals, 
      break_duration, 
      break_end_time, 
      break_start_time, 
      openTime, 
      patientNurseRatio, 
      closeTime 
    } = req.body;

    // Using updateOne with upsert to update or insert the document
    await db.collection('settings').updateOne(
      {},
      { 
        $set: { 
          numberOfChairs: Number(numberOfChairs), 
          goals, 
          break_duration: Number(break_duration), 
          break_end_time: String(break_end_time), 
          break_start_time: String(break_start_time), 
          openTime: String(openTime), 
          patientNurseRatio: Number(patientNurseRatio), 
          closeTime: String(closeTime)
        }
      },
      { upsert: true }
    );

    res.status(200).json({ payload: { message: 'Settings updated successfully' } });
  } catch (error) {
    console.error('Error in updateSettings:', error.message);
    res.status(500).json({ errorMessage: 'Server error' });
  }
};