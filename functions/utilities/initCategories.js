const admin = require("firebase-admin");
const { initializeDefaultCategories } = require("./defaultCategories");

// Initialize Firebase Admin with your service account
const serviceAccount = require("../src/service-account.json");

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});

// Run the initialization
initializeDefaultCategories(admin)
  .then(result => {
    console.log("Initialization result:", result);
    process.exit(0);
  })
  .catch(error => {
    console.error("Initialization failed:", error);
    process.exit(1);
  }); 