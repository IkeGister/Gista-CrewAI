/**
 * Update User Structure
 * 
 * This script migrates an existing user from the old structure (where gists and links
 * are stored directly in the user document) to the new subcollection-based structure.
 */

const admin = require('firebase-admin');
const serviceAccount = require('../Firebase/config/serviceAccountKey.json');

// Initialize Firebase Admin SDK
admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});

const db = admin.firestore();

// Default to a test user ID, but you can pass a user ID as a command line argument
const USER_ID = process.argv[2] || 'crewAI-backend-tester';
// To migrate all users, set this to true (or pass --all as the second argument)
const MIGRATE_ALL_USERS = process.argv[3] === '--all';

/**
 * Migrate a single user to the subcollection structure
 * @param {string} userId - The ID of the user to migrate
 */
async function migrateUser(userId) {
  console.log(`Starting migration for user: ${userId}...`);
  
  try {
    // Get the user document
    const userDoc = await db.collection('users').doc(userId).get();
    
    if (!userDoc.exists) {
      console.error(`User ${userId} does not exist`);
      return;
    }
    
    const userData = userDoc.data();
    const gists = userData.gists || [];
    const links = userData.links || [];
    
    console.log(`Found user ${userId} with ${gists.length} gists and ${links.length} links`);
    
    // Migrate gists to subcollections
    const gistPromises = gists.map(async (gist) => {
      const gistId = gist.gistId || gist.id;
      if (!gistId) {
        console.warn('Skipping gist without ID:', gist);
        return;
      }
      
      // Normalize the gist data
      const normalizedGist = {
        id: gistId,
        title: gist.title || 'Untitled Gist',
        content: gist.content || '',
        category: gist.category || 'Uncategorized',
        is_played: gist.is_played || false,
        is_published: gist.is_published || false,
        link: gist.link || '',
        image_url: gist.image_url || '',
        publisher: gist.publisher || 'theNewGista',
        playback_duration: gist.playback_duration || 0,
        ratings: gist.ratings || 0,
        segments: gist.segments || [],
        status: gist.status || {
          inProduction: false,
          production_status: 'draft'
        },
        createdAt: gist.date_created ? new Date(gist.date_created) : admin.firestore.FieldValue.serverTimestamp(),
        updatedAt: admin.firestore.FieldValue.serverTimestamp()
      };
      
      // Save the gist to the subcollection
      console.log(`Migrating gist ${gistId} to subcollection`);
      await db.collection('users').doc(userId).collection('gists').doc(gistId).set(normalizedGist);
      
      // Find and migrate links associated with this gist
      const gistLinks = links.filter(link => 
        link.gist_created && link.gist_created.gistId === gistId);
      
      for (const link of gistLinks) {
        const linkId = link.gist_created.link_id || `link_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        // Normalize the link data
        const normalizedLink = {
          id: linkId,
          url: link.gist_created.url || '',
          title: link.gist_created.link_title || '',
          description: link.gist_created.description || '',
          category: link.category || 'Uncategorized',
          date_added: link.date_added ? new Date(link.date_added) : admin.firestore.FieldValue.serverTimestamp(),
          gistId: gistId,
          inProduction: link.inProduction || false,
          production_status: link.production_status || 'draft',
          updatedAt: admin.firestore.FieldValue.serverTimestamp()
        };
        
        // Save the link to the gist's links subcollection
        console.log(`Migrating link ${linkId} for gist ${gistId} to subcollection`);
        await db.collection('users').doc(userId)
          .collection('gists').doc(gistId)
          .collection('links').doc(linkId)
          .set(normalizedLink);
      }
    });
    
    // Migrate general links (links not associated with any gist)
    const generalLinkPromises = links
      .filter(link => !link.gist_created || !link.gist_created.gistId)
      .map(async (link) => {
        const linkId = link.id || `link_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        // Normalize the link data
        const normalizedLink = {
          id: linkId,
          url: link.url || '',
          title: link.title || '',
          description: link.description || '',
          category: link.category || 'Uncategorized',
          date_added: link.date_added ? new Date(link.date_added) : admin.firestore.FieldValue.serverTimestamp(),
          inProduction: link.inProduction || false,
          production_status: link.production_status || 'draft',
          updatedAt: admin.firestore.FieldValue.serverTimestamp()
        };
        
        // Save the link to the user's links subcollection
        console.log(`Migrating general link ${linkId} to subcollection`);
        await db.collection('users').doc(userId)
          .collection('links').doc(linkId)
          .set(normalizedLink);
      });
    
    // Wait for all migrations to complete
    await Promise.all([...gistPromises, ...generalLinkPromises]);
    
    // Optionally, you can update the user document to mark it as migrated
    await db.collection('users').doc(userId).update({
      migrated_to_subcollections: true,
      updatedAt: admin.firestore.FieldValue.serverTimestamp()
    });
    
    console.log(`Migration completed for user ${userId}`);
    
  } catch (error) {
    console.error(`Error migrating user ${userId}:`, error);
  }
}

/**
 * Migrate all users to the subcollection structure
 */
async function migrateAllUsers() {
  try {
    console.log('Starting migration for all users...');
    
    // Get all users
    const usersSnapshot = await db.collection('users').get();
    
    if (usersSnapshot.empty) {
      console.log('No users found to migrate');
      return;
    }
    
    // Process each user in sequence to avoid overwhelming the database
    for (const userDoc of usersSnapshot.docs) {
      const userId = userDoc.id;
      await migrateUser(userId);
    }
    
    console.log('Migration completed for all users');
    
  } catch (error) {
    console.error('Error migrating all users:', error);
  } finally {
    // Terminate the Firebase Admin SDK
    await admin.app().delete();
  }
}

// Run the migration
if (MIGRATE_ALL_USERS) {
  migrateAllUsers();
} else {
  migrateUser(USER_ID).then(() => {
    // Terminate the Firebase Admin SDK
    admin.app().delete();
  });
} 