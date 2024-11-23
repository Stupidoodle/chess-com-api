"""Models module defines classes for players and statistics using Chess.com API.

It includes representations of a player, their details, and their performance
statistics across various chess formats.
"""

from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional, Set, Union

from chess_com_api.exceptions import RateLimitError

if TYPE_CHECKING:
    from chess_com_api.client import ChessComClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Player:
    """Representation of a player, encapsulating their details and behaviors.

    The Player class stores information related to a player, such as their username,
    status, and other relevant details. It provides methods to instantiate a Player
    from a dictionary and to fetch related country details asynchronously using a
    specific client.

    :ivar username: The player's username.
    :type username: str
    :ivar player_id: The unique identifier of the player.
    :type player_id: int
    :ivar title: The player's title in the game, if any.
    :type title: Optional[str]
    :ivar status: The current status of the player.
    :type status: str
    :ivar name: The player's real name, if available.
    :type name: Optional[str]
    :ivar avatar: URL to the player's avatar, if available.
    :type avatar: Optional[str]
    :ivar location: The player's location, if available.
    :type location: Optional[str]
    :ivar country_url: URL to the player's country information.
    :type country_url: str
    :ivar _country: The fetched country information of the player.
    :type _country: Optional[Country]
    :ivar joined: Timestamp when the player joined.
    :type joined: datetime
    :ivar last_online: Timestamp when the player was last online.
    :type last_online: datetime
    :ivar followers: Number of followers the player has.
    :type followers: int
    :ivar is_streamer: Indicates whether the player is a streamer.
    :type is_streamer: bool
    :ivar twitch_url: URL to the player's Twitch channel, if available.
    :type twitch_url: Optional[str]
    :ivar fide: The player's FIDE rating, if available.
    :type fide: Optional[int]
    """

    username: str
    player_id: int
    title: Optional[str]
    status: str
    name: Optional[str]
    avatar: Optional[str]
    location: Optional[str]
    country_url: str
    _country: Optional[Country] = field(default=None, init=False, repr=False)
    joined: datetime
    last_online: datetime
    followers: int
    is_streamer: bool = False
    twitch_url: Optional[str] = None
    fide: Optional[int] = None

    # TODO: Add streaming_platforms

    @classmethod
    def from_dict(cls, data: Union[Dict[str, Any], bytes, None]) -> "Player":
        """Create a Player instance from a dictionary.

        This method initializes a new Player object using the provided dictionary data,
        extracting and mapping the relevant fields to the Player's attributes.

        :param data: The data dictionary containing player details.
        :type data: Dict
        :return: A new Player instance.
        :rtype: Player
        """
        if isinstance(data, Dict):
            return cls(
                username=data["username"],
                player_id=data["player_id"],
                title=data.get("title"),
                status=data["status"],
                name=data.get("name"),
                avatar=data.get("avatar"),
                location=data.get("location"),
                country_url=data["country"],
                joined=datetime.fromtimestamp(data["joined"]),
                last_online=datetime.fromtimestamp(data["last_online"]),
                followers=data["followers"],
                is_streamer=data.get("is_streamer", False),
                twitch_url=data.get("twitch_url"),
                fide=data.get("fide"),
            )
        else:
            raise ValueError("Invalid input. Expected a dictionary.")

    async def fetch_country(self, client: ChessComClient) -> "Country":
        """Fetch country information for the given client.

        This method fetches the country information associated with the client's country
        URL. The information is obtained asynchronously from the provided ChessComClient
        instance.

        :param client: The ChessComClient instance used to fetch country information.
        :type client: ChessComClient
        :return: A Country instance representing the country information.
        :rtype: Country
        """
        self._country = await client.get_country(
            iso_code=self.country_url.split("/")[-1]
        )
        return self._country

    @property
    def country(self) -> "Country":
        """Return the associated country for the instance.

        If the country has not been fetched prior to calling this property,
        a ValueError will be raised, indicating that the fetch operation
        needs to be performed first, using the fetch_country method.

        :return: The country associated with the instance.
        :rtype: Country
        :raises ValueError: If the country has not been fetched yet.
        """
        if self._country is None:
            raise ValueError(
                "Country has not been fetched. Call `fetch_country` with an API "
                "client first."
            )
        return self._country


@dataclass
class PlayerStats:
    """Represents the statistics of a player in various chess formats.

    This class encapsulates the performance details of a player across different chess
    formats such as daily, rapid, bullet, blitz, and chess960. Additionally, it includes
    statistics for tactics, lessons, and puzzle rush. The class also provides a method
    to instantiate an instance from a dictionary.

    :ivar chess_daily: Statistics for daily chess games.
    :type chess_daily: Optional[Dict]
    :ivar chess_rapid: Statistics for rapid chess games.
    :type chess_rapid: Optional[Dict]
    :ivar chess_bullet: Statistics for bullet chess games.
    :type chess_bullet: Optional[Dict]
    :ivar chess_blitz: Statistics for blitz chess games.
    :type chess_blitz: Optional[Dict]
    :ivar chess960_daily: Statistics for daily chess960 games.
    :type chess960_daily: Optional[Dict]
    :ivar tactics: Statistics for tactics training.
    :type tactics: Optional[Dict]
    :ivar lessons: Statistics for lessons taken.
    :type lessons: Optional[Dict]
    :ivar puzzle_rush: Statistics for puzzle rush mode.
    :type puzzle_rush: Optional[Dict]
    """

    chess_daily: Optional[Dict[str, Any]]
    chess_rapid: Optional[Dict[str, Any]]
    chess_bullet: Optional[Dict[str, Any]]
    chess_blitz: Optional[Dict[str, Any]]
    chess960_daily: Optional[Dict[str, Any]]
    tactics: Optional[Dict[str, Any]]
    lessons: Optional[Dict[str, Any]]
    puzzle_rush: Optional[Dict[str, Any]]

    @classmethod
    def from_dict(cls, data: Union[Dict[str, Any], bytes, None]) -> "PlayerStats":
        """Create a PlayerStats instance from a dictionary.

        This method extracts relevant keys from a dictionary to create
        an instance of the PlayerStats class.

        :param data: A dictionary containing the player's statistics.
        :type data: Dict
        :return: A PlayerStats instance initialized with the dictionary data.
        :rtype: PlayerStats
        """
        if isinstance(data, dict):
            return cls(
                chess_daily=data.get("chess_daily"),
                chess_rapid=data.get("chess_rapid"),
                chess_bullet=data.get("chess_bullet"),
                chess_blitz=data.get("chess_blitz"),
                chess960_daily=data.get("chess960_daily"),
                tactics=data.get("tactics"),
                lessons=data.get("lessons"),
                puzzle_rush=data.get("puzzle_rush"),
            )
        else:
            raise ValueError("Invalid input data. Expected a dictionary.")


@dataclass
class DailyGame:
    """Class representing a daily game with its details.

    This class encapsulates details of a daily game including its URL, move-by date,
    last activity date, and draw offer status. It provides a method to instantiate
    an object from a dictionary.

    :ivar url: URL of the daily game.
    :type url: str
    :ivar move_by: Time by which a move must be made.
    :type move_by: datetime
    :ivar last_activity: Timestamp of the last activity in the game.
    :type last_activity: datetime
    :ivar draw_offer: Indicates whether a draw offer is present.
    :type draw_offer: Optional[bool]
    """

    url: str
    move_by: datetime
    last_activity: datetime
    draw_offer: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: Union[Dict[str, Any], bytes, None]) -> "DailyGame":
        """Create an instance of DailyGame from a dictionary.

        This method constructs and returns an instance of DailyGame by parsing the input
        dictionary. If the "draw_offer" key exists, it checks the value of "move_by" and
        "draw_offer" but does not alter the creation process based on these checks.

        :param data: Dictionary containing the necessary data to
         instantiate a DailyGame.
        :type data: Dict
        :return: A new instance of DailyGame initialized with the given data.
        :rtype: DailyGame
        """
        if isinstance(data, dict):
            if "draw_offer" in data.keys():
                if data["move_by"] == 0 or data["draw_offer"]:
                    pass
            return cls(
                url=data["url"],
                move_by=datetime.fromtimestamp(data["move_by"]),
                last_activity=datetime.fromtimestamp(data["last_activity"]),
                draw_offer=False,
            )
        else:
            raise ValueError("Invalid input data. Expected a dictionary.")


@dataclass
class White:
    """Represent a player who plays the white pieces in a chess game.

    This class encapsulates the details of a player using the white pieces,
    including their rating, game result, URL, username, and unique identifier.
    It also provides functionality to fetch and store detailed player information
    using an asynchronous client.

    :ivar rating: The player's rating.
    :type rating: int
    :ivar result: The game result from the player's perspective.
    :type result: str
    :ivar user_url: The unique URL associated with the player.
    :type user_url: str
    :ivar username: The player's username.
    :type username: str
    :ivar uuid: The unique identifier for the player.
    :type uuid: str
    """

    rating: int
    result: str
    user_url: str
    username: str
    uuid: str
    _user: Optional[Player] = field(default=None, init=False, repr=False)

    @classmethod
    def from_dict(cls, data: Union[Dict[str, Any], bytes, None]) -> "White":
        """Create an instance of the class from a dictionary.

        :param data: The dictionary containing the instance data.
        :type data: Dict
        :return: An instance of the class with attributes populated from the dictionary.
        :rtype: White
        """
        if isinstance(data, dict):
            return cls(
                rating=data["rating"],
                result=data["result"],
                user_url=data["@id"],
                username=data["username"],
                uuid=data["uuid"],
            )
        else:
            raise ValueError("Invalid input data. Expected a dictionary.")

    async def fetch_user(self, client: ChessComClient) -> "Player":
        """Fetch user data from the Chess.com API.

        This method retrieves user data from the Chess.com API using the provided
        client. If the user data has already been retrieved, it returns the cached
        data instead.

        :param client: The client to use for fetching the player data.
        :type client: ChessComClient
        :return: The player data fetched from the Chess.com API.
        :rtype: Player
        """
        if self._user is None:
            self._user = await client.get_player(username=self.username)
        return self._user

    @property
    def user(self) -> "Player":
        """Get the user object.

        Retrieve the user object if it has been fetched previously; otherwise, raise a
        ValueError indicating that the user has not been fetched.

        :return: The fetched user object.
        :rtype: Player
        :raises ValueError: If the user has not been fetched.
        """
        if self._user is None:
            raise ValueError(
                "User has not been fetched. Call `fetch_user` with an API client first."
            )
        return self._user


@dataclass
class Black:
    """Represents a chess player with specific attributes for black pieces.

    Detailed description of the class, its purpose, and usage. This class includes
    the player's rating, result, user URL, username, and unique identifier. It also
    supports fetching a Player object through an asynchronous API call.

    :ivar rating: Player's rating.
    :type rating: int
    :ivar result: Game result.
    :type result: str
    :ivar user_url: URL to the user's profile.
    :type user_url: str
    :ivar username: Player's username.
    :type username: str
    :ivar uuid: Player's unique identifier.
    :type uuid: str
    :ivar _user: Cache for the player's detailed data.
    :type _user: Optional[Player]
    """

    rating: int
    result: str
    user_url: str
    username: str
    uuid: str
    _user: Optional[Player] = field(default=None, init=False, repr=False)

    @classmethod
    def from_dict(cls, data: Union[Dict[str, Any], bytes, None]) -> "Black":
        """Create an instance of the class `Black` from a dictionary.

        This method initializes a `Black` instance using data from a dictionary. The
        dictionary should contain keys such as 'rating', 'result', '@id', 'username',
        and 'uuid' to map correctly to the properties of the `Black` class.

        :param data: Dictionary containing user data.
        :type data: Dict
        :return: Instance of `Black` initialized with data from the dictionary.
        :rtype: Black
        """
        if isinstance(data, dict):
            return cls(
                rating=data["rating"],
                result=data["result"],
                user_url=data["@id"],
                username=data["username"],
                uuid=data["uuid"],
            )
        else:
            raise ValueError("Invalid input data. Expected a dictionary.")

    async def fetch_user(self, client: ChessComClient) -> "Player":
        """Fetch user information asynchronously from Chess.com client.

        This method retrieves user information using the Chess.com client. If the
        user information has been previously fetched, it returns the cached data
        instead of making a new request.

        :param client: Chess.com client used to fetch player information.
        :type client: ChessComClient
        :return: Player object with user information.
        :rtype: Player
        """
        if self._user is None:
            self._user = await client.get_player(username=self.username)
        return self._user

    @property
    def user(self) -> "Player":
        """Get the user associated with this instance.

        :return: The user associated with this instance.
        :rtype: Player
        :raises ValueError: If the user has not been fetched and `_user` is None.
        """
        if self._user is None:
            raise ValueError(
                "User has not been fetched. Call `fetch_user` with an API client first."
            )
        return self._user


