const express = require("express");
const admin = require("firebase-admin");
const router = express.Router();

// Get all categories
router.get("/", async (req, res) => {
  try {
    const categoriesSnapshot = await admin.firestore()
      .collection("categories")
      .orderBy("_id")  // Order by _id to get them in sequence
      .get();

    const categories = [];
    categoriesSnapshot.forEach(doc => {
      categories.push(doc.data());
    });

    res.json({ 
      categories,
      count: categories.length
    });
  } catch (error) {
    console.error("Error fetching categories:", error);
    res.status(500).json({ error: error.message });
  }
});

// Get category by slug
router.get("/:slug", async (req, res) => {
  try {
    const { slug } = req.params;
    const categoriesSnapshot = await admin.firestore()
      .collection("categories")
      .where("slug", "==", slug)
      .get();

    if (categoriesSnapshot.empty) {
      return res.status(404).json({ error: "Category not found" });
    }

    const category = categoriesSnapshot.docs[0].data();
    res.json(category);
  } catch (error) {
    console.error("Error fetching category:", error);
    res.status(500).json({ error: error.message });
  }
});

// Update category tags
router.put("/update-tags/:id", async (req, res) => {
  try {
    const { id } = req.params;
    const { tags } = req.body;

    if (!Array.isArray(tags)) {
      return res.status(400).json({ error: "Tags must be an array" });
    }

    const categoryRef = admin.firestore().collection("categories").doc(id);
    const categoryDoc = await categoryRef.get();

    if (!categoryDoc.exists) {
      return res.status(404).json({ error: "Category not found" });
    }

    await categoryRef.update({
      tags: tags
    });

    const updatedDoc = await categoryRef.get();
    res.json({ 
      message: "Category tags updated successfully",
      category: updatedDoc.data()
    });
  } catch (error) {
    console.error("Error updating category tags:", error);
    res.status(500).json({ error: error.message });
  }
});

// Add new category with auto-incrementing ID
router.post("/add", async (req, res) => {
  try {
    const { name, tags } = req.body;

    if (!name || !tags) {
      return res.status(400).json({ error: "Name and tags are required" });
    }

    // Create slug from name
    const slug = name.toLowerCase().replace(/[^a-z0-9]+/g, "-");

    // Check if slug already exists
    const existingCat = await admin.firestore()
      .collection("categories")
      .where("slug", "==", slug)
      .get();

    if (!existingCat.empty) {
      return res.status(400).json({ error: "Category with this name already exists" });
    }

    // Get the last category ID
    const lastCategory = await admin.firestore()
      .collection("categories")
      .orderBy("_id", "desc")
      .limit(1)
      .get();

    // Generate next ID
    let nextId;
    if (lastCategory.empty) {
      nextId = "cat001";
    } else {
      const lastId = lastCategory.docs[0].data()._id;
      const lastNumber = parseInt(lastId.slice(3));  // Get number from "cat001" -> 1
      nextId = `cat${String(lastNumber + 1).padStart(3, '0')}`;  // Format: cat002, cat003, etc.
    }

    const categoryData = {
      _id: nextId,
      name,
      slug,
      tags
    };

    await admin.firestore()
      .collection("categories")
      .doc(nextId)
      .set(categoryData);

    res.status(201).json({ 
      message: "Category added successfully",
      category: categoryData
    });
  } catch (error) {
    console.error("Error adding category:", error);
    res.status(500).json({ error: error.message });
  }
});

// Update category
router.put("/update/:id", async (req, res) => {
  try {
    const { id } = req.params;
    const { name, tags } = req.body;

    if (!name && !tags) {
      return res.status(400).json({ error: "At least one field (name or tags) is required" });
    }

    const categoryRef = admin.firestore().collection("categories").doc(id);
    const categoryDoc = await categoryRef.get();

    if (!categoryDoc.exists) {
      return res.status(404).json({ error: "Category not found" });
    }

    const updateData = {};
    if (name) {
      updateData.name = name;
      updateData.slug = name.toLowerCase().replace(/[^a-z0-9]+/g, "-");
      
      // Check if new slug would conflict with existing category
      if (updateData.slug !== categoryDoc.data().slug) {
        const existingCat = await admin.firestore()
          .collection("categories")
          .where("slug", "==", updateData.slug)
          .get();

        if (!existingCat.empty) {
          return res.status(400).json({ error: "Category with this name already exists" });
        }
      }
    }
    if (tags) {
      updateData.tags = tags;
    }

    await categoryRef.update(updateData);

    const updatedDoc = await categoryRef.get();
    res.json({ 
      message: "Category updated successfully",
      category: updatedDoc.data()
    });
  } catch (error) {
    console.error("Error updating category:", error);
    res.status(500).json({ error: error.message });
  }
});

module.exports = router; 