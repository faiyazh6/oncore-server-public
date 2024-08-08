const mongoose = require('mongoose');
const dotenv = require('dotenv');

dotenv.config();

const uri = process.env.MONGO_URI;

let db;

const connectDB = async () => {
  if (db) return db;
  
  try {
    const conn = await mongoose.connect(process.env.MONGO_URI, {
      dbName: 'Paoli'
    });

    db = conn.connection.db;
    console.log("Successfully connected to MongoDB Atlas with Mongoose");
    return db;
  } catch (err) {
    console.error(err.message);
    process.exit(1);
  }
};

module.exports = connectDB;