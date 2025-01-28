const express = require('express');
const admin = require('firebase-admin');
const router = express.Router();

// Create/Add gist
router.post('/add/:user_id', async (req, res) => {
    try {
        const { user_id } = req.params;
        const gistData = req.body;

        // Validate required fields
        const requiredFields = ['title', 'link', 'image_url', 'category', 'segments'];
        for (const field of requiredFields) {
            if (!gistData[field]) {
                return res.status(400).json({ error: `Missing required field: ${field}` });
            }
        }

        // Validate segments structure
        if (!Array.isArray(gistData.segments) || !gistData.segments.length) {
            return res.status(400).json({ error: 'Segments must be a non-empty array' });
        }

        // Create gist with full schema
        const gistWithMetadata = {
            title: gistData.title,
            category: gistData.category,
            date_created: admin.firestore.FieldValue.serverTimestamp(),
            image_url: gistData.image_url,
            is_played: false,
            is_published: true,  // Default to true, can be overridden
            link: gistData.link,
            playback_duration: gistData.playback_duration || 0,
            publisher: gistData.publisher || "theNewGista",
            ratings: gistData.ratings || 0,
            segments: gistData.segments.map((segment, index) => ({
                segment_audioUrl: segment.audioUrl,
                segment_duration: segment.duration,
                segment_index: index,
                segment_title: segment.title
            })),
            status: {
                is_done_playing: false,
                is_now_playing: false,
                playback_time: 0
            },
            users: gistData.users || 0
        };

        // Add gist to user's gists array
        await admin.firestore().collection('users').doc(user_id).update({
            gists: admin.firestore.FieldValue.arrayUnion(gistWithMetadata)
        });

        res.json({ 
            message: "Gist added successfully",
            gist: gistWithMetadata
        });
    } catch (error) {
        console.error('Error adding gist:', error);
        res.status(500).json({ error: error.message });
    }
});

// Update gist status
router.put('/update/:user_id/:gist_id', async (req, res) => {
    try {
        const { user_id, gist_id } = req.params;
        const updates = req.body;

        const userRef = admin.firestore().collection('users').doc(user_id);
        const userDoc = await userRef.get();

        if (!userDoc.exists) {
            return res.status(404).json({ error: 'User not found' });
        }

        const userData = userDoc.data();
        const gistIndex = userData.gists.findIndex(gist => gist.gistId === gist_id);

        if (gistIndex === -1) {
            return res.status(404).json({ error: 'Gist not found' });
        }

        // Update status fields
        const currentGist = userData.gists[gistIndex];
        userData.gists[gistIndex] = {
            ...currentGist,
            status: {
                is_done_playing: updates.is_done_playing || currentGist.status.is_done_playing,
                is_now_playing: updates.is_now_playing || currentGist.status.is_now_playing,
                playback_time: updates.playback_time || currentGist.status.playback_time
            },
            is_played: updates.is_played || currentGist.is_played,
            ratings: updates.ratings || currentGist.ratings,
            users: updates.users || currentGist.users
        };

        await userRef.update({
            gists: userData.gists
        });

        res.json({ message: "Gist updated successfully" });
    } catch (error) {
        console.error('Error updating gist:', error);
        res.status(500).json({ error: error.message });
    }
});

// Get user's gists
router.get('/:user_id', async (req, res) => {
    try {
        const { user_id } = req.params;
        const userDoc = await admin.firestore().collection('users').doc(user_id).get();

        if (!userDoc.exists) {
            return res.status(404).json({ error: 'User not found' });
        }

        const userData = userDoc.data();
        res.json({ gists: userData.gists || [] });
    } catch (error) {
        console.error('Error fetching gists:', error);
        res.status(500).json({ error: error.message });
    }
});

module.exports = router; 