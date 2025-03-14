const express = require("express");
const admin = require("firebase-admin");
const router = express.Router();
const { v4: uuidv4 } = require('uuid');
const axios = require('axios');

// Store link
router.post("/store", async (req, res) => {
  try {
    const { user_id, link, auto_create_gist = true } = req.body;

    // Generate a unique link ID
    const link_id = `link_${Date.now()}`;

    // Create link document with metadata
    const linkData = {
      category: link.category || "Uncategorized",
      date_added: new Date().toISOString(),  // Changed from serverTimestamp to ISO string
      gist_created: {
        gist_created: false,  // Initially false
        gist_id: null,
        image_url: null,
        link_id: link_id,
        link_title: link.title || "",
        link_type: link.url?.endsWith(".pdf") ? "PDF" : "Web",
        url: link.url
      }
    };

    // Add link to user's links subcollection
    await admin.firestore()
      .collection("users")
      .doc(user_id)
      .collection("links")
      .doc(link_id)
      .set(linkData);

    // If auto_create_gist is enabled, create a gist from the link
    let gistId = null;
    
    if (auto_create_gist) {
      try {
        // Prepare gist data from the link
        const gistId = `gist_${uuidv4().replace(/-/g, '')}`;
        
        const gistData = {
          gistId: gistId,
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

        // Add gist to the user's gists subcollection
        await admin.firestore()
          .collection("users")
          .doc(user_id)
          .collection("gists")
          .doc(gistId)
          .set(gistData);

        // Update the link to indicate a gist was created
        await admin.firestore()
          .collection("users")
          .doc(user_id)
          .collection("links")
          .doc(link_id)
          .update({
            "gist_created.gist_created": true,
            "gist_created.gist_id": gistId
          });

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

    const linkRef = admin.firestore()
      .collection("users")
      .doc(user_id)
      .collection("links")
      .doc(link_id);
    
    const linkDoc = await linkRef.get();
        
    if (!linkDoc.exists) {
      return res.status(404).json({ error: "Link not found" });
    }

    const linkData = linkDoc.data();

    // Update the gist_created object within the link document
    await linkRef.update({
      "gist_created.gist_created": true,
      "gist_created.gist_id": finalGistId,
      "gist_created.image_url": image_url || linkData.gist_created.image_url,
      "gist_created.link_title": link_title || linkData.gist_created.link_title
    });

    // Get the updated link
    const updatedLinkDoc = await linkRef.get();
    const updatedLinkData = updatedLinkDoc.data();

    res.json({ 
      message: "Link gist status updated successfully",
      link: updatedLinkData
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
    
    // Check if user exists
    const userDoc = await admin.firestore().collection("users").doc(user_id).get();
    if (!userDoc.exists) {
      return res.status(404).json({ error: "User not found" });
    }

    // Get all links from subcollection
    const linksSnapshot = await admin.firestore()
      .collection("users")
      .doc(user_id)
      .collection("links")
      .get();

    const links = [];
    linksSnapshot.forEach(doc => {
      links.push(doc.data());
    });

    res.json({ 
      links: links,
      count: links.length
    });
  } catch (error) {
    console.error("Error fetching links:", error);
    res.status(500).json({ error: error.message });
  }
});

module.exports = router; 