# TODO: Update Doc
@dataclass
class Game:
    """Represents a chess game and provides methods to interact with game details.

    The `Game` class encapsulates all relevant information about a chess game,
    including player URLs, FEN, PGN, time control, and other game-specific details.
    It also provides methods to asynchronously fetch information about the players
    participating in the game.

    :ivar white_url: URL of the white player.
    :type white_url: str
    :ivar black_url: URL of the black player.
    :type black_url: str
    :ivar url: URL of the game.
    :type url: str
    :ivar fen: FEN string of the game state.
    :type fen: str
    :ivar pgn: PGN string of the game.
    :type pgn: str
    :ivar time_control: Time control settings of the game.
    :type time_control: str
    :ivar time_class: Time class of the game (e.g., blitz, bullet, etc.).
    :type time_class: str
    :ivar rules: Chess ruleset used for the game.
    :type rules: str
    :ivar rated: Indicates if the game is rated.
    :type rated: bool
    :ivar accuracies: Accuracy details of the game.
    :type accuracies: Optional[Dict]
    :ivar tournament: Tournament in which the game was played.
    :type tournament: Optional[str]
    :ivar match: Match details of the game.
    :type match: Optional[str]
    :ivar eco: ECO code for the game.
    :type eco: Optional[str]
    :ivar start_time: Unix timestamp for the game's start time.
    :type start_time: Optional[int]
    :ivar end_time: Unix timestamp for the game's end time.
    :type end_time: Optional[int]
    :ivar _black: Private attribute for the black player instance.
    :type _black: Optional[Player]
    :ivar _white: Private attribute for the white player instance.
    :type _white: Optional[Player]
    """

    white_url: str
    black_url: str
    url: str
    fen: str
    time_control: str
    time_class: str
    rules: str
    rated: bool
    accuracies: Optional[Dict[str, float]] = None
    tournament: Optional[str] = None
    # TODO: Parse to match
    match: Optional[str] = None
    eco: Optional[str] = None
    start_time: Optional[int] = None
    end_time: Optional[int] = None
    _black: Optional[Player] = field(default=None, init=False, repr=False)
    _white: Optional[Player] = field(default=None, init=False, repr=False)
    id: Optional[int] = None
    pgn: Optional[str] = None
    tcn: Optional[str] = None
    initial_setup: Optional[str] = None
    uuid: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Union[Dict[str, Any], bytes, None]) -> "Game":
        """Convert a dictionary to a Game instance.

        Detailed description of how this class method converts the provided
        dictionary to an instance of the Game class by mapping dictionary keys to
        instance attributes.

        :param data: Dictionary containing game details. Keys should include 'white',
         'black', 'url', 'fen', 'pgn', 'time_control', 'time_class', 'rules',
         and optionally 'rated', 'accuracies', 'tournament', 'match', 'eco',
         'start_time', and 'end_time'.
        :type data: Dict
        :return: An instance of the Game class populated with the provided
         dictionary data.
        :rtype: Game
        """
        if isinstance(data, dict):
            return cls(
                white_url=data["white"],
                black_url=data["black"],
                url=data["url"],
                fen=data["fen"],
                time_control=data["time_control"],
                time_class=data["time_class"],
                rules=data["rules"],
                rated=data.get("rated", False),
                accuracies=data.get("accuracies"),
                tournament=data.get("tournament"),
                match=data.get("match"),
                eco=data.get("eco"),
                start_time=data.get("start_time"),
                end_time=data.get("end_time"),
                id=int(data["url"].split("/")[-1]),
                pgn=data.get("pgn"),
                tcn=data.get("tcn"),
                initial_setup=data.get("initial_setup"),
                uuid=data.get("uuid"),
            )
        else:
            raise ValueError("Invalid input data. Expected a dictionary.")

    async def fetch_white(self, client: ChessComClient) -> "Player":
        """Fetch the player information for the white player using the provided client.

        This method asynchronously retrieves the player data from the specified URL
        for the white player and sets it to the instance variable `_white`.

        :param client: An instance of `ChessComClient` used to retrieve player data.
        :type client: ChessComClient

        :return: The `Player` object containing the white player's information.
        :rtype: Player
        """
        self._white = await client.get_player(username=self.white_url.split("/")[-1])
        return self._white

    async def fetch_black(self, client: ChessComClient) -> "Player":
        """Fetch the black player details asynchronously.

        This function fetches the details of the black player by making an asynchronous
        call to the ChessComClient. The username of the black player is extracted from
        the black_url, and then the function retrieves the player's details from the
        client.

        :param client: The ChessComClient instance used to fetch the player details.
        :type client: ChessComClient
        :return: The details of the black player.
        :rtype: dict
        """
        self._black = await client.get_player(username=self.black_url.split("/")[-1])
        return self._black

    @property
    def white(self) -> "Player":
        """Get the white player.

        Fetch the white player if it has not been fetched yet. Raises a ValueError
        if the white player has not been fetched.

        :return: The white player.
        :rtype: Player
        :raises ValueError: If the white player has not been fetched.
        """
        if self._white is None:
            raise ValueError(
                "White player has not been fetched. Call `fetch_white` with an API "
                "client first."
            )
        return self._white

    @property
    def black(self) -> "Player":
        """Return the black player instance.

        This method retrieves the black player instance stored in the
        _current attribute. If the _current attribute has not been set,
        it raises a ValueError indicating that the black player has not
        been fetched yet and suggests calling `fetch_black` with an API client.

        :return: Black player instance.
        :rtype: Player
        :raises ValueError: If the black player has not been fetched.
        """
        if self._black is None:
            raise ValueError(
                "Black player has not been fetched. Call `fetch_black` with an API "
                "client first."
            )
        return self._black

    def __eq__(self, other: Any) -> bool:
        """Check equality based on game attributes."""
        if not isinstance(other, Game):
            return NotImplemented
        return (
            self.url == other.url
            and self.white_url == other.white_url
            and self.black_url == other.black_url
            and self.fen == other.fen
            and self.pgn == other.pgn
            and self.time_control == other.time_control
            and self.time_class == other.time_class
            and self.id == other.id
        )

    def __hash__(self) -> int:
        """Generate a hash based on game attributes."""
        return hash(
            (
                self.url,
                self.white_url,
                self.black_url,
                self.fen,
                self.pgn,
                self.time_control,
                self.time_class,
                self.id,
            )
        )


@dataclass
class GameArchive:
    """Represents a game archive."""

    archive_urls: List[str]
    username: str
    _games: Optional[Set[BoardGame]] = field(default=None, init=False)
    _fetched_archives: Dict[str, List[BoardGame]] = field(
        default_factory=dict, init=False
    )
    _availability_cache: Optional[Dict[int, List[str]]] = field(
        default=None, init=False
    )

    @classmethod
    def from_dict(
        cls, data: Union[Dict[str, Any], bytes, None], username: Optional[str] = None
    ) -> "GameArchive":
        """Create an instance of the class from a dictionary."""
        if not isinstance(data, dict):
            raise ValueError("Invalid input data. Expected a dictionary.")
        archive_urls = data.get("archives", [])
        if not isinstance(archive_urls, list):
            raise ValueError("Invalid input data. Expected a list of archive URLs.")
        if len(archive_urls) == 0:
            raise ValueError("Invalid input data. Expected a list of archive URLs.")
        if username is None:
            return cls(
                archive_urls=archive_urls, username=archive_urls[0].split("/")[-4]
            )
        else:
            return cls(archive_urls=archive_urls, username=username)

    def available_archives(self) -> Dict[int, List[str]]:
        """Return a cached dictionary of available years and months."""
        if self._availability_cache is None:
            availability: Dict[int, List[str]] = {}
            for url in self.archive_urls:
                match = re.search(r"/games/(\d{4})/(\d{2})", url)
                if match:
                    year, month = int(match.group(1)), str(match.group(2))
                    availability.setdefault(year, []).append(month)
            self._availability_cache = {
                year: sorted(months) for year, months in availability.items()
            }
        return self._availability_cache

    async def fetch_archive(
        self, client: ChessComClient, year: int, month: str
    ) -> List[BoardGame]:
        """Get a list of games from the archive."""
        url = f"{client.BASE_URL}/player/" f"{self.username}/games/{year}/{month}"
        if url in self._fetched_archives:
            return self._fetched_archives[url]
        games = await client.get_archived_games(self.username, year=year, month=month)
        if not isinstance(games, list):
            raise ValueError("Invalid input data. Expected a list of games.")
        if self._games is None:
            # noinspection PyTypeChecker
            self._games = set(games)
        self._games.update(games)
        self._fetched_archives[url] = games
        return games

    async def fetch_games(
        self, client: ChessComClient, batch_size: int = 10
    ) -> Optional[List[Game]]:
        """Fetch all games from the archive in batches."""

        async def fetch_single_archive(url: str) -> Optional[List[BoardGame]]:
            match = re.search(r"/games/(\d{4})/(\d{2})", url)
            if match:
                year, month = int(match.group(1)), str(match.group(2))
                return await self.fetch_archive(client, year, month)
            return []

        # Process archives in batches
        batches = [
            self.archive_urls[i : i + batch_size]
            for i in range(0, len(self.archive_urls), batch_size)
        ]
        all_games: List[BoardGame] = []
        for batch in batches:
            tasks = [fetch_single_archive(url) for url in batch]
            batch_results = await asyncio.gather(*tasks)
            all_games.extend(
                game for games in batch_results if games is not None for game in games
            )

        self._games = set(all_games)
        return list(self._games)

    async def get_game(
        self,
        client: ChessComClient,  # Replace Any with ChessComClient
        game_id: int,
        year: Optional[int] = None,
        month: Optional[str] = None,
    ) -> Optional[Game]:  # Replace Any with Game class
        """Get a single game from the archive."""
        await self._fetch_archives_based_on_params(client, year, month)

        if self._games is None:
            raise ValueError("No games found.")
        for game in self._games:
            if game.id == game_id:
                return game
        raise ValueError("Game not found.")

    async def _fetch_archives_based_on_params(
        self,
        client: ChessComClient,
        year: Optional[int],
        month: Optional[str],
    ) -> None:
        """Fetch archives based on the year and month parameters."""
        availability = self.available_archives()

        # Fetch all games if no year and no month are specified
        if not year and not month:
            await self.fetch_games(client=client)
            return

        # Fetch games for a specific month across all years
        if not year and month:
            for year, months in availability.items():
                if month in months:
                    await self.fetch_archive(client=client, year=year, month=month)
            return

        # Fetch games for a specific year across all months
        if year and not month:
            for month in availability.get(year, []):
                await self.fetch_archive(client=client, year=year, month=month)
            return

        # Fetch games for a specific year and month
        if year and month:
            await self.fetch_archive(client=client, year=year, month=month)
            return

        # Raise an error for invalid parameters (shouldn't be reachable)
        raise ValueError("Invalid parameters for fetching archives.")

    @property
    def games(self) -> List[Game]:
        """Return a list of games from the archive."""
        if self._games is None:
            raise ValueError(
                "Games have not been fetched. Call `fetch_archive` or "
                "`fetch_games` first."
            )
        return list(self._games)


