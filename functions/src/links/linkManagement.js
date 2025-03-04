const express = require("express");
const admin = require("firebase-admin");
const router = express.Router();

// Store link
router.post("/store", async (req, res) => {
  try {
    const { user_id, link } = req.body;

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

    res.json({ 
      message: "Link stored successfully",
      link: linkData
    });
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