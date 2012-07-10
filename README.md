README added 10th July 2012

<<<<<
Small tool to allow you to:
Find freeleech torrents (BBT doesn't provide this feature)
Find freeleech torrents within certain size boundry
Find freeleech torrents that are also bonus torrents
Find freeleech torrents that are also bonus torrents within certain size boundry
Periodical check for the above in case you want to hoarde bonus points and set your client to watch script directory.


The main issue with bonus points hoarding on BBT is the fact that bonus torrents are often on the edge of not being a bonus torrent. What I mean is that when you become a seeder of such a torrent yourself, you might have tipped over the bound of maximum seeders to keep the torrent a bonus one.
Unfortunatelly, BBT doesn't reveal the exact bonus criteria, but even if it did, it's probably some internal data that would be too much effort to watch. The consequence is that if you set the watched to watch bonus torrents and remove them when they stop being bonus, you might get stuck in a circle of adding and removing the same torrent as you are the one stopping the torrent from being the bonus one.
>>>>>



Actually, scratch all of the above, this might just prove too inconvinient for other users of the site. This will now officially become a tool to batch grab freeleech torrents (with size specification), any bonus torrents (with size specification) and any normal torrents (with size specification). There will be no periodical checking and torrent removal. Therefore the tool is still quite useful if you just want to quickly get 500 torrents of under 10MB each (optionally freeleech and/or bonus), but nothing more.

I'm going to have some free time (when I say free time, I mean I have 3 other projects to work on and tons of more important things to do) over the next two weeks so I will most likely work on this.

As far as I know, this doesn't work right now due to some rehauls over at BBT.
This is pretty high up on my list as I am going to be soon under a reign of residential Internet connection again.

NOTE: This project might suddenly become Python 2 although I might produce two versions if it turns out easy to port.