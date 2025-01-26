
RESERVATIONS_DB = {
    "Joanna Szych": "3 reservations: Monday 6PM, Wednesday 8PM, Friday 5PM",
    "Monica Geller": "1 reservation: Tuesday 4PM", 
}

def check_reservations_in_db(full_name):
    if full_name in RESERVATIONS_DB.keys():
        current_reservations = RESERVATIONS_DB.get(full_name)
        return f"Here is the list of reservations for {full_name}: {current_reservations}"
    else:
        return f"There are currently no reservations for {full_name}"