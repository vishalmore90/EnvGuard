// Fixture: JavaScript project index file
// Tests all process.env access patterns

// Pattern 1: process.env.KEY (member expression)
const dbUrl = process.env.DATABASE_URL;

// Pattern 2: process.env["KEY"] (bracket, double quotes)
const apiKey = process.env["API_KEY"];

// Pattern 3: process.env['KEY'] (bracket, single quotes)
const debug = process.env['DEBUG'];

// With fallback operator (|| or ??) — default is at JS level, not env access level
const port = process.env.PORT || "3000";
const nodeEnv = process.env.NODE_ENV ?? "development";

// This dynamic key should NOT be detected
const key = "SOME_KEY";
const dynamic = process.env[key];

// Comment containing process.env.SHOULD_NOT_BE_DETECTED — should be skipped
