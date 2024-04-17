# Steam + How Long to Beat

tl;dr - Quick and dirty script to get your steam library by review score and add to it it's estimated completion time.

I am currently studying game dev at the university and I have way too many games on Steam. 

Sometimes I need to play a game, from start to finish, to do some research work for the university. Most of the times we can select which game to play.
I got a little frustrated with Steam not having a good way to see how long does a game take to beat (unlike GOG that has that information).

![Lorenzo Stanco](https://www.lorenzostanco.com/lab/steam/) has a great website to extract information from Steam using only your Steam username (you have to have a public profile).
How Long To Beat (HL2B) is a very nice site to search for the estimated duration of games.

I've used both websites to get my list of games, filter it by a tag, ordered it by score and add the estimated time to it.

If it fails to find a game on HL2B with the Steam name, it then applies an heuristic to simplify the name into something that might be available on the platform.

For ordering by score, it tries to compare by metascore. If a game doesn't have metascore, it uses its user score but only if the game has more than X number of user reviews.

So, in the end, I have a list of games that have some review based ordering and I can select a game that fits into my schedule...

I prefer to sort it by score, even if review scores are somewhat debatable sometimes.

## How to run it
You'll need to go to both ![Lorenzo Stanco's site](https://www.lorenzostanco.com/lab/steam/) and HL2B, with the developer tab open and select XHR in the network tab.
You'll need to get the nonce from Lorenzo's site and the request id from hl2b. You can inspect the request in the developers tools.

To get the nonce from Lorenzo's site, insert your username and press enter and you'll see the request showing up.
To get the user request, go to ![How Long To Beat](https://www.howlongtobeat.com) and search for anything. You'll see a request coming up on the search endpoint. Use that to retrieve the request id.

## TODO

- Change the script for it to be able to do this automatically, without needing to visit the site.

### Nice to have:
- Insert more pre-made filters;
- Improve code organization;
- Make it easier to add new filters and search options.