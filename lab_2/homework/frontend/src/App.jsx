import React, { useState } from 'react';
import SearchStandingsForm from './components/SearchStandingsForm';
import SearchMatchesForm from './components/SearchMatchesForm.jsx';
import './App.css'


const App = () => {
  const [view, setView] = useState('home');

  const handleViewChange = (viewName) => {
    setView(viewName);
  };

   return (
    <div className="app-container">
      <header className="app-header">
        <h1>Football Standings & Matches</h1>
      </header>

      <div className="buttons-container">
        <button
          className="btn"
          onClick={() => handleViewChange('form')}
        >
          Show League Table
        </button>
        <button
          className="btn"
          onClick={() => handleViewChange('matches')}
        >
          Show Matches
        </button>
      </div>


      {view === 'form' && <SearchStandingsForm />}
      {view === 'matches' && <SearchMatchesForm />}
    </div>
  );


};

export default App;
