/**
 * Test Gista Subcollection API Endpoints
 * 
 * This script tests the API endpoints for the subcollection-based implementation
 * using the specific test user ID 'Gista-crewAI-Tester' to differentiate
 * from the remote service's test objects.
 */

const axios = require('axios');
const assert = require('assert');

// Configuration
const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:5001/your-project/us-central1/apiSubcollections';
const API_KEY = process.env.API_KEY || 'test-api-key';
const TEST_USER_ID = 'Gista-crewAI-Tester';

// Headers for API requests
const headers = {
  'Content-Type': 'application/json',
  'X-API-Key': API_KEY
};

// Test functions
async function testGetUserGists() {
  try {
    console.log('Testing get user gists endpoint...');
    const response = await axios.get(`${API_BASE_URL}/api/gists/subcollections/${TEST_USER_ID}`, { headers });
    
    console.log('Response:', response.status);
    assert.strictEqual(response.status, 200);
    assert.ok(Array.isArray(response.data.gists), 'Response should contain an array of gists');
    
    console.log('✅ Get user gists test passed');
    return response.data.gists;
  } catch (error) {
    console.error('❌ Get user gists test failed:', error.message);
    if (error.response) {
      console.error('Response data:', error.response.data);
    }
    throw error;
  }
}

async function testGetSpecificGist(gistId) {
  try {
    console.log(`Testing get specific gist endpoint for gist ${gistId}...`);
    const response = await axios.get(`${API_BASE_URL}/api/gists/subcollections/${TEST_USER_ID}/${gistId}`, { headers });
    
    console.log('Response:', response.status);
    assert.strictEqual(response.status, 200);
    assert.strictEqual(response.data.id, gistId, 'Gist ID should match');
    
    console.log('✅ Get specific gist test passed');
    return response.data;
  } catch (error) {
    console.error('❌ Get specific gist test failed:', error.message);
    if (error.response) {
      console.error('Response data:', error.response.data);
    }
    throw error;
  }
}

async function testGetUserLinks() {
  try {
    console.log('Testing get user links endpoint...');
    const response = await axios.get(`${API_BASE_URL}/api/links/subcollections/${TEST_USER_ID}`, { headers });
    
    console.log('Response:', response.status);
    assert.strictEqual(response.status, 200);
    assert.ok(Array.isArray(response.data.links), 'Response should contain an array of links');
    
    console.log('✅ Get user links test passed');
    return response.data.links;
  } catch (error) {
    console.error('❌ Get user links test failed:', error.message);
    if (error.response) {
      console.error('Response data:', error.response.data);
    }
    throw error;
  }
}

async function testStoreLink() {
  try {
    console.log('Testing store link endpoint...');
    const linkData = {
      user_id: TEST_USER_ID,
      link: {
        gist_created: {
          link_title: 'Gista Test Link',
          url: 'https://example.com/gista-test',
          image_url: 'https://example.com/gista-test.jpg'
        },
        category: 'Gista Test Category',
        description: 'This is a Gista test link'
      },
      auto_create_gist: true
    };
    
    const response = await axios.post(`${API_BASE_URL}/api/links/subcollections/store`, linkData, { headers });
    
    console.log('Response:', response.status);
    assert.strictEqual(response.status, 200);
    assert.ok(response.data.gistId, 'Response should contain a gistId');
    
    console.log('✅ Store link test passed');
    return response.data.gistId;
  } catch (error) {
    console.error('❌ Store link test failed:', error.message);
    if (error.response) {
      console.error('Response data:', error.response.data);
    }
    throw error;
  }
}

async function testAddGist() {
  try {
    console.log('Testing add gist endpoint...');
    const gistData = {
      title: 'Gista Test Gist',
      image_url: 'https://example.com/gista-test.jpg',
      link: 'https://example.com/gista-test',
      category: 'Gista Test Category',
      segments: [
        {
          title: 'Gista Test Segment',
          audioUrl: 'https://example.com/gista-test.mp3',
          duration: '60',
          index: 0
        }
      ]
    };
    
    const response = await axios.post(`${API_BASE_URL}/api/gists/subcollections/add/${TEST_USER_ID}`, gistData, { headers });
    
    console.log('Response:', response.status);
    assert.strictEqual(response.status, 200);
    assert.strictEqual(response.data.message, 'Gist added successfully');
    assert.ok(response.data.gist, 'Response should contain the gist data');
    
    console.log('✅ Add gist test passed');
    return response.data.gist.id;
  } catch (error) {
    console.error('❌ Add gist test failed:', error.message);
    if (error.response) {
      console.error('Response data:', error.response.data);
    }
    throw error;
  }
}

async function testUpdateGistStatus(gistId) {
  try {
    console.log(`Testing signal-based update gist status endpoint for gist ${gistId}...`);
    // Using empty JSON object - signal-based approach
    const response = await axios.put(`${API_BASE_URL}/api/gists/${TEST_USER_ID}/${gistId}/status`, {}, { headers });
    
    console.log('Response:', response.status);
    assert.strictEqual(response.status, 200);
    
    // Check if the response contains a link URL (signal-based API response)
    if (response.data.link) {
      console.log(`Received link URL in response: ${response.data.link}`);
    }
    
    // If response has status field, verify it
    if (response.data.status) {
      if (response.data.status.inProduction !== undefined) {
        console.log(`Status inProduction: ${response.data.status.inProduction}`);
      }
      if (response.data.status.production_status) {
        console.log(`Status production_status: ${response.data.status.production_status}`);
      }
    }
    
    console.log('✅ Signal-based update gist status test passed');
    return response.data;
  } catch (error) {
    console.error('❌ Update gist status test failed:', error.message);
    if (error.response) {
      console.error('Response data:', error.response.data);
    }
    throw error;
  }
}

// Run all tests
async function runTests() {
  try {
    console.log('Starting API tests for Gista subcollection implementation...');
    console.log('API Base URL:', API_BASE_URL);
    console.log('Test User ID:', TEST_USER_ID);
    
    // Test getting user gists
    const gists = await testGetUserGists();
    
    // Test getting specific gist (if gists exist)
    let gistId;
    if (gists && gists.length > 0) {
      gistId = gists[0].id;
      await testGetSpecificGist(gistId);
    } else {
      console.log('No existing gists found, skipping specific gist test');
    }
    
    // Test getting user links
    await testGetUserLinks();
    
    // Test storing a link
    const newGistId = await testStoreLink();
    
    // Test getting the newly created gist
    await testGetSpecificGist(newGistId);
    
    // Test adding a gist
    const addedGistId = await testAddGist();
    
    // Test updating gist status using signal-based approach
    await testUpdateGistStatus(addedGistId);
    
    console.log('All tests completed successfully! 🎉');
    console.log('Note: The signal-based API for updating gist status is now implemented and working.');
    console.log('The API does not require any request body - simply making the PUT request triggers the status update.');
  } catch (error) {
    console.error('Test suite failed:', error.message);
    process.exit(1);
  }
}

// Run the tests
runTests(); 