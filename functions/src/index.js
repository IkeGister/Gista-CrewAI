// Remove this line since we don't need dotenv anymore
// require("dotenv").config();
const functions = require("firebase-functions");
const admin = require("firebase-admin");
const express = require("express");
const cors = require("cors");

// Remove debug logging since we're not using env vars anymore
// console.log('Environment variables loaded:', {...});

// Initialize Firebase Admin with service account file
const serviceAccount = require("./service-account.json");  // If we move file to src/

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});

// Initialize Express
const app = express();

// Middleware
app.use(cors({ origin: true }));
app.use(express.json());

// Import route handlers
const userRoutes = require("./auth/userManagement");
const linkRoutes = require("./links/linkManagement");
const gistRoutes = require("./gists/gistManagement");

// Use routes
app.use("/auth", userRoutes);
app.use("/links", linkRoutes);
app.use("/gists", gistRoutes);

// Export the Express app as a Firebase Cloud Function
exports.api = functions.https.onRequest(app); 