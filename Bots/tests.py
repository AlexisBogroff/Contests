from coding_game_2bots import *
print('\n'*10)

# ==========================================
#               MAIN DEBUG
# ==========================================

if __name__ == '__main__':
    # n laps
    input1 = 10
    # cp count
    input2 = "2"
    # cps positions
    input3 = ["14517 7786", "14517 7786"]
    # state info
    input4 = [
        "11343 6317 0 0 25 1",
        "14517 6786 3000 2000 1 1",
        "11343 6317 0 0 80 1",
    ]

    # Instanciate classes
    env = Env(debug = True)
    #pods = [Pod(), Pod()]
    #opponents = [Opponent(), Opponent()]
    pods = [Pod(debug = True)]
    opponents = []

    # Retrieve game init information
    env.set_laps(input1)
    env.set_cp_count(input2)
    env.set_cps_lists(input3)

    # Identify map structures
    #env.analyze_map()
    for agent in pods + opponents:
        agent.init_history()

    game_iter = 0

    # game loop
    while game_iter < 3:
        
        game_iter += 1
        print('\n\nNext iter:', game_iter)

        # Update state variables
        for agent in pods + opponents:
            agent.update_state_info(input4[game_iter - 1], env)

        # Select and set strategy
        for pod in pods:
            pod.evaluate_strategy()

        # Execute strat
        for pod in pods:
            pod.do_strat()
            pod.dispaly_infos()

        for pod in pods:
            pod.append_history()
