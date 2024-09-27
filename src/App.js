import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { FaWalking, FaUserInjured } from 'react-icons/fa'; // Replaced FaPersonFalling with FaUserInjured

// Function to get the color based on severity
const getSeverityColor = (severity) => {
  switch (severity) {
    case 'mild':
      return 'yellow';
    case 'moderate':
      return 'orange';
    case 'severe':
      return 'red';
    default:
      return 'green';  // Default color for no fall
  }
};

function App() {
  const [radarStatus, setRadarStatus] = useState('No data yet');
  const [fallSeverity, setFallSeverity] = useState('none');

  useEffect(() => {
    axios.get('http://localhost:5000/radar-data')
      .then(response => {
        const data = response.data;
        setRadarStatus(data.status === 'fall_detected' ? 'Fall detected!' : 'No fall detected');
        setFallSeverity(data.fall_severity);
      })
      .catch(error => {
        console.error('Error fetching radar data:', error);
      });
  }, []);

  return (
    <div className="App">
      <h1>Radar Fall Detection</h1>
      <div style={{ color: radarStatus === 'Fall detected!' ? getSeverityColor(fallSeverity) : 'green' }}>
        {/* Display icon and status */}
        {radarStatus === 'Fall detected!' ? <FaUserInjured size={50} /> : <FaWalking size={50} />}
        <p>{radarStatus}</p>

        {/* Display severity if a fall is detected */}
        {radarStatus === 'Fall detected!' && <p>Severity: {fallSeverity}</p>}
      </div>
    </div>
  );
}

export default App;