# chess_com_api/models.py

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from difflib import Match
from typing import Dict, List, Optional
from typing import TYPE_CHECKING

from chess_com_api.exceptions import RateLimitError

if TYPE_CHECKING:
    from chess_com_api.client import ChessComClient


@dataclass
class Player:
    """Chess.com player profile."""
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
    def from_dict(cls, data: Dict) -> "Player":
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
            fide=data.get("fide")
        )

    async def fetch_country(self, client: ChessComClient) -> "Country":
        self._country = await client.get_country(iso_code=self.country_url.split("/")[-1])
        return self._country

    @property
    def country(self) -> "Country":
        if self._country is None:
            raise ValueError("Country has not been fetched. Call `fetch_country` with an API client first.")
        return self._country


@dataclass
class PlayerStats:
    """Player's chess statistics."""
    chess_daily: Optional[Dict]
    chess_rapid: Optional[Dict]
    chess_bullet: Optional[Dict]
    chess_blitz: Optional[Dict]
    chess960_daily: Optional[Dict]
    tactics: Optional[Dict]
    lessons: Optional[Dict]
    puzzle_rush: Optional[Dict]

    @classmethod
    def from_dict(cls, data: Dict) -> "PlayerStats":
        return cls(
            chess_daily=data.get("chess_daily"),
            chess_rapid=data.get("chess_rapid"),
            chess_bullet=data.get("chess_bullet"),
            chess_blitz=data.get("chess_blitz"),
            chess960_daily=data.get("chess960_daily"),
            tactics=data.get("tactics"),
            lessons=data.get("lessons"),
            puzzle_rush=data.get("puzzle_rush")
        )


@dataclass
class DailyGame:
    """Chess.com daily game information."""
    url: str
    move_by: datetime
    last_activity: datetime
    draw_offer: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: Dict) -> "DailyGame":
        if "draw_offer" in data.keys():
            if data["move_by"] == 0 or data["draw_offer"] == True:
                pass
        return cls(
            url=data["url"],
            move_by=datetime.fromtimestamp(data["move_by"]),
            last_activity=datetime.fromtimestamp(data["last_activity"]),
            draw_offer=False
        )


@dataclass
class White:
    """Chess.com white player information."""
    rating: int
    result: str
    user_url: str
    username: str
    uuid: str
    _user: Optional[Player] = field(default=None, init=False, repr=False)

    @classmethod
    def from_dict(cls, data: Dict) -> "White":
        return cls(
            rating=data["rating"],
            result=data["result"],
            user_url=data["@id"],
            username=data["username"],
            uuid=data["uuid"]
        )

    async def fetch_user(self, client: ChessComClient) -> "Player":
        if self._user is None:
            self._user = await client.get_player(username=self.username)
        return self._user

    @property
    def user(self) -> "Player":
        if self._user is None:
            raise ValueError("User has not been fetched. Call `fetch_user` with an API client first.")
        return self._user


@dataclass
class Black:
    """Chess.com black player information."""
    rating: int
    result: str
    user_url: str
    username: str
    uuid: str
    _user: Optional[Player] = field(default=None, init=False, repr=False)

    @classmethod
    def from_dict(cls, data: Dict) -> "Black":
        return cls(
            rating=data["rating"],
            result=data["result"],
            user_url=data["@id"],
            username=data["username"],
            uuid=data["uuid"]
        )

    async def fetch_user(self, client: ChessComClient) -> "Player":
        if self._user is None:
            self._user = await client.get_player(username=self.username)
        return self._user

    @property
    def user(self) -> "Player":
        if self._user is None:
            raise ValueError("User has not been fetched. Call `fetch_user` with an API client first.")
        return self._user


@dataclass
class Game:
    """Chess game information."""
    white_url: str
    black_url: str
    url: str
    fen: str
    pgn: str
    time_control: str
    time_class: str
    rules: str
    rated: bool
    accuracies: Optional[Dict] = None
    tournament: Optional[str] = None
    # TODO: Parse to match
    match: Optional[str] = None
    eco: Optional[str] = None
    start_time: Optional[int] = None
    end_time: Optional[int] = None
    _black: Optional[Player] = field(default=None, init=False, repr=False)
    _white: Optional[Player] = field(default=None, init=False, repr=False)

    @classmethod
    def from_dict(cls, data: Dict) -> "Game":
        return cls(
            white_url=data["white"],
            black_url=data["black"],
            url=data["url"],
            fen=data["fen"],
            pgn=data["pgn"],
            time_control=data["time_control"],
            time_class=data["time_class"],
            rules=data["rules"],
            rated=data.get("rated", True),
            accuracies=data.get("accuracies"),
            tournament=data.get("tournament"),
            match=data.get("match"),
            eco=data.get("eco"),
            start_time=data.get("start_time"),
            end_time=data.get("end_time")
        )

    async def fetch_white(self, client: ChessComClient) -> "Player":
        self._white = await client.get_player(username=self.white_url.split("/")[-1])
        return self._white

    async def fetch_black(self, client: ChessComClient):
        self._black = await client.get_player(username=self.black_url.split("/")[-1])
        return self._black

    @property
    def white(self) -> "Player":
        if self._white is None:
            raise ValueError("White player has not been fetched. Call `fetch_white` with an API client first.")
        return self._white

    @property
    def black(self) -> "Player":
        if self._black is None:
            raise ValueError("Black player has not been fetched. Call `fetch_black` with an API client first.")
        return self._black


@dataclass
class UserClub:
    def __init__(self, club_id: str, name: str, last_activity: datetime, icon: str, url: str, joined: datetime):
        self.club_id = club_id
        self.name = name
        self.last_activity = last_activity
        self.icon = icon
        self.url = url
        self.joined = joined

    @classmethod
    def from_dict(cls, data: Dict) -> "UserClub":
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
    def from_dict(cls, data: Dict) -> "Club":
        """Create a Club instance from a dictionary."""
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
    club_urls: List[str]
    _clubs: Optional[List["Club"]] = field(default=None, init=False, repr=False)

    @classmethod
    def from_dict(cls, data):
        return cls(
            club_urls=data["clubs"]
        )

    async def fetch_clubs(self, client: ChessComClient) -> "List[Club]":
        self._clubs = self._clubs or []
        seen_club_ids = {club.id for club in self._clubs}

        async def fetch_club(club_url):
            club_id = club_url.split("/")[-1]
            if club_id in seen_club_ids:
                return None  # Skip already fetched clubs
            try:
                print(f"Fetching club with ID: {club_id}")
                club = await client.get_club(url_id=club_id)
                seen_club_ids.add(club_id)
                return club
            except RateLimitError:
                print(f"Rate limit hit while fetching club {club_id}. Retrying...")
                await asyncio.sleep(2)  # Retry after fixed backoff
                return await fetch_club(club_url)  # Retry logic already in `_make_request`
            except Exception as e:
                print(f"Error fetching club {club_id}: {e}")
                return None

        # Fetch club details concurrently
        tasks = [fetch_club(club_url) for club_url in self.club_urls]
        fetched_clubs = await asyncio.gather(*tasks, return_exceptions=True)

        # Add unique clubs to `_clubs`
        for club in filter(None, fetched_clubs):  # Filter out None values and errors
            print(f"Fetched club: {club.name}")
            self._clubs.append(club)

        return self._clubs

    @property
    def clubs(self) -> "List[Club]":
        if self._clubs is None:
            raise ValueError("Clubs have not been fetched. Call `fetch_clubs` with an API client first.")
        return self._clubs


@dataclass
class Group:
    fair_play_removals: List[str]
    games: List[Game]

    @classmethod
    def from_dict(cls, data) -> "Group":
        return cls(
            fair_play_removals=data["fair_play_removals"],
            games=[Game.from_dict(game) for game in data["games"]]
        )


# TODO: We might want to rename this
@dataclass
class Round:
    group_urls: List[str]
    _groups: Optional[List[Group]] = field(default=None, init=False, repr=False)
    players: List[Dict[str, str]]

    @classmethod
    def from_dict(cls, data) -> "Round":
        return cls(
            group_urls=data["groups"],
            players=data["players"]
        )

    async def fetch_groups(self, client: ChessComClient) -> "List[Group]":
        self._groups = self._groups or []
        seen_groups = {group for group in self._groups}

        async def fetch_group(group_url):
            parts = group_url.split("/")[-3:]
            group_id = (parts[0], int(parts[1]), int(parts[2]))
            if group_id in seen_groups:
                return None
            try:
                group = await client.get_tournament_round_group(*group_id)
                seen_groups.add(group_id)
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

        self._groups.extend(filter(None, fetched_groups))
        return self._groups

    @property
    def groups(self) -> "List[Group]":
        if self._groups is None:
            raise ValueError("Groups have not been fetched. Call `fetch_groups` with an API client first.")
        return self._groups


@dataclass
class Tournament:
    """Chess.com tournament information."""
    name: str
    url: str
    description: Optional[str]
    creator: str
    status: str
    finish_time: Optional[int]
    settings: Dict
    players: List[Dict]
    round_urls: List[str]
    _rounds: Optional[List[Round]] = field(default=None, init=False, repr=False)

    @classmethod
    def from_dict(cls, data: Dict) -> "Tournament":
        return cls(
            name=data["name"],
            url=data["url"],
            description=data.get("description"),
            creator=data["creator"],
            status=data["status"],
            finish_time=data.get("finish_time"),
            settings=data["settings"],
            players=data["players"],
            round_urls=data["rounds"]
        )

    async def fetch_rounds(self, client: ChessComClient) -> "List[Round]":
        self._rounds = self._rounds or []
        seen_rounds = {round for round in self._rounds}

        async def fetch_round(round_url):
            round_id = (round_url.split("/")[-2], int(round_url.split("/")[-1]))
            if round_id in seen_rounds:
                return None
            try:
                round_obj = await client.get_tournament_round(*round_id)
                seen_rounds.add(round_id)
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

        self._rounds.extend(filter(None, fetched_rounds))
        return self._rounds

    @property
    def rounds(self) -> "List[Round]":
        if self._rounds is None:
            raise ValueError("Rounds have not been fetched. Call `fetch_rounds` with an API client first.")
        return self._rounds


@dataclass
class BoardGame(Game):
    """Chess.com game information with White and Black objects."""
    white: Optional[White] = field(default=None, init=False)
    black: Optional[Black] = field(default=None, init=False)

    @classmethod
    def from_dict(cls, data: Dict) -> "BoardGame":
        # Create the base instance
        instance = cls(
            white_url=data["white"]["@id"],  # Parent field
            black_url=data["black"]["@id"],  # Parent field
            url=data["url"],
            fen=data["fen"],
            pgn=data["pgn"],
            time_control=data["time_control"],
            time_class=data["time_class"],
            rules=data["rules"],
            rated=data.get("rated", True),
            accuracies=data.get("accuracies"),
            tournament=data.get("tournament"),
            match=data.get("match"),
            eco=data.get("eco"),
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
        )

        # Set computed fields
        instance.white = White.from_dict(data["white"])
        instance.black = Black.from_dict(data["black"])

        return instance


@dataclass
class Board:
    """Chess.com board information."""
    board_scores: Dict
    games: List[BoardGame]

    @classmethod
    def from_dict(cls, data: Dict) -> "Board":
        return cls(
            board_scores=data["board_scores"],
            games=[BoardGame.from_dict(board_game) for board_game in data["games"]]
        )


@dataclass
class MatchResult:
    played_as_white: Optional[str]
    played_as_black: Optional[str]

    @classmethod
    def from_dict(cls, data: Dict) -> "MatchResult":
        return cls(
            played_as_white=data.get("played_as_white", None),
            played_as_black=data.get("played_as_black", None)
        )


@dataclass
class FinishedPlayerMatch:
    """Finished team match information."""
    name: str
    url: str
    id: str
    club_url: str
    _club: Optional[Club] = field(default=None, init=False, repr=False)
    results: MatchResult
    board_url: str
    _board: Optional[Board] = field(default=None, init=False, repr=False)

    @classmethod
    def from_dict(cls, data: Dict) -> "FinishedPlayerMatch":
        return cls(
            name=data["name"],
            url=data["url"],
            id=data["@id"],
            club_url=data["club"],
            results=MatchResult.from_dict(data["results"]),
            board_url=data["board"]
        )

    async def fetch_club(self, client: ChessComClient) -> "Club":
        if self._club is None:
            self._club = await client.get_club(url_id=self.club_url.split("/")[-1])
        return self._club

    @property
    def club(self) -> "Club":
        if self._club is None:
            raise ValueError("Club has not been fetched. Call `fetch_club` with an API client first.")
        return self._club

    async def fetch_board(self, client: ChessComClient) -> "Board":
        if self._board is None:
            self._board = await client.get_match_board(match_id=int(self.board_url.split("/")[-2]),
                                                       board_num=int(self.board_url.split("/")[-1]))
        return self._board

    @property
    def board(self) -> "Board":
        if self._board is None:
            raise ValueError("Board has not been fetched. Call `fetch_board` with an API client first.")
        return self._board


@dataclass
class InProgressPlayerMatch:
    """In-progress team match information."""
    name: str
    url: str
    id: str
    club_url: str
    _club: Optional[Club] = field(default=None, init=False, repr=False)
    results: MatchResult
    board_url: str
    _board: Optional[Board] = field(default=None, init=False, repr=False)

    @classmethod
    def from_dict(cls, data: Dict) -> "InProgressPlayerMatch":
        return cls(
            name=data["name"],
            url=data["url"],
            id=data["@id"],
            club_url=data["club"],
            results=MatchResult.from_dict(data["results"]),
            board_url=data["board"]
        )

    async def fetch_club(self, client: ChessComClient) -> "Club":
        if self._club is None:
            self._club = await client.get_club(url_id=self.club_url.split("/")[-1])
        return self._club

    @property
    def club(self) -> "Club":
        if self._club is None:
            raise ValueError("Club has not been fetched. Call `fetch_club` with an API client first.")
        return self._club

    async def fetch_board(self, client: ChessComClient) -> "Board":
        if self._board is None:
            self._board = await client.get_match_board(match_id=int(self.board_url.split("/")[-2]),
                                                       board_num=int(self.board_url.split("/")[-1]))
        return self._board

    @property
    def board(self) -> "Board":
        if self._board is None:
            raise ValueError("Board has not been fetched. Call `fetch_board` with an API client first.")
        return self._board


@dataclass
class RegisteredPlayerMatch:
    """Registered team match information."""
    name: str
    url: str
    club_url: str
    _club: Optional[Club] = field(default=None, init=False, repr=False)
    match_url: str
    _match: Optional[Match] = field(default=None, init=False, repr=False)

    @classmethod
    def from_dict(cls, data) -> "RegisteredPlayerMatch":
        return cls(
            name=data["name"],
            url=data["url"],
            club_url=data["club"],
            match_url=data["@id"]
        )

    async def fetch_club(self, client: ChessComClient) -> "Club":
        if self._club is None:
            self._club = await client.get_club(url_id=self.club_url.split("/")[-1])
        return self._club

    @property
    def club(self) -> "Club":
        if self._club is None:
            raise ValueError("Club has not been fetched. Call `fetch_club` with an API client first.")
        return self._club

    async def fetch_match(self, client: ChessComClient) -> "Match":
        if self._match is None:
            self._match = await client.get_match(match_id=int(self.match_url.split("/")[-1]))
        return self._match

    @property
    def match(self) -> "Match":
        if self._match is None:
            raise ValueError("Match has not been fetched. Call `fetch_match` with an API client first.")
        return self._match


@dataclass
class PlayerMatches:
    finished: List[FinishedPlayerMatch]
    in_progress: List[InProgressPlayerMatch]
    registered: List[RegisteredPlayerMatch]

    @classmethod
    def from_dict(cls, data: Dict) -> "PlayerMatches":
        return cls(
            finished=[FinishedPlayerMatch.from_dict(finished_player_match) for finished_player_match in
                      data["finished"]],
            in_progress=[InProgressPlayerMatch.from_dict(in_progress_player_match) for in_progress_player_match in
                         data["in_progress"]],
            registered=[RegisteredPlayerMatch.from_dict(registered_player_match) for registered_player_match in
                        data["registered"]]
        )


@dataclass
class FinishedPlayerTournament:
    """Finished tournament player information."""
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
    def from_dict(cls, data: Dict) -> "FinishedPlayerTournament":
        return cls(
            url=data["url"],
            tournament_url=data["@id"],
            wins=data["wins"],
            losses=data["losses"],
            draws=data["draws"],
            points_awarded=data.get("points_awarded", 0),
            placement=data["placement"],
            status=data["status"],
            total_players=data["total_players"]
        )

    async def fetch_tournament(self, client: ChessComClient) -> "Tournament":
        if self._tournament is None:
            self._tournament = await client.get_tournament(url_id=self.tournament_url.split("/")[-1])
        return self._tournament

    @property
    def tournament(self) -> "Tournament":
        if self._tournament is None:
            raise ValueError("Tournament has not been fetched. Call `fetch_tournament` with an API client first.")
        return self._tournament


@dataclass
class InProgressPlayerTournament:
    """In-progress tournament player information."""
    url: str
    tournament_url: str
    _tournament: Optional[Tournament] = field(default=None, init=False, repr=False)
    wins: int
    losses: int
    draws: int
    status: str
    total_players: int

    @classmethod
    def from_dict(cls, data: Dict) -> "InProgressPlayerTournament":
        return cls(
            url=data["url"],
            tournament_url=data["@id"],
            wins=data["wins"],
            losses=data["losses"],
            draws=data["draws"],
            status=data["status"],
            total_players=data["total_players"]
        )

    async def fetch_tournament(self, client: ChessComClient) -> "Tournament":
        if self._tournament is None:
            self._tournament = await client.get_tournament(url_id=self.tournament_url.split("/")[-1])
        return self._tournament

    @property
    def tournament(self) -> "Tournament":
        if self._tournament is None:
            raise ValueError("Tournament has not been fetched. Call `fetch_tournament` with an API client first.")
        return self._tournament


@dataclass
class RegisteredPlayerTournament:
    """Registered tournament player information."""
    url: str
    tournament_url: str
    _tournament: Optional[Tournament] = field(default=None, init=False, repr=False)
    status: str

    @classmethod
    def from_dict(cls, data: Dict) -> "RegisteredPlayerTournament":
        return cls(
            url=data["url"],
            tournament_url=data["@id"],
            status=data["status"]
        )

    async def fetch_tournament(self, client: ChessComClient) -> "Tournament":
        if self._tournament is None:
            self._tournament = await client.get_tournament(url_id=self.tournament_url.split("/")[-1])
        return self._tournament

    @property
    def tournament(self) -> "Tournament":
        if self._tournament is None:
            raise ValueError("Tournament has not been fetched. Call `fetch_tournament` with an API client first.")
        return self._tournament


@dataclass
class PlayerTournaments:
    """Chess.com player tournaments information."""
    finished: List[FinishedPlayerTournament]
    in_progress: List[InProgressPlayerTournament]
    registered: List[RegisteredPlayerTournament]

    @classmethod
    def from_dict(cls, data) -> "PlayerTournaments":
        return cls(
            finished=[FinishedPlayerTournament.from_dict(finished_player_tournament) for finished_player_tournament in
                      data["finished"]],
            in_progress=[InProgressPlayerTournament.from_dict(in_progress_player_tournament) for
                         in_progress_player_tournament in data["in_progress"]],
            registered=[RegisteredPlayerTournament.from_dict(registered_player_tournament) for
                        registered_player_tournament in
                        data["registered"]]
        )


@dataclass
class FinishedClubMatch:
    """Finished club match information."""
    name: str
    match_url: str
    _match: Optional[Match] = field(default=None, init=False, repr=False)
    opponent_url: str
    _opponent: Optional[Club] = field(default=None, init=False, repr=False)
    start_time: int
    time_class: str
    result: str

    @classmethod
    def from_dict(cls, data: Dict) -> "FinishedClubMatch":
        return cls(
            name=data["name"],
            match_url=data["@id"],
            opponent_url=data["opponent"],
            start_time=data["start_time"],
            time_class=data["time_class"],
            result=data["result"]
        )

    async def fetch_match(self, client: ChessComClient) -> "Match":
        if self._match is None:
            self._match = await client.get_match(match_id=int(self.match_url.split("/")[-1]))
        return self._match

    @property
    def match(self) -> "Match":
        if self._match is None:
            raise ValueError("Match has not been fetched. Call `fetch_match` with an API client first.")
        return self._match

    async def fetch_opponent(self, client: ChessComClient) -> "Club":
        if self._opponent is None:
            self._opponent = await client.get_club(url_id=self.opponent_url.split("/")[-1])
        return self._opponent

    @property
    def opponent(self) -> "Club":
        if self._opponent is None:
            raise ValueError("Opponent has not been fetched. Call `fetch_opponent` with an API client first.")
        return self._opponent


@dataclass
class InProgressClubMatch:
    """In-progress club match information."""
    name: str
    match_url: str
    _match: Optional[Match] = field(default=None, init=False, repr=False)
    opponent_url: str
    _opponent: Optional[Club] = field(default=None, init=False, repr=False)
    start_time: int
    time_class: str

    @classmethod
    def from_dict(cls, data: Dict) -> "InProgressClubMatch":
        return cls(
            name=data["name"],
            match_url=data["@id"],
            opponent_url=data["opponent"],
            start_time=data["start_time"],
            time_class=data["time_class"]
        )

    async def fetch_match(self, client: ChessComClient) -> "Match":
        if self._match is None:
            self._match = await client.get_match(match_id=int(self.match_url.split("/")[-1]))
        return self._match

    @property
    def match(self) -> "Match":
        if self._match is None:
            raise ValueError("Match has not been fetched. Call `fetch_match` with an API client first.")
        return self._match

    async def fetch_opponent(self, client: ChessComClient) -> "Club":
        if self._opponent is None:
            self._opponent = await client.get_club(url_id=self.opponent_url.split("/")[-1])
        return self._opponent

    @property
    def opponent(self) -> "Club":
        if self._opponent is None:
            raise ValueError("Opponent has not been fetched. Call `fetch_opponent` with an API client first.")
        return self._opponent


@dataclass
class RegisteredClubMatch:
    """Registered club match information."""
    name: str
    match_url: str
    _match: Optional[Match] = field(default=None, init=False, repr=False)
    opponent_url: str
    _opponent: Optional[Club] = field(default=None, init=False, repr=False)
    time_class: str

    @classmethod
    def from_dict(cls, data: Dict) -> "RegisteredClubMatch":
        return cls(
            name=data["name"],
            match_url=data["@id"],
            opponent_url=data["opponent"],
            time_class=data["time_class"]
        )

    async def fetch_match(self, client: ChessComClient) -> "Match":
        if self._match is None:
            self._match = await client.get_match(match_id=int(self.match_url.split("/")[-1]))
        return self._match

    @property
    def match(self) -> "Match":
        if self._match is None:
            raise ValueError("Match has not been fetched. Call `fetch_match` with an API client first.")
        return self._match

    async def fetch_opponent(self, client: ChessComClient) -> "Club":
        if self._opponent is None:
            self._opponent = await client.get_club(url_id=self.opponent_url.split("/")[-1])
        return self._opponent

    @property
    def opponent(self) -> "Club":
        if self._opponent is None:
            raise ValueError("Opponent has not been fetched. Call `fetch_opponent` with an API client first.")
        return self._opponent


@dataclass
class ClubMatches:
    """Chess.com club matches information."""
    finished: List[FinishedClubMatch]
    in_progress: List[InProgressClubMatch]
    registered: List[RegisteredClubMatch]

    @classmethod
    def from_dict(cls, data) -> "ClubMatches":
        return cls(
            finished=[FinishedClubMatch.from_dict(finished_club_match) for finished_club_match in
                      data["finished"]],
            in_progress=[InProgressClubMatch.from_dict(in_progress_club_match) for
                         in_progress_club_match in data["in_progress"]],
            registered=[RegisteredClubMatch.from_dict(registered_club_match) for registered_club_match in
                        data["registered"]]
        )


@dataclass
class Match:
    """Chess.com team match information."""
    match_url: str
    name: str
    url: str
    description: Optional[str]
    start_time: Optional[int]
    end_time: Optional[int]
    status: str
    board_count: int
    _boards: Optional[List[Board]] = field(default=None, init=False, repr=False)
    # TODO: Implement dataclass for settings
    settings: Dict
    # TODO: Implement dataclass for teams
    teams: Dict

    @classmethod
    def from_dict(cls, data: Dict) -> "Match":
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
            teams=data["teams"]
        )

    async def fetch_boards(self, client: ChessComClient) -> "List[Board]":
        self._boards = self._boards or []
        seen_boards = {board for board in self._boards}

        async def fetch_board(board_num):
            if board_num in seen_boards:
                return None
            try:
                board = await client.get_match_board(match_id=int(self.match_url.split("/")[-1]), board_num=board_num)
                seen_boards.add(board_num)
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

        self._boards.extend(filter(None, fetched_boards))
        return self._boards

    @property
    def boards(self) -> "List[Board]":
        if self._boards is None:
            raise ValueError("Boards have not been fetched. Call `fetch_boards` with an API client first.")
        return self._boards


@dataclass
class Country:
    """Chess.com country information."""
    code: str
    name: str

    @classmethod
    def from_dict(cls, data: Dict) -> "Country":
        return cls(
            code=data["code"],
            name=data["name"]
        )


@dataclass
class DailyPuzzle:
    """Chess.com daily puzzle information."""
    title: str
    url: str
    publish_time: int
    fen: str
    pgn: str
    image: str

    @classmethod
    def from_dict(cls, data: Dict) -> "DailyPuzzle":
        return cls(
            title=data["title"],
            url=data["url"],
            publish_time=data["publish_time"],
            fen=data["fen"],
            pgn=data["pgn"],
            image=data["image"]
        )


@dataclass
class Streamer:
    """Chess.com streamer information."""
    username: str
    avatar: str
    twitch_url: str
    url: str
    is_live: bool
    is_community_streamer: bool
    platforms: List[Dict]

    @classmethod
    def from_dict(cls, data: Dict) -> "Streamer":
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
                    "is_main_live_platform": platform.get("is_main_live_platform", False),
                }
                for platform in data.get("platforms", [])  # Iterate through `platforms`
            ]
        )


@dataclass
class LeaderboardEntry:
    """Chess.com leaderboard entry."""
    player_id: int
    username: str
    score: int
    rank: int
    url: str

    @classmethod
    def from_dict(cls, data: Dict) -> "LeaderboardEntry":
        return cls(
            player_id=data["player_id"],
            username=data["username"],
            score=data["score"],
            rank=data["rank"],
            url=data["url"]
        )


@dataclass
class Leaderboard:
    """Chess.com complete leaderboard."""
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
    def from_dict(cls, data: Dict) -> "Leaderboard":
        return cls(
            daily=[LeaderboardEntry.from_dict(entry) for entry in data.get("daily", [])],
            daily960=[LeaderboardEntry.from_dict(entry) for entry in data.get("daily960", [])],
            live_rapid=[LeaderboardEntry.from_dict(entry) for entry in data.get("live_rapid", [])],
            live_blitz=[LeaderboardEntry.from_dict(entry) for entry in data.get("live_blitz", [])],
            live_bullet=[LeaderboardEntry.from_dict(entry) for entry in data.get("live_bullet", [])],
            live_bughouse=[LeaderboardEntry.from_dict(entry) for entry in data.get("live_bughouse", [])],
            live_blitz960=[LeaderboardEntry.from_dict(entry) for entry in data.get("live_blitz960", [])],
            live_threecheck=[LeaderboardEntry.from_dict(entry) for entry in data.get("live_threecheck", [])],
            live_crazyhouse=[LeaderboardEntry.from_dict(entry) for entry in data.get("live_crazyhouse", [])],
            live_kingofthehill=[LeaderboardEntry.from_dict(entry) for entry in data.get("live_kingofthehill", [])],
            lessons=[LeaderboardEntry.from_dict(entry) for entry in data.get("lessons", [])],
            tactics=[LeaderboardEntry.from_dict(entry) for entry in data.get("tactics", [])]
        )
