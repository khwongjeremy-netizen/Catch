import time

def get_group_data():
    """Phase 1: Manually inputting the state of the group."""
    print("--- SETUP: SYNC STUDY GROUP DATA ---")
    
    # 1. User Setup
    user_name = input("Enter your name: ")
    user_on_device = input("Is your device on? (y/n): ").lower() == 'y'
    user_studying = input("Are you currently studying? (y/n): ").lower() == 'y'
    user_hours = float(input("How many hours have you studied today?: "))
    
    # 2. Friends Setup
    num_friends = int(input("\nHow many friends are in your group?: "))
    friends_list = []
    
    for i in range(num_friends):
        print(f"\n--- Friend #{i+1} ---")
        f_name = input("Friend's name: ")
        f_studying = input(f"Is {f_name} currently studying? (y/n): ").lower() == 'y'
        f_hours = float(input(f"How many hours has {f_name} studied today?: "))
        
        friends_list.append({
            "name": f_name,
            "is_studying": f_studying,
            "study_hours": f_hours
        })

    # Pack it into the structure
    return {
        "user": {
            "name": user_name,
            "is_studying": user_studying,
            "device_on": user_on_device,
            "study_hours": user_hours
        },
        "friends": friends_list
    }

def update_logic(group_data):
    """Phase 2: The Logic Engine (Processing the data)"""
    user = group_data["user"]
    friends = group_data["friends"]

    # 1. CHECK: Is anyone else working?
    anyone_else_studying = any(f["is_studying"] for f in friends)
    
    # 2. CHECK: Is the user stalling?
    user_is_stalling = user["device_on"] and not user["is_studying"]

    # 3. RESULT: The Core Boolean
    send_notification = anyone_else_studying and user_is_stalling

    # 4. STATS: Calculating the Group Dynamics
    all_hours = [f["study_hours"] for f in friends]
    
    if all_hours:
        group_avg = sum(all_hours) / len(all_hours)
        leader_hours = max(all_hours)
        study_gap = leader_hours - user["study_hours"]
    else:
        group_avg, study_gap = 0, 0

    # 5. OUTPUT
    print(f"\n--- FINAL LOGIC REPORT ---")
    print(f"User Stalling: {user_is_stalling}")
    print(f"Friends Active: {anyone_else_studying}")
    print(f">>> SEND NOTIFICATION: {send_notification} <<<")
    print(f"Group Avg: {group_avg:.2f}h | Gap from Leader: {study_gap:.2f}h")
    
    if send_notification:
        print("ACTION: Trigger annoying messages now.")

# --- EXECUTION ---
if __name__ == "__main__":
    # Get the data from user input
    current_group_data = get_group_data()
    
    # Run the logic once based on that input
    update_logic(current_group_data)