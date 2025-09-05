## A Python wrapper for the OtakuGIFS API, created by INFINITE_. using httpx

[API LINK](https://otakugifs.xyz)

### How to install
```
pip install OTAKUGIFS
```

### How to use

#### Step 1
Import OTAKUGIFS and create an instance.
```py 
from OTAKUGIFS import OTAKUGIFS
gifs = OTAKUGIFS()
```


#### Step 2
Call the method for your corresponding gif reaction. For example if you want a reaction for hug you can do this:
```py
gifs.hug(format="GIF")
```
Format can be:
  - GIF
  - AVIF
  - WebP

Returns -> A string with the url of the reaction.


### All reactions
airkiss , angrystare , bite , bleh , blush , brofist , celebrate , cheers , clap , confused , cool , cry , cuddle , dance , drool , evillaugh , facepalm , handhold , happy , headbang , hug , huh , kiss , laugh , lick , love , mad , nervous , no , nom , nosebleed , nuzzle , nyah , pat , peek , pinch , poke , pout , punch , roll , run , sad , scared , shout , shrug , shy , sigh , sip , slap , sleep , slowclap , smack , smile , smug , sneeze , sorry , stare , stop , surprised , sweat , thumbsup , tickle , tired , wave , wink , woah , yawn , yay , yes