Project 3 – Flight Route and Fare Comparator

Name: Prachi Raj Bhandari
Student ID: 2412053

This project implements a command-line flight planning system that compares different travel options between two airports. The system reads flight schedule data, builds a graph of airports and flights, and computes optimal itineraries based on time and cost constraints.

The program is designed as a Python CLI tool and focuses on correct data structures, graph traversal, and algorithmic reasoning rather than UI or real-world booking systems.

Project Overview

The flight planner supports the following features:

Reading flight schedules from text or CSV files

Building a directed graph of airports and flights

Finding the earliest arrival itinerary

Finding the cheapest itinerary for:

Economy

Business

First class

Enforcing minimum layover constraints

Printing a readable comparison table

Fully tested using pytest

All flights are assumed to occur on the same day.

Input Data Format

The program supports two formats.

Text file format (space separated):

ORIGIN DEST FLIGHT_NUMBER DEPART ARRIVE ECONOMY BUSINESS FIRST

Example:
ICN NRT FW101 08:00 10:00 300 800 1500

CSV file format:

origin,dest,flight_number,depart,arrive,economy,business,first

Example:
ICN,NRT,FW101,08:00,10:00,300,800,1500

Blank lines and lines starting with # are ignored.

Data Structures Used

Graph representation:

Airports are nodes

Flights are directed edges

Implemented using an adjacency list:
dict mapping airport code to a list of outgoing Flight objects

Hash tables are used for:

Graph adjacency lists

Tracking best arrival times

Tracking cheapest costs

Reconstructing itineraries

Algorithms

Earliest arrival search:

Uses a priority queue

Optimizes by arrival time

Enforces earliest departure and minimum layover constraints

Cheapest itinerary search:

Uses a priority queue

Optimizes by total cost for a selected cabin

Still enforces all time and layover constraints

Both searches are Dijkstra-style shortest path algorithms adapted for flight scheduling.

Time and Space Complexity

Building the graph:

Time complexity: O(N)

Space complexity: O(N)
Where N is the number of flights.

Earliest arrival search:

Time complexity: O(E log V)

Space complexity: O(V)
Where V is the number of airports and E is the number of flights.

Cheapest itinerary search:

Time complexity: O(E log V)

Space complexity: O(V)

Command Line Usage

Run the comparison command as follows:

python flight_planner.py compare FLIGHT_FILE ORIGIN DEST DEPARTURE_TIME

Example:

python flight_planner.py compare data/flights_global.txt ICN SFO 08:00

This prints a comparison table showing:

Earliest arrival itinerary

Cheapest economy itinerary

Cheapest business itinerary

Cheapest first class itinerary

If no valid itinerary exists, the output clearly indicates that case.

Testing

The project includes a full pytest test suite covering:

Time parsing and formatting

Flight file parsing

Graph construction

Earliest arrival search

Cheapest itinerary search

Output formatting

End-to-end CLI execution

To run all tests:

pytest -q

A pytest.ini file is included so tests run without additional environment variables.

Project Status

All tests pass successfully.
The CLI runs correctly.
The project meets all assignment requirements.

This submission represents the final and complete version of Project 3.