/**
 * Direct Test for Subcollection Operations
 * 
 * This script tests the subcollection operations directly using Firebase Admin SDK
 * without relying on API endpoints. It follows the test flow:
 * 1. Create a user
 * 2. Store a link
 * 3. Create a gist
 * 4. Update gist status (simulating remote service)
 */

const admin = require('firebase-admin');
const serviceAccount = require('../Firebase/config/serviceAccountKey.json');

// Initialize Firebase Admin SDK
admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});

const db = admin.firestore();
const TEST_USER_ID = 'Gista-crewAI-Tester';

/**
 * Test the subcollection operations
 */
async function testSubcollections() {
  try {
    console.log('==========================================');
    console.log('  Testing Subcollection Operations');
    console.log('==========================================');
    console.log(`Using test user ID: ${TEST_USER_ID}`);
    
    // Step 1: Get or create user
    console.log('\n📋 Step 1: Get or create user');
    const userRef = db.collection('users').doc(TEST_USER_ID);
    const userDoc = await userRef.get();
    
    if (!userDoc.exists) {
      console.log('User does not exist, creating new user...');
      await userRef.set({
        id: TEST_USER_ID,
        username: 'Gista Test User',
        email: 'gista-test@example.com',
        createdAt: admin.firestore.FieldValue.serverTimestamp(),
        updatedAt: admin.firestore.FieldValue.serverTimestamp()
      });
      console.log('✅ User created successfully');
    } else {
      console.log('✅ User already exists');
    }
    
    // Step 2: Store a link
    console.log('\n📋 Step 2: Store a link');
    const linkId = `link_test_${Date.now()}`;
    const linkData = {
      id: linkId,
      url: 'https://example.com/gista-test-link',
      title: 'Gista Test Link',
      description: 'This is a test link for Gista-CrewAI',
      category: 'Test',
      date_added: admin.firestore.FieldValue.serverTimestamp(),
      inProduction: false,
      production_status: 'draft',
      updatedAt: admin.firestore.FieldValue.serverTimestamp()
    };
    
    await userRef.collection('links').doc(linkId).set(linkData);
    console.log(`✅ Link ${linkId} stored successfully`);
    
    // Step 3: Create a gist from the link
    console.log('\n📋 Step 3: Create a gist');
    const gistId = `gist_test_${Date.now()}`;
    const gistData = {
      id: gistId,
      title: 'Gista Test Gist',
      content: 'This is a test gist for Gista-CrewAI',
      category: 'Test',
      is_played: false,
      is_published: true,
      link: linkData.url,
      image_url: 'https://example.com/image.jpg',
      publisher: 'theNewGista',
      playback_duration: 60,
      ratings: 0,
      segments: [
        {
          segment_title: 'Test Segment',
          segment_audioUrl: 'https://example.com/audio.mp3',
          playback_duration: '60',
          segment_index: '0'
        }
      ],
      status: {
        inProduction: false,
        production_status: 'draft'
      },
      createdAt: admin.firestore.FieldValue.serverTimestamp(),
      updatedAt: admin.firestore.FieldValue.serverTimestamp()
    };
    
    await userRef.collection('gists').doc(gistId).set(gistData);
    console.log(`✅ Gist ${gistId} created successfully`);
    
    // Also associate the link with the gist
    await userRef.collection('links').doc(linkId).update({
      gistId: gistId
    });
    
    // Add the link to the gist's links subcollection
    linkData.gistId = gistId;
    await userRef.collection('gists').doc(gistId).collection('links').doc(linkId).set(linkData);
    console.log(`✅ Link ${linkId} associated with gist ${gistId}`);
    
    // Step 4: Update gist status (simulating remote service update)
    console.log('\n📋 Step 4: Update gist status (simulating remote service)');
    await userRef.collection('gists').doc(gistId).update({
      'status.inProduction': true,
      'status.production_status': 'In Production',
      'updatedAt': admin.firestore.FieldValue.serverTimestamp()
    });
    console.log(`✅ Gist ${gistId} status updated to In Production`);
    
    // Step 5: Get all gists for the user
    console.log('\n📋 Step 5: Get all gists for the user');
    const gistsSnapshot = await userRef.collection('gists').get();
    console.log(`Found ${gistsSnapshot.size} gists for user ${TEST_USER_ID}:`);
    gistsSnapshot.forEach(doc => {
      const gist = doc.data();
      console.log(`- ${gist.id}: ${gist.title} (Status: ${gist.status.production_status})`);
    });
    
    // Step 6: Get all links for a specific gist
    console.log(`\n📋 Step 6: Get all links for gist ${gistId}`);
    const linksSnapshot = await userRef.collection('gists').doc(gistId).collection('links').get();
    console.log(`Found ${linksSnapshot.size} links for gist ${gistId}:`);
    linksSnapshot.forEach(doc => {
      const link = doc.data();
      console.log(`- ${link.id}: ${link.title} (${link.url})`);
    });
    
    // Step 7: Update a property in the gist (not production status)
    console.log('\n📋 Step 7: Update a property in the gist (not production status)');
    await userRef.collection('gists').doc(gistId).update({
      'title': 'Updated Gist Title',
      'is_played': true,
      'updatedAt': admin.firestore.FieldValue.serverTimestamp()
    });
    console.log(`✅ Gist ${gistId} properties updated`);
    
    // Verify the update
    const updatedGistDoc = await userRef.collection('gists').doc(gistId).get();
    const updatedGist = updatedGistDoc.data();
    console.log('Updated gist properties:');
    console.log(`- Title: ${updatedGist.title}`);
    console.log(`- Is Played: ${updatedGist.is_played}`);
    console.log(`- Status: ${updatedGist.status.production_status} (inProduction: ${updatedGist.status.inProduction})`);
    
    console.log('\n==========================================');
    console.log('  Subcollection Tests Completed Successfully! 🎉');
    console.log('==========================================');
    
  } catch (error) {
    console.error('❌ Error during subcollection tests:', error);
  } finally {
    // Terminate the Firebase Admin SDK
    await admin.app().delete();
  }
}

// Run the test
testSubcollections(); 