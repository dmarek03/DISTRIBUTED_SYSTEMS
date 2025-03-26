import React, {useState} from "react";
import {leagues, champions_league_stages} from "./ComboboxData.jsx";
import Matches from "./Matches.jsx";
import api from "../api.js";

const SearchMatchesForm = () => {
    const [leagueName, setLeagueName] = useState('');
    const [championsLeaguStage, setChampionsLeagueStage] = useState('');
    const [season, setSeason] = useState('');
    const [matchday, setMatchday] = useState('');

    const [matchesData, setMatchesData] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleSubmit = async (event) => {
        event.preventDefault()
        setMatchesData(null);
        setError(null);
        setIsLoading(false);

        if(!leagueName || !season || !matchday){
            setError("Each filter options should be set before submitting")
        }

        if (leagueName && season && matchday) {

            setIsLoading(true);

            try {
                const response = await api.get('/v1/matches/', {
                    params: {
                        league_name: leagueName,
                        season: season,
                        matchday: matchday,
                        champions_league_stage: championsLeaguStage,
                    },
                });

                setMatchesData(response.data);

            } catch (error) {
                setError(error.response?.data?.detail || "Error fetching matches");

            } finally {
                setIsLoading(false);
            }
        }


    };

    return (
    <div className="form-container">
      <form onSubmit={handleSubmit} className="form">
        <div className="form-fields">
          {/* League name */}
          <div className="form-field">
            <label className="form-label">League:</label>
            <select
              value={leagueName}
              onChange={(e) => setLeagueName(e.target.value)}
              className="form-input"
            >
              <option value="">-- Select league --</option>
              {leagues.map((league) => (
                <option key={league.value} value={league.value}>
                  {league.label}
                </option>
              ))}
            </select>
          </div>

          {/* Season */}
          <div className="form-field">
            <label className="form-label">Season:</label>
            <input
              type="number"
              value={season}
              onChange={(e) => setSeason(e.target.value)}
              placeholder="Enter season"
              className="form-input"
              min='1872'
            />
          </div>
          {leagueName === 'CL' && (
              <div className='form-field'>
                  <label className='form-label'>Stage:</label>
                  <select
                    value={championsLeaguStage}
                    onChange={(e) => setChampionsLeagueStage(e.target.value)}
                    className='form-input'
                  >
                     <option value=''>-- Select Stage --</option>
                      {champions_league_stages.map((stage) => (
                          <option key={stage.value} value={stage.value}>
                              {stage.label}
                          </option>
                      ))}
                  </select>
              </div>
          )}

          {/* Matchday */}
          <div className="form-field">
            <label className="form-label">Matchday:</label>
            <input
              type="number"
              value={matchday}
              onChange={(e) => setMatchday(e.target.value)}
              placeholder="Enter matchday"
              className="form-input"
              min='1'
            />
          </div>
        </div>

        {/* Submit button */}
        <button type="submit" className="submit-button">
          Submit
        </button>

        {isLoading && <p className="loading-text">Loading...</p>}
        {error && <p className="error-text">{error}</p>}
        {matchesData && <Matches matches={matchesData} />}
      </form>
    </div>
  );
};

export default SearchMatchesForm;