@dataclass
class UserClub:
    """Represents a user club with details about club ID, name, and activity.

    UserClub is a data class storing information related to a specific club,
    including its identifier, name, last activity timestamp, icon URL, club URL,
    and the date the user joined the club.

    :ivar club_id: Unique identifier for the club.
    :type club_id: str
    :ivar name: Name of the club.
    :type name: str
    :ivar last_activity: Timestamp of the last activity in the club.
    :type last_activity: datetime
    :ivar icon: URL of the club's icon.
    :type icon: str
    :ivar url: URL of the club's homepage.
    :type url: str
    :ivar joined: Timestamp of when the user joined the club.
    :type joined: datetime
    """

    def __init__(
        self,
        club_id: str,
        name: str,
        last_activity: datetime,
        icon: str,
        url: str,
        joined: datetime,
    ):
        """Initialize the club with the given details.

        :param club_id: Unique identifier for the club.
        :type club_id: str
        :param name: Name of the club.
        :type name: str
        :param last_activity: Timestamp of the last activity in the club.
        :type last_activity: datetime
        :param icon: URL of the club's icon.
        :type icon: str
        :param url: URL of the club's homepage.
        :type url: str
        :param joined: Timestamp of when the user joined the club.
        :type joined: datetime
        """
        self.club_id = club_id
        self.name = name
        self.last_activity = last_activity
        self.icon = icon
        self.url = url
        self.joined = joined

    @classmethod
    def from_dict(cls, data: Union[Dict[str, Any], bytes, None]) -> "UserClub":
        """Create an instance of UserClub from a dictionary.

        This class method takes a dictionary containing club data and returns an
        instance of UserClub with the corresponding attributes.

        :param data: A dictionary containing the club data.
        :type data: Dict
        :return: An instance of UserClub with attributes populated
         from the dictionary data.
        :rtype: UserClub
        """
        if not isinstance(data, dict):
            raise ValueError("Invalid input data. Expected a dictionary.")
        return cls(
            club_id=data.get("@id", ""),  # Use "@id" for the unique identifier
            name=data.get("name", ""),
            last_activity=datetime.fromtimestamp(data.get("last_activity", 0)),
            icon=data.get("icon", ""),
            url=data.get("url", ""),
            joined=datetime.fromtimestamp(data.get("joined", 0)),
        )


@dataclass
class Club:
    """Represents a club with various attributes.

    This class encapsulates the details of a club including its ID, name, country,
    average daily rating, members count, creation date, last activity date, admin
    information, visibility status, join request status, icon, description, and URL.

    :ivar id: Unique identifier for the club.
    :type id: str
    :ivar name: Name of the club.
    :type name: str
    :ivar club_id: Integer club ID.
    :type club_id: int
    :ivar country: Country where the club is based.
    :type country: str
    :ivar average_daily_rating: Average daily rating of the club.
    :type average_daily_rating: int
    :ivar members_count: Number of members in the club.
    :type members_count: int
    :ivar created: Timestamp of when the club was created.
    :type created: datetime
    :ivar last_activity: Timestamp of the last activity in the club.
    :type last_activity: datetime
    :ivar admin: List of administrators of the club.
    :type admin: List[str]
    :ivar visibility: Visibility status of the club.
    :type visibility: str
    :ivar join_request: Join request status for the club.
    :type join_request: str
    :ivar icon: URL or path to the club's icon.
    :type icon: str
    :ivar description: Description of the club.
    :type description: str
    :ivar url: URL of the club's page.
    :type url: str
    """

    id: str
    name: str
    club_id: int
    country: str
    average_daily_rating: int
    members_count: int
    created: datetime
    last_activity: datetime
    admin: List[str] = field(default_factory=list)
    visibility: str = ""
    join_request: str = ""
    icon: str = ""
    description: str = ""
    url: str = ""

    @classmethod
    def from_dict(cls, data: Union[Dict[str, Any], bytes, None]) -> "Club":
        """Create an instance of Club from a dictionary.

        Given a dictionary with keys and values corresponding to attributes of the
        Club class, instantiate and return a new Club object. Default values are
        provided for keys that are missing in the dictionary.

        :param data: Dictionary containing Club attributes.
        :type data: Dict
        :return: A new instance of Club.
        :rtype: Club
        """
        if not isinstance(data, dict):
            raise ValueError("Invalid input data. Expected a dictionary.")
        return cls(
            id=data.get("@id", ""),
            name=data.get("name", ""),
            club_id=data.get("club_id", 0),
            country=data.get("country", ""),
            average_daily_rating=data.get("average_daily_rating", 0),
            members_count=data.get("members_count", 0),
            created=datetime.fromtimestamp(data.get("created", 0)),
            last_activity=datetime.fromtimestamp(data.get("last_activity", 0)),
            admin=data.get("admin", []),
            visibility=data.get("visibility", ""),
            join_request=data.get("join_request", ""),
            icon=data.get("icon", ""),
            description=data.get("description", ""),
            url=data.get("url", ""),
        )


@dataclass
class CountryClubs:
    """Holds information related to country clubs and fetches club from an external API.

    This class is designed to hold and manage a list of country club URLs. It
    provides methods to fetch detailed club information, caching previously fetched
    results to avoid redundant network calls. This ensures efficient fetch operations
    and allows access to club details when needed.

    :ivar club_urls: List of club URLs to be fetched.
    :type club_urls: List[str]
    :ivar _clubs: List of fetched club objects, initialized to None and populated after
     fetching.
    :type _clubs: Optional[List["Club"]]
    """

    club_urls: List[str]
    _clubs: Optional[List["Club"]] = field(default=None, init=False, repr=False)

    @classmethod
    def from_dict(cls, data: Union[Dict[str, Any], bytes, None]) -> "CountryClubs":
        """Create an instance of the class from a dictionary.

        This method allows initializing the class with data provided in a dictionary
        format. The dictionary should contain a key "clubs" which holds the value for
        the `club_urls` attribute of the class.

        :param data: A dictionary containing the initialization data.
        :type data: dict
        :return: An instance of the class initialized with the provided data.
        :rtype: cls
        """
        if not isinstance(data, dict):
            raise ValueError("Invalid input data. Expected a dictionary.")
        return cls(club_urls=data["clubs"])

    async def fetch_clubs(self, client: ChessComClient) -> "List[Club]":
        """Fetch clubs using the given Chess.com client.

        Fetches club details concurrently, ensuring already fetched clubs are not
        fetched again. Handles rate limit errors by retrying the request after a
        fixed backoff period. Any errors during fetch are logged and the club is
        skipped.

        :param client: An instance of ChessComClient to fetch clubs.
        :type client: ChessComClient
        :return: A list of unique fetched clubs.
        :rtype: List[Club]
        """
        self._clubs = self._clubs or []
        seen_club_ids = {club.id.split("/")[-1] for club in self._clubs}

        async def fetch_club(club_url: str) -> Optional[Club]:
            club_id = club_url.split("/")[-1]
            if club_id in seen_club_ids:
                return None  # Skip already fetched clubs
            try:
                print(f"Fetching club with ID: {club_id}")
                club = await client.get_club(url_id=club_id)
                if club:
                    seen_club_ids.add(club.id.split("/")[-1])
                return club
            except RateLimitError:
                print(f"Rate limit hit while fetching club {club_id}. Retrying...")
                await asyncio.sleep(2)  # Retry after fixed backoff
                return await fetch_club(
                    club_url
                )  # Retry logic already in `_make_request`
            except Exception as e:
                print(f"Error fetching club {club_id}: {e}")
                return None

        # Fetch club details concurrently
        tasks = [fetch_club(club_url) for club_url in self.club_urls]
        fetched_clubs = await asyncio.gather(*tasks, return_exceptions=True)

        # Add unique clubs to `_clubs`
        for club in filter(None, fetched_clubs):  # Filter out None values and errors
            if isinstance(club, Club):
                print(f"Fetched club: {club.name}")
                self._clubs.append(club)

        return self._clubs

    @property
    def clubs(self) -> "List[Club]":
        """Get the list of clubs.

        This property returns the list of clubs associated with the instance.
        The clubs need to be fetched beforehand via an API client.

        :raises ValueError: If the clubs have not been fetched.

        :return: The list of clubs.
        :rtype: List[Club]
        """
        if self._clubs is None:
            raise ValueError(
                "Clubs have not been fetched. Call `fetch_clubs` with an API client "
                "first."
            )
        return self._clubs


@dataclass
class Group:
    """Represents a group of games and their fair play removals.

    This class is used to encapsulate the information related to a group,
    including the list of games and any fair play removals associated with them.

    :ivar fair_play_removals: List of fair play removals.
    :type fair_play_removals: List[str]
    :ivar games: List of games in the group.
    :type games: List[Game]
    """

    fair_play_removals: List[str]
    games: List[Game]

    @classmethod
    def from_dict(cls, data: Union[Dict[str, Any], bytes, None]) -> "Group":
        """Create a Group instance from a dictionary.

        This method takes a dictionary representation of a Group and returns
        a new Group instance. The dictionary should include information about
        fair_play_removals and a list of games.

        :param data: Dictionary containing the Group data.
        :type data: dict
        :return: A new Group instance.
        :rtype: Group
        """
        if not isinstance(data, dict):
            raise ValueError("Invalid input data. Expected a dictionary.")
        return cls(
            fair_play_removals=data["fair_play_removals"],
            games=[Game.from_dict(game) for game in data["games"]],
        )

    def __eq__(self, other: Any) -> bool:
        """Check equality based on games and fair play removals."""
        if not isinstance(other, Group):
            return NotImplemented
        return (
            self.fair_play_removals == other.fair_play_removals
            and self.games == other.games
        )

    def __hash__(self) -> int:
        """Generate a hash based on fair play removals and games."""
        return hash((tuple(self.fair_play_removals), tuple(self.games)))


# TODO: We might want to rename this
@dataclass
class Round:
    """Represents a round in a chess tournament.

    The Round class encapsulates the details of a specific round in a chess
    tournament, including the URLs of groups participating in the round and the
    players involved. It provides functionality to fetch detailed information
    about these groups asynchronously.

    :ivar group_urls: List of URLs corresponding to the groups in this round.
    :type group_urls: List[str]
    :ivar _groups: Internal storage for the group objects once fetched.
    :type _groups: Optional[List[Group]]
    :ivar players: List of dictionaries with player information.
    :type players: List[Dict[str, str]]
    """

    group_urls: List[str]
    _groups: Optional[List[Group]] = field(default=None, init=False, repr=False)
    players: List[Dict[str, str]]
    _seen_group_urls: set[tuple[str, int, int]] = field(default_factory=set)

    @classmethod
    def from_dict(cls, data: Union[Dict[str, Any], bytes, None]) -> "Round":
        """Create an instance of the `Round` class from a dictionary.

        :param data: The dictionary containing group URLs and players.
        :type data: dict
        :return: An instance of the `Round` class.
        :rtype: Round
        """
        if not isinstance(data, dict):
            raise ValueError("Invalid input data. Expected a dictionary.")
        return cls(group_urls=data["groups"], players=data["players"])

    async def fetch_groups(self, client: ChessComClient) -> "List[Group]":
        """Fetch groups from the Chess.com API client.

        This function fetches tournament round groups from the Chess.com client for
        the URLs provided in `self.group_urls`. If a group has already been fetched,
        it will not be fetched again. The function handles rate limiting by retrying
        after a brief pause.

        :param client: Instance of ChessComClient used to fetch group data.
        :type client: ChessComClient
        :return: List of fetched groups.
        :rtype: List[Group]
        """
        self._groups = self._groups or []
        self._seen_group_urls = self._seen_group_urls or set()

        async def fetch_group(group_url: str) -> Optional["Group"]:
            parts = group_url.split("/")[-3:]
            group_id = (parts[0], int(parts[1]), int(parts[2]))
            if group_id in self._seen_group_urls:
                return None
            try:
                group = await client.get_tournament_round_group(*group_id)
                self._seen_group_urls.add(group_id)
                return group
            except RateLimitError:
                print(f"Rate limit hit for group {group_id}. Retrying...")
                await asyncio.sleep(2)
                return await fetch_group(group_url)
            except Exception as e:
                print(f"Error fetching group {group_id}: {e}")
                return None

        tasks = [fetch_group(url) for url in self.group_urls]
        fetched_groups = await asyncio.gather(*tasks, return_exceptions=True)

        if not isinstance(fetched_groups, list):
            raise ValueError("Invalid input data. Expected a list.")
        valid_groups: Iterable[Group] = (
            g for g in fetched_groups if isinstance(g, Group)
        )
        self._groups.extend(valid_groups)

        return self._groups

    @property
    def groups(self) -> "List[Group]":
        """Get the list of groups.

        Raises a ValueError if the groups have not been fetched.

        :raises ValueError: If groups have not been fetched.
                            Call `fetch_groups` with an API client first.
        :return: The list of groups.
        :rtype: List[Group]
        """
        if self._groups is None:
            raise ValueError(
                "Groups have not been fetched. Call `fetch_groups` with an API client "
                "first."
            )
        return self._groups

    def __eq__(self, other: Any) -> bool:
        """Compare two objects."""
        if not isinstance(other, Round):
            return NotImplemented
        return self.group_urls == other.group_urls and self.players == other.players

    def __hash__(self) -> int:
        """Generate a hash based on the group URLs and the players."""
        return hash(
            (
                tuple(self.group_urls),
                tuple(frozenset(player.items()) for player in self.players),
            )
        )


