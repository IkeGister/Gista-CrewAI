/**
 * Create Subcollection Test Data
 * 
 * This script creates test data using the new subcollection structure
 * to verify it works correctly. It creates a test user with gists and links
 * using the subcollection structure.
 */

const admin = require('firebase-admin');
const serviceAccount = require('../Firebase/config/serviceAccountKey.json');

// Initialize Firebase Admin SDK
admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});

const db = admin.firestore();
const TEST_USER_ID = 'crewAI-backend-tester';

/**
 * Create test data with the subcollection structure
 */
async function createTestData() {
  try {
    console.log('Creating test data with subcollection structure...');
    
    // Create or update user document
    await db.collection('users').doc(TEST_USER_ID).set({
      id: TEST_USER_ID,
      username: 'Test User',
      email: 'test@example.com',
      createdAt: admin.firestore.FieldValue.serverTimestamp(),
      updatedAt: admin.firestore.FieldValue.serverTimestamp()
    }, { merge: true });
    
    console.log(`Created/updated user document for ${TEST_USER_ID}`);
    
    // Create test gists in the subcollection
    const gistsData = [
      {
        id: 'gist_test_1',
        title: 'Test Gist 1',
        content: 'This is test gist 1 content',
        category: 'Technology',
        is_played: false,
        is_published: true,
        link: 'https://example.com/article1',
        image_url: 'https://example.com/image1.jpg',
        publisher: 'theNewGista',
        playback_duration: 120,
        ratings: 4,
        segments: [
          {
            segment_title: 'Introduction',
            segment_audioUrl: 'https://example.com/audio1.mp3',
            playback_duration: '60',
            segment_index: '0'
          },
          {
            segment_title: 'Main Content',
            segment_audioUrl: 'https://example.com/audio2.mp3',
            playback_duration: '60',
            segment_index: '1'
          }
        ],
        status: {
          inProduction: false,
          production_status: 'completed'
        },
        createdAt: admin.firestore.FieldValue.serverTimestamp(),
        updatedAt: admin.firestore.FieldValue.serverTimestamp()
      },
      {
        id: 'gist_test_2',
        title: 'Test Gist 2',
        content: 'This is test gist 2 content',
        category: 'Business',
        is_played: true,
        is_published: true,
        link: 'https://example.com/article2',
        image_url: 'https://example.com/image2.jpg',
        publisher: 'theNewGista',
        playback_duration: 180,
        ratings: 5,
        segments: [
          {
            segment_title: 'Overview',
            segment_audioUrl: 'https://example.com/audio3.mp3',
            playback_duration: '90',
            segment_index: '0'
          },
          {
            segment_title: 'Details',
            segment_audioUrl: 'https://example.com/audio4.mp3',
            playback_duration: '90',
            segment_index: '1'
          }
        ],
        status: {
          inProduction: false,
          production_status: 'draft'
        },
        createdAt: admin.firestore.FieldValue.serverTimestamp(),
        updatedAt: admin.firestore.FieldValue.serverTimestamp()
      }
    ];
    
    // Add gists to the subcollection
    for (const gistData of gistsData) {
      const gistId = gistData.id;
      await db.collection('users').doc(TEST_USER_ID).collection('gists').doc(gistId).set(gistData);
      console.log(`Created gist ${gistId} in subcollection`);
      
      // Add links for this gist
      const linksData = [
        {
          id: `link_${gistId}_1`,
          url: `https://example.com/${gistId}/link1`,
          title: `Link 1 for ${gistId}`,
          description: 'This is a test link',
          category: 'Technology',
          date_added: admin.firestore.FieldValue.serverTimestamp(),
          gistId: gistId,
          inProduction: false,
          production_status: 'published',
          updatedAt: admin.firestore.FieldValue.serverTimestamp()
        },
        {
          id: `link_${gistId}_2`,
          url: `https://example.com/${gistId}/link2`,
          title: `Link 2 for ${gistId}`,
          description: 'This is another test link',
          category: 'Business',
          date_added: admin.firestore.FieldValue.serverTimestamp(),
          gistId: gistId,
          inProduction: false,
          production_status: 'review',
          updatedAt: admin.firestore.FieldValue.serverTimestamp()
        }
      ];
      
      // Add links to the gist's links subcollection
      for (const linkData of linksData) {
        const linkId = linkData.id;
        await db.collection('users').doc(TEST_USER_ID)
          .collection('gists').doc(gistId)
          .collection('links').doc(linkId)
          .set(linkData);
        console.log(`Created link ${linkId} for gist ${gistId}`);
      }
    }
    
    // Add some general links directly to the user's links subcollection
    const generalLinks = [
      {
        id: 'link_general_1',
        url: 'https://example.com/general1',
        title: 'General Link 1',
        description: 'This is a general test link',
        category: 'News',
        date_added: admin.firestore.FieldValue.serverTimestamp(),
        inProduction: false,
        production_status: 'published',
        updatedAt: admin.firestore.FieldValue.serverTimestamp()
      },
      {
        id: 'link_general_2',
        url: 'https://example.com/general2',
        title: 'General Link 2',
        description: 'This is another general test link',
        category: 'Entertainment',
        date_added: admin.firestore.FieldValue.serverTimestamp(),
        inProduction: false,
        production_status: 'draft',
        updatedAt: admin.firestore.FieldValue.serverTimestamp()
      }
    ];
    
    // Add general links to the user's links subcollection
    for (const linkData of generalLinks) {
      const linkId = linkData.id;
      await db.collection('users').doc(TEST_USER_ID)
        .collection('links').doc(linkId)
        .set(linkData);
      console.log(`Created general link ${linkId}`);
    }
    
    console.log('Test data creation completed successfully!');
    
  } catch (error) {
    console.error('Error creating test data:', error);
  } finally {
    // Terminate the Firebase Admin SDK
    await admin.app().delete();
  }
}

// Run the function
createTestData(); 