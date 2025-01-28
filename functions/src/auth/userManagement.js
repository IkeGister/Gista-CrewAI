const express = require('express');
const admin = require('firebase-admin');
const router = express.Router();

// Create user
router.post('/create-user', async (req, res) => {
    try {
        const { email, password, username } = req.body;

        // Create user in Firebase Auth
        const userRecord = await admin.auth().createUser({
            email,
            password,
        });

        // Create user document in Firestore
        await admin.firestore().collection('users').doc(userRecord.uid).set({
            email,
            username,
            gists: [],
            links: [],
            createdAt: admin.firestore.FieldValue.serverTimestamp()
        });

        res.status(201).json({ 
            message: "User created successfully",
            userId: userRecord.uid 
        });
    } catch (error) {
        console.error('Error creating user:', error);
        res.status(500).json({ error: error.message });
    }
});

// Update user
router.put('/update-user', async (req, res) => {
    try {
        // Verify ID token from Authorization header
        const idToken = req.headers.authorization && req.headers.authorization.split('Bearer ')[1];
        if (!idToken) {
            return res.status(401).json({ error: 'No token provided' });
        }

        const decodedToken = await admin.auth().verifyIdToken(idToken);
        const userId = decodedToken.uid;

        const updateData = req.body;
        
        // Update user document in Firestore
        await admin.firestore().collection('users').doc(userId).update(updateData);

        res.json({ message: "User updated successfully" });
    } catch (error) {
        console.error('Error updating user:', error);
        res.status(500).json({ error: error.message });
    }
});

module.exports = router; 