@dataclass
class Tournament:
    """Represent a chess tournament with its various attributes and methods.

    The `Tournament` class provides a structured way to describe a chess tournament,
    including its name, URL, description, creator, status, finish time, settings,
    players, and rounds. It offers methods to construct a `Tournament` instance from
    a dictionary, fetch tournament rounds using an asynchronous client, and access
    the rounds securely.

    :ivar name: Name of the tournament.
    :type name: str
    :ivar url: URL of the tournament.
    :type url: str
    :ivar description: Optional description of the tournament.
    :type description: Optional[str]
    :ivar creator: Creator of the tournament.
    :type creator: str
    :ivar status: Status of the tournament.
    :type status: str
    :ivar finish_time: Optional finish time of the tournament represented as an epoch
        timestamp.
    :type finish_time: Optional[int]
    :ivar settings: Settings of the tournament.
    :type settings: Dict
    :ivar players: List of players participating in the tournament.
    :type players: List[Dict]
    :ivar round_urls: URLs for each round of the tournament.
    :type round_urls: List[str]
    :ivar _rounds: List of fetched rounds, initially set to None.
    :type _rounds: Optional[List[Round]]
    """

    name: str
    url: str
    description: Optional[str]
    creator: str
    status: str
    finish_time: Optional[int]
    settings: Dict[str, Any]
    players: List[Dict[str, str]]
    round_urls: List[str]
    _rounds: List[Round] = field(default_factory=list, init=False, repr=False)

    @classmethod
    def from_dict(cls, data: Union[Dict[str, Any], bytes, None]) -> "Tournament":
        """Create a `Tournament` instance from a dictionary.

        This method constructs a `Tournament` instance by extracting necessary data
        from the provided dictionary. It requires specific keys to be present
        in the dictionary, such as "name", "url", "creator", "status", "settings",
        "players", and "rounds". Optionally, "description" and "finish_time" keys can
        also be included if available in the dictionary.

        :param data: Dictionary containing tournament data. Keys include:
                        - "name",
                        - "url",
                        - "description" (optional),
                        - "creator",
                        - "status",
                        - "finish_time" (optional),
                        - "settings",
                        - "players",
                        - "rounds".
        :type data: Dict
        :return: A `Tournament` class instance created from the `data` dictionary.
        :rtype: Tournament
        """
        if not isinstance(data, dict):
            raise ValueError("Invalid input data. Expected a dictionary.")
        return cls(
            name=data["name"],
            url=data["url"],
            description=data.get("description"),
            creator=data["creator"],
            status=data["status"],
            finish_time=data.get("finish_time"),
            settings=data["settings"],
            players=data["players"],
            round_urls=data["rounds"],
        )

    async def fetch_rounds(self, client: ChessComClient) -> "List[Round]":
        """Fetch rounds for the given Chess.com client.

        This method retrieves tournament rounds by their URLs. It ensures no
        duplicates and retries when a rate limit error occurs.

        :param client: The ChessComClient instance used to fetch the rounds.
        :type client: ChessComClient
        :return: A list of fetched rounds.
        :rtype: List[Round]
        """
        seen_rounds = set(self._rounds)

        async def fetch_round(round_url: str) -> Optional[Round]:
            round_id = (round_url.split("/")[-2], int(round_url.split("/")[-1]))
            if round_id in seen_rounds:
                return None
            try:
                round_obj = await client.get_tournament_round(*round_id)
                seen_rounds.add(round_obj)
                return round_obj
            except RateLimitError:
                print(f"Rate limit hit for round {round_id}. Retrying...")
                await asyncio.sleep(2)
                return await fetch_round(round_url)
            except Exception as e:
                print(f"Error fetching round {round_id}: {e}")
                return None

        tasks = [fetch_round(url) for url in self.round_urls]
        fetched_rounds = await asyncio.gather(*tasks, return_exceptions=True)
        filtered_rounds: List[Optional[Round]] = [
            r if isinstance(r, Round) else None for r in fetched_rounds
        ]
        self._rounds.extend(filter(None, filtered_rounds))
        return self._rounds

    @property
    def rounds(self) -> "List[Round]":
        """Get the rounds of the competition.

        Detailed sumamry: This property method returns the list of rounds associated
        with the competition. If `_rounds` has not been set (i.e., remains `None`),
        an exception is raised instructing the user to fetch the rounds first via an
        appropriate API client.

        :raises ValueError: If rounds have not been set (i.e., `_rounds` is `None`).
        :rtype: List[Round]

        :return: The list of rounds for the competition.
        """
        if self._rounds is None:
            raise ValueError(
                "Rounds have not been fetched. Call `fetch_rounds` with an API client "
                "first."
            )
        return self._rounds


@dataclass
class BoardGame(Game):
    """Represents a board game derived from the base Game class.

    The BoardGame class provides additional properties and methods specific to board
    games, including attributes for `white` and `black` players, which are instances
    of corresponding player types. A board game can be created from a dictionary using
    the `from_dict` class method.

    :ivar white: Instance of White player.
    :type white: Optional[White]
    :ivar black: Instance of Black player.
    :type black: Optional[Black]
    """

    white: Optional[White] = field(default=None, init=False)  # type: ignore
    black: Optional[Black] = field(default=None, init=False)  # type: ignore

    @classmethod
    def from_dict(cls, data: Union[Dict[str, Any], bytes, None]) -> "BoardGame":
        """Create a BoardGame instance from a dictionary.

        The method instantiates a BoardGame object based on the data
        provided in the dictionary. It initializes the key attributes
        and sets the computed fields for white and black pieces.

        :param data: A dictionary containing details of the board game.
        :type data: Dict

        :return: An instance of BoardGame created from dictionary data.
        :rtype: BoardGame
        """
        # Create the base instance
        if not isinstance(data, dict):
            raise ValueError("Invalid input data. Expected a dictionary.")
        instance = cls(
            white_url=data["white"]["@id"],  # Parent field
            black_url=data["black"]["@id"],  # Parent field
            url=data["url"],
            fen=data["fen"],
            time_control=data["time_control"],
            time_class=data["time_class"],
            rules=data["rules"],
            rated=data.get("rated", False),
            accuracies=data.get("accuracies"),
            tournament=data.get("tournament"),
            match=data.get("match"),
            eco=data.get("eco"),
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
            id=int(data["url"].split("/")[-1]),
            pgn=data.get("pgn"),
            tcn=data.get("tcn"),
            initial_setup=data.get("initial_setup"),
            uuid=data.get("uuid"),
        )

        # Set computed fields
        instance.white = White.from_dict(data["white"])
        instance.black = Black.from_dict(data["black"])

        return instance

    def __eq__(self, other: Any) -> bool:
        """Check equality based on game attributes."""
        if not isinstance(other, Game):
            return NotImplemented
        return (
            self.url == other.url
            and self.white_url == other.white_url
            and self.black_url == other.black_url
            and self.fen == other.fen
            and self.pgn == other.pgn
            and self.time_control == other.time_control
            and self.time_class == other.time_class
            and self.id == other.id
        )

    def __hash__(self) -> int:
        """Generate a hash based on game attributes."""
        return hash(
            (
                self.url,
                self.white_url,
                self.black_url,
                self.fen,
                self.pgn,
                self.time_control,
                self.time_class,
                self.id,
            )
        )


@dataclass
class Board:
    """Represents a collection of board games and their associated scores.

    This class facilitates the representation and manipulation of a collection
    of board games and their corresponding scores. It provides functionalities
    to instantiate a Board object from a dictionary.

    :ivar board_scores: A dictionary mapping board game names to their scores.
    :type board_scores: Dict
    :ivar games: A list of BoardGame objects representing different board games.
    :type games: List[BoardGame]
    """

    board_scores: Dict[str, int]
    games: List[BoardGame]

    @classmethod
    def from_dict(cls, data: Union[Dict[str, Any], bytes, None]) -> "Board":
        """Create a `Board` instance from a dictionary representation.

        :param data: The dictionary containing board
         information and list of board games.
        :type data: Dict
        :return: A `Board` instance created from the given dictionary.
        :rtype: Board
        """
        if not isinstance(data, dict):
            raise ValueError("Invalid input data. Expected a dictionary.")
        return cls(
            board_scores=data["board_scores"],
            games=[BoardGame.from_dict(board_game) for board_game in data["games"]],
        )


@dataclass
class MatchResult:
    """Representation of match results data for a game.

    This class stores data about the players who played as white and black in a
    match. It provides a class method to instantiate objects from a dictionary.

    :ivar played_as_white: Name of the player who played as white.
    :type played_as_white: Optional[str]
    :ivar played_as_black: Name of the player who played as black.
    :type played_as_black: Optional[str]
    """

    played_as_white: Optional[str]
    played_as_black: Optional[str]

    @classmethod
    def from_dict(cls, data: Union[Dict[str, Any], bytes, None]) -> "MatchResult":
        """Create a `MatchResult` instance from a dictionary.

        This method extracts the relevant information from the provided dictionary to
        initialize and return a `MatchResult` instance.

        :param data: Dictionary containing match result data.
        :type data: Dict
        :return: An instance of `MatchResult`.
        :rtype: MatchResult
        """
        if not isinstance(data, dict):
            raise ValueError("Invalid input data. Expected a dictionary.")
        return cls(
            played_as_white=data.get("played_as_white", None),
            played_as_black=data.get("played_as_black", None),
        )


