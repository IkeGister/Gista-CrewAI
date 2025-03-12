const express = require('express');
const admin = require('firebase-admin');
const router = express.Router();

// Create user with Firebase Auth
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

// Create user with custom ID (without Firebase Auth)
router.post('/create_user', async (req, res) => {
    try {
        const { user_id, email, username } = req.body;
        
        if (!user_id || !email || !username) {
            return res.status(400).json({ error: "user_id, email, and username are required" });
        }
        
        // Check if user already exists
        const userRef = admin.firestore().collection('users').doc(user_id);
        const userDoc = await userRef.get();
        
        if (userDoc.exists) {
            return res.status(400).json({ message: "User already exists" });
        }
        
        // Create user document in Firestore with the provided user_id
        await userRef.set({
            email,
            username,
            user_id,
            gists: [],
            links: [],
            createdAt: admin.firestore.FieldValue.serverTimestamp()
        });
        
        res.status(201).json({ 
            message: "User created successfully",
            user_id: user_id
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

// Delete user
router.delete('/delete_user/:user_id', async (req, res) => {
    try {
        const { user_id } = req.params;
        
        // Check if user exists
        const userRef = admin.firestore().collection('users').doc(user_id);
        const userDoc = await userRef.get();
        
        if (!userDoc.exists) {
            return res.status(404).json({ error: "User not found" });
        }
        
        // Delete user document from Firestore
        await userRef.delete();
        
        // Optionally, also delete the user from Firebase Auth if they exist there
        try {
            await admin.auth().getUser(user_id);
            await admin.auth().deleteUser(user_id);
        } catch (authError) {
            // If user doesn't exist in Auth, just continue
            console.log(`User ${user_id} not found in Auth or couldn't be deleted: ${authError.message}`);
        }
        
        res.status(200).json({ message: `User ${user_id} deleted successfully` });
    } catch (error) {
        console.error('Error deleting user:', error);
        res.status(500).json({ error: error.message });
    }
});

module.exports = router; 