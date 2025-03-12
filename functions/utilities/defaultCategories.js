const admin = require("firebase-admin");

const defaultCategories = [
  {
    _id: "cat001",
    name: "Business",
    slug: "business",
    tags: ["finance", "economics", "startups"]
  },
  {
    _id: "cat002",
    name: "Technology",
    slug: "technology",
    tags: ["innovation", "gadgets", "software"]
  },
  {
    _id: "cat003",
    name: "Sports",
    slug: "sports",
    tags: ["football", "basketball", "athletics"]
  },
  {
    _id: "cat004",
    name: "AI",
    slug: "ai",
    tags: ["machine-learning", "deep-learning", "automation"]
  },
  {
    _id: "cat005",
    name: "Health & Wellness",
    slug: "health-wellness",
    tags: ["fitness", "mental-health", "nutrition"]
  },
  {
    _id: "cat006",
    name: "Entertainment",
    slug: "entertainment",
    tags: ["movies", "music", "television"]
  },
  {
    _id: "cat007",
    name: "Politics",
    slug: "politics",
    tags: ["government", "elections", "policy"]
  },
  {
    _id: "cat008",
    name: "Education",
    slug: "education",
    tags: ["learning", "academics", "schools"]
  },
  {
    _id: "cat009",
    name: "Travel",
    slug: "travel",
    tags: ["tourism", "vacations", "adventure"]
  },
  {
    _id: "cat010",
    name: "Food & Dining",
    slug: "food-dining",
    tags: ["recipes", "restaurants", "cooking"]
  },
  {
    _id: "cat011",
    name: "Fashion & Style",
    slug: "fashion-style",
    tags: ["clothing", "trends", "beauty"]
  },
  {
    _id: "cat012",
    name: "Science & Research",
    slug: "science-research",
    tags: ["discoveries", "experiments", "innovation"]
  },
  {
    _id: "cat013",
    name: "Arts & Culture",
    slug: "arts-culture",
    tags: ["painting", "theatre", "literature"]
  },
  {
    _id: "cat014",
    name: "Gaming",
    slug: "gaming",
    tags: ["video-games", "esports", "board-games"]
  },
  {
    _id: "cat015",
    name: "Environment & Sustainability",
    slug: "environment-sustainability",
    tags: ["climate-change", "renewable-energy", "conservation"]
  }
];

const initializeDefaultCategories = async (admin) => {
  try {
    const categoriesRef = admin.firestore().collection("categories");
    const batch = admin.firestore().batch();

    for (const category of defaultCategories) {
      const docRef = categoriesRef.doc(category._id);
      batch.set(docRef, category, { merge: true }); // merge: true to avoid overwriting existing docs
    }

    await batch.commit();
    console.log("Default categories initialized successfully");
    return { success: true, count: defaultCategories.length };
  } catch (error) {
    console.error("Error initializing default categories:", error);
    return { success: false, error: error.message };
  }
};

module.exports = {
  defaultCategories,
  initializeDefaultCategories
}; 