@dataclass
class FinishedPlayerMatch:
    """Represents a player's finished match in a chess club context.

    Contains the player's details, results, club information, and board details.
    Supports fetching additional information like club and board data asynchronously
    using a provided client.

    :ivar name: Player's name.
    :type name: str
    :ivar url: URL to the player's profile or match.
    :type url: str
    :ivar id: Unique identifier for the player's match.
    :type id: str
    :ivar club_url: URL to the player's club.
    :type club_url: str
    :ivar _club: Privately stored club instance, fetched asynchronously.
    :type _club: Optional[Club]
    :ivar results: Results of the player's match.
    :type results: MatchResult
    :ivar board_url: URL to the match board.
    :type board_url: str
    :ivar _board: Privately stored board instance, fetched asynchronously.
    :type _board: Optional[Board]
    """

    name: str
    url: str
    id: str
    club_url: str
    _club: Optional[Club] = field(default=None, init=False, repr=False)
    results: MatchResult
    board_url: str
    _board: Optional[Board] = field(default=None, init=False, repr=False)

    @classmethod
    def from_dict(
        cls, data: Union[Dict[str, Any], bytes, None]
    ) -> "FinishedPlayerMatch":
        """Create a FinishedPlayerMatch instance from a dictionary.

        This class method takes a dictionary representing a finished player match and
        converts it into an instance of FinishedPlayerMatch with all required
        attributes.

        :param data: The dictionary containing finished player match details.
        :type data: Dict
        :return: A FinishedPlayerMatch instance created from the provided dictionary.
        :rtype: FinishedPlayerMatch
        """
        if not isinstance(data, dict):
            raise ValueError("Invalid input data. Expected a dictionary.")
        return cls(
            name=data["name"],
            url=data["url"],
            id=data["@id"],
            club_url=data["club"],
            results=MatchResult.from_dict(data["results"]),
            board_url=data["board"],
        )

    async def fetch_club(self, client: ChessComClient) -> "Club":
        """Fetch club details asynchronously using the provided client instance.

        This method retrieves the club information by making an API call through
        the `client` parameter. If the club data is already available, it
        returns the cached information instead of fetching it again.

        :param client: An instance of `ChessComClient` used to make the API call.
        :type client: ChessComClient
        :return: An instance of `Club` containing the club details.
        :rtype: Club
        """
        if self._club is None:
            self._club = await client.get_club(url_id=self.club_url.split("/")[-1])
        return self._club

    @property
    def club(self) -> "Club":
        """Get the associated club object.

        This property raises a ValueError if the club has not been fetched yet.
        Ensure to call `fetch_club` with an API client prior to accessing this property.

        :return: The club associated with this object.
        :rtype: Club
        :raises ValueError: If the club has not been fetched.
        """
        if self._club is None:
            raise ValueError(
                "Club has not been fetched. Call `fetch_club` with an API client first."
            )
        return self._club

    async def fetch_board(self, client: ChessComClient) -> "Board":
        """Fetch board information for a chess match.

        This asynchronous method fetches board details for a specific chess match
        using the provided ChessComClient. The method fetches data only if the
        board has not been previously fetched and cached.

        :param client: Instance of ChessComClient used to fetch match board details.
        :type client: ChessComClient
        :return: The fetched chess board details.
        :rtype: Board
        """
        if self._board is None:
            self._board = await client.get_match_board(
                match_id=int(self.board_url.split("/")[-2]),
                board_num=int(self.board_url.split("/")[-1]),
            )
        return self._board

    @property
    def board(self) -> "Board":
        """Provide access to the board property.

        If the board is not fetched, raise a ValueError.

        :return: The board instance.
        :rtype: Board
        """
        if self._board is None:
            raise ValueError(
                "Board has not been fetched. Call `fetch_board` with an API client "
                "first."
            )
        return self._board


@dataclass
class InProgressPlayerMatch:
    """Representation of an in-progress player match in a chess competition.

    Provides methods to fetch associated club and board details asynchronously
    using provided clients.

    :ivar name: Name of the player.
    :type name: str
    :ivar url: URL of the player profile.
    :type url: str
    :ivar id: Unique identifier of the player.
    :type id: str
    :ivar club_url: URL of the player's club.
    :type club_url: str
    :ivar _club: Internal cache for fetched club data.
    :type _club: Optional[Club]
    :ivar results: Results of the match.
    :type results: MatchResult
    :ivar board_url: URL of the board where the match is played.
    :type board_url: str
    :ivar _board: Internal cache for fetched board data.
    :type _board: Optional[Board]
    """

    name: str
    url: str
    id: str
    club_url: str
    _club: Optional[Club] = field(default=None, init=False, repr=False)
    results: MatchResult
    board_url: str
    _board: Optional[Board] = field(default=None, init=False, repr=False)

    @classmethod
    def from_dict(
        cls, data: Union[Dict[str, Any], bytes, None]
    ) -> "InProgressPlayerMatch":
        """Create an instance of InProgressPlayerMatch from a dictionary.

        This method constructs an object of InProgressPlayerMatch using the
        key-value pairs from the provided dictionary.

        :param data: Dictionary containing the data required to create
            an instance of InProgressPlayerMatch.
            - name: The name of the player (str).
            - url: The URL associated with the player (str).
            - @id: The ID of the player (str).
            - club: The URL of the player's club (str).
            - results: The match results which are passed to
              `MatchResult.from_dict` method.
            - board: The URL of the player's board (str).
        :return: An instance of InProgressPlayerMatch.
        """
        if not isinstance(data, dict):
            raise ValueError("Invalid input data. Expected a dictionary.")
        return cls(
            name=data["name"],
            url=data["url"],
            id=data["@id"],
            club_url=data["club"],
            results=MatchResult.from_dict(data["results"]),
            board_url=data["board"],
        )

    async def fetch_club(self, client: ChessComClient) -> "Club":
        """Fetch club information from ChessComClient.

        Fetches information about a chess club using the provided ChessComClient. If the
        information has already been fetched, it returns the cached club information.

        :param client: ChessComClient used to fetch club information.
        :type client: ChessComClient

        :return: Club information.
        :rtype: Club
        """
        if self._club is None:
            self._club = await client.get_club(url_id=self.club_url.split("/")[-1])
        return self._club

    @property
    def club(self) -> "Club":
        """Get the club instance.

        This property returns the club instance associated with the current object.
        If the club instance has not been fetched, it raises a `ValueError`.
        Ensure to call `fetch_club` with an appropriate API client to fetch the club
        before accessing this property.

        :raises ValueError: If the club instance has not been fetched.
        :rtype: Club
        :return: The club instance associated with the object.
        """
        if self._club is None:
            raise ValueError(
                "Club has not been fetched. Call `fetch_club` with an API client first."
            )
        return self._club

    async def fetch_board(self, client: ChessComClient) -> "Board":
        """Fetch the chess board associated with the given client.

        This method fetches the board from the provided client's match board URL.
        It updates the `_board` attribute by making an asynchronous call
        to `get_match_board` method of the `ChessComClient`.

        :param client: Instance of `ChessComClient` used to fetch the board.
        :type client: ChessComClient
        :return: The fetched chess board.
        :rtype: Board
        """
        if self._board is None:
            self._board = await client.get_match_board(
                match_id=int(self.board_url.split("/")[-2]),
                board_num=int(self.board_url.split("/")[-1]),
            )
        return self._board

    @property
    def board(self) -> "Board":
        """Get the current state of the board.

        Retrieve the board object which contains the current game state. This method
        raises a ValueError if the board has not been fetched yet. Ensure to call
        `fetch_board` with an API client before accessing the board.

        :raises ValueError: If the board has not been fetched yet.
        :return: The current board object.
        :rtype: Board
        """
        if self._board is None:
            raise ValueError(
                "Board has not been fetched. Call `fetch_board` with an API client "
                "first."
            )
        return self._board


@dataclass
class RegisteredPlayerMatch:
    """Class representing a registered player's match in a chess competition.

    The RegisteredPlayerMatch class encapsulates the details of a registered player's
    match, including the player's name, various URLs associated with their club and
    match, and methods to fetch additional information about their club and match.

    :ivar name: The name of the player.
    :type name: str
    :ivar url: The URL of the player's profile.
    :type url: str
    :ivar club_url: The URL of the player's club.
    :type club_url: str
    :ivar _club: The player's club details, fetched asynchronously.
    :type _club: Optional[Club]
    :ivar match_url: The URL of the player's match.
    :type match_url: str
    :ivar _match: The player's match details, fetched asynchronously.
    :type _match: Optional[Match]
    """

    name: str
    url: str
    club_url: str
    _club: Optional[Club] = field(default=None, init=False, repr=False)
    match_url: str
    _match: Optional[Match] = field(default=None, init=False, repr=False)

    @classmethod
    def from_dict(
        cls, data: Union[Dict[str, Any], bytes, None]
    ) -> "RegisteredPlayerMatch":
        """Create a RegisteredPlayerMatch instance from a dictionary.

        :param data: Dictionary containing the data to
         create a RegisteredPlayerMatch instance.
        :type data: dict
        :return: A new instance of RegisteredPlayerMatch.
        :rtype: RegisteredPlayerMatch
        """
        if not isinstance(data, dict):
            raise ValueError("Invalid input data. Expected a dictionary.")
        return cls(
            name=data["name"],
            url=data["url"],
            club_url=data["club"],
            match_url=data["@id"],
        )

    async def fetch_club(self, client: ChessComClient) -> "Club":
        """Fetch the club details from the Chess.com client.

        If the club details are not already cached, retrieves the club information
        from the provided Chess.com client and caches it for future use.
        The club URL is split to extract the club's unique identifier, which is
        then used to retrieve the club data using the client's `get_club` method.

        :param client: The ChessComClient instance used to fetch club details.
        :type client: ChessComClient
        :return: The fetched club details.
        :rtype: Club
        """
        if self._club is None:
            self._club = await client.get_club(url_id=self.club_url.split("/")[-1])
        return self._club

    @property
    def club(self) -> "Club":
        """Get the club object.

        Raises an error if the club has not been fetched yet. Ensure to call
        `fetch_club` with an API client before accessing this property.

        :return: The fetched club instance.
        :rtype: Club
        :raises: ValueError if the club is not fetched.
        """
        if self._club is None:
            raise ValueError(
                "Club has not been fetched. Call `fetch_club` with an API client first."
            )
        return self._club

    async def fetch_match(self, client: ChessComClient) -> "Match":
        """Fetch match information from Chess.com using the provided client.

        If the match information has not been previously fetched, this method will
        use the ChessComClient to retrieve the match details based on the match ID
        extracted from the match URL. The match information is then cached for future
        use.

        :param client: The client used to interact with the Chess.com API.
        :type client: ChessComClient
        :return: The match details fetched from the Chess.com API.
        :rtype: Match
        """
        if self._match is None:
            self._match = await client.get_match(
                match_id=int(self.match_url.split("/")[-1])
            )
        return self._match

    @property
    def match(self) -> "Match":
        """Retrieve the match object. If the match has not been fetched, raise an error.

        The match object is fetched through an external API using the `fetch_match`
        method. If the match has not been fetched before trying to retrieve it,
        a ValueError will be raised to indicate that the data is not available.

        :raises ValueError: If the match has not been fetched.

        :return: The fetched match object.
        :rtype: Match
        """
        if self._match is None:
            raise ValueError(
                "Match has not been fetched. Call `fetch_match` with an API client "
                "first."
            )
        return self._match


@dataclass
class PlayerMatches:
    """Represents a collection of player matches.

    This class encapsulates the matches that a player has finished, is currently in
    progress with, and is registered for. It provides methods to create instances
    of itself from a dictionary, supporting easy data deserialization.

    :ivar finished: List of finished player matches.
    :type finished: List[FinishedPlayerMatch]
    :ivar in_progress: List of player matches that are currently in progress.
    :type in_progress: List[InProgressPlayerMatch]
    :ivar registered: List of player matches that the player is registered for.
    :type registered: List[RegisteredPlayerMatch]
    """

    finished: List[FinishedPlayerMatch]
    in_progress: List[InProgressPlayerMatch]
    registered: List[RegisteredPlayerMatch]

    @classmethod
    def from_dict(cls, data: Union[Dict[str, Any], bytes, None]) -> "PlayerMatches":
        """Create a PlayerMatches instance from a dictionary.

        :param data: Dictionary containing match information. The dictionary should have
            "finished", "in_progress", and "registered"
            keys with lists of respective matches.
        :type data: Dict
        :return: A PlayerMatches instance populated with FinishedPlayerMatch,
            InProgressPlayerMatch, and RegisteredPlayerMatch.
        :rtype: PlayerMatches
        """
        if not isinstance(data, dict):
            raise ValueError("Invalid input data. Expected a dictionary.")
        return cls(
            finished=[
                FinishedPlayerMatch.from_dict(finished_player_match)
                for finished_player_match in data["finished"]
            ],
            in_progress=[
                InProgressPlayerMatch.from_dict(in_progress_player_match)
                for in_progress_player_match in data["in_progress"]
            ],
            registered=[
                RegisteredPlayerMatch.from_dict(registered_player_match)
                for registered_player_match in data["registered"]
            ],
        )


