# graphwar-polynomial-fit
Goddamn I love getting nerdsnipped

Livestream where I wrote this (past midnight, tiredly wrote it): https://www.youtube.com/watch?v=JZ4o6mho0YY

![](https://github.com/CKalitin/graphwar-polynomial-fit/blob/master/googlesheetsscreenshot.png)

There's this game [graphwar](https://store.steampowered.com/app/1899700/Graphwar/). I've had the amazing honour of being nerdsnipped by a friend into beating this game. You have agents on a screen and must write a function which your projectile will follow to kill your opponents agents. Clearly this game is at horrible risk of being completely beated by anyone who can fit a polynomial. I did this in real time while playing with friends in google sheets, this is a slow underoptimized method, so throw python and a late night at the problem.

### How to use

![](https://github.com/CKalitin/graphwar-polynomial-fit/blob/master/examplescreenshot.png)

![](https://github.com/CKalitin/graphwar-polynomial-fit/blob/master/examplescreenshot2.png)

When the game starts, take a screenshot using windows-shift-s of the game screen (not the entire game, just the screen with the agents on it). Save this as "input-game-screenshot.jpg" in the directory of the code (overwrite existing file).

Left click on green dots representing agents to add them to the path. Left click again to delete them.

Right click to add arbitrary points to the path, left click to remove these. 

Copy and paste the outputted polynomial in the CLI into the game.

Use up and down arrows to change the degree of the polynomial. 
