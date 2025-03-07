const admin = require('firebase-admin');
const path = require('path');

/**
 * Firebase Configuration Handler
 * Manages Firebase initialization and provides access to Firebase services
 */
class FirebaseConfig {
  constructor() {
    this._initialize();
  }

  _initialize() {
    try {
      // Use the service-account.json file directly
      const serviceAccountPath = path.resolve(__dirname, '../service-account.json');
      
      // Initialize Firebase Admin with the service account file
      this.app = admin.initializeApp({
        credential: admin.credential.cert(serviceAccountPath),
        storageBucket: "dof-ai.firebasestorage.app"
      });
      
      console.log('Firebase Admin initialized successfully with service account file');
      
      // Initialize Firebase services
      this.db = admin.firestore();
      this.auth = admin.auth();
      
      // Initialize Storage (wrapped in try-catch to handle potential errors)
      try {
        this.storage = admin.storage();
        this.bucket = this.storage.bucket();
        console.log('Storage initialized successfully');
      } catch (error) {
        console.warn('Firebase Storage initialization failed:', error.message);
        console.warn('Storage functionality will not be available');
        this.storage = null;
        this.bucket = null;
      }
    } catch (error) {
      console.error('Firebase initialization failed:', error);
      throw error;
    }
  }
}

// Create a singleton instance
const firebaseConfig = new FirebaseConfig();

// Export the Firebase services
module.exports = {
  admin,
  app: firebaseConfig.app,
  db: firebaseConfig.db,
  auth: firebaseConfig.auth,
  storage: firebaseConfig.storage,
  bucket: firebaseConfig.bucket
}; 