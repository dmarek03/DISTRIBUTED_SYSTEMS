
const leagues = [
        {label:'Premier League', value:'PL'},
        {label:'Ligue 1', value:'FL1'},
        {label:'Bundesliga', value:'BL1'},
        {label:'Serie A', value:'SA'},
        {label:"La Liga", value:"PD"},
        {label: "Champions League", value: "CL"},
    ];


const champions_league_stages = [
    {label:'League stage', value:'LEAGUE_STAGE'},
    {label:'Playoffs', value:'PLAYOFFS'},
    {label:'Last 16', value:'LAST_16'},
    {label:'Quarter finals', value:'QUARTER_FINALS'},
    {label:'Semi finals', value:'SEMI_FINALS'},
    {label:'Final', value:'FINAL'},

]

    const orderByOptions = [
        {label:'Points', value: 'points'},
        {label:'Won', value: 'won'},
        {label:'Draw', value: 'draw'},
        {label:'Lost', value: 'lost'},
        {label:'Goals for', value: 'goals_for'},
        {label:'Goals Against', value: 'goals_against'},
        {label:'Goal Difference', value: 'goal_diff'},

    ]

    const descendingOptions = [
        {label:'True', value:true},
        {label:'False', value:false},

    ]
export  {
  leagues,
  champions_league_stages,
  orderByOptions,
  descendingOptions
};
