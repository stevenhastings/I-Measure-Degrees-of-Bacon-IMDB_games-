import csv
import sys
import pandas as pd
import time

from util import StackFrontier, QueueFrontier
from util import  Node

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass

actors = pd.read_csv("DATA\\actors.csv")
peeps = pd.read_csv("DATA\\people.csv")

def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "DATA"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    samp = actors['Name'].sample()
    sampler = samp.values
    target = person_id_for_name(input(f"Enter my pick please: {sampler[0]}: "))
    # target = person_id_for_name(sampler[0])
    if target is None:
        sys.exit("Person not found.")
    if target == '?':
        sys.exit("Person not known")

    # print(peeps[peeps['name'] == source], peeps[peeps['name'] == target])
    time.sleep(15)

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"Here's a hint. . . there are only {degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in. . .")
            answer = input("what movie? ")
            # time.sleep(10)
            if answer == movie:
                print("Well done!")
            else:

                print(f"the answer we were looking for was: {movie}")

            




def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
    solution_found = False
    no_solution = False
    solution = list()

    initial = Node(state=source, parent=None, action=None)
    frontier = QueueFrontier()
    frontier.add(initial)
    explored = set()
    i = 0
    while solution_found == False:

        if frontier.empty() == True:
            no_solution = True
            solution_found = True
        
        node = frontier.remove()
        # print("\n\nNode in= ",node, ' i=', i)

        if node.state == target:
            # Return the solution
            solution_found = True
            while node.parent is not None:
                pid, mid = node.state, node.action
                solution.append((mid, pid))
                node = node.parent
            solution.reverse()

        explored.add(node)
        children = neighbors_for_person(node.state)
        for child in children:
            child_node = Node(state=child[1], action=child[0],parent=node)
            frontier.add(child_node)
            if child_node.state == target:
                # Return the solution
                solution_found = True
                while child_node.parent is not None:
                    pid, mid = child_node.state, child_node.action
                    solution.append((mid, pid))
                    child_node = child_node.parent
                solution.reverse()
    
    if solution_found == True:
        if no_solution == True:
            return None
        return solution


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
