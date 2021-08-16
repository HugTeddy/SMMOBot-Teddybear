## Guild Commands
Teddybear bot provides a variety of tools to help manage and analyze guild performance. These include guild tracking, leaderboards, guilds stats, safemode status and MoE request systems. Check out the commands below for more information.

### Guild Stat Commands
Analytics for player activity within guild and overall guild activity/status

| Command | Desc. | Example |
| -- | -- | -- |
| `guildleaderboard [daily\|weekly] <type>` | Lists data for all linked players | `~guildleaderboard daily pvp` or `~guildleaderboard weekly steps` |
| `advguildleaderboard [start] [end] <type>` | Lists data for all linked players, custom duration | `~guildleaderboard 2/3 2/15 pvp` or `~guildleaderboard 2/7 3/4 steps` |
| `guildactivity <kills>` | Checks linked players for min kill count within the week | `~guildactivity 50` |
| `guildboard <type>` | Grabs guild leaderboard for registered guild | `~guildboard npc` |
| `guildstats` | Grabs daily steps, level, pvp, and npc leaderboards (top 100 players in guild) | `~guildstats` |


### Request System
Allows guild to implement request and tracking system for MoE requests from guild members. This system gives direct send item links as well a logs previous interactions letting guild leaders easily send and track MoE and overall usage.

| Command | Desc. |
| -- | -- |
| `request <amount>` | Makes a new request |
| `requestlist` | See pending requests |
| `requesttime` | shows current request time |
| `requestcomplete <index>` | Completes active request [Guild Manager Only] |
| `requesthistory` | shows previous requests [Guild Manager Only] |
| `requestcap <amount>` | Caps mushrooms per request [Guild Manager Only] |
| `requesttag @role` | Mentions role when request is added [Guild Manager Only] |


### Guild Management Commands
Commands to help link, unlink player and overall management

| Command | Desc. | Example |
| -- | -- | -- |
| `adminlink @user <smmoid>` | Links discord user to smmo player for discord server leaderboards | `~adminlink @HugTed 423723` |
| `adminunlink userid` | unlinks discord user to smmo player for discord server leaderboards | `~adminunlink 151819430026936320` |
| `guildlinkmissing` | Compares linked players to list of guild members on SMMO, lists missing players | `~guildlinkmissing` |
| `guildlinkcheck` | Compares linked players to list of guild mmebers on SMMO, lists linked players that are not in guild | `~guildlinkcheck` |
| `guildattackcheck <guildid>` | Checks guild for attackable members | `~guildattackcheck 933` |
| `guildsync` | Links all guild players with smmoids of username matches | `~guildsync` |
| `guildsafecheck` | Shows guild players out of safemode | `~guildsafecheck` |
| `guildrolecheck` | Shows discord members that have the guild role that are not linked | `~guildrolecheck` |
