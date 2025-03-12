/**
 * Type definitions for Gist and related interfaces
 */

/**
 * Segment interface - represents a segment within a gist
 */
export interface Segment {
  // Required fields
  title: string;                // Title of the segment
  audioUrl: string;             // URL to the audio file
  duration: string;             // Duration of the segment in seconds (as a string)
  index: number;                // Position of the segment (integer)
}

/**
 * GistStatus interface - represents the status of a gist
 */
export interface GistStatus {
  production_status: string;    // Status of production (default: "Reviewing Content")
  inProduction: boolean;        // Whether the gist is in production (default: false)
}

/**
 * Gist interface - represents a complete gist object
 */
export interface Gist {
  // Required fields
  title: string;                // Title of the gist
  image_url: string;            // URL to the image associated with the gist
  link: string;                 // URL of the content that the gist is based on
  category: string;             // Category of the gist
  link_id: string;              // ID of the link that this gist is associated with
  segments: Segment[];          // Array of segments (must contain at least one segment)
  
  // Optional fields with defaults
  gistId?: string;              // Unique identifier (generated if not provided)
  isFinished: boolean;          // Whether the gist is finished (default: false)
  is_played: boolean;           // Whether the gist has been played (default: false)
  is_published: boolean;        // Whether the gist is published (default: true)
  playbackDuration: number;     // Duration of the gist in seconds (default: 0)
  playbackTime: number;         // Current playback time (default: 0)
  publisher: string;            // Publisher of the gist (default: "theNewGista")
  ratings: number;              // Ratings for the gist (default: 0)
  users: number;                // Number of users who have interacted with the gist (default: 0)
  date_created?: string;        // Creation date (ISO format, generated if not provided)
  status: GistStatus;           // Status object
}

/**
 * GistResponse interface - represents the server response when creating or retrieving a gist
 */
export interface GistResponse {
  gistId: string;
  title: string;
  image_url: string;
  link: string;
  category: string;
  date_created: string;
  is_played: boolean;
  is_published: boolean;
  playback_duration: number;
  publisher: string;
  ratings: number;
  segments: {
    segment_title: string;
    segment_audioUrl: string;
    playback_duration: string;
    segment_index: string;
  }[];
  status: GistStatus;
  users: number;
}

/**
 * CreateGistRequest interface - represents the minimum required fields to create a gist
 */
export interface CreateGistRequest {
  title: string;
  image_url: string;
  link: string;
  category: string;
  link_id: string;
  segments: Segment[];
  isFinished?: boolean;
  playbackDuration?: number;
  playbackTime?: number;
}

/**
 * UpdateGistRequest interface - represents the request to update a gist
 */
export interface UpdateGistRequest {
  // Status-related fields
  inProduction?: boolean;
  production_status?: string;
  
  // Other fields that can be updated
  is_played?: boolean;
  ratings?: number;
  users?: number;
} 