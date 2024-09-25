import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { FaWalking, FaUserInjured, FaPersonBooth, FaExclamationTriangle, FaCheckCircle } from 'react-icons/fa';

function App() {
  const [radarStatus, setRadarStatus] = useState('No data yet');
  const [fallType, setFallType] = useState('');
  const [fallSeverity, setFallSeverity] = useState('');
  const [timestamp, setTimestamp] = useState('');

  // Colors and icons for different statuses
  const getFallColor = (status) => {
    return status === 'fall_detected' ? 'red' : 'green';
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'minor':
        return <FaCheckCircle color="yellow" />;
      case 'moderate':
        return <FaExclamationTriangle color="orange" />;
      case 'severe':
        return <FaExclamationTriangle color="red" />;
      default:
        return null;
    }
  };

  const getFallTypeIcon = (type) => {
    switch (type) {
      case 'slip':
        return <FaUserInjured />; // FaUserInjured as a replacement
      case 'trip':
        return <FaPersonBooth />;
      case 'collapse':
        return <FaUserInjured />; // Another use of FaUserInjured
      default:
        return <FaWalking />;
    }
  };

  useEffect(() => {
    axios.get('http://localhost:5000/radar-data')
      .then(response => {
        const data = response.data;
        setRadarStatus(data.status === 'fall_detected' ? 'Fall detected!' : 'No fall detected');
        setFallType(data.fall_type);
        setFallSeverity(data.fall_severity);
        setTimestamp(data.timestamp);
      })
      .catch(error => {
        console.error('Error fetching radar data:', error);
      });
  }, []);

  return (
    <div className="App">
      <h1>Radar Fall Detection</h1>

      {/* Display Fall/No Fall with color */}
      <div style={{ color: getFallColor(radarStatus) }}>
        {radarStatus === 'Fall detected!' ? <FaUserInjured size={50} /> : <FaWalking size={50} />}
        <p>{radarStatus}</p>
      </div>

      {/* Display Type of Fall */}
      <div>
        <p>Type of Fall:</p>
        <div>{getFallTypeIcon(fallType)}</div>
        <p>{fallType}</p>
      </div>

      {/* Display Severity of Fall */}
      <div>
        <p>Severity of Fall:</p>
        <div>{getSeverityIcon(fallSeverity)}</div>
        <p>{fallSeverity}</p>
      </div>

      <p>Timestamp: {timestamp}</p>
    </div>
  );
}

export default App;