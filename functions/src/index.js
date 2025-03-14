const functions = require("firebase-functions");
const express = require("express");
const cors = require("cors");

// Import our Firebase configuration
const { admin, db, auth, storage } = require("./config/firebase");

// Initialize Express
const app = express();

// Middleware
app.use(cors({ origin: true }));
app.use(express.json());

// Import route handlers
const userRoutes = require("./auth/userManagement");
const linkRoutes = require("./links/linkManagement");
const gistRoutes = require("./gists/gistManagement");
const categoryRoutes = require("./categories/categoriesManagement");

// Use routes
app.use("/auth", userRoutes);
app.use("/links", linkRoutes);
app.use("/gists", gistRoutes);
app.use("/categories", categoryRoutes);

// Simple test route
app.get("/test", (req, res) => {
  res.json({ 
    message: "Express API is working!",
    firebaseConnected: !!admin && !!db
  });
});

// Simple test function
exports.helloWorld = functions.https.onRequest((req, res) => {
  res.send("Hello from Firebase!");
});

// Export the Express app as Firebase Cloud Functions
exports.api = functions.https.onRequest(app);
exports.apiSubcollections = functions.https.onRequest(app);
exports.notificationsSubcollections = functions.https.onRequest((req, res) => {
  res.json({ message: "Notifications service is running with subcollections." });
});
