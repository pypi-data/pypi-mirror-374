import asyncio
from pyltover import Pyltover


with open(".devkey", "r") as f:
    token = f.read()


async def main():
    pyltover = Pyltover(token)
    await pyltover.init_champions_db()

    resp = await pyltover.euw1.v4.get_total_champion_mastery_score(
        "iyPYkvZg9bA-vnOKhE1ADcmkT6Z89VwQuxm_t9lHJZg-8PDDHqa1ASGzmiobXJ7Pu8wD3ZbqMuHcsw"
    )
    # print(resp)

    resp = await pyltover.europe.v1.get_account_by_riot_id("EUNE", "SoltanSoren")
    # print(resp)

    resp = await pyltover.europe.v5.get_list_of_match_ids_by_puuid(
        "iyPYkvZg9bA-vnOKhE1ADcmkT6Z89VwQuxm_t9lHJZg-8PDDHqa1ASGzmiobXJ7Pu8wD3ZbqMuHcsw"
    )
    # print(resp)
    for g in resp:
        resp = await pyltover.europe.v5.get_match_by_id(g)
        team1f = False
        team2f = False
        team_1_pings = 0
        team_2_pings = 0
        for p in resp.info.participants:
            if p.team_id == 100 and team1f is False:
                print("Team 1:")
                team1f = True
            elif p.team_id == 200 and team2f is False:
                print("Team 2:")
                team2f = True

            pings = (
                p.hold_pings
                + p.push_pings
                + p.all_in_pings
                + p.command_pings
                + p.get_back_pings
                + p.assist_me_pings
                + p.on_my_way_pings
                + p.need_vision_pings
                + p.enemy_vision_pings
                + p.enemy_missing_pings
                + p.vision_cleared_pings
            )
            if p.team_id == 100:
                team_1_pings += pings
            elif p.team_id == 200:
                team_2_pings += pings
            print(p.riot_id_game_name, "won" if p.win else "lost", pings)

        for t in resp.info.teams:
            if t.win:
                winner = t.team_id
                break

        print(f"winner: {winner // 100}")
        print("team 1 total pings: ", team_1_pings)
        print("team 2 total pings: ", team_2_pings)
        print("-------------------------------")
        print("-------------------------------")
        print("-------------------------------")


asyncio.run(main())
