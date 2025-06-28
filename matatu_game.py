# matatu_game.py

class Matatu:
    def __init__(self, name: str, capacity: int = 14, speed_level: int = 1,
                 fare_bonus_level: int = 1, maintenance_level: int = 1):
        self.name: str = name
        self.route: 'Route' | None = None  # Forward declaration for type hint
        self.capacity: int = capacity
        self.speed_level: int = speed_level  # Higher is faster
        self.fare_bonus_level: int = fare_bonus_level # Higher means more fare
        self.maintenance_level: int = maintenance_level # Higher means less breakdown chance (feature for later)

        self.is_on_trip: bool = False
        self.trip_turns_remaining: int = 0

    def __str__(self) -> str:
        route_name = self.route.name if self.route else "Not assigned"
        status = f"On trip ({self.trip_turns_remaining} turns left)" if self.is_on_trip else "Idle"
        return (f"Matatu: {self.name} | Capacity: {self.capacity} | Speed: Lvl {self.speed_level} | "
                f"Fare Bonus: Lvl {self.fare_bonus_level} | Maintenance: Lvl {self.maintenance_level} | "
                f"Route: {route_name} | Status: {status}")

class Route:
    def __init__(self, name: str, base_duration: int, base_fare_per_passenger: int,
                 available_in_locations: list[str]):
        self.name: str = name
        self.base_duration: int = base_duration  # In turns
        self.base_fare_per_passenger: int = base_fare_per_passenger
        self.available_in_locations: list[str] = available_in_locations

    def __str__(self) -> str:
        return (f"Route: {self.name} | Duration: {self.base_duration} turns | "
                f"Base Fare: KES {self.base_fare_per_passenger}/passenger | "
                f"Starts From: {', '.join(self.available_in_locations)}")

class Player:
    def __init__(self, starting_money: int, starting_location: str):
        self.money: int = starting_money
        self.matatus: list[Matatu] = []
        self.current_location: str = starting_location

    def __str__(self) -> str:
        matatu_names = [m.name for m in self.matatus] if self.matatus else ["None"]
        return (f"Player Status: Money: KES {self.money} | Location: {self.current_location} | "
                f"Matatus: {', '.join(matatu_names)}")

# --- Constants for game setup ---
INITIAL_MONEY = 5000
INITIAL_LOCATION = "Rongai"
STARTING_MATATU_NAME = "KCK 001A"

# --- Game Data ---
AVAILABLE_ROUTES: list[Route] = []

def setup_new_game() -> tuple[Player, list[Route]]:
    """Initializes a new game state."""
    player = Player(starting_money=INITIAL_MONEY, starting_location=INITIAL_LOCATION)

    # Create the first matatu for the player
    # Ensure fare_bonus_level is set, e.g. in Matatu constructor default or here
    first_matatu = Matatu(name=STARTING_MATATU_NAME, capacity=14, speed_level=1, fare_bonus_level=1)
    player.matatus.append(first_matatu)

    AVAILABLE_ROUTES.clear()
    AVAILABLE_ROUTES.extend([
        Route(name="Rongai - City Centre", base_duration=5, base_fare_per_passenger=100, available_in_locations=["Rongai"]),
        Route(name="Umoja - CBD", base_duration=4, base_fare_per_passenger=70, available_in_locations=["Umoja"]),
        Route(name="Kayole - OTC", base_duration=6, base_fare_per_passenger=50, available_in_locations=["Kayole"]),
        Route(name="BuruBuru - Westlands", base_duration=5, base_fare_per_passenger=80, available_in_locations=["BuruBuru"]),
    ])

    print("Welcome to Matatu Fleet Manager!")
    print(f"You are starting in {player.current_location} with KES {player.money}.")
    print(f"Your first matatu is {first_matatu.name}.")

    return player, AVAILABLE_ROUTES

# --- Action functions ---
def view_matatus(player: Player):
    print("\n--- Your Matatus ---")
    if not player.matatus:
        print("You don't own any matatus yet.")
        return
    for i, matatu in enumerate(player.matatus):
        print(f"{i+1}. {matatu}")

def view_routes(player: Player, all_routes: list[Route]):
    print("\n--- Available Routes from Your Location ---")
    routes_from_location = [r for r in all_routes if player.current_location in r.available_in_locations]
    if not routes_from_location:
        print(f"No routes available from {player.current_location} at the moment.")
        return
    for i, route in enumerate(routes_from_location):
        print(f"{i+1}. {route}")

def assign_matatu_to_route(player: Player, all_routes: list[Route]):
    print("\n--- Assign Matatu to Route ---")

    if not player.matatus:
        print("You don't own any matatus yet.")
        return

    print("Select a Matatu to assign/re-assign a route:")
    # List only idle matatus or all? For now, list all and prevent if on trip.
    for i, matatu in enumerate(player.matatus):
        status = "On Trip" if matatu.is_on_trip else "Idle"
        current_route_name = matatu.route.name if matatu.route else "None"
        print(f"{i+1}. {matatu.name} (Status: {status}, Current Route: {current_route_name})")

    selected_matatu = None
    try:
        matatu_choice_input = input("Enter number of matatu to assign (or 0 to cancel): ")
        if not matatu_choice_input: # Handle empty input
            print("No selection made. Returning to menu.")
            return
        matatu_choice_idx = int(matatu_choice_input) - 1

        if matatu_choice_idx == -1: # User chose 0 to cancel
            print("Operation cancelled.")
            return

        if not (0 <= matatu_choice_idx < len(player.matatus)):
            print("Invalid matatu choice.")
            return

        selected_matatu = player.matatus[matatu_choice_idx]

        if selected_matatu.is_on_trip:
            print(f"{selected_matatu.name} is currently on a trip and cannot be re-assigned a route now.")
            return # Exit the function

    except ValueError:
        print("Invalid input. Please enter a number for matatu selection.")
        return
    except Exception as e: # Catch any other unexpected error
        print(f"An unexpected error occurred during matatu selection: {e}")
        return

    # If we reach here, selected_matatu should be a valid, idle matatu object
    if not selected_matatu: # Should not happen if logic above is correct
        print("Error selecting matatu. Please try again.")
        return

    # --- Route Selection ---
    print(f"\nAvailable routes from your current location ({player.current_location}):")

    # Filter routes based on player's current location
    eligible_routes = [r for r in all_routes if player.current_location in r.available_in_locations]

    if not eligible_routes:
        print(f"No routes available from {player.current_location}. You might need to travel or check route definitions.")
        return

    for i, route in enumerate(eligible_routes):
        print(f"{i+1}. {route.name} (Duration: {route.base_duration} turns, Fare/Pax: {route.base_fare_per_passenger})")

    try:
        route_choice_input = input(f"Choose a route for {selected_matatu.name} (enter number, or 0 to cancel): ")
        if not route_choice_input: # Handle empty input
            print("No route selection made. Assignment cancelled.")
            return
        route_choice_idx = int(route_choice_input) - 1

        if route_choice_idx == -1: # User chose 0 to cancel
            print("Route assignment cancelled.")
            return

        if not (0 <= route_choice_idx < len(eligible_routes)):
            print("Invalid route choice.")
            return

        selected_route = eligible_routes[route_choice_idx]
        selected_matatu.route = selected_route # Assign the actual Route object
        print(f"{selected_matatu.name} has been assigned to route: {selected_route.name}.")

    except ValueError:
        print("Invalid input. Please enter a number for route selection.")
    except Exception as e: # Catch any other unexpected error
        print(f"An unexpected error occurred during route selection: {e}")


def start_matatu_trip(player: Player):
    print("\n--- Start Matatu Trip ---")

    idle_matatus_with_route = []
    for m in player.matatus:
        if not m.is_on_trip and m.route:
            idle_matatus_with_route.append(m)

    if not idle_matatus_with_route:
        print("No matatus are currently idle AND assigned to a route.")
        print("Use 'Assign Matatu to Route' first if needed.")
        return

    print("Available Matatus to start trip (must be idle and have a route):")
    for i, matatu in enumerate(idle_matatus_with_route):
        # Ensure matatu.route is not None before accessing matatu.route.name
        route_name_display = matatu.route.name if matatu.route else "N/A"
        print(f"{i+1}. {matatu.name} (Route: {route_name_display})")

    try:
        choice_input = input("Choose a matatu to start trip (enter number, or 0 to cancel): ")
        if not choice_input: # Handle empty input
            print("No selection made. Returning to menu.")
            return

        choice_idx = int(choice_input) - 1

        if choice_idx == -1: # User entered 0 to cancel
            print("Operation cancelled.")
            return

        if 0 <= choice_idx < len(idle_matatus_with_route):
            selected_matatu = idle_matatus_with_route[choice_idx]

            # This check is technically redundant due to how idle_matatus_with_route is populated
            # but it's a good safeguard.
            if selected_matatu.route:
                # Calculate trip duration, adjusted by speed_level
                # Higher speed_level reduces duration. Level 1 is base.
                # Example: Level 1 = 0% reduction, Level 2 = 10% reduction, Level 3 = 20%
                # Max reduction capped at, say, 50% (speed_level 6). Min duration 1 turn.
                speed_reduction_percentage = min((selected_matatu.speed_level - 1) * 0.1, 0.5)
                duration_modifier = 1 - speed_reduction_percentage

                # Ensure base_duration is accessed correctly from the route object
                calculated_duration = selected_matatu.route.base_duration * duration_modifier
                selected_matatu.trip_turns_remaining = max(1, int(round(calculated_duration)))

                selected_matatu.is_on_trip = True

                print(f"{selected_matatu.name} is now on its way via route '{selected_matatu.route.name}'.")
                print(f"Estimated trip duration: {selected_matatu.trip_turns_remaining} turns.")
            else:
                # This state should ideally not be reached if logic for idle_matatus_with_route is correct
                print("Error: Selected matatu does not have a route, though it appeared in the list. Please assign one first.")
        else:
            print("Invalid choice number.")
    except ValueError:
        print("Invalid input. Please enter a number.")
    except Exception as e: # Catch any other unexpected errors during selection
        print(f"An unexpected error occurred: {e}")

def visit_workshop(player: Player):
    print("\n--- Workshop ---")
    print("The workshop is not yet open for business.")
    print("Future upgrades and matatu purchases will be available here.")
    print("(Coming Soon!)")
    # Actual implementation in a later step

def advance_day(player: Player, all_routes: list[Route]): # all_routes might be used later for events
    print("\n--- Advancing Day ---")

    trips_completed_this_turn = 0
    earnings_this_turn = 0

    if not player.matatus:
        print("You have no matatus to advance.")
        return

    for matatu in player.matatus:
        if matatu.is_on_trip:
            matatu.trip_turns_remaining -= 1
            print(f"{matatu.name} is on its route. {matatu.trip_turns_remaining} turns remaining.")

            if matatu.trip_turns_remaining <= 0:
                # Trip completed
                if matatu.route: # Should always have a route if on trip, but good to check
                    # Earnings calculation
                    trip_earnings_base = matatu.capacity * matatu.route.base_fare_per_passenger

                    # Apply fare bonus (e.g., each level adds 10% to base fare, level 1 is no bonus)
                    fare_bonus_multiplier = 1 + ((matatu.fare_bonus_level - 1) * 0.1)
                    actual_earnings = int(trip_earnings_base * fare_bonus_multiplier)

                    player.money += actual_earnings
                    earnings_this_turn += actual_earnings
                    trips_completed_this_turn += 1

                    print(f"SUCCESS! {matatu.name} completed its trip on route '{matatu.route.name}'.")
                    print(f"Earned KES {actual_earnings}.")

                    matatu.is_on_trip = False
                    # Matatu keeps its assigned route, just becomes idle
                else:
                    # This case should ideally not happen if logic is correct
                    print(f"ERROR: {matatu.name} was on a trip but had no route assigned upon completion.")
                    matatu.is_on_trip = False
        # else:
            # Matatu is idle, do nothing for it in advance_day unless we add parking fees etc. later

    if trips_completed_this_turn > 0:
        print(f"\nTotal earnings this turn: KES {earnings_this_turn}.")
    else:
        # Check if there are any matatus at all, and if any are on trips
        has_matatus = bool(player.matatus)
        active_trips = any(m.is_on_trip for m in player.matatus)

        if has_matatus and not active_trips:
            print("No matatus are currently on a trip.")
        elif active_trips: # Implies has_matatus is true
            print("No trips completed this turn, but some are still ongoing.")
        # If not has_matatus, the message "You have no matatus to advance." from the start of the function covers it.

    print("Day advanced.")


def main_game_loop():
    """Main loop for the game."""
    player, all_routes = setup_new_game()

    running = True
    while running:
        print("\n" + "="*30)
        print(player) # Display player status
        print("="*30)
        print("\nWhat would you like to do?")
        print("1. View Your Matatus")
        print("2. View Available Routes (from current location)")
        print("3. Assign Matatu to Route")
        print("4. Start Matatu Trip")
        print("5. Visit Workshop")
        print("6. Advance Day (Simulate)")
        print("0. Exit Game")

        choice = input("Enter your choice: ")

        if choice == '1':
            view_matatus(player)
        elif choice == '2':
            view_routes(player, all_routes)
        elif choice == '3':
            assign_matatu_to_route(player, all_routes) # Pass all_routes
        elif choice == '4':
            start_matatu_trip(player)
        elif choice == '5':
            visit_workshop(player)
        elif choice == '6':
            advance_day(player, all_routes) # Pass all_routes
        elif choice == '0':
            print("Thanks for playing Matatu Fleet Manager!")
            running = False
        else:
            print("Invalid choice. Please try again.")

        if running:
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    main_game_loop()