@dataclass
class FinishedPlayerTournament:
    """Represents a player’s performance in a completed chess tournament.

    This class encapsulates details regarding a player's results in a specific
    chess tournament. It provides functionality to convert data from a dictionary
    and fetch the tournament details using an API client.

    :ivar url: URL of the player's tournament results.
    :type url: str
    :ivar tournament_url: URL of the tournament.
    :type tournament_url: str
    :ivar wins: Number of wins the player has achieved.
    :type wins: int
    :ivar losses: Number of losses the player has encountered.
    :type losses: int
    :ivar draws: Number of draws the player has encountered.
    :type draws: int
    :ivar points_awarded: Points awarded to the player.
    :type points_awarded: int
    :ivar placement: Placement of the player in the tournament.
    :type placement: int
    :ivar status: Status of the player in the tournament.
    :type status: str
    :ivar total_players: Total number of players in the tournament.
    :type total_players: int
    """

    url: str
    tournament_url: str
    _tournament: Optional[Tournament] = field(default=None, init=False, repr=False)
    wins: int
    losses: int
    draws: int
    points_awarded: int
    placement: int
    status: str
    total_players: int

    @classmethod
    def from_dict(
        cls, data: Union[Dict[str, Any], bytes, None]
    ) -> "FinishedPlayerTournament":
        """Construct a FinishedPlayerTournament instance from a dictionary.

        :param data: Dictionary containing tournament details.
        :type data: Dict
        :return: Instantiated FinishedPlayerTournament object.
        :rtype: FinishedPlayerTournament
        """
        if not isinstance(data, dict):
            raise ValueError("Invalid input data. Expected a dictionary.")
        return cls(
            url=data["url"],
            tournament_url=data["@id"],
            wins=data["wins"],
            losses=data["losses"],
            draws=data["draws"],
            points_awarded=data.get("points_awarded", 0),
            placement=data["placement"],
            status=data["status"],
            total_players=data["total_players"],
        )

    async def fetch_tournament(self, client: ChessComClient) -> "Tournament":
        """Fetch the tournament details using the provided ChessComClient instance.

        Retrieve and cache tournament data from the given client based on the URL
        identifier.

        :param client: The ChessComClient instance to use for fetching tournament data.
        :type client: ChessComClient
        :return: The fetched Tournament object.
        :rtype: Tournament
        """
        if self._tournament is None:
            self._tournament = await client.get_tournament(
                url_id=self.tournament_url.split("/")[-1]
            )
        return self._tournament

    @property
    def tournament(self) -> "Tournament":
        """Return the fetched tournament if it has been fetched.

        :return: The fetched tournament.
        :rtype: Tournament
        """
        if self._tournament is None:
            raise ValueError(
                "Tournament has not been fetched. Call `fetch_tournament` with an API "
                "client first."
            )
        return self._tournament


@dataclass
class InProgressPlayerTournament:
    """Represent an in-progress player tournament.

    This class is used to encapsulate details about a player's ongoing tournament. It
    includes methods to populate the class from a dictionary, fetch tournament details
    from a Chess.com client, and access the tournament instance.

    :ivar url: URL of the player.
    :type url: str
    :ivar tournament_url: URL of the tournament.
    :type tournament_url: str
    :ivar _tournament: Underlying tournament details (optional).
    :type _tournament: Optional[Tournament]
    :ivar wins: Number of wins.
    :type wins: int
    :ivar losses: Number of losses.
    :type losses: int
    :ivar draws: Number of draws.
    :type draws: int
    :ivar status: Current status of the tournament.
    :type status: str
    :ivar total_players: Total number of players in the tournament.
    :type total_players: int
    """

    url: str
    tournament_url: str
    _tournament: Optional[Tournament] = field(default=None, init=False, repr=False)
    wins: int
    losses: int
    draws: int
    status: str
    total_players: int

    @classmethod
    def from_dict(
        cls, data: Union[Dict[str, Any], bytes, None]
    ) -> "InProgressPlayerTournament":
        """Convert a dictionary to an InProgressPlayerTournament instance.

        :param data: The dictionary containing tournament details.
        :type data: Dict
        :return: An instance of InProgressPlayerTournament based on the dictionary data.
        :rtype: InProgressPlayerTournament
        """
        if not isinstance(data, dict):
            raise ValueError("Invalid input data. Expected a dictionary.")
        return cls(
            url=data["url"],
            tournament_url=data["@id"],
            wins=data["wins"],
            losses=data["losses"],
            draws=data["draws"],
            status=data["status"],
            total_players=data["total_players"],
        )

    async def fetch_tournament(self, client: ChessComClient) -> "Tournament":
        """Fetch the tournament details from the ChessComClient.

        This method fetches and returns the tournament details using the provided
        ChessComClient instance if they have not been fetched previously.

        :param client: An instance of ChessComClient used to fetch tournament details.
        :type client: ChessComClient
        :return: A Tournament instance containing the details of the tournament.
        :rtype: Tournament
        """
        if self._tournament is None:
            self._tournament = await client.get_tournament(
                url_id=self.tournament_url.split("/")[-1]
            )
        return self._tournament

    @property
    def tournament(self) -> "Tournament":
        """Get the current tournament instance.

        Detailed Summary: This property method provides access to the Tournament
        instance. Before accessing the tournament, you must ensure that the
        tournament has been fetched using the `fetch_tournament` method. If the
        tournament has not been fetched, attempting to access it will raise a
        ValueError.

        :raises ValueError: If the tournament has not been fetched.
        :return: Current tournament instance.
        :rtype: Tournament
        """
        if self._tournament is None:
            raise ValueError(
                "Tournament has not been fetched. Call `fetch_tournament` with an API "
                "client first."
            )
        return self._tournament


@dataclass
class RegisteredPlayerTournament:
    """Represents a registered player's tournament details.

    The RegisteredPlayerTournament class holds information about a player's status
    and the URL to the tournament. It allows fetching detailed tournament information
    asynchronously when needed.

    :ivar url: The URL to the registered player.
    :type url: str
    :ivar tournament_url: The URL to the tournament.
    :type tournament_url: str
    :ivar _tournament: Private variable that stores the Tournament object once fetched.
    :type _tournament: Optional[Tournament]
    :ivar status: The status of the registered player in the tournament.
    :type status: str
    """

    url: str
    tournament_url: str
    _tournament: Optional[Tournament] = field(default=None, init=False, repr=False)
    status: str

    @classmethod
    def from_dict(
        cls, data: Union[Dict[str, Any], bytes, None]
    ) -> "RegisteredPlayerTournament":
        """Convert a dictionary to a RegisteredPlayerTournament object.

        This class method takes a dictionary containing the keys 'url', '@id',
        and 'status', and creates an instance of the RegisteredPlayerTournament class
        using these values.

        :param data: Dictionary containing tournament registration details.
        :type data: Dict
        :return: RegisteredPlayerTournament object instantiated with the provided data.
        :rtype: RegisteredPlayerTournament
        """
        if not isinstance(data, dict):
            raise ValueError("Invalid input data. Expected a dictionary.")
        return cls(url=data["url"], tournament_url=data["@id"], status=data["status"])

    async def fetch_tournament(self, client: ChessComClient) -> "Tournament":
        """Retrieve tournament details asynchronously from the Chess.com API.

        This function fetches tournament details if they have not already been
        retrieved. The tournament details are fetched based on the tournament URL.

        :param client: An instance of the ChessComClient used to fetch tournament data.
        :type client: ChessComClient
        :return: An instance of the Tournament class containing tournament details.
        :rtype: Tournament
        """
        if self._tournament is None:
            self._tournament = await client.get_tournament(
                url_id=self.tournament_url.split("/")[-1]
            )
        return self._tournament

    @property
    def tournament(self) -> "Tournament":
        """Returns the tournament instance.

        :return: The fetched tournament instance.
        :rtype: Tournament
        :raises ValueError: If the tournament has not been fetched.
        """
        if self._tournament is None:
            raise ValueError(
                "Tournament has not been fetched. Call `fetch_tournament` with an API "
                "client first."
            )
        return self._tournament


@dataclass
class PlayerTournaments:
    """Representation of a player's participation in tournaments.

    This class holds details about the tournaments a player has finished, is currently
    in-progress with, and is registered for, providing a unified view of a player's
    tournament history and current involvement.

    :ivar finished: Tournaments that the player has completed.
    :type finished: List[FinishedPlayerTournament]
    :ivar in_progress: Tournaments that the player is currently participating in.
    :type in_progress: List[InProgressPlayerTournament]
    :ivar registered: Tournaments that the player is registered for but has not started.
    :type registered: List[RegisteredPlayerTournament]
    """

    finished: List[FinishedPlayerTournament]
    in_progress: List[InProgressPlayerTournament]
    registered: List[RegisteredPlayerTournament]

    @classmethod
    def from_dict(cls, data: Union[Dict[str, Any], bytes, None]) -> "PlayerTournaments":
        """Create a PlayerTournaments instance from a dictionary.

        :param data: Data dictionary containing information about player's tournaments.
        :type data: dict
        :return: A new instance of PlayerTournaments.
        :rtype: PlayerTournaments
        """
        if not isinstance(data, dict):
            raise ValueError("Invalid input data. Expected a dictionary.")
        return cls(
            finished=[
                FinishedPlayerTournament.from_dict(finished_player_tournament)
                for finished_player_tournament in data["finished"]
            ],
            in_progress=[
                InProgressPlayerTournament.from_dict(in_progress_player_tournament)
                for in_progress_player_tournament in data["in_progress"]
            ],
            registered=[
                RegisteredPlayerTournament.from_dict(registered_player_tournament)
                for registered_player_tournament in data["registered"]
            ],
        )


@dataclass
class FinishedClubMatch:
    """Represents a finished chess club match.

    This class encapsulates the details and operations related to a finished chess
    club match. It includes match information such as the opponent, match results,
    and allows fetching additional details like the match and opponent's chess club
    through asynchronous operations.

    :ivar name: The name of the chess club match.
    :type name: str
    :ivar match_url: URL to the match details.
    :type match_url: str
    :ivar _match: Cached match object fetched from Chess.com.
    :type _match: Optional[Match]
    :ivar opponent_url: URL to the opponent's details.
    :type opponent_url: str
    :ivar _opponent: Cached opponent club object fetched from Chess.com.
    :type _opponent: Optional[Club]
    :ivar start_time: The start time of the match.
    :type start_time: int
    :ivar time_class: The time class of the match (e.g., blitz, bullet).
    :type time_class: str
    :ivar result: The result of the match.
    :type result: str
    """

    name: str
    match_url: str
    _match: Optional[Match] = field(default=None, init=False, repr=False)
    opponent_url: str
    _opponent: Optional[Club] = field(default=None, init=False, repr=False)
    start_time: int
    time_class: str
    result: str

    @classmethod
    def from_dict(cls, data: Union[Dict[str, Any], bytes, None]) -> "FinishedClubMatch":
        """Create an instance of FinishedClubMatch from a dictionary.

        This method constructs an instance of the FinishedClubMatch class using
        the provided dictionary containing relevant match data. The data dictionary
        should include keys corresponding to the attributes of the FinishedClubMatch
        class.

        :param data: Dictionary containing match data.
        :type data: Dict
        :return: An instance of the FinishedClubMatch class.
        :rtype: FinishedClubMatch
        """
        if not isinstance(data, dict):
            raise ValueError("Invalid input data. Expected a dictionary.")
        return cls(
            name=data["name"],
            match_url=data["@id"],
            opponent_url=data["opponent"],
            start_time=data["start_time"],
            time_class=data["time_class"],
            result=data["result"],
        )

    async def fetch_match(self, client: ChessComClient) -> "Match":
        """Fetch and cache a chess match using the given Chess.com client.

        This function is an asynchronous coroutine that fetches a chess match from
        Chess.com using the provided client. If the match has already been fetched
        previously, it returns the cached match instead of making another request.

        :param client: The Chess.com client to fetch the match data.
        :type client: ChessComClient
        :return: The fetched or cached chess match.
        :rtype: Match
        """
        if self._match is None:
            self._match = await client.get_match(
                match_id=int(self.match_url.split("/")[-1])
            )
        return self._match

    @property
    def match(self) -> "Match":
        """Get the match object.

        This property retrieves the match object if it has been fetched.
        If the match object has not been fetched, it raises a ValueError,
        indicating that the `fetch_match` method should be called with an
        API client first.

        :raises ValueError: If the match object has not been fetched.
        :returns: The match object.
        :rtype: Match
        """
        if self._match is None:
            raise ValueError(
                "Match has not been fetched. Call `fetch_match` with an API client "
                "first."
            )
        return self._match

    async def fetch_opponent(self, client: ChessComClient) -> "Club":
        """Fetch opponent's chess club details asynchronously.

        This method retrieves the Chess club details of an opponent using the provided
        Chess.com client. If the opponent's details have not been fetched yet, it uses
        the client's `get_club` method to fetch and cache them.

        :param client: The Chess.com client used to fetch club details.
        :type client: ChessComClient
        :return: The opponent's club details.
        :rtype: Club
        """
        if self._opponent is None:
            self._opponent = await client.get_club(
                url_id=self.opponent_url.split("/")[-1]
            )
        return self._opponent

    @property
    def opponent(self) -> "Club":
        """Get the opponent.

        Fetch the opponent from the internal state if it has been set.

        :raises ValueError: If opponent has not been fetched.
        :return: The opponent club instance.
        :rtype: Club
        """
        if self._opponent is None:
            raise ValueError(
                "Opponent has not been fetched. Call `fetch_opponent` with an API "
                "client first."
            )
        return self._opponent


@dataclass
class InProgressClubMatch:
    """Representation of an in-progress club match.

    The `InProgressClubMatch` class encapsulates the details of a chess club match that
    is currently in progress. It provides methods for fetching the match and opponent
    information using a provided API client.

    :ivar name: Name of the club match.
    :type name: str
    :ivar match_url: URL of the club match.
    :type match_url: str
    :ivar _match: Cached match details, fetched using an API client.
    :type _match: Optional[Match]
    :ivar opponent_url: URL of the opponent club.
    :type opponent_url: str
    :ivar _opponent: Cached opponent details, fetched using an API client.
    :type _opponent: Optional[Club]
    :ivar start_time: Start time of the match.
    :type start_time: int
    :ivar time_class: Classification of the match timing (e.g., bullet, blitz).
    :type time_class: str
    """

    name: str
    match_url: str
    _match: Optional[Match] = field(default=None, init=False, repr=False)
    opponent_url: str
    _opponent: Optional[Club] = field(default=None, init=False, repr=False)
    start_time: int
    time_class: str

    @classmethod
    def from_dict(
        cls, data: Union[Dict[str, Any], bytes, None]
    ) -> "InProgressClubMatch":
        """Create an instance of InProgressClubMatch from a dictionary.

        :param data: Dictionary containing match details.
        :type data: Dict
        :return: Instance of InProgressClubMatch.
        :rtype: InProgressClubMatch
        """
        if not isinstance(data, dict):
            raise ValueError("Invalid input data. Expected a dictionary.")
        return cls(
            name=data["name"],
            match_url=data["@id"],
            opponent_url=data["opponent"],
            start_time=data["start_time"],
            time_class=data["time_class"],
        )

    async def fetch_match(self, client: ChessComClient) -> "Match":
        """Fetch match information from Chess.com.

        This method fetches match details using the provided ChessComClient instance.
        It initializes the match attribute if it is not already set.

        :param client: ChessComClient instance used to fetch match data.
        :type client: ChessComClient
        :return: Match instance containing match details.
        :rtype: Match
        """
        if self._match is None:
            self._match = await client.get_match(
                match_id=int(self.match_url.split("/")[-1])
            )
        return self._match

    @property
    def match(self) -> "Match":
        """Return the current match if it has been fetched.

        The match is fetched only when `fetch_match` is called with an appropriate
        API client. If the match has not been fetched, this property raises a
        ValueError.

        :return: The fetched match.
        :rtype: Match
        :raises ValueError: If the match has not been fetched.
        """
        if self._match is None:
            raise ValueError(
                "Match has not been fetched. Call `fetch_match` with an API client "
                "first."
            )
        return self._match

    async def fetch_opponent(self, client: ChessComClient) -> "Club":
        """Fetch and return the opponent club.

        :param client: The ChessComClient instance used to fetch the opponent club.
        :type client: ChessComClient
        :return: The opponent club.
        :rtype: Club
        """
        if self._opponent is None:
            self._opponent = await client.get_club(
                url_id=self.opponent_url.split("/")[-1]
            )
        return self._opponent

    @property
    def opponent(self) -> "Club":
        """Get the opponent club.

        This property retrieves the opponent club if it has been fetched. If the
        opponent has not been fetched, it raises a ValueError.

        :raises ValueError: If the opponent has not been fetched yet.
        :return: The opponent club.
        :rtype: Club
        """
        if self._opponent is None:
            raise ValueError(
                "Opponent has not been fetched. Call `fetch_opponent` with an API "
                "client first."
            )
        return self._opponent


@dataclass
class RegisteredClubMatch:
    """Represent a registered club match.

    This class models a registered match in a chess club, encapsulating details about
    the match and the opponent's club. It includes methods to fetch detailed match
    and opponent information asynchronously from the Chess.com API.

    :ivar name: Name of the match.
    :type name: str
    :ivar match_url: URL of the match.
    :type match_url: str
    :ivar _match: Cached match information.
    :type _match: Optional[Match]
    :ivar opponent_url: URL of the opponent club.
    :type opponent_url: str
    :ivar _opponent: Cached opponent club information.
    :type _opponent: Optional[Club]
    :ivar time_class: Class of the match time (e.g., blitz, rapid).
    :type time_class: str
    """

    name: str
    match_url: str
    _match: Optional[Match] = field(default=None, init=False, repr=False)
    opponent_url: str
    _opponent: Optional[Club] = field(default=None, init=False, repr=False)
    time_class: str

    @classmethod
    def from_dict(
        cls, data: Union[Dict[str, Any], bytes, None]
    ) -> "RegisteredClubMatch":
        """Create an instance of RegisteredClubMatch from a dictionary.

        :param data: Dictionary containing match information. Expected keys are
                     'name', '@id', 'opponent', and 'time_class'.
        :type data: Dict
        :return: Instance of RegisteredClubMatch.
        :rtype: RegisteredClubMatch
        """
        if not isinstance(data, dict):
            raise ValueError("Invalid input data. Expected a dictionary.")
        return cls(
            name=data["name"],
            match_url=data["@id"],
            opponent_url=data["opponent"],
            time_class=data["time_class"],
        )

    async def fetch_match(self, client: ChessComClient) -> "Match":
        """Fetch match information from the Chess.com API.

        This asynchronous method accepts a ChessComClient instance and fetches match
        details based on the match ID extracted from the match URL. If the match
        details are already cached in the _match attribute, it returns the cached
        data. Otherwise, it retrieves the match details from the API and caches them.

        :param client: Instance of ChessComClient used to fetch match details.
        :type client: ChessComClient
        :return: Match details fetched from the Chess.com API.
        :rtype: Match
        """
        if self._match is None:
            self._match = await client.get_match(
                match_id=int(self.match_url.split("/")[-1])
            )
        return self._match

    @property
    def match(self) -> "Match":
        """Get the fetched match.

        This method retrieves the match that has been fetched. If the match has not
        been fetched yet, it raises a ValueError with an appropriate message.

        :raises ValueError: If the match has not been fetched.
        :return: The fetched match.
        :rtype: Match
        """
        if self._match is None:
            raise ValueError(
                "Match has not been fetched. Call `fetch_match` with an API client "
                "first."
            )
        return self._match

    async def fetch_opponent(self, client: ChessComClient) -> "Club":
        """Fetch the opponent's club from the Chess.com client if not already cached.

        This method retrieves the club information of the opponent using the
        Chess.com client. If the opponent's club has already been fetched and cached,
        it returns the cached value. Otherwise, it fetches the club information using
        the client's `get_club` method with the URL identifier extracted from the
        opponent's URL.

        :param client: Instance of ChessComClient used to fetch club information.
        :type client: ChessComClient
        :return: The opponent's club information.
        :rtype: Club
        """
        if self._opponent is None:
            self._opponent = await client.get_club(
                url_id=self.opponent_url.split("/")[-1]
            )
        return self._opponent

    @property
    def opponent(self) -> "Club":
        """Get the opponent club object for the current club.

        Ensure that the opponent club has been fetched before calling this property.

        :return: The opponent club.
        :rtype: Club
        :raises ValueError: If the opponent has not been fetched.
        """
        if self._opponent is None:
            raise ValueError(
                "Opponent has not been fetched. Call `fetch_opponent` with an API "
                "client first."
            )
        return self._opponent


@dataclass
class ClubMatches:
    """Represents a collection of club matches.

    This class is used to manage and encapsulate different states of club matches. It
    provides functionality to instantiate the class from a dictionary format which
    includes lists of finished, in-progress, and registered matches.

    :ivar finished: List of finished club matches.
    :type finished: List[FinishedClubMatch]
    :ivar in_progress: List of club matches currently in progress.
    :type in_progress: List[InProgressClubMatch]
    :ivar registered: List of registered club matches.
    :type registered: List[RegisteredClubMatch]
    """

    finished: List[FinishedClubMatch]
    in_progress: List[InProgressClubMatch]
    registered: List[RegisteredClubMatch]

    @classmethod
    def from_dict(cls, data: Union[Dict[str, Any], bytes, None]) -> "ClubMatches":
        """Create a `ClubMatches` instance from a dictionary.

        :param data: A dictionary containing the club matches data with keys 'finished',
            'in_progress', and 'registered'.
        :type data: dict
        :return: An instance of `ClubMatches` initialized with parsed match data.
        :rtype: ClubMatches
        """
        if not isinstance(data, dict):
            raise ValueError("Invalid input data. Expected a dictionary.")
        return cls(
            finished=[
                FinishedClubMatch.from_dict(finished_club_match)
                for finished_club_match in data["finished"]
            ],
            in_progress=[
                InProgressClubMatch.from_dict(in_progress_club_match)
                for in_progress_club_match in data["in_progress"]
            ],
            registered=[
                RegisteredClubMatch.from_dict(registered_club_match)
                for registered_club_match in data["registered"]
            ],
        )


@dataclass
class Match:
    """Represent a chess match including its details and operations.

    This class holds data about a chess match such as name, URL, start time, end time,
    status, and more. It also provides methods to create a Match instance from
    a dictionary and fetch its associated boards using an async client.

    :ivar match_url: URL of the match.
    :type match_url: str
    :ivar name: Name of the match.
    :type name: str
    :ivar url: URL specific to the match.
    :type url: str
    :ivar description: Description of the match.
    :type description: Optional[str]
    :ivar start_time: Match start time as a timestamp.
    :type start_time: Optional[int]
    :ivar end_time: Match end time as a timestamp.
    :type end_time: Optional[int]
    :ivar status: Current status of the match.
    :type status: str
    :ivar board_count: Number of boards in the match.
    :type board_count: int
    :ivar settings: Settings related to the match.
    :type settings: Dict
    :ivar teams: Information about the teams participating in the match.
    :type teams: Dict
    :ivar _boards: List of boards, fetched asynchronously.
    :type _boards: Optional[List[Board]]
    """

    match_url: str
    name: str
    url: str
    description: Optional[str]
    start_time: Optional[int]
    end_time: Optional[int]
    status: str
    board_count: int
    _boards: Optional[List[Union[Board, BaseException, None]]] = field(
        default=None, init=False, repr=False
    )
    # TODO: Implement dataclass for settings
    settings: Dict[str, Any]
    # TODO: Implement dataclass for teams
    teams: Dict[str, Any]
    _seen_board_ids: Set[int] = field(default_factory=set, init=False, repr=False)

    @classmethod
    def from_dict(cls, data: Union[Dict[str, Any], bytes, None]) -> "Match":
        """Create a Match instance from a dictionary.

        This method extracts relevant information from a dictionary
        and uses it to create a new Match instance.

        :param data: The dictionary containing match data.
        :type data: Dict
        :return: A new instance of Match created from the given dictionary.
        :rtype: Match
        """
        if not isinstance(data, dict):
            raise ValueError("Invalid input data. Expected a dictionary.")
        return cls(
            match_url=data["@id"],
            name=data["name"],
            url=data["url"],
            description=data.get("description"),
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
            status=data["status"],
            board_count=data["boards"],
            settings=data["settings"],
            teams=data["teams"],
        )

    async def fetch_boards(self, client: ChessComClient) -> "List[Board]":
        """Fetch all boards associated with the match for the provided client.

        This method initializes the boards list if it's not already done,
        and fetches each board concurrently while handling rate limits
        and other possible exceptions.

        :param client: The client used to communicate with Chess.com.
        :type client: ChessComClient
        :return: List of boards fetched.
        :rtype: List[Board]
        """
        self._boards = self._boards or []
        seen_board_ids = self._seen_board_ids or set()

        async def fetch_board(board_num: int) -> Optional[Board]:
            if board_num in seen_board_ids:
                return None
            try:
                board = await client.get_match_board(
                    match_id=int(self.match_url.split("/")[-1]), board_num=board_num
                )
                seen_board_ids.add(board_num)
                return board
            except RateLimitError:
                print(f"Rate limit hit for board {board_num}. Retrying...")
                await asyncio.sleep(2)
                return await fetch_board(board_num)
            except Exception as e:
                print(f"Error fetching board {board_num}: {e}")
                return None

        tasks = [fetch_board(i) for i in range(1, self.board_count + 1)]
        fetched_boards = await asyncio.gather(*tasks, return_exceptions=True)

        self._boards.extend(
            filter(
                lambda x: isinstance(x, Board) and not isinstance(x, BaseException),
                fetched_boards,
            )
        )
        return [board for board in self._boards if isinstance(board, Board)]

    @property
    def boards(self) -> "Optional[List[Union[Board, BaseException, None]]]":
        """Get the list of boards.

        Raises a ValueError if boards have not been fetched.

        :raises ValueError: If boards have not been fetched.
        :return: List of boards.
        :rtype: List[Board]
        """
        if self._boards is None or not isinstance(self._boards, list):
            raise ValueError(
                "Boards have not been fetched. Call `fetch_boards` with an API client "
                "first."
            )
        return self._boards


@dataclass
class Country:
    """Represents a country with a unique code and name.

    A Country object comprises a code and a name, and can be instantiated directly
    or through a class method that parses a dictionary.

    :ivar code: The unique code representing the country.
               This could be a standard country code like 'US' for the United States.
    :type code: str
    :ivar name: The name of the country.
    :type name: str
    """

    code: str
    name: str

    @classmethod
    def from_dict(cls, data: Union[Dict[str, Any], bytes, None]) -> "Country":
        """Convert a dictionary to a Country object.

        :param data: Dictionary containing country data.
        :type data: Dict
        :return: Instance of Country.
        :rtype: Country
        """
        if not isinstance(data, dict):
            raise ValueError("Invalid input data. Expected a dictionary.")
        return cls(code=data["code"], name=data["name"])


@dataclass
class DailyPuzzle:
    """Represents a daily chess puzzle.

    The DailyPuzzle class encapsulates details about a chess puzzle including
    its title, URL, publication time, FEN string, PGN string, and image URL.
    It also provides a class method to create an instance from a dictionary.

    :ivar title: The title of the chess puzzle.
    :type title: str
    :ivar url: The URL where the puzzle can be accessed.
    :type url: str
    :ivar publish_time: The timestamp when the puzzle was published.
    :type publish_time: int
    :ivar fen: The FEN string representing the puzzle position.
    :type fen: str
    :ivar pgn: The PGN string representing the puzzle solution.
    :type pgn: str
    :ivar image: The URL to the image of the chess puzzle.
    :type image: str
    """

    title: str
    url: str
    publish_time: int
    fen: str
    pgn: str
    image: str

    @classmethod
    def from_dict(cls, data: Union[Dict[str, Any], bytes, None]) -> "DailyPuzzle":
        """Create a DailyPuzzle instance from a dictionary.

        :param data: Dictionary containing the puzzle data.
        :type data: Dict
        :return: An instance of DailyPuzzle.
        :rtype: DailyPuzzle
        """
        if not isinstance(data, dict):
            raise ValueError("Invalid input data. Expected a dictionary.")
        return cls(
            title=data["title"],
            url=data["url"],
            publish_time=data["publish_time"],
            fen=data["fen"],
            pgn=data["pgn"],
            image=data["image"],
        )


@dataclass
class Streamer:
    """Represents a streamer with attributes related to their streaming platforms.

    This class encapsulates the information about a streamer, including their username,
    avatar, URLs for Twitch and other platforms, live status, community streamer flag,
    and the list of platforms where they stream.

    :ivar username: Username of the streamer.
    :type username: str
    :ivar avatar: URL to the streamer's avatar image.
    :type avatar: str
    :ivar twitch_url: URL to the streamer's Twitch channel.
    :type twitch_url: str
    :ivar url: General URL associated with the streamer.
    :type url: str
    :ivar is_live: Indicates if the streamer is currently live.
    :type is_live: bool
    :ivar is_community_streamer: Indicates if the streamer is a community streamer.
    :type is_community_streamer: bool
    :ivar platforms: List of platforms where the streamer is available, each with
        details such as type, stream URL, channel URL, live status, and
        main live platform status.
    :type platforms: List[Dict]
    """

    username: str
    avatar: str
    twitch_url: str
    url: str
    is_live: bool
    is_community_streamer: bool
    platforms: List[Dict[str, Any]]

    @classmethod
    def from_dict(cls, data: Union[Dict[str, Any], bytes, None]) -> "Streamer":
        """Create a Streamer object from a dictionary.

        This method allows you to create an instance of the Streamer class using a
        dictionary with specific keys. If certain keys are missing in the dictionary,
        default values are provided.

        :param data: Dictionary containing the keys 'username', 'avatar', 'twitch_url',
            'url', 'is_live', 'is_community_streamer', and 'platforms'. Each platform in
            'platforms' should be a dictionary with keys 'type', 'stream_url',
            'channel_url', 'is_live', and 'is_main_live_platform'.
        :type data: Dict
        :return: New instance of Streamer class created from the given dictionary.
        :rtype: Streamer
        """
        if not isinstance(data, dict):
            raise ValueError("Invalid input data. Expected a dictionary.")
        return cls(
            username=data["username"],
            avatar=data.get("avatar", ""),
            twitch_url=data.get("twitch_url", ""),  # Handle missing `twitch_url`
            url=data["url"],
            is_live=data.get("is_live", False),
            is_community_streamer=data.get("is_community_streamer", False),
            platforms=[
                {
                    "type": platform.get("type", ""),
                    "stream_url": platform.get("stream_url", ""),
                    "channel_url": platform.get("channel_url", ""),
                    "is_live": platform.get("is_live", False),
                    "is_main_live_platform": platform.get(
                        "is_main_live_platform", False
                    ),
                }
                for platform in data.get("platforms", [])  # Iterate through `platforms`
            ],
        )


@dataclass
class LeaderboardEntry:
    """Representation of a leaderboard entry.

    The LeaderboardEntry class encapsulates the data for a single entry in a
    leaderboard, including player_id, username, score, rank, and url. This class can
    be initialized either directly or from a dictionary using the provided class method.

    :ivar player_id: ID of the player.
    :type player_id: int
    :ivar username: Username of the player.
    :type username: str
    :ivar score: Score of the player.
    :type score: int
    :ivar rank: Rank of the player in the leaderboard.
    :type rank: int
    :ivar url: URL associated with the player's profile or avatar.
    :type url: str
    """

    player_id: int
    username: str
    score: int
    rank: int
    url: str

    @classmethod
    def from_dict(cls, data: Union[Dict[str, Any], bytes, None]) -> "LeaderboardEntry":
        """Create a LeaderboardEntry instance from a dictionary.

        :param data: A dictionary containing leaderboard entry data. The keys of the
            dictionary should be "player_id", "username", "score", "rank", and "url".
        :type data: Dict
        :return: An instance of `LeaderboardEntry` created from the provided dictionary.
        :rtype: LeaderboardEntry
        """
        if not isinstance(data, dict):
            raise ValueError("Invalid input data. Expected a dictionary.")
        return cls(
            player_id=data["player_id"],
            username=data["username"],
            score=data["score"],
            rank=data["rank"],
            url=data["url"],
        )


@dataclass
class Leaderboard:
    """Representation of a leaderboard for various game categories.

    The Leaderboard class encapsulates data for different types of chess and other
    game leaderboards. It provides functionality to instantiate an object from
    dictionary data, mapping several leaderboard categories to their corresponding
    entries.

    :ivar daily: Leaderboard entries for the daily category.
    :type daily: List[LeaderboardEntry]
    :ivar daily960: Leaderboard entries for the daily960 category.
    :type daily960: List[LeaderboardEntry]
    :ivar live_rapid: Leaderboard entries for the live rapid category.
    :type live_rapid: List[LeaderboardEntry]
    :ivar live_blitz: Leaderboard entries for the live blitz category.
    :type live_blitz: List[LeaderboardEntry]
    :ivar live_bullet: Leaderboard entries for the live bullet category.
    :type live_bullet: List[LeaderboardEntry]
    :ivar live_bughouse: Leaderboard entries for the live bughouse category.
    :type live_bughouse: List[LeaderboardEntry]
    :ivar live_blitz960: Leaderboard entries for the live blitz960 category.
    :type live_blitz960: List[LeaderboardEntry]
    :ivar live_threecheck: Leaderboard entries for the live threecheck category.
    :type live_threecheck: List[LeaderboardEntry]
    :ivar live_crazyhouse: Leaderboard entries for the live crazyhouse category.
    :type live_crazyhouse: List[LeaderboardEntry]
    :ivar live_kingofthehill: Leaderboard entries
     for the live king of the hill category.
    :type live_kingofthehill: List[LeaderboardEntry]
    :ivar lessons: Leaderboard entries for the lessons category.
    :type lessons: List[LeaderboardEntry]
    :ivar tactics: Leaderboard entries for the tactics category.
    :type tactics: List[LeaderboardEntry]
    """

    daily: List[LeaderboardEntry]
    daily960: List[LeaderboardEntry]
    live_rapid: List[LeaderboardEntry]
    live_blitz: List[LeaderboardEntry]
    live_bullet: List[LeaderboardEntry]
    live_bughouse: List[LeaderboardEntry]
    live_blitz960: List[LeaderboardEntry]
    live_threecheck: List[LeaderboardEntry]
    live_crazyhouse: List[LeaderboardEntry]
    live_kingofthehill: List[LeaderboardEntry]
    lessons: List[LeaderboardEntry]
    tactics: List[LeaderboardEntry]

    @classmethod
    def from_dict(cls, data: Union[Dict[str, Any], bytes, None]) -> "Leaderboard":
        """Create a Leaderboard instance from a dictionary.

        This class method parses a dictionary to create an instance of the Leaderboard
        class, mapping various leaderboard categories to their corresponding entries.

        :param data: Dictionary containing leaderboard data.
        :type data: Dict
        :return: An instance of the Leaderboard class.
        :rtype: Leaderboard
        """
        if not isinstance(data, dict):
            raise ValueError("Invalid input data. Expected a dictionary.")
        return cls(
            daily=[
                LeaderboardEntry.from_dict(entry) for entry in data.get("daily", [])
            ],
            daily960=[
                LeaderboardEntry.from_dict(entry) for entry in data.get("daily960", [])
            ],
            live_rapid=[
                LeaderboardEntry.from_dict(entry)
                for entry in data.get("live_rapid", [])
            ],
            live_blitz=[
                LeaderboardEntry.from_dict(entry)
                for entry in data.get("live_blitz", [])
            ],
            live_bullet=[
                LeaderboardEntry.from_dict(entry)
                for entry in data.get("live_bullet", [])
            ],
            live_bughouse=[
                LeaderboardEntry.from_dict(entry)
                for entry in data.get("live_bughouse", [])
            ],
            live_blitz960=[
                LeaderboardEntry.from_dict(entry)
                for entry in data.get("live_blitz960", [])
            ],
            live_threecheck=[
                LeaderboardEntry.from_dict(entry)
                for entry in data.get("live_threecheck", [])
            ],
            live_crazyhouse=[
                LeaderboardEntry.from_dict(entry)
                for entry in data.get("live_crazyhouse", [])
            ],
            live_kingofthehill=[
                LeaderboardEntry.from_dict(entry)
                for entry in data.get("live_kingofthehill", [])
            ],
            lessons=[
                LeaderboardEntry.from_dict(entry) for entry in data.get("lessons", [])
            ],
            tactics=[
                LeaderboardEntry.from_dict(entry) for entry in data.get("tactics", [])
            ],
        )
