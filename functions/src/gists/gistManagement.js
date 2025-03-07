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

        // Create gist with structure matching the database
        const gistWithMetadata = {
            gistId: link_id, // Use the link_id as the gistId for consistency
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

        // Add gist to user's gists array
        await admin.firestore().collection('users').doc(user_id).update({
            gists: admin.firestore.FieldValue.arrayUnion(gistWithMetadata)
        });

        // Now update the corresponding link to mark the gist as created
        const userRef = admin.firestore().collection('users').doc(user_id);
        const userDoc = await userRef.get();
        
        if (userDoc.exists) {
            const userData = userDoc.data();
            const linkIndex = userData.links.findIndex(
                link => link.gist_created.link_id === link_id
            );
            
            if (linkIndex !== -1) {
                // Update the link's gist_created status
                userData.links[linkIndex].gist_created = {
                    ...userData.links[linkIndex].gist_created,
                    gist_created: true,
                    gist_id: link_id,
                    image_url: gistData.image_url,
                    link_title: gistData.title || userData.links[linkIndex].gist_created.link_title
                };
                
                await userRef.update({ links: userData.links });
            }
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
        
        // Handle status updates with proper field migration
        const updatedStatus = {
            // Use inProduction with fallback to in_productionQueue for backward compatibility
            inProduction: updates.status?.inProduction ?? currentGist.status?.inProduction ?? currentGist.status?.in_productionQueue ?? false,
            // Use production_status with a default value
            production_status: updates.status?.production_status ?? currentGist.status?.production_status ?? "Reviewing Content"
        };
        
        // Create updated gist with clean status object (no deprecated fields)
        userData.gists[gistIndex] = {
            ...currentGist,
            status: updatedStatus,
            is_played: updates.is_played ?? currentGist.is_played ?? false,
            ratings: updates.ratings ?? currentGist.ratings ?? 0,
            users: updates.users ?? currentGist.users ?? 0
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

// Delete gist
router.delete('/delete/:user_id/:gist_id', async (req, res) => {
    try {
        const { user_id, gist_id } = req.params;
        
        // Get the user document
        const userRef = admin.firestore().collection('users').doc(user_id);
        const userDoc = await userRef.get();
        
        if (!userDoc.exists) {
            return res.status(404).json({ error: 'User not found' });
        }
        
        // Get the current gists array
        const userData = userDoc.data();
        const gists = userData.gists || [];
        
        // Find the gist index
        const gistIndex = gists.findIndex(gist => gist.gistId === gist_id);
        
        // If gist not found
        if (gistIndex === -1) {
            return res.status(404).json({ error: 'Gist not found' });
        }
        
        // Remove the gist from the array
        gists.splice(gistIndex, 1);
        
        // Update the user document with the modified gists array
        await userRef.update({ gists: gists });
        
        // Also update any links that reference this gist
        const links = userData.links || [];
        let linksUpdated = false;
        
        for (let i = 0; i < links.length; i++) {
            if (links[i].gist_created && links[i].gist_created.gist_id === gist_id) {
                links[i].gist_created.gist_created = false;
                links[i].gist_created.gist_id = null;
                linksUpdated = true;
            }
        }
        
        if (linksUpdated) {
            await userRef.update({ links: links });
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