import datetime
import asyncio
import my_gspread
import pro_eu_registration

from pro_eu_static_variables import schedule_log_channel_id, sign_in_channel_id, role_tier_one_id, role_tier_two_id, guild_id, client

pro_eu_teams_channel_id = 590184107124850688
cap_news_channel_id = 613372129618165761

role_team_captain_id = 627137347028254730

def get_hour_and_minute() -> list:
    # return a list of current hour and minute
    hour = datetime.datetime.now().hour
    minute = datetime.datetime.now().minute

    return [hour, minute]


async def give_role_text_channel_permissions(role_id, text_channel_id, **permissions):
    guild = await client.fetch_guild(guild_id)
    target_role = guild.get_role(role_id)
    target_channel = client.get_channel(text_channel_id)

    await target_channel.set_permissions(target_role, **permissions)

async def give_tier_send_messages_permission(role_id):
    await give_role_text_channel_permissions(role_id, sign_in_channel_id, read_messages=True, send_messages=True,
                                             read_message_history=True)

async def take_tier_send_messages_permission(role_id):
    await give_role_text_channel_permissions(role_id, sign_in_channel_id, read_messages=True, send_messages=False,
                                             read_message_history=True)

async def unlock_pro_eu_teams_channel(role_id):
    await give_role_text_channel_permissions(role_id, pro_eu_teams_channel_id, read_messages=True, send_message=True,
                                             read_message_history=True)

async def lock_pro_eu_teams_channel(role_id):
    await give_role_text_channel_permissions(role_id, pro_eu_teams_channel_id, read_messages=True, send_messages=False,
                                             read_message_history=True)

async def auto_lock_unlock_main():
    print("Starting loop for auto (un)lock.")
    await client.wait_until_ready()

    while True:

        now = get_hour_and_minute()
        hour = now[0]
        minute = now[1]
        weekday_index = datetime.datetime.today().weekday()

        # unlocking for tier 1
        if hour == 11 and minute == 0 and weekday_index != 5:
            print("schedule unlock")
            schedule_log_channel = client.get_channel(schedule_log_channel_id)
            sign_in_channel = client.get_channel(sign_in_channel_id)

            await schedule_log_channel.send("Executing automatic unlock for tier 1...")

            my_gspread.refresh_google_tokens()
            answer = "Resetting the sign ups ..."

            await schedule_log_channel.send(answer)

            pro_eu_registration.delete_column(my_gspread.signed_team_sheet, 1)

            await pro_eu_registration.edit_signed_team_message([])

            pro_eu_registration.set_reset_indicator(0)
            answer = "Reset done."

            await schedule_log_channel.send(answer)

            pro_eu_registration.set_lock_indicator(0)
            answer = "Changing permissions for tier 1 role."

            await schedule_log_channel.send(answer)

            await give_tier_send_messages_permission(role_tier_one_id)

            inform_team_captain_message = "Registration is now open for <@&{}>.".format(role_tier_one_id)

            await sign_in_channel.send(inform_team_captain_message)

            answer = "Automatic unlock complete for tier 1."

            await schedule_log_channel.send(answer)

            print("Going to sleep...")

            await asyncio.sleep(2 * 60 * 60)  # sleeps 2 hours



        # unlocking for tier 2
        elif hour == 14 and minute == 0 and weekday_index != 5:
            print("schedule unlock")
            schedule_log_channel = client.get_channel(schedule_log_channel_id)
            sign_in_channel = client.get_channel(sign_in_channel_id)

            await schedule_log_channel.send("Executing automatic unlock for tier 2...")

            answer = "Changing permissions for tier 2 role."

            await schedule_log_channel.send(answer)

            await give_tier_send_messages_permission(role_tier_two_id)

            inform_team_captain_message = "Registration is now open for <@&{}>.".format(role_tier_two_id)

            await sign_in_channel.send(inform_team_captain_message)

            answer = "Automatic unlock complete for tier 2."

            await schedule_log_channel.send(answer)

            print("Going to sleep...")

            await asyncio.sleep(3 * 60 * 60)  # sleeps 3 hours

        # locking
        elif hour == 18 and minute == 0 and weekday_index != 5:
            print("Schedule lock")
            schedule_log_channel = client.get_channel(schedule_log_channel_id)
            sign_in_channel = client.get_channel(sign_in_channel_id)

            await schedule_log_channel.send("Executing automatic lock...")

            answer = "Changing permissions for tier 1 and tier 2 role."

            await schedule_log_channel.send(answer)

            await take_tier_send_messages_permission(role_tier_one_id)

            await take_tier_send_messages_permission(role_tier_two_id)

            my_gspread.refresh_google_tokens()

            pro_eu_registration.set_lock_indicator(1)

            inform_team_captain_message = "Registration locked."

            await sign_in_channel.send(inform_team_captain_message)

            await schedule_log_channel.send("Automatic lock complete.")

            print("Going in a long sleep...")

            await asyncio.sleep(13 * 60 * 60)  # runs every 5 seconds

        #unlocking pro-eu-teams channel
        elif hour == 0 and minute == 0 and weekday_index == 6:
            print("pro-eu-teams unlocked")
            schedule_log_channel = client.get_channel(schedule_log_channel_id)
            cap_channel = client.get_channel(cap_news_channel_id)

            await schedule_log_channel.send("Executing automatic unlock...")

            answer = "Changing permission to unlock the pro eu teams channel"

            await schedule_log_channel.send(answer)

            await unlock_pro_eu_teams_channel(role_team_captain_id)

            inform_in_cap_news_channel = "Hello <@&{}>,\n\nThe <@&{}> it's open until the end of the day.".format(role_team_captain_id, pro_eu_teams_channel_id)

            await cap_channel.send(inform_in_cap_news_channel)

            await schedule_log_channel.send("Unlock completed")
            
            print("Im going to sleep")

            await asyncio.sleep(24 * 60 * 60) #sleeps 24 hours, i dont know if thats right so pls check this

        #locking the pro-eu-teams channel
        elif hour == 0 and minute == 0 and weekday_index == 0:
            print("pro-eu-teams locked")
            schedule_log_channel = client.get_channel(schedule_log_channel_id)
            cap_channel = client.get_channel(cap_news_channel_id)

            await schedule_log_channel.send("Executing automatic lock...")

            answer = "Changing permission to lock the pro eu teams channel"

            await schedule_log_channel.send(answer)

            await lock_pro_eu_teams_channel(role_team_captain_id)

            inform_in_cap_news_channel = "Hello <@&{}>,\n\nThe <@#{}> is closed until next Sunday."

            await cap_channel.send(inform_in_cap_news_channel)

            await schedule_log_channel.send("Lock completed")

            await asyncio.sleep(11 * 60 * 60) #sleeps 11 hours, i dont know if thats right so pls check this

        else:
            print("sleep for 56 secs...")
            await asyncio.sleep(56) #runs every 59 seconds
