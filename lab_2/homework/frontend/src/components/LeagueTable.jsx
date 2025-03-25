import React from "react";

const LeagueTable = ({ standings_list }) => {
  return (
    <div className="league-table">
      <h3 className="text-xl font-bold mb-4">League Table</h3>
      {standings_list && standings_list.length > 0 ? (
        <table className="w-full border-collapse">
          <thead>
            <tr className="border-b border-gray-700 text-left">
              <th className="p-2">#</th>
              <th className="p-2">Club</th>
              <th className="p-2">Played</th>
              <th className="p-2">Won</th>
              <th className="p-2">Drawn</th>
              <th className="p-2">Lost</th>
              <th className="p-2">GF</th>
              <th className="p-2">GA</th>
              <th className="p-2">GD</th>
              <th className="p-2 font-bold">Points</th>
              <th className="p-2">Last 5 games</th>
            </tr>
          </thead>
          <tbody>
            {standings_list.map((team, index) => (
                <tr key={team.name} className="border-b border-gray-800">
                    <td className="p-2">{index + 1}</td>
                    <td className="p-2 flex items-center">
                        <div className="team-logo-container">
                            <img src={team.logo} alt={team.name} className="team-logo"/>
                            <span>{team.name}</span>
                        </div>
                    </td>
                    <td className="p-2">{team.played_games}</td>
                    <td className="p-2">{team.won}</td>
                    <td className="p-2">{team.draw}</td>
                    <td className="p-2">{team.lost}</td>
                    <td className="p-2">{team.goals_for}</td>
                    <td className="p-2">{team.goals_against}</td>
                    <td className="p-2">{team.goal_diff}</td>
                    <td className="p-2 font-bold">{team.points}</td>
                    <td className="p-2 last-5-games">
                        {team.form.split(",").map((result, i) => (
                            <span
                                key={i}
                                className={`result-icon ${
                                    result === "W"
                                        ? "win"
                                        : result === "D"
                                            ? "draw"
                                            : "loss"
                                }`}
                            >
                      {result}
                    </span>
                        ))}
                    </td>
                </tr>
            ))}
          </tbody>
        </table>
      ) : (
          <p className="no-table-data">No league table found for the selected criteria</p>
      )}
    </div>
  );
};

export default LeagueTable;
