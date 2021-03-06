# chessfana
Leverage the chess.com API to draw graphs &amp; tables with Grafana.  chessfana is comprised of two python scripts.

- getChessStats.py<br>
- chessfanaCgi.py

getChessStats.py: This script downloads chess games from chess.com.  Providing the script whith a username will result in a json file containing all the users games.  On line 3 of the script there is a minYear attribute that restricts how many years back it will look.

        Usage:  python3 getChessStats.py <USERNAME>

chessfanaCgi.py:

This is a cgi script that will process the chess json files when called on by the Grafana JSON data store.  On line three you can set the directory for the \<username\>_chessGames.json files.

**High Level Diagram**
![alt tag](https://github.com/netdsg/chessfana/blob/master/chessFanaDiagram.png)
**Step #1**<br>
Install Grafna

**Step #2**<br>
Install the Grafana JSON by simpod data source type.  This is a plugin that can be found at grafana.com

**Step #3**<br>
Select a web server for the chessfanaCgi.py script.  One solution would be to install apache on the same server Grafana is on.  

**Step #4**<br>
Choose a directory for the json game files.  Set the jsonGameDirectory variable to this value in getChessStats.py & chessfanaCgi.py.  This variable is near the top in each script.

**Step #5**<br>
Run getChessStats.py for each user you'd like to graph.  It may be desireable to set up a cron job to run this daily.

**Step #6**<br>
In the Grafana GUI, configure a chessfana data source by selecting the JSON data source type and pointing it at chessfanaCgi.py.  For example:
URL :  http://\<SERVER\>/cgi-bin/chessfanaCgi.py

**Step #7**<br>
Set up a dashboard that leverages the newly created chessfana data source.

**Example Grafana Dashboard**<br>
GrafanaChessfanaDashboardExample.json is an example Grafana dashboard that uses chessfana.

**Example Graphs & Table**
![alt tag](https://github.com/netdsg/chessfana/blob/master/rating.png)
![alt tag](https://github.com/netdsg/chessfana/blob/master/twoUserGraph.png)
![alt tag](https://github.com/netdsg/chessfana/blob/master/top20.png)
![alt tag](https://github.com/netdsg/chessfana/blob/master/blitzWithOpponentRating.png)
![alt tag](https://github.com/netdsg/chessfana/blob/master/blitzWinChart.png)

