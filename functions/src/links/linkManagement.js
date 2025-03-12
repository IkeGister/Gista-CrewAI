const express = require("express");
const admin = require("firebase-admin");
const router = express.Router();
const { v4: uuidv4 } = require('uuid');
const axios = require('axios');

// Store link
router.post("/store", async (req, res) => {
  try {
    const { user_id, link, auto_create_gist = true } = req.body;

    // Create link document with metadata
    const linkData = {
      category: link.category || "Uncategorized",
      date_added: new Date().toISOString(),  // Changed from serverTimestamp to ISO string
      gist_created: {
        gist_created: false,  // Initially false
        gist_id: null,
        image_url: null,
        link_id: `link_${Date.now()}`,  // Generate unique link ID
        link_title: link.title || "",
        link_type: link.url?.endsWith(".pdf") ? "PDF" : "Web",
        url: link.url
      }
    };

    // Add link to user's links array
    await admin.firestore().collection("users").doc(user_id).update({
      links: admin.firestore.FieldValue.arrayUnion(linkData)
    });

    // If auto_create_gist is enabled, create a gist from the link
    let gistId = null;
    
    if (auto_create_gist) {
      try {
        // Prepare gist data from the link
        const gistData = {
          gistId: `gist_${uuidv4().replace(/-/g, '')}`,
          title: linkData.gist_created.link_title || "Untitled Gist",
          image_url: linkData.gist_created.image_url || "",
          link: linkData.gist_created.url || "",
          category: linkData.category || "Uncategorized",
          link_id: linkData.gist_created.link_id,
          segments: [],  // Empty segments to be filled by CrewAI
          is_published: true,
          is_played: false,
          playback_duration: 0,
          publisher: "theNewGista",
          ratings: 0,
          users: 0,
          date_created: new Date().toISOString(),
          status: {
            inProduction: false,
            production_status: 'Reviewing Content',
          }
        };
        
        gistId = gistData.gistId;

        // Add the gist to Firebase
        await admin.firestore().collection("users").doc(user_id).update({
          gists: admin.firestore.FieldValue.arrayUnion(gistData)
        });

        // Update the link to indicate a gist was created
        const userRef = admin.firestore().collection("users").doc(user_id);
        const userDoc = await userRef.get();
        const userData = userDoc.data();
        
        // Find the link we just added and update its gist_created status
        const updatedLinks = userData.links.map(userLink => {
          if (userLink.gist_created?.link_id === linkData.gist_created.link_id) {
            return {
              ...userLink,
              gist_created: {
                ...userLink.gist_created,
                gist_created: true,
                gist_id: gistId
              }
            };
          }
          return userLink;
        });
        
        // Update the user document
        await userRef.update({ links: updatedLinks });

        // Notify the CrewAI service about the new gist
        try {
          // Call the CrewAI service to update the gist status using signal-based approach
          await axios.put(`https://us-central1-dof-ai.cloudfunctions.net/api/gists/${user_id}/${gistId}/status`, {});
          
          console.log(`CrewAI service notified about new gist: ${gistId}`);
        } catch (e) {
          // Log the error but don't fail the gist creation
          console.error(`Error notifying CrewAI service: ${e.message}`);
        }
      } catch (e) {
        // Log the error but don't fail the link creation
        console.error(`Error auto-creating gist: ${e.message}`);
        return res.status(500).json({ error: "Link stored but failed to create gist" });
      }
    }

    // Ultra-minimal response with just the gistId if created
    if (auto_create_gist && gistId) {
      return res.json({ gistId });
    } else {
      // If auto_create_gist was false, just return a success message
      return res.json({ message: "Link stored successfully" });
    }
  } catch (error) {
    console.error("Error storing link:", error);
    res.status(500).json({ error: error.message });
  }
});

// Update link when gist is created
router.put("/update-gist-status/:user_id/:link_id", async (req, res) => {
  try {
    const { user_id, link_id } = req.params;
    const { gist_id, image_url, link_title } = req.body;

    // Use link_id as gist_id if not provided to ensure consistency
    const finalGistId = gist_id || link_id;

    const userRef = admin.firestore().collection("users").doc(user_id);
    const userDoc = await userRef.get();
        
    if (!userDoc.exists) {
      return res.status(404).json({ error: "User not found" });
    }

    const userData = userDoc.data();
    const linkIndex = userData.links.findIndex(
      link => link.gist_created.link_id === link_id
    );

    if (linkIndex === -1) {
      return res.status(404).json({ error: "Link not found" });
    }

    // Update the gist_created object
    userData.links[linkIndex].gist_created = {
      ...userData.links[linkIndex].gist_created,
      gist_created: true,
      gist_id: finalGistId,
      image_url,
      link_title: link_title || userData.links[linkIndex].gist_created.link_title
    };

    await userRef.update({ links: userData.links });

    res.json({ 
      message: "Link gist status updated successfully",
      link: userData.links[linkIndex]
    });
  } catch (error) {
    console.error("Error updating link gist status:", error);
    res.status(500).json({ error: error.message });
  }
});

// Get user's links
router.get("/:user_id", async (req, res) => {
  try {
    const { user_id } = req.params;
    const userDoc = await admin.firestore().collection("users").doc(user_id).get();

    if (!userDoc.exists) {
      return res.status(404).json({ error: "User not found" });
    }

    const userData = userDoc.data();
    res.json({ 
      links: userData.links || [],
      count: (userData.links || []).length
    });
  } catch (error) {
    console.error("Error fetching links:", error);
    res.status(500).json({ error: error.message });
  }
});

module.exports = router; 
