<?php
// Database connection parameters from your scrape.py
$host = 'localhost';
$user = 'root';
$password = '#HiMaNsHu123';
$database = 'job_lists';

// Set headers for JSON response
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');

// Handle errors
try {
    // Connect to database
    $conn = new mysqli($host, $user, $password, $database);
    
    // Check connection
    if ($conn->connect_error) {
        throw new Exception('Connection failed: ' . $conn->connect_error);
    }
    
    // Get filter parameters from request
    $keywords = isset($_GET['keywords']) ? $conn->real_escape_string($_GET['keywords']) : '';
    $location = isset($_GET['location']) ? $conn->real_escape_string($_GET['location']) : '';
    $jobType = isset($_GET['job_type']) ? $conn->real_escape_string($_GET['job_type']) : '';
    $page = isset($_GET['page']) ? intval($_GET['page']) : 1;
    $jobsPerPage = isset($_GET['per_page']) ? intval($_GET['per_page']) : 6;
    
    // Calculate offset for pagination
    $offset = ($page - 1) * $jobsPerPage;
    
    // Build the query with filters
    $query = "SELECT * FROM jobs WHERE 1=1";
    
    if ($keywords) {
        $query .= " AND (title LIKE '%$keywords%' OR company LIKE '%$keywords%')";
    }
    
    if ($location) {
        $query .= " AND location LIKE '%$location%'";
    }
    
    if ($jobType) {
        $query .= " AND job_type LIKE '%$jobType%'";
    }
    
    // Get total count for pagination
    $countResult = $conn->query($query);
    $totalJobs = $countResult->num_rows;
    
    // Add pagination to query
    $query .= " LIMIT $offset, $jobsPerPage";
    
    // Execute the query
    $result = $conn->query($query);
    
    // Prepare response
    $jobs = [];
    if ($result->num_rows > 0) {
        while($row = $result->fetch_assoc()) {
            // Convert MySQL row to a format matching your frontend expectations
            $jobs[] = [
                'id' => $row['id'],
                'title' => $row['title'],
                'company' => $row['company'],
                'location' => $row['location'],
                'type' => $row['job_type'] ? strtolower(str_replace(' ', '-', $row['job_type'])) : 'full-time',
                'date_posted' => $row['date_posted'],
                'link' => $row['link'],
                // Adding placeholder values for fields not in your database
                'experience' => 'entry',
                'description' => 'Job opportunity for qualified candidates. Contact the company for more details.',
                'tags' => ['Job Opening'],
                'accessibilityFeatures' => ['flexible'],
                'source' => 'disabilitytalent'
            ];
        }
    }
    
    // Return JSON response with pagination info
    echo json_encode([
        'jobs' => $jobs,
        'pagination' => [
            'total' => $totalJobs,
            'page' => $page,
            'perPage' => $jobsPerPage,
            'totalPages' => ceil($totalJobs / $jobsPerPage)
        ]
    ]);
    
} catch (Exception $e) {
    // Return error response
    http_response_code(500);
    echo json_encode(['error' => $e->getMessage()]);
}

// Close connection
if (isset($conn)) {
    $conn->close();
}
?>