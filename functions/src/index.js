const functions = require("firebase-functions");
const admin = require("firebase-admin");
const express = require("express");
const cors = require("cors");

// Initialize Firebase Admin without service account
admin.initializeApp();

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
  res.json({ message: "Express API is working!" });
});

// Simple test function
exports.helloWorld = functions.https.onRequest((req, res) => {
  res.send("Hello from Firebase!");
});

// Export the Express app as a Firebase Cloud Function
exports.api = functions.https.onRequest(app);
