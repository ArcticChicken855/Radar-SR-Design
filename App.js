import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { FaWalking, FaUserInjured } from 'react-icons/fa';

const getSeverityColor = (severity) => {
    switch (severity) {
        case 'mild': return 'yellow';
        case 'moderate': return 'orange';
        case 'severe': return 'red';
        default: return 'green';
    }
};

function App() {
    const [radarStatus, setRadarStatus] = useState('No data yet');
    const [fallSeverity, setFallSeverity] = useState('none');

    useEffect(() => {
        axios.get('http://138.197.73.178:5000/radar-data')  // External server IP
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
            <div style={{ color: getSeverityColor(fallSeverity) }}>
                {radarStatus === 'Fall detected!' ? <FaUserInjured size={50} /> : <FaWalking size={50} />}
                <p>{radarStatus}</p>
                {radarStatus === 'Fall detected!' && <p>Severity: {fallSeverity}</p>}
            </div>
        </div>
    );
}

export default App;