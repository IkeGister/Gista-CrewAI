const express = require('express');
const admin = require('firebase-admin');
const router = express.Router();

// Create/Add gist
router.post('/add/:user_id', async (req, res) => {
    try {
        const { user_id } = req.params;
        const gistData = req.body;
        
        console.log("Received gist data:", JSON.stringify(gistData, null, 2));
        
        const link_id = gistData.link_id; // Extract link_id from request body

        // Validate required fields
        const requiredFields = ['title', 'link', 'image_url', 'category', 'segments', 'link_id'];
        for (const field of requiredFields) {
            if (!gistData[field]) {
                return res.status(400).json({ error: `Missing required field: ${field}` });
            }
        }

        // Validate segments structure
        if (!Array.isArray(gistData.segments) || !gistData.segments.length) {
            return res.status(400).json({ error: 'Segments must be a non-empty array' });
        }

        // Use link_id as gistId (or generate one if not provided)
        const gistId = link_id || `gist_${Date.now()}`;
        
        // Create gist with structure matching the database
        const gistWithMetadata = {
            gistId: gistId,
            title: gistData.title,
            category: gistData.category,
            date_created: new Date().toISOString(),
            image_url: gistData.image_url,
            is_played: false,
            is_published: true,  // Default to true, can be overridden
            link: gistData.link,
            playback_duration: gistData.playback_duration || 0,
            publisher: gistData.publisher || "theNewGista",
            ratings: gistData.ratings || 0,
            segments: gistData.segments.map((segment, index) => ({
                segment_title: segment.title,
                segment_audioUrl: segment.audioUrl,
                playback_duration: segment.duration?.toString() || "0",
                segment_index: (segment.index !== undefined) ? segment.index : index.toString()
            })),
            // Handle status fields properly
            status: {
                // Use status object if provided, otherwise use individual fields or defaults
                production_status: gistData.status?.production_status || gistData.production_status || 'Reviewing Content',
                // Use inProduction with fallback to in_productionQueue for backward compatibility
                inProduction: gistData.status?.inProduction ?? gistData.inProduction ?? gistData.status?.in_productionQueue ?? gistData.in_productionQueue ?? false
            },
            users: gistData.users || 0
        };

        // Add gist to user's gists subcollection
        await admin.firestore()
            .collection('users')
            .doc(user_id)
            .collection('gists')
            .doc(gistId)
            .set(gistWithMetadata);

        // Now update the corresponding link to mark the gist as created
        // First check if the link exists in the links subcollection
        const linkRef = admin.firestore()
            .collection('users')
            .doc(user_id)
            .collection('links')
            .doc(link_id);
            
        const linkDoc = await linkRef.get();
        
        if (linkDoc.exists) {
            // Update the link's gist_created status
            await linkRef.update({
                'gist_created.gist_created': true,
                'gist_created.gist_id': gistId,
                'gist_created.image_url': gistData.image_url,
                'gist_created.link_title': gistData.title || linkDoc.data().gist_created.link_title
            });
        }

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

        const gistRef = admin.firestore()
            .collection('users')
            .doc(user_id)
            .collection('gists')
            .doc(gist_id);
            
        const gistDoc = await gistRef.get();

        if (!gistDoc.exists) {
            return res.status(404).json({ error: 'Gist not found' });
        }

        const currentGist = gistDoc.data();
        
        // Handle status updates with proper field migration
        const updatedStatus = {
            // Use inProduction with fallback to in_productionQueue for backward compatibility
            inProduction: updates.status?.inProduction ?? currentGist.status?.inProduction ?? currentGist.status?.in_productionQueue ?? false,
            // Use production_status with a default value
            production_status: updates.status?.production_status ?? currentGist.status?.production_status ?? "Reviewing Content"
        };
        
        // Update only the specified fields or status
        const updateData = {
            status: updatedStatus
        };
        
        // Add other fields if they exist in the update request
        if (updates.is_played !== undefined) updateData.is_played = updates.is_played;
        if (updates.ratings !== undefined) updateData.ratings = updates.ratings;
        if (updates.users !== undefined) updateData.users = updates.users;
        
        await gistRef.update(updateData);

        res.json({ message: "Gist updated successfully" });
    } catch (error) {
        console.error('Error updating gist:', error);
        res.status(500).json({ error: error.message });
    }
});

// Signal-based status update endpoint
router.put('/:user_id/:gist_id/status', async (req, res) => {
    try {
        const { user_id, gist_id } = req.params;
        
        const gistRef = admin.firestore()
            .collection('users')
            .doc(user_id)
            .collection('gists')
            .doc(gist_id);
            
        const gistDoc = await gistRef.get();

        if (!gistDoc.exists) {
            return res.status(404).json({ error: 'Gist not found' });
        }

        // Update the status to mark it as in production
        await gistRef.update({
            'status.inProduction': true,
            'status.production_status': 'In Production'
        });

        res.json({ 
            message: "Gist status updated successfully",
            status: {
                inProduction: true,
                production_status: 'In Production'
            }
        });
    } catch (error) {
        console.error('Error updating gist status:', error);
        res.status(500).json({ error: error.message });
    }
});

// Delete gist
router.delete('/delete/:user_id/:gist_id', async (req, res) => {
    try {
        const { user_id, gist_id } = req.params;
        
        // Get reference to the gist in the subcollection
        const gistRef = admin.firestore()
            .collection('users')
            .doc(user_id)
            .collection('gists')
            .doc(gist_id);
            
        const gistDoc = await gistRef.get();
        
        if (!gistDoc.exists) {
            return res.status(404).json({ error: 'Gist not found' });
        }
        
        // Delete the gist document
        await gistRef.delete();
        
        // Find and update any links that reference this gist
        const linksSnapshot = await admin.firestore()
            .collection('users')
            .doc(user_id)
            .collection('links')
            .where('gist_created.gist_id', '==', gist_id)
            .get();
        
        const updatePromises = [];
        linksSnapshot.forEach(doc => {
            updatePromises.push(doc.ref.update({
                'gist_created.gist_created': false,
                'gist_created.gist_id': null
            }));
        });
        
        // Wait for all updates to complete
        if (updatePromises.length > 0) {
            await Promise.all(updatePromises);
        }
        
        res.status(200).json({ message: `Gist ${gist_id} deleted successfully` });
    } catch (error) {
        console.error('Error deleting gist:', error);
        res.status(500).json({ error: error.message });
    }
});

// Get user's gists
router.get('/:user_id', async (req, res) => {
    try {
        const { user_id } = req.params;
        
        // Check if user exists
        const userDoc = await admin.firestore().collection('users').doc(user_id).get();
        if (!userDoc.exists) {
            return res.status(404).json({ error: 'User not found' });
        }

        // Get all gists from subcollection
        const gistsSnapshot = await admin.firestore()
            .collection('users')
            .doc(user_id)
            .collection('gists')
            .get();

        const gists = [];
        gistsSnapshot.forEach(doc => {
            gists.push(doc.data());
        });

        res.json({ gists: gists });
    } catch (error) {
        console.error('Error fetching gists:', error);
        res.status(500).json({ error: error.message });
    }
});

// Get specific gist
router.get('/:user_id/:gist_id', async (req, res) => {
    try {
        const { user_id, gist_id } = req.params;
        
        const gistRef = admin.firestore()
            .collection('users')
            .doc(user_id)
            .collection('gists')
            .doc(gist_id);
            
        const gistDoc = await gistRef.get();

        if (!gistDoc.exists) {
            return res.status(404).json({ error: 'Gist not found' });
        }

        res.json({ gist: gistDoc.data() });
    } catch (error) {
        console.error('Error fetching specific gist:', error);
        res.status(500).json({ error: error.message });
    }
});

module.exports = router; 