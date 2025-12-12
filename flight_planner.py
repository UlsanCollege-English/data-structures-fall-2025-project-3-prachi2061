from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Literal, Optional
import heapq

MIN_LAYOVER_MINUTES = 60
Cabin = Literal["economy", "business", "first"]


@dataclass(frozen=True)
class Flight:
    origin: str
    dest: str
    flight_number: str
    depart: int
    arrive: int
    economy: int
    business: int
    first: int

    def price_for(self, cabin: Cabin) -> int:
        if cabin == "economy":
            return self.economy
        if cabin == "business":
            return self.business
        if cabin == "first":
            return self.first
        raise ValueError


@dataclass
class Itinerary:
    flights: List[Flight]

    def is_empty(self) -> bool:
        return not self.flights

    @property
    def origin(self) -> Optional[str]:
        if not self.flights:
            return None
        return self.flights[0].origin

    @property
    def dest(self) -> Optional[str]:
        if not self.flights:
            return None
        return self.flights[-1].dest

    @property
    def depart_time(self) -> Optional[int]:
        if not self.flights:
            return None
        return self.flights[0].depart

    @property
    def arrive_time(self) -> Optional[int]:
        if not self.flights:
            return None
        return self.flights[-1].arrive

    def total_price(self, cabin: Cabin) -> int:
        return sum(f.price_for(cabin) for f in self.flights)

    def num_stops(self) -> int:
        return max(0, len(self.flights) - 1)


Graph = Dict[str, List[Flight]]


def parse_time(hhmm: str) -> int:
    h, m = hhmm.split(":")
    h = int(h)
    m = int(m)
    if not (0 <= h < 24 and 0 <= m < 60):
        raise ValueError
    return h * 60 + m


def format_time(minutes: int) -> str:
    h = minutes // 60
    m = minutes % 60
    return f"{h:02d}:{m:02d}"


def parse_flight_line_txt(line: str) -> Optional[Flight]:
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    parts = line.split()
    if len(parts) != 8:
        raise ValueError
    origin, dest, num, de, ar, e, b, f = parts
    depart = parse_time(de)
    arrive = parse_time(ar)
    if arrive <= depart:
        raise ValueError
    return Flight(origin, dest, num, depart, arrive, int(e), int(b), int(f))


def load_flights_txt(path: str) -> List[Flight]:
    flights = []
    with open(path) as file:
        for i, line in enumerate(file, 1):
            try:
                f = parse_flight_line_txt(line)
                if f:
                    flights.append(f)
            except Exception as e:
                raise ValueError(f"{path}:{i}: {e}")
    return flights


def load_flights_csv(path: str) -> List[Flight]:
    flights = []
    with open(path) as file:
        reader = csv.DictReader(file)
        req = ["origin", "dest", "flight_number", "depart", "arrive", "economy", "business", "first"]
        for r in req:
            if r not in reader.fieldnames:
                raise ValueError
        for row in reader:
            dep = parse_time(row["depart"])
            arr = parse_time(row["arrive"])
            if arr <= dep:
                raise ValueError
            flights.append(
                Flight(
                    row["origin"],
                    row["dest"],
                    row["flight_number"],
                    dep,
                    arr,
                    int(row["economy"]),
                    int(row["business"]),
                    int(row["first"]),
                )
            )
    return flights


def load_flights(path: str) -> List[Flight]:
    if Path(path).suffix.lower() == ".csv":
        return load_flights_csv(path)
    return load_flights_txt(path)


def build_graph(flights: Iterable[Flight]) -> Graph:
    graph: Graph = {}
    for f in flights:
        graph.setdefault(f.origin, []).append(f)
    return graph


def reconstruct_itinerary(prev: Dict[str, Flight], dest: str) -> Itinerary:
    path = []
    cur = dest
    while cur in prev:
        fl = prev[cur]
        path.append(fl)
        cur = fl.origin
    path.reverse()
    return Itinerary(path)


def find_earliest_itinerary(graph: Graph, start: str, dest: str, earliest_departure: int) -> Optional[Itinerary]:
    dist = {}
    prev: Dict[str, Flight] = {}
    pq = [(earliest_departure, start)]
    dist[start] = earliest_departure
    visited = set()

    while pq:
        cur_time, airport = heapq.heappop(pq)
        if airport in visited:
            continue
        visited.add(airport)
        if airport == dest:
            return reconstruct_itinerary(prev, dest)
        for f in graph.get(airport, []):
            required = cur_time if airport == start else cur_time + MIN_LAYOVER_MINUTES
            if f.depart >= required:
                if f.dest not in dist or f.arrive < dist[f.dest]:
                    dist[f.dest] = f.arrive
                    prev[f.dest] = f
                    heapq.heappush(pq, (f.arrive, f.dest))
    return None


def find_cheapest_itinerary(graph: Graph, start: str, dest: str, earliest_departure: int, cabin: Cabin) -> Optional[Itinerary]:
    dist = {}
    prev: Dict[str, Flight] = {}
    pq = [(0, earliest_departure, start)]
    dist[start] = 0
    visited = set()

    while pq:
        cost, arr_time, airport = heapq.heappop(pq)
        if (airport, cost) in visited:
            continue
        visited.add((airport, cost))
        if airport == dest:
            return reconstruct_itinerary(prev, dest)
        for f in graph.get(airport, []):
            earliest_allowed = arr_time if airport == start else arr_time + MIN_LAYOVER_MINUTES
            if f.depart >= earliest_allowed:
                new_cost = cost + f.price_for(cabin)
                if f.dest not in dist or new_cost < dist[f.dest]:
                    dist[f.dest] = new_cost
                    prev[f.dest] = f
                    heapq.heappush(pq, (new_cost, f.arrive, f.dest))
    return None


@dataclass
class ComparisonRow:
    mode: str
    cabin: Optional[Cabin]
    itinerary: Optional[Itinerary]
    note: str = ""


def format_comparison_table(
    origin: str,
    dest: str,
    earliest_departure: int,
    rows: List[ComparisonRow],
) -> str:
    lines = []
    lines.append(f"{origin} -> {dest}")

    header = "Mode | Cabin | Dep | Arr | Duration | Stops | Total Price | Note"
    lines.append(header)
    lines.append("-" * len(header))

    for r in rows:
        if r.itinerary is None:
            lines.append(
                f"{r.mode} | {r.cabin or 'N/A'} | N/A | N/A | N/A | N/A | N/A | {r.note}"
            )
            continue

        dep = format_time(r.itinerary.depart_time)
        arr = format_time(r.itinerary.arrive_time)
        dur = r.itinerary.arrive_time - r.itinerary.depart_time
        dh = dur // 60
        dm = dur % 60
        duration = f"{dh}h{dm:02d}m"
        stops = r.itinerary.num_stops()
        price = r.itinerary.total_price(r.cabin) if r.cabin else "N/A"

        lines.append(
            f"{r.mode} | {r.cabin or 'N/A'} | {dep} | {arr} | {duration} | {stops} | {price} | {r.note}"
        )

    return "\n".join(lines)


def run_compare(args: argparse.Namespace) -> None:
    earliest = parse_time(args.departure_time)
    flights = load_flights(args.flight_file)
    graph = build_graph(flights)

    it1 = find_earliest_itinerary(graph, args.origin, args.dest, earliest)
    it2 = find_cheapest_itinerary(graph, args.origin, args.dest, earliest, "economy")
    it3 = find_cheapest_itinerary(graph, args.origin, args.dest, earliest, "business")
    it4 = find_cheapest_itinerary(graph, args.origin, args.dest, earliest, "first")

    rows = [
        ComparisonRow("Earliest arrival", None, it1, "" if it1 else "(no valid itinerary)"),
        ComparisonRow("Cheapest | economy", "economy", it2, "" if it2 else "(no valid itinerary)"),
        ComparisonRow("Cheapest | business", "business", it3, "" if it3 else "(no valid itinerary)"),
        ComparisonRow("Cheapest | first", "first", it4, "" if it4 else "(no valid itinerary)"),
    ]

    print(format_comparison_table(args.origin, args.dest, earliest, rows))


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="FlyWise — Flight Route & Fare Comparator.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    compare_parser = subparsers.add_parser("compare")
    compare_parser.add_argument("flight_file")
    compare_parser.add_argument("origin")
    compare_parser.add_argument("dest")
    compare_parser.add_argument("departure_time")
    compare_parser.set_defaults(func=run_compare)

    return parser


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
