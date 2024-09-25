import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { FaWalking, FaPersonFalling } from 'react-icons/fa';

function App() {
  const [radarStatus, setRadarStatus] = useState('No data yet');

  // Fetch data from Flask backend
  useEffect(() => {
    axios.get('http://localhost:5000/radar-data')
      .then(response => {
        const data = response.data;
        setRadarStatus(data.status === 'fall_detected' ? 'Fall detected!' : 'No fall detected');
      })
      .catch(error => {
        console.error('Error fetching radar data:', error);
      });
  }, []);

  return (
    <div className="App">
      <h1>Radar Fall Detection</h1>
      <div style={{ color: radarStatus === 'Fall detected!' ? 'red' : 'green' }}>
        {radarStatus === 'Fall detected!' ? <FaPersonFalling size={50} /> : <FaWalking size={50} />}
        <p>{radarStatus}</p>
      </div>
    </div>
  );
}

export default App;