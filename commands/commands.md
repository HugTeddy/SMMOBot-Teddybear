## General Commands

### Player Games
| Command | Desc. | Example |
| -- | -- | -- |
| `deathroll @user bet` | Starts a game of death roll with another user | `~dr @HugTed 1 Potato` |
| `dice @user bet` | Starts a game of dice with another user | `~dice @HugTed 1 Potato` |
| `coinflip @user bet` | Starts a game of coin flip with another user | `~cf @HugTed 1 Potato` |
| `farm` | Lets player farm plants/fruits for Teddybear Credit | `~farmhelp` |
| `wordle` | Lets player guess a word of the day and recieve credit for correct letters | `~wordlehelp` |
| `egg` | Hatch a random pet by stepping in SimpleMMO | `~egghelp` |
| `memory` | Try and get all the coordinates for different items before time runs out | `~memhelp` |
| `cook` | Cook a variety of dishes to get Teddybear Credit | `~cookhelp` |


### General Misc
| Command | Desc. | Example |
| -- | -- | -- |
| `roll <dice>` | Rolls dice (e.g. roll 1d6) | `~roll 1d6`|
| `poll <question>? <answer1>\|<answer2>...` | Displays a poll for users | `~poll true or false question? True\|False` |
| `remindme <time> <message>` | Sets a reminder | `~remindme 1h Hydrate` |


## Player SMMO Commands
| Command | Desc. | Example |
| -- | -- | -- |
| `profile [user]` | Shows linked SMMO User | `~profile @user` or `~profile` |
| `searchProfile "<name>" [min level]` | Searches for user with name/level | `~searchprofile "Name" 1` |
| `stats [daily/weekly] [user]` | Shows daily user stats | `~stats daily` or `~stats daily @user` |
| `advstats [start] [end] [user]` | Shows user stats for custom time period | `~advstats 2/1 2/5` or `~advstats 2/1 2/5 @user` |
| `graph [user]` | Graphs weekly user activity | `~graph @user` or `~graph` |
| `l <SMMOUserID>` | Links SMMO User to Discord | `~l 123456` |
| `linkhelp` | Help message on how to link SMMO profile | `~linkhelp` |
| `lu <SMMOUserID>` | Looksup SMMO Player Profile | `~lu 123456` |
| `attack <SMMOUserID>` | Calculates SMMO Hit/Attack Values | `~a @user @user` or `~a 123456 234567` |
| `top <daily\|weekly>` | Top 3 List All Groups (Levels, Quests, Pvp, Npc) | `~top` or `~top weekly` |
| `top10 <daily\|weekly> <steps\|pvp\|npc\|levels>` | Top 10 List | `~top10 daily pvp` or `~top10 weekly steps` |
| `wallethelp` | Displays help message for wallet commands | `~wallethelp` |
| `bal` | show battle arena leaderboards based on league | `~bal copper` |
| `time` | Shows current server time | `~time` |
| `pc @user` | player card | `~playercard`|
| `bal <league>` | Shows battle arena leaderboard for various leagues | `~bal copper` |


## Guild SMMO Commands
### General Commands
| Command | Desc. | Example |
| -- | -- | -- |
| `guildgraph` | Displays graph of guild exp and pvp status | `~guildgraph` |
| `guildtop` | List of guild exp rankings and weekly exp gain | `~guildtop` |
| `guildleaderboard [daily\|weekly] <type>` | Lists data for all linked players | `~guildleaderboard daily pvp` or `~guildleaderboard weekly steps` |
| `advguildleaderboard [start] [end] <type>` | Lists data for all linked players, custom duration | `~guildleaderboard 2/3 2/15 pvp` or `~guildleaderboard 2/7 3/4 steps` |
| `guildactivity <kills>` | Checks linked players for min kill count within the week | `~guildactivity 50` |
| `guildlinkmissing` | Compares linked players to list of guild members on SMMO, lists missing players | `~guildlinkmissing` |
| `guildlinkcheck` | Compares linked players to list of guild mmebers on SMMO, lists linked players that are not in guild | `~guildlinkcheck` |
| `guildattackcheck <guildid>` | Checks guild for attackable members | `~guildattackcheck 933` |
| `guildsync` | Links all guild players with smmoids of username matches | `~guildsync` |


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


## SMMO World Boss + Orphan Notifications
These are setup commands for discord channels, some may require `guild_manage` permissions in the discord guild.
### World Boss
| Command | Desc. | Example |
| -- | -- | -- |
| `addPing [1\|5\|10\|15\|30\|60]` | Adds world boss reminder at x mins | `~addPing 1 @user` |
| `removePing [1\|5\|10\|15\|30\|60]` | Removes world boss reminder at x mins | `~removePing 1 @user` |
| `currentPings [1\|5\|10\|15\|30\|60]` | Checks current setup for guild world boss pings | `~currentPings 1` |
| `pingHelp` | shows help message for world boss pings  | `~pingHelp` |
| `wbHelp` | shows help message for world boss setup | `~wbHelp` |


### Orphanage
| Command | Desc. | Example |
| -- | -- | -- |
| `addOrphan <channel>` | Tags new channel to load orphanage messages | `~addOrphan #channel` |
| `removeOrphan <channel>` | Removes channel to send orphan messages | `~removeOrphan #channel` |
| `orphanage` | show current orphanage status | `~orphanage` |
| `adoptOrphan @role` | tags certain role when notified for orphanage | `~adoptOrphan @role` |


## Bot/User Preferences
| Command | Desc. |
| -- | -- |
| `botInvite` | Displays invite link for this bot
| `aboutMe` | Displays short aboutme and credits
| `changeprefix <prefix>` | Changes prefix for all bot commands
| `toggleEmoji` | Toggles context emojis for user
| `toggleGuildEmoji` | Toggles context emojis for guild
| `toggleItems` | Toggles context items for user
| `toggleGuildItems` | Toggles context items for guild
| `toggleGuildShortItems` | Toggles short item context mode
| `craftinglist` | Displays craftable items and crafting level
| `craft <itemname>` | Displays mats needed for crafting



## Other Systems
### Profile Customization
The new Ted Token system allows verified users to customize their personal `~p` menu, including thing such as embed color, avatar, and custom tags.
To earn tokens, have another verified user `~tip @user`, each user gets one token to tip every 24 hours.
| Command | Desc. |
| -- | -- |
| `tipmenu` | Displays required token amounts for each perk |
| `tip @user` | Tips another user a Ted Token |
| `profileimage [imagelink]` | Change embed avatar |
| `profilecolor [decimalcolor]` | Change embed color, decimal colors e.g. `~profilecolor 1234567` |


### Item Database & Chat Embeds
| Command | Desc. |
| -- | -- |
| `item <id>` | Shows item with specific ID
| `[[item name]]` | Displays item information in detail
| `[!item name!]` | Displays item art 
| `[[myava]]` | Displays player avatar
| `[[market]]` | Displayer player market link
