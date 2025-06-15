import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import ATSToolApp from './components/ATSToolApp';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<ATSToolApp />} />
          <Route path="/ats" element={<ATSToolApp />} />
          {/* Other routes */}
        </Routes>
      </div>
    </Router>
  );
}

export default App;