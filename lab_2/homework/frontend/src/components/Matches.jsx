import React from "react";

const MatchesList = ({ matches }) => {
  console.log(matches);
  return (
    <div className="matches-list">
      <h2 className="text-xl font-semibold text-white">Matches</h2>
      {matches && matches.length > 0 ? (
        <div className="matches-grid">
          {matches.map((match, index) => (
            <div key={index} className="match-card">
              <div className="match-header">
                {/* Home team */}
                <div className="match-team left">
                  <span>{match.home_team.name}</span>
                  <img
                    src={match.home_team.logo}
                    alt={match.home_team.name}
                    className="team-logo"
                  />
                </div>

                {/* Match result */}
                <div className="match-score">
                  {match.result && match.result !== "None:None"
                    ? match.result
                    : " -   :   - "}
                </div>

                {/* Away team */}
                <div className="match-team right">
                  <img
                    src={match.away_team.logo}
                    alt={match.away_team.name}
                    className="team-logo"
                  />
                  <span>{match.away_team.name}</span>
                </div>
              </div>
              <div className="match-datetime">{match.datetime}</div>
            </div>
          ))}
        </div>
      ) : (
        <p className="no-matches">
          No matches found for the selected criteria
        </p>
      )}
    </div>
  );
};


export default MatchesList;
