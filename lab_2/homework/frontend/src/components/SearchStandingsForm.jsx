import React, {useState} from "react";
import { leagues,champions_league_stages, orderByOptions, descendingOptions } from './ComboboxData';
import LeagueTable from "./LeagueTable.jsx";
import api from "../api.js";

const SearchStandingsForm = () =>{

    const [leagueName, setLeagueName] = useState('');
    const [championsLeagueStage, setChampionsLeagueStage] = useState('');
    const [season, setSeason] = useState('');
    const [matchday, setMatchday] = useState('');
    const [orderBy, setOrderBy] = useState('');
    const [desc, setDesc] = useState('');


    const [standingsData, setStandingsData] = useState(null)
    const [isLoading, setIsLoading] = useState(false)
    const[error, setError] = useState(null)

    const handleSubmit = async (event) => {
        event.preventDefault();
        setStandingsData(null);
        setError(null);
        setIsLoading(false);

        if(!leagueName || !season || !matchday || !orderBy || !desc){
            setError('Each filter options should be set before submitting');
        }

        if (leagueName && season && matchday && orderBy && desc) {
            setIsLoading(true);


            try {
                const response = await api.get('v1/standings/', {
                    params:{
                        league_name: leagueName,
                        season: season,
                        matchday: matchday,
                        order_by: orderBy,
                        desc: desc,
                        champions_league_stages: championsLeagueStage
                    }
                });
                setStandingsData(response.data);

            }catch (error){
                console.error(error.response);
                setError(error.response?.data?.detail || "Error downloading standings data");
            }
            finally {
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

            {/*Champions League stage*/}
            {leagueName === 'CL' && (
                <div className='form-field'>
                    <label className='form-label'>Stage:</label>
                    <select
                      value={championsLeagueStage}
                      onChange={(e) => setChampionsLeagueStage(e.target.value)}
                      className='form-input'
                    >
                      <option value =''>-- Select stage --</option>
                        {champions_league_stages.map((stage) =>(
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

        <div className="form-fields">
          {/* Order By */}
          <div className="form-field">
            <label className="form-label">Order by:</label>
            <select
              value={orderBy}
              onChange={(e) => setOrderBy(e.target.value)}
              className="form-input"
            >
              <option value="">-- Select ordering method --</option>
              {orderByOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* Descending */}
          <div className="form-field">
            <label className="form-label">Descending:</label>
            <select
              value={desc}
              onChange={(e) => setDesc(e.target.value)}
              className="form-input"
            >
              <option value="">-- Descending --</option>
              {descendingOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/*Submit button */}
        <button type="submit" className="submit-button">
          Submit
        </button>

        {isLoading && <p className="loading-text">Loading ...</p>}
        {error && <p className="error-text">{error}</p>}
        {standingsData && <LeagueTable standings_list={standingsData} />}
      </form>
    </div>
  );
};

export default SearchStandingsForm;