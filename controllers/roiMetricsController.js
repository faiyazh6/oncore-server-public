const connectDB = require('../config/db');

exports.getRoiMetrics = async (req, res) => {
  try {

    const db = await connectDB();

    const { date } = req.query;
    console.log('Date query parameter:', date); // Debugging line

    const roiMetrics = await db.collection('roi_metrics').findOne({ date: date });

    if (!roiMetrics) {
      console.log('No ROI metrics found for the specified date'); // Debugging line
      return res.status(404).json({ errorMessage: 'No ROI metrics found for the specified date' });
    }

    console.log('ROI metrics found:', roiMetrics); // Debugging line
    res.status(200).json({ payload: roiMetrics });
  } catch (error) {
    console.error('Error in getRoiMetrics:', error.message);
    res.status(500).json({ errorMessage: 'Server error' });
  }
};