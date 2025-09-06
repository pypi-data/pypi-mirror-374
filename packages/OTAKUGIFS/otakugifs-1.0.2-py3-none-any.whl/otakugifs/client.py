import httpx

class OtakuGIFS:
    """A Python wrapper for the OtakuGIFS API.
    Example:
        >>> from OtakuGIFS import OtakuGIFS
        >>> gif = OtakuGIFS()
        >>> hug_url = gif.hug(format="GIF")
        >>> print(hug_url)

    Available reaction methods:
        - airkiss(format: str = 'gif') -> str
        - angrystare(format: str = 'gif') -> str
        - bite(format: str = 'gif') -> str
        - bleh(format: str = 'gif') -> str
        - blush(format: str = 'gif') -> str
        - brofist(format: str = 'gif') -> str
        - celebrate(format: str = 'gif') -> str
        - cheers(format: str = 'gif') -> str
        - clap(format: str = 'gif') -> str
        - confused(format: str = 'gif') -> str
        - cool(format: str = 'gif') -> str
        - cry(format: str = 'gif') -> str
        - cuddle(format: str = 'gif') -> str
        - dance(format: str = 'gif') -> str
        - drool(format: str = 'gif') -> str
        - evillaugh(format: str = 'gif') -> str
        - facepalm(format: str = 'gif') -> str
        - handhold(format: str = 'gif') -> str
        - happy(format: str = 'gif') -> str
        - headbang(format: str = 'gif') -> str
        - hug(format: str = 'gif') -> str
        - huh(format: str = 'gif') -> str
        - kiss(format: str = 'gif') -> str
        - laugh(format: str = 'gif') -> str
        - lick(format: str = 'gif') -> str
        - love(format: str = 'gif') -> str
        - mad(format: str = 'gif') -> str
        - nervous(format: str = 'gif') -> str
        - no(format: str = 'gif') -> str
        - nom(format: str = 'gif') -> str
        - nosebleed(format: str = 'gif') -> str
        - nuzzle(format: str = 'gif') -> str
        - nyah(format: str = 'gif') -> str
        - pat(format: str = 'gif') -> str
        - peek(format: str = 'gif') -> str
        - pinch(format: str = 'gif') -> str
        - poke(format: str = 'gif') -> str
        - pout(format: str = 'gif') -> str
        - punch(format: str = 'gif') -> str
        - roll(format: str = 'gif') -> str
        - run(format: str = 'gif') -> str
        - sad(format: str = 'gif') -> str
        - scared(format: str = 'gif') -> str
        - shout(format: str = 'gif') -> str
        - shrug(format: str = 'gif') -> str
        - shy(format: str = 'gif') -> str
        - sigh(format: str = 'gif') -> str
        - sip(format: str = 'gif') -> str
        - slap(format: str = 'gif') -> str
        - sleep(format: str = 'gif') -> str
        - slowclap(format: str = 'gif') -> str
        - smack(format: str = 'gif') -> str
        - smile(format: str = 'gif') -> str
        - smug(format: str = 'gif') -> str
        - sneeze(format: str = 'gif') -> str
        - sorry(format: str = 'gif') -> str
        - stare(format: str = 'gif') -> str
        - stop(format: str = 'gif') -> str
        - surprised(format: str = 'gif') -> str
        - sweat(format: str = 'gif') -> str
        - thumbsup(format: str = 'gif') -> str
        - tickle(format: str = 'gif') -> str
        - tired(format: str = 'gif') -> str
        - wave(format: str = 'gif') -> str
        - wink(format: str = 'gif') -> str
        - woah(format: str = 'gif') -> str
        - yawn(format: str = 'gif') -> str
        - yay(format: str = 'gif') -> str
        - yes(format: str = 'gif') -> str
    """
    def __init__(self):
        self._base_url = "https://api.otakugifs.xyz/gif".rstrip('/')

    def _request(self, method: str, endpoint: str, format: str = "GIF"):
        url = f"{self._base_url}?reaction={endpoint}&format={format}"
        try:
            with httpx.Client() as client:
                response = client.request(method, url)
                response.raise_for_status()
                if response.status_code == 204:
                    return None
                return response.json()["url"]
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            print(f"An error occurred while requesting {e.request.url!r}.")
            raise

    def airkiss(self, format: str = "GIF"):
        """
        Generate a airkiss reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the airkiss reaction image.
        """
        return self._request("GET", "airkiss", format)

    def angrystare(self, format: str = "GIF"):
        """
        Generate a angrystare reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the angrystare reaction image.
        """
        return self._request("GET", "angrystare", format)

    def bite(self, format: str = "GIF"):
        """
        Generate a bite reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the bite reaction image.
        """
        return self._request("GET", "bite", format)

    def bleh(self, format: str = "GIF"):
        """
        Generate a bleh reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the bleh reaction image.
        """
        return self._request("GET", "bleh", format)

    def blush(self, format: str = "GIF"):
        """
        Generate a blush reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the blush reaction image.
        """
        return self._request("GET", "blush", format)

    def brofist(self, format: str = "GIF"):
        """
        Generate a brofist reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the brofist reaction image.
        """
        return self._request("GET", "brofist", format)

    def celebrate(self, format: str = "GIF"):
        """
        Generate a celebrate reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the celebrate reaction image.
        """
        return self._request("GET", "celebrate", format)

    def cheers(self, format: str = "GIF"):
        """
        Generate a cheers reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the cheers reaction image.
        """
        return self._request("GET", "cheers", format)

    def clap(self, format: str = "GIF"):
        """
        Generate a clap reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the clap reaction image.
        """
        return self._request("GET", "clap", format)

    def confused(self, format: str = "GIF"):
        """
        Generate a confused reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the confused reaction image.
        """
        return self._request("GET", "confused", format)

    def cool(self, format: str = "GIF"):
        """
        Generate a cool reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the cool reaction image.
        """
        return self._request("GET", "cool", format)

    def cry(self, format: str = "GIF"):
        """
        Generate a cry reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the cry reaction image.
        """
        return self._request("GET", "cry", format)

    def cuddle(self, format: str = "GIF"):
        """
        Generate a cuddle reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the cuddle reaction image.
        """
        return self._request("GET", "cuddle", format)

    def dance(self, format: str = "GIF"):
        """
        Generate a dance reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the dance reaction image.
        """
        return self._request("GET", "dance", format)

    def drool(self, format: str = "GIF"):
        """
        Generate a drool reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the drool reaction image.
        """
        return self._request("GET", "drool", format)

    def evillaugh(self, format: str = "GIF"):
        """
        Generate a evillaugh reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the evillaugh reaction image.
        """
        return self._request("GET", "evillaugh", format)

    def facepalm(self, format: str = "GIF"):
        """
        Generate a facepalm reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the facepalm reaction image.
        """
        return self._request("GET", "facepalm", format)

    def handhold(self, format: str = "GIF"):
        """
        Generate a handhold reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the handhold reaction image.
        """
        return self._request("GET", "handhold", format)

    def happy(self, format: str = "GIF"):
        """
        Generate a happy reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the happy reaction image.
        """
        return self._request("GET", "happy", format)

    def headbang(self, format: str = "GIF"):
        """
        Generate a headbang reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the headbang reaction image.
        """
        return self._request("GET", "headbang", format)

    def hug(self, format: str = "GIF"):
        """
        Generate a hug reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the hug reaction image.
        """
        return self._request("GET", "hug", format)

    def huh(self, format: str = "GIF"):
        """
        Generate a huh reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the huh reaction image.
        """
        return self._request("GET", "huh", format)

    def kiss(self, format: str = "GIF"):
        """
        Generate a kiss reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the kiss reaction image.
        """
        return self._request("GET", "kiss", format)

    def laugh(self, format: str = "GIF"):
        """
        Generate a laugh reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the laugh reaction image.
        """
        return self._request("GET", "laugh", format)

    def lick(self, format: str = "GIF"):
        """
        Generate a lick reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the lick reaction image.
        """
        return self._request("GET", "lick", format)

    def love(self, format: str = "GIF"):
        """
        Generate a love reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the love reaction image.
        """
        return self._request("GET", "love", format)

    def mad(self, format: str = "GIF"):
        """
        Generate a mad reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the mad reaction image.
        """
        return self._request("GET", "mad", format)

    def nervous(self, format: str = "GIF"):
        """
        Generate a nervous reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the nervous reaction image.
        """
        return self._request("GET", "nervous", format)

    def no(self, format: str = "GIF"):
        """
        Generate a no reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the no reaction image.
        """
        return self._request("GET", "no", format)

    def nom(self, format: str = "GIF"):
        """
        Generate a nom reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the nom reaction image.
        """
        return self._request("GET", "nom", format)

    def nosebleed(self, format: str = "GIF"):
        """
        Generate a nosebleed reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the nosebleed reaction image.
        """
        return self._request("GET", "nosebleed", format)

    def nuzzle(self, format: str = "GIF"):
        """
        Generate a nuzzle reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the nuzzle reaction image.
        """
        return self._request("GET", "nuzzle", format)

    def nyah(self, format: str = "GIF"):
        """
        Generate a nyah reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the nyah reaction image.
        """
        return self._request("GET", "nyah", format)

    def pat(self, format: str = "GIF"):
        """
        Generate a pat reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the pat reaction image.
        """
        return self._request("GET", "pat", format)

    def peek(self, format: str = "GIF"):
        """
        Generate a peek reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the peek reaction image.
        """
        return self._request("GET", "peek", format)

    def pinch(self, format: str = "GIF"):
        """
        Generate a pinch reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the pinch reaction image.
        """
        return self._request("GET", "pinch", format)

    def poke(self, format: str = "GIF"):
        """
        Generate a poke reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the poke reaction image.
        """
        return self._request("GET", "poke", format)

    def pout(self, format: str = "GIF"):
        """
        Generate a pout reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the pout reaction image.
        """
        return self._request("GET", "pout", format)

    def punch(self, format: str = "GIF"):
        """
        Generate a punch reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the punch reaction image.
        """
        return self._request("GET", "punch", format)

    def roll(self, format: str = "GIF"):
        """
        Generate a roll reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the roll reaction image.
        """
        return self._request("GET", "roll", format)

    def run(self, format: str = "GIF"):
        """
        Generate a run reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the run reaction image.
        """
        return self._request("GET", "run", format)

    def sad(self, format: str = "GIF"):
        """
        Generate a sad reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the sad reaction image.
        """
        return self._request("GET", "sad", format)

    def scared(self, format: str = "GIF"):
        """
        Generate a scared reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the scared reaction image.
        """
        return self._request("GET", "scared", format)

    def shout(self, format: str = "GIF"):
        """
        Generate a shout reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the shout reaction image.
        """
        return self._request("GET", "shout", format)

    def shrug(self, format: str = "GIF"):
        """
        Generate a shrug reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the shrug reaction image.
        """
        return self._request("GET", "shrug", format)

    def shy(self, format: str = "GIF"):
        """
        Generate a shy reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the shy reaction image.
        """
        return self._request("GET", "shy", format)

    def sigh(self, format: str = "GIF"):
        """
        Generate a sigh reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the sigh reaction image.
        """
        return self._request("GET", "sigh", format)

    def sip(self, format: str = "GIF"):
        """
        Generate a sip reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the sip reaction image.
        """
        return self._request("GET", "sip", format)

    def slap(self, format: str = "GIF"):
        """
        Generate a slap reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the slap reaction image.
        """
        return self._request("GET", "slap", format)

    def sleep(self, format: str = "GIF"):
        """
        Generate a sleep reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the sleep reaction image.
        """
        return self._request("GET", "sleep", format)

    def slowclap(self, format: str = "GIF"):
        """
        Generate a slowclap reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the slowclap reaction image.
        """
        return self._request("GET", "slowclap", format)

    def smack(self, format: str = "GIF"):
        """
        Generate a smack reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the smack reaction image.
        """
        return self._request("GET", "smack", format)

    def smile(self, format: str = "GIF"):
        """
        Generate a smile reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the smile reaction image.
        """
        return self._request("GET", "smile", format)

    def smug(self, format: str = "GIF"):
        """
        Generate a smug reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the smug reaction image.
        """
        return self._request("GET", "smug", format)

    def sneeze(self, format: str = "GIF"):
        """
        Generate a sneeze reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the sneeze reaction image.
        """
        return self._request("GET", "sneeze", format)

    def sorry(self, format: str = "GIF"):
        """
        Generate a sorry reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the sorry reaction image.
        """
        return self._request("GET", "sorry", format)

    def stare(self, format: str = "GIF"):
        """
        Generate a stare reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the stare reaction image.
        """
        return self._request("GET", "stare", format)

    def stop(self, format: str = "GIF"):
        """
        Generate a stop reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the stop reaction image.
        """
        return self._request("GET", "stop", format)

    def surprised(self, format: str = "GIF"):
        """
        Generate a surprised reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the surprised reaction image.
        """
        return self._request("GET", "surprised", format)

    def sweat(self, format: str = "GIF"):
        """
        Generate a sweat reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the sweat reaction image.
        """
        return self._request("GET", "sweat", format)

    def thumbsup(self, format: str = "GIF"):
        """
        Generate a thumbsup reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the thumbsup reaction image.
        """
        return self._request("GET", "thumbsup", format)

    def tickle(self, format: str = "GIF"):
        """
        Generate a tickle reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the tickle reaction image.
        """
        return self._request("GET", "tickle", format)

    def tired(self, format: str = "GIF"):
        """
        Generate a tired reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the tired reaction image.
        """
        return self._request("GET", "tired", format)

    def wave(self, format: str = "GIF"):
        """
        Generate a wave reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the wave reaction image.
        """
        return self._request("GET", "wave", format)

    def wink(self, format: str = "GIF"):
        """
        Generate a wink reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the wink reaction image.
        """
        return self._request("GET", "wink", format)

    def woah(self, format: str = "GIF"):
        """
        Generate a woah reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the woah reaction image.
        """
        return self._request("GET", "woah", format)

    def yawn(self, format: str = "GIF"):
        """
        Generate a yawn reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the yawn reaction image.
        """
        return self._request("GET", "yawn", format)

    def yay(self, format: str = "GIF"):
        """
        Generate a yay reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the yay reaction image.
        """
        return self._request("GET", "yay", format)

    def yes(self, format: str = "GIF"):
        """
        Generate a yes reaction.
        Args:
            format (str): The desired format of the reaction (default is "GIF", others: WebP, AVIF).
        Returns:
            str: URL of the yes reaction image.
        """
        return self._request("GET", "yes", format)
