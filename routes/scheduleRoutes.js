const express = require('express');
const router = express.Router();
const { uploadSchedule, analyzeSchedule, optimizeSchedule, lockSchedule, getLockStatus, unlockSchedule } = require('../controllers/scheduleController');
const multer = require('multer');

const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

router.post('/upload-schedule', upload.single('file'), uploadSchedule);
router.get('/analyze-schedule', analyzeSchedule);
router.get('/optimize-schedule', optimizeSchedule);
router.post('/lock-schedule', lockSchedule);
router.post('/unlock-schedule', unlockSchedule);
router.get('/get-lock-status', getLockStatus);

// router.get('/nurse/:nurseId', scheduleController.getNurseData);
// router.get('/chair/:chairId', scheduleController.getChairData);
// router.get('/patient/:patientId', scheduleController.getPatientData);

module.exports = router;