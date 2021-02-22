import streamlit as st 
from nba_api.stats.static import teams
from nba_api.stats.static import players
from nba_api.stats.endpoints import commonplayerinfo
from nba_api.stats.endpoints import shotchartdetail
from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.endpoints import leaguestandings
from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.endpoints import drafthistory
from nba_api.stats.endpoints import alltimeleadersgrids
from nba_api.stats.endpoints import boxscoresummaryv2
from nba_api.stats.endpoints import teamgamelog
from nba_api.stats.endpoints import scoreboardv2
from nba_api.stats.endpoints import scoreboardv2
from nba_api.stats.endpoints import playerawards
from nba_api.stats.endpoints import boxscoretraditionalv2
from nba_api.stats.endpoints import leaguegamefinder
from nba_api.stats.endpoints import boxscorematchups
from nba_api.stats.endpoints import winprobabilitypbp
from datetime import date, timedelta
from csv import reader
import csv 
import json
import datetime
import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
import seaborn as sns 
from matplotlib import cm 
from matplotlib.patches import Circle, Rectangle, Arc, ConnectionPatch
from matplotlib.patches import Polygon
from datetime import datetime

st.sidebar.title(":basketball: NBA Unicorn")
page = st.sidebar.selectbox("Please Select One",('NBA Scoreboard','NBA Box Score','Team Contract Situation','NBA Contracts','Player Information', 'Player Statistics', 'Player Shot Chart', 'NBA Statistical History','NBA Award and Chapionship History','Draft History','League Standings','About'))

if page == 'NBA Scoreboard':
    st.title('Todays Games and Yesterdays Scores/Leaders')

    teams = []
    leaders = []
    
    day = datetime.now() - timedelta(days=0)    
    day = day.strftime('%m/%d/%Y')

    gamefinder = []
    today = {}

    #today games
    st.header('Todays Games:')
    games = json.loads(leaguegamefinder.LeagueGameFinder(league_id_nullable='00',player_or_team_abbreviation="",date_to_nullable=day,date_from_nullable=day).league_game_finder_results.get_json())['data']
    for game in games:
        if not game[4] in gamefinder:
            gamefinder.append(game[4])

    today_score = json.loads(scoreboardv2.ScoreboardV2(day_offset=0).get_json())['resultSets'][0]['rowSet']
    for row in today_score:
        today[row[2]] = {'Matchup':row[5][-6:-3] + " @ " + row[5][12:15],'Time':row[4],'Score':'','National TV':row[11],'Home Feed':row[12],'Away Feed':row[13],'Arena':row[15]}

    for game in gamefinder:
        box_score = json.loads(winprobabilitypbp.WinProbabilityPBP(game_id=game).game_info.get_json())['data'][0]
        today[game]['Score'] = str(box_score[7]) + "-" + str(box_score[4])  

    games = []
    for game in today:
        games.append(today[game].values())
    games.insert(0, ["Matchup", "Time", "Score", "National TV", "Home Feed", "Away Feed", "Arena"])

    st.markdown("""
    <style>
    table td:nth-child(1) {
        display: none
    }
    table th:nth-child(1) {
        display: none
    }
    thead { 
        display: none; 
        }
    </style>
    """, unsafe_allow_html=True)

    st.table(games)

    #yesterday games
    st.header('Yesterday Scores:')

    gamefinder = []
    yesterday = {}

    lastday = datetime.now() - timedelta(days=1)    
    lastday = lastday.strftime('%m/%d/%Y')
    
    games = json.loads(leaguegamefinder.LeagueGameFinder(league_id_nullable='00',player_or_team_abbreviation="",date_to_nullable=lastday,date_from_nullable=lastday).league_game_finder_results.get_json())['data']
    for game in games:
        if not game[4] in gamefinder:
            gamefinder.append(game[4])
    
    yesterday_score = json.loads(scoreboardv2.ScoreboardV2(day_offset=-1).get_json())['resultSets'][0]['rowSet']
    for row in yesterday_score:
        yesterday[row[2]] = {'Matchup':row[5][-6:-3] + " @ " + row[5][12:15],'Time':row[4],'Score':'','National TV':row[11],'Home Feed':row[12],'Away Feed':row[13],'Arena':row[15]}

    for game in gamefinder:
        box_score = json.loads(winprobabilitypbp.WinProbabilityPBP(game_id=game).game_info.get_json())['data'][0]
        yesterday[game]['Score'] = str(box_score[7]) + "-" + str(box_score[4])  

    games = []
    for game in yesterday:
        games.append(yesterday[game].values())
    games.insert(0, ["Matchup", "Time", "Score", "National TV", "Home Feed", "Away Feed", "Arena"])

    st.table(games)
  
    #yesterday leaders
    st.header('Yesterday Leaders:')
    st.write('P =                Points, R =            Rebounds, A =           Assists')
    yesterday_leaders = json.loads(scoreboardv2.ScoreboardV2(day_offset=-1).team_leaders.get_json())['data']
    for row in yesterday_leaders:
        leaders.append(({'Team':row[2] + " " + row[3],'Scoring Leader':'P: ' + row[6],'Points':row[7],'Rebound Leader':'R: '+ row[9],'Rebounds':row[10],'Assist Leader':'A: ' + row[12],'Assists':row[13]}))

    st.table(leaders)
elif page == 'NBA Box Score':
    st.title('NBA Box Score')
    st.subheader('Games are from yesterday')

    gamefinder = []
    stats = []
    yesterday = {}

    lastday = datetime.now() - timedelta(days=1)    
    lastday = lastday.strftime('%m/%d/%Y')

    games = json.loads(leaguegamefinder.LeagueGameFinder(league_id_nullable='00',player_or_team_abbreviation="",date_to_nullable=lastday,date_from_nullable=lastday).league_game_finder_results.get_json())['data']
    for game in games:
        if not game[4] in gamefinder:
            gamefinder.append(game[4])
    st.markdown("""
    <style>
    table td:nth-child(1) {
        display: none
    }
    table th:nth-child(1) {
        display: none
    }
    thead { 
        display: none; 
        }
    </style>
    """, unsafe_allow_html=True)

    games = []
    oldbox = []
    for game in gamefinder:
        box_score = json.loads(boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game).player_stats.get_json())['data']
        
        box_score.insert(0, ["Team","Player","Minutes",'PTS','REB','AST', "FG", "3PT","FT",'STL', 'BLK', 'TO', 'PF', 'OREB', '+/-'])    
        box_score.pop(0)
        box_score = [[b[2],b[5],b[8],b[26],b[20],b[21],str(b[9]) + "-" + str(b[10]),str(b[12]) + "-" + str(b[13]),str(b[15]) + "-" + str(b[16]),b[22],b[23],b[24],b[25],b[18],b[27]] for b in box_score]
        box_score.insert(0, ["Team","Player","Minutes",'PTS','REB','AST', "FG", "3PT","FT",'STL', 'BLK', 'TO', 'PF', 'OREB', '+/-'])

        st.table(box_score)
elif page == 'Team Contract Situation':
    st.title('View Team Cap Situation')

    location = teams.get_teams()
    for teams in location:

    	team_names = [l['full_name'] for l in location]
    	team_names = sorted(team_names)

    team_names.insert(0, "Select or Type a Team")

    hello = st.selectbox(
        ' ',
        (team_names))

    if hello == "Select or Type a Team":
        st.write('')
    else: 
        st.subheader(f'Here is the contract situation for the {hello}. Salary Cap info located at bottom.')
        st.subheader("* Player Option")
        st.subheader('** Team Option')

    players = []

    if hello != "Select or Type a Team":
        with open ('nbaplayersalaries.csv', 'r') as read_obj:
            csv_reader = reader(read_obj)
            for row in csv_reader:
                if row[2] == hello:  
                    players.append({"League Rank":row[0],"Player":row[1],"2020-2021":row[3], "2021-2022":row[4], "2022-2023":row[5], "2023-2024":row[6], "2024-2025":row[7], "2025-26": row[8], "Signed Using":row[9], "Guarenteed":row[10]})          
        
            st.markdown("""
            <style>
            table td:nth-child(1) {
                display: none
            }
            table th:nth-child(1) {
            display: none
            }
            </style>
            """, unsafe_allow_html=True)
            
            st.table(players)
    
    players = []
    with open ('capspace.csv', 'r') as read_obj:
        csv_reader = reader(read_obj)
        for row in csv_reader: 
            if row[0] == hello: 
                players.append({"Team":row[0],"2020-2021":row[1], "2021-2022":row[2],"2022-2023":row[3],"2023-2024":row[4],"2024-2025":row[5],"2025-2026":row[6]})
    
    if hello == "Select or Type a Team":
        st.write('')
    else: 
        st.subheader(f'Here is the {hello} total team cap in the upcoming seasons.') 
    
        st.table(players)

    if hello == "Select or Type a Team":
        st.write('')
    elif 109140000 -  float(players[0]['2020-2021'].replace('$', '').replace(',', ''))   > 0 :  
        st.subheader('They have ' + '${:,.0f}'.format(109140000-float(players[0]['2020-2021'].replace('$', '').replace(',', '')) ) + ' avaiable.')
        st.subheader('NBA Salary Cap for 2020-21 is $109.140M. Tax Level is $132.627M.') 
    else:
        st.subheader('They are currently over the cap by ' + '${:,.0f}'.format(float(players[0]['2020-2021'].replace('$', '').replace(',', '')) - 109140000))
        st.subheader('The NBA Salary Cap for 2020-21 is $109.140M. The Luxury Tax Level is $132.627M.')
elif page == 'NBA Contracts':
    st.title("League Wide Salary and Contract Details")
    st.header("Please choose a player to view contract details or explore list")
    st.subheader("* Player Option")
    st.subheader('** Team Option')
    st.write('')
    st.subheader("Choose a Player to View Their Contract or Scroll Down to View all NBA contracts")

    active_player_dict = players.get_active_players()

    active_league = players.get_active_players()
    for player in active_league:

        player_active_information = [l['full_name'] for l in active_league]

    player_active_information.insert(0, "Select or Type a Player")

    name = st.selectbox(
        ' ',
        (player_active_information))

    names = []

    with open ('nbaplayersalaries.csv', 'r') as read_obj:
        csv_reader = reader(read_obj)
        for row in csv_reader:
            if row[1] == name:
                names.append({"Team":row[2],"2020-2021":row[3],"2021-2022":row[4], "2022-2023":row[5], "2023-2024":row[6], "2024-2025":row[7], "2025-2026":row[8], "Signed Using":row[9], "Guarenteed":row[10]})

    if name == "Select or Type a Player":
        st.write("")
    else:
        st.table(names)

    players = []

    st.header("League Wide Contract Situation")

    with open ('nbaplayersalaries.csv', 'r') as read_obj:
        csv_reader = reader(read_obj)
        for row in csv_reader:
            players.append({"Player Name":row[1],"Team":row[2],"2020-2021":row[3],"2021-2022":row[4], "2022-2023":row[5], "2023-2024":row[6], "2024-2025":row[7], "2025-2026":row[8], "Signed Using":row[9], "Guarenteed":row[10]})

    st.table(players)
elif page == 'Player Information': 
    st.title('Player Information')

    player_dict = players.get_players()

    league = players.get_players()
    for player in league:

        player_information = [l['full_name'] for l in league]

    player_information.insert(0, "Please Select or Type a Players Name")

    name = st.selectbox(
        ' ',
        (player_information))

    bron = [player for player in player_dict if player['full_name'].lower() == name.lower()]
    if len(bron) > 0:
        bron = bron[0]

    if name != "Please Select or Type a Players Name":
  
        players = []
    # get players information 
        player_data = json.loads(commonplayerinfo.CommonPlayerInfo(player_id=bron['id']).get_json())['resultSets'][0]['rowSet'][0]
        player_stats = json.loads(commonplayerinfo.CommonPlayerInfo(player_id=bron['id']).player_headline_stats.get_json())['data']
        for row in player_stats: 
            players.append(({'Points':str(row[3])[:+4],'Assists':str(row[4])[:+4],'Rebounds':str(row[5])[:+4]}))
        st.markdown("""
        <style>
        table td:nth-child(1) {
            display: none
        }
        table th:nth-child(1) {
            display: none
        }
        </style>
        """, unsafe_allow_html=True)
            
        active = player_data[16]
        if active == "Inactive":
            st.subheader('Career Stats')
        else:
            st.subheader('Season Stats')
        st.table(players)   
        birthday = player_data[7][0:10]
        dayofbirth = datetime.strptime(birthday, '%Y-%m-%d')
        diff = datetime.now() - dayofbirth
        age_info = int(diff.days/365)
        st.subheader(f'Age: {age_info} Years Old' + " " + f'(DOB:{birthday})')
        college = player_data[8]
        st.subheader(f'Education: {college}')
        drafted = player_data[29]
        drafted_round = player_data[30]
        drafted_number = player_data[31]
        if drafted == 'Undrafted':
            st.subheader('Draft: Undrafted')
        else:
            st.subheader(f'Drafted: Round {drafted_round}, Pick {drafted_number}, In {drafted} ')
        current_team = player_data[19]
        status = player_data[16]
        if status == 'Inactive':
            st.subheader('')
        else:
            st.subheader(f'Team: {current_team}')
        country = player_data[9]
        st.subheader(f'Nationality: {country}')
        height = player_data[11]
        st.subheader(f'Height: {height}')
        weight = player_data[12]
        st.subheader(f'Weight: {weight}')
        position = player_data[15]
        st.subheader(f'Position: {position}')
        season_exp = player_data[13]
        season_experience = player_data[24]
        season_now = player_data[25]
        st.subheader(f'Experience: {season_exp} Seasons' + " " + f'(Active From: {season_experience} - {season_now})')  
elif page == 'Player Statistics': 
    st.title('Player Statistics')

    player_dict = players.get_players()

    league = players.get_players()
    for player in league:

    	player_information = [l['full_name'] for l in league]

    player_information.insert(0, "Please Select or Type a Players Name")

    name = st.selectbox(
        '',
        (player_information))

    st.subheader("Please choose between PerGame (Default), Totals, and Per36")
    scoring_type = st.selectbox(
        '',
        ('PerGame', 'Totals', 'Per36'))

    bron = [player for player in player_dict if player['full_name'].lower() == name.lower()]
    if len(bron) > 0:
        bron = bron[0]  

    players = []

    if name != "Please Select or Type a Players Name":
        career_stats = json.loads(playercareerstats.PlayerCareerStats(player_id=bron['id'], per_mode36=scoring_type).get_json())['resultSets'][0]['rowSet']
        for row in career_stats:
            players.append({'Year':row[1], 'Team': row[4], 'Age': row[5], 'GP': row[6], 'Minutes':str(row[8])[:+4], 'Points': str(row[26])[:+4], 'Rebounds':str(row[20])[:+4], 'Assists':str(row[21])[:+4], 'Steals':str(row[22])[:+4], 'Blocks':str(row[23])[:+4], 'TOV':str(row[24])[:+4], 'FG%':str(round(row[11]*100)) + "%",'3Pt %':str(round(row[14]*100)) + "%", 'FT%':str(round(row[17]*100)) + "%"})
        st.markdown("""
        <style>
        table td:nth-child(1) {
            display: none
        }
        table th:nth-child(1) {
            display: none
        }
        </style>
        """, unsafe_allow_html=True)


        newlist = sorted(players, key=lambda k: k['Year'], reverse=True)

        st.table(newlist)
elif page == 'Player Shot Chart': 
    st.title("NBA Shot Chart By Season")

    years = []
    for year in range (2020,1995, -1):
        years.append(str(year) + "-" + (str(year+1)[-2:]))

    st.subheader('Please pick a year (Required). Note: NBA provides shot data for every player in the league for each season since 1996-97')
    years.insert(0, "Select a year")
    jonnyissexy = st.selectbox(
        '',
        years)

    st.subheader('Please choose between Regular Season (Default) or Playoffs.')
    season_type = st.selectbox(
        '',
        ('Regular Season', 'Playoffs'))

    #get player shot chart detail
    def get_player_shotchartdetail(player_name, season_id, season_type): 

        #player dictionary 
        nba_players = players.get_players()
        player_dict = [player for player in nba_players if player['full_name'] == player_name]

        if len(player_dict) == 0: 
            return None, None
    
        #career dataframe
        career = playercareerstats.PlayerCareerStats(player_id=player_dict[0]['id'])
        career_df = json.loads(career.get_json())['resultSets'][0]['rowSet']

        #team id during the season
        team_ids = [season[3] for season in career_df if season[1] == season_id]

        #st.write(career_df[0])
        shots = []
        for team_id in team_ids: 
            shotchartlist = shotchartdetail.ShotChartDetail(team_id=int(team_id),
                                                    player_id=int(player_dict[0]['id']),
                                                    season_type_all_star=season_type,
                                                    season_nullable=season_id,
                                                    context_measure_simple="FGA").get_data_frames()
            shots.extend(shotchartlist)

        return shotchartlist[0], shotchartlist[1]

    #draw court function
    def draw_court(ax=None, color="blue", lw=1, outer_lines=False):

            if ax is None:
                ax = plt.gca()

            #Basketball Hoop
            hoop = Circle((0,0), radius=7.5, linewidth=lw, color=color, fill=False)
            #backboard 
            backboard = Rectangle((-30, -12.5), 60, 0, linewidth=lw, color=color)
            #the paiint 
            #outer box 
            outer_box = Rectangle((-80, -47.5), 160, 190, linewidth=lw, color=color, fill=False)
            #inner box 
            inner_box = Rectangle((-60, -47.5), 120, 190, linewidth=lw, color=color, fill=False)
            #freethrow top arc 
            top_free_throw = Arc((0, 142.5), 120, 120, theta1=0, theta2=180, linewidth=lw, color=color, fill=False)
            #freethrow bottom arc 
            bottom_free_throw = Arc((0, 142.5), 120, 120, theta1=180, theta2=0, linewidth=lw, color=color)
            #restricted zone 
            restricted = Arc((0,0), 80, 80, theta1=0, theta2=180, linewidth=lw, color=color)
            #three point line 
            corner_three_a = Rectangle((-220, -47.5), 0, 140, linewidth=lw, color=color)
            corner_three_b = Rectangle((220, -47.5), 0, 140, linewidth=lw, color=color)
            three_arc = Arc((0,0), 475, 475, theta1=22, theta2=158, linewidth=lw, color=color)
            #center court 
            center_outer_arc = Arc((0, 422.5), 120, 120, theta1=180, theta2=0, linewidth=lw, color=color)
            center_inner_arc = Arc((0, 422.5), 40, 40, theta1=180, theta2= 0, linewidth=lw, color=color)

            court_elements = [hoop, backboard, outer_box, inner_box, top_free_throw, bottom_free_throw, restricted, corner_three_a, corner_three_b, three_arc, center_outer_arc, center_inner_arc]

            outer_lines=True
            if outer_lines:
                outer_lines = Rectangle((-250, -47.5), 500, 470, linewidth=lw, color=color, fill=False)
                court_elements.append(outer_lines)

            for element in court_elements:
                ax.add_patch(element)

    #shot chart function 
    def shot_chart(data, title="", color="b", xlim=(-250, 250), ylim=(422.5,-47.5), line_color="blue",
                court_color="white", court_lw=2, outer_lines=False,
                flip_court=False, gridsize=None,
                ax=None, despine=False):

        if (ax is None):
            ax = plt.gca()

        if not flip_court:
            ax.set_xlim(xlim)
            ax.set_ylim(ylim)
        else:
            ax.set_xlim(xlim[::-1])
            ax.set_ylim(ylim[::-1])

        ax.tick_params(labelbottom="off", labelleft="off")
        ax.set_title(title, fontsize=16)

        #draws the court using the draw_court()
        draw_court(ax, color=line_color, lw=court_lw, outer_lines=outer_lines)

        # seperate color by make or miss
        x_missed = data[data['EVENT_TYPE'] == 'Missed Shot']['LOC_X']
        y_missed = data[data['EVENT_TYPE'] == 'Missed Shot']['LOC_Y']

        x_made = data[data['EVENT_TYPE'] == 'Made Shot']['LOC_X']
        y_made = data[data['EVENT_TYPE'] == 'Made Shot']['LOC_Y']

        #plot missed shots 
        ax.scatter(x_missed, y_missed, c='r', marker="x", s=100, linewidths=3)
        #plot made shots 
        ax.scatter(x_made, y_made, facecolors='none', edgecolors='g', marker='o', s=100, linewidths=3)

    league = players.get_players()
    for player in league:

    	player_names = [l['full_name'] for l in league]

    player_names.insert(0, "Select a player")

    st.subheader('Please select or type a players name to view their shot chart from the season choosen above (Required)')
    name = st.selectbox(
        '',
        player_names)

    player_dict = players.get_players()

    if __name__ == "__main__":
        player_shotchart_df, league_avg = get_player_shotchartdetail(name, jonnyissexy, season_type)
    
        if player_shotchart_df is None:
            st.write(" ")
        else:
            shot_chart(player_shotchart_df, title=name + " " + jonnyissexy)
            plt.show()

        #print(player_shotchart_df)
        #print(league_avg)
            xlim = (-250, 250)
            ylim = (422.5, -47.5)

            ax = plt.gca()
            ax.set_xlim(xlim[::-1])
            ax.set_ylim(ylim[::-1])
            draw_court(ax)
            plt.show()

    st.set_option('deprecation.showPyplotGlobalUse', False)
    st.pyplot()
elif page == 'NBA Statistical History':
    st.title('NBA Statistical History')
    players = []

    history = "Statistical Records"

    if history == "Statistical Records":
        st.subheader('Please select a record')
        type_of_record = st.selectbox(
            '', 
            ('','Assists', 'Points', 'Rebounds', 'Steals', 'Blocks', 'Defensive Rebounds', 'Offensive Rebounds', '3PM','FGM','FG%',
                'FTM', 'FTA', 'FT%','Games Played','Personal Fouls','Turnovers'))

        st.subheader('Please choose between Regular (Default) or Playoffs')
        season_reg = st.selectbox(
            '',
            ('Regular Season', 'Playoffs'))

        st.subheader('Please choose between Totals (Default) or PerGame')
        permode = st.selectbox(
            '',
            ('Totals', 'PerGame'))
    else: 
        st.write('')

    if type_of_record == "Assists":
        all_time_records = alltimeleadersgrids.AllTimeLeadersGrids(season_type=season_reg,per_mode_simple=permode)
        # assists
        players = []
        assists = json.loads(all_time_records.ast_leaders.get_json())['data']
        for row in assists: 
            players.append({'Player':row[1],'Career Assists':row[2]})
        st.markdown("""
        <style>
        table td:nth-child(1) {
            display: none
        }
        table th:nth-child(1) {
            display: none
        }
        </style>
        """, unsafe_allow_html=True)

        st.table(players)
    else:
        st.write('')
    if type_of_record == "Points":
        all_time_records = alltimeleadersgrids.AllTimeLeadersGrids(season_type=season_reg,per_mode_simple=permode)
        year = []
        points = json.loads(all_time_records.pts_leaders.get_json())['data']
        for row in points: 
            year.append({'Player':row[1],'Career Points':row[2]})
        st.table(year)
        st.markdown("""
        <style>
        table td:nth-child(1) {
            display: none
        }
        table th:nth-child(1) {
            display: none
        }
        </style>
        """, unsafe_allow_html=True)
    else: 
        st.write('')
    if type_of_record == "Rebounds":
        all_time_records = alltimeleadersgrids.AllTimeLeadersGrids(season_type=season_reg,per_mode_simple=permode)
        rebound = []
        rebounds = json.loads(all_time_records.reb_leaders.get_json())['data']
        for row in rebounds: 
            if permode == "PerGame":
                rebound.append({'Player':row[1],'Career Total Rebounds':str(row[2])[:+4]})
            else:
                rebound.append({'Player':row[1],'Career Total Rebounds':row[2]})
        st.table(rebound)
        st.markdown("""
        <style>
        table td:nth-child(1) {
            display: none
        }
        table th:nth-child(1) {
            display: none
        }
        </style>
        """, unsafe_allow_html=True)
    else: 
        st.write('')    
    if type_of_record == "Steals":
        all_time_records = alltimeleadersgrids.AllTimeLeadersGrids(season_type=season_reg,per_mode_simple=permode)
        steal = []
        steals = json.loads(all_time_records.stl_leaders.get_json())['data']
        for row in steals:
            if permode == "PerGame":
                steal.append({'Player':row[1],'Career Steals':str(row[2])[:+3]})
            else:
                steal.append({'Player':row[1],'Career Steals':row[2]})
        st.table(steal)
        st.markdown("""
        <style>
        table td:nth-child(1) {
            display: none
        }
        table th:nth-child(1) {
            display: none
        }
        </style>
        """, unsafe_allow_html=True)
    else: 
        st.write('') 
    if type_of_record == "Blocks":
        all_time_records = alltimeleadersgrids.AllTimeLeadersGrids(season_type=season_reg,per_mode_simple=permode)
        block = []
        blocks = json.loads(all_time_records.blk_leaders.get_json())['data']
        for row in blocks: 
            if permode == "PerGame":
                block.append({'Player':row[1],'Career Blocks':str(row[2])[:+3]})
            else:
                block.append({'Player':row[1],'Career Blocks':row[2]})
        st.table(block)
        st.markdown("""
        <style>
        table td:nth-child(1) {
            display: none
        }
        table th:nth-child(1) {
            display: none
        }
        </style>
        """, unsafe_allow_html=True)
    else: 
        st.write('') 
    if type_of_record == "Defensive Rebounds":
        all_time_records = alltimeleadersgrids.AllTimeLeadersGrids(season_type=season_reg,per_mode_simple=permode)
        defrebound = []
        defrebounds = json.loads(all_time_records.dreb_leaders.get_json())['data']
        for row in defrebounds: 
            if permode == "PerGame":
                defrebound.append({'Player':row[1],'Career Defensive Rebounds':str(row[2])[:+3]})
            else:
                defrebound.append({'Player':row[1],'Career Defensive Rebounds':row[2]})
        st.table(defrebound)
        st.markdown("""
        <style>
        table td:nth-child(1) {
            display: none
        }
        table th:nth-child(1) {
            display: none
        }
        </style>
        """, unsafe_allow_html=True)
    else: 
        st.write('') 
    if type_of_record == "Offensive Rebounds":
        all_time_records = alltimeleadersgrids.AllTimeLeadersGrids(season_type=season_reg,per_mode_simple=permode)
        offrebound = []
        offrebounds = json.loads(all_time_records.oreb_leaders.get_json())['data']
        for row in offrebounds: 
            if permode == "PerGame":
                offrebound.append({'Player':row[1],'Career Offensive Rebounds':str(row[2])[:+3]})
            else:
                offrebound.append({'Player':row[1],'Career Offensive Rebounds':row[2]})
        st.table(offrebound)
        st.markdown("""
        <style>
        table td:nth-child(1) {
            display: none
        }
        table th:nth-child(1) {
            display: none
        }
        </style>
        """, unsafe_allow_html=True)
    else: 
        st.write('') 
    if type_of_record == "3PM":
        all_time_records = alltimeleadersgrids.AllTimeLeadersGrids(season_type=season_reg,per_mode_simple=permode)
        threepm = []
        fg3m = json.loads(all_time_records.fg3_m_leaders.get_json())['data']
        for row in fg3m: 
            if permode == "PerGame":
                threepm.append({'Player':row[1],'Career 3s Made':str(row[2])[:+3]})
            else:
                threepm.append({'Player':row[1],'Career 3s Made':row[2]})
        st.table(threepm)
        st.markdown("""
        <style>
        table td:nth-child(1) {
            display: none
        }
        table th:nth-child(1) {
            display: none
        }
        </style>
        """, unsafe_allow_html=True)
    else: 
        st.write('') 
    if type_of_record == "FGM":
        all_time_records = alltimeleadersgrids.AllTimeLeadersGrids(season_type=season_reg,per_mode_simple=permode)
        fieldgm = []
        fgm = json.loads(all_time_records.fgm_leaders.get_json())['data']
        for row in fgm: 
            if permode == "PerGame":
                fieldgm.append({'Player':row[1],'Career Field Goals Made':str(row[2])[:+4]})
            else:
                fieldgm.append({'Player':row[1],'Career Field Goals Made':row[2]})
        st.table(fieldgm)
        st.markdown("""
        <style>
        table td:nth-child(1) {
            display: none
        }
        table th:nth-child(1) {
            display: none
        }
        </style>
        """, unsafe_allow_html=True)
    else: 
        st.write('') 
    if type_of_record == "FG%":
        all_time_records = alltimeleadersgrids.AllTimeLeadersGrids(season_type=season_reg,per_mode_simple=permode)
        fghigh = []
        fgpct = json.loads(all_time_records.fg_pct_leaders.get_json())['data']
        for row in fgpct: 
            fghigh.append({'Player':row[1],'Career Highest FG %':str(round(row[2]*100)) + "%"})
        fghigh.insert(0,{'Player':"", 'Career Highest FG %':""})
        st.table(fghigh)
        st.markdown("""
        <style>
        table td:nth-child(1) {
            display: none
        }
        table th:nth-child(1) {
            display: none
        }
        </style>
        """, unsafe_allow_html=True)
    else: 
        st.write('') 
    if type_of_record == "FTM":
        all_time_records = alltimeleadersgrids.AllTimeLeadersGrids(season_type=season_reg,per_mode_simple=permode)
        freethrow = []
        ftm = json.loads(all_time_records.ftm_leaders.get_json())['data']
        for row in ftm: 
            if permode == "PerGame":
                freethrow.append({'Player':row[1],'Career Free Throws Made':str(row[2])[:+3]})
            else:
                freethrow.append({'Player':row[1],'Career Free Throws Made':row[2]})
        st.table(freethrow)
        st.markdown("""
        <style>
        table td:nth-child(1) {
            display: none
        }
        table th:nth-child(1) {
            display: none
        }
        </style>
        """, unsafe_allow_html=True)
    else: 
        st.write('') 
    if type_of_record == "FTA":
        all_time_records = alltimeleadersgrids.AllTimeLeadersGrids(season_type=season_reg,per_mode_simple=permode)
        freethrowattempted = []
        fta = json.loads(all_time_records.fta_leaders.get_json())['data']
        for row in fta: 
            if permode =="PerGame":
                freethrowattempted.append({'Player':row[1],'Career Free Throws Attempted':str(row[2])[:+4]})
            else:
                freethrowattempted.append({'Player':row[1],'Career Free Throws Attempted':row[2]})
        st.table(freethrowattempted)
        st.markdown("""
        <style>
        table td:nth-child(1) {
            display: none
        }
        table th:nth-child(1) {
            display: none
        }
        </style>
        """, unsafe_allow_html=True)
    else: 
        st.write('') 
    if type_of_record == "FT%":
        all_time_records = alltimeleadersgrids.AllTimeLeadersGrids(season_type=season_reg,per_mode_simple=permode)
        freethrowpercent = []
        ftpct = json.loads(all_time_records.ft_pct_leaders.get_json())['data']
        for row in ftpct: 
            freethrowpercent.append({'Player':row[1],'Career Highest FT %':str(round(row[2]*100)) + "%"})
        st.table(freethrowpercent)
        st.markdown("""
        <style>
        table td:nth-child(1) {
            display: none
        }
        table th:nth-child(1) {
            display: none
        }
        </style>
        """, unsafe_allow_html=True)
    else: 
        st.write('') 
    if type_of_record == "Games Played":
        all_time_records = alltimeleadersgrids.AllTimeLeadersGrids(season_type=season_reg,per_mode_simple=permode)
        gamesplayed = []
        gp = json.loads(all_time_records.g_p_leaders.get_json())['data']
        for row in gp: 
            gamesplayed.append({'Player':row[1],'Career Games Played':row[2]})
        st.table(gamesplayed)
        st.markdown("""
        <style>
        table td:nth-child(1) {
            display: none
        }
        table th:nth-child(1) {
            display: none
        }
        </style>
        """, unsafe_allow_html=True)
    else: 
        st.write('') 
    if type_of_record == "Personal Fouls":
        all_time_records = alltimeleadersgrids.AllTimeLeadersGrids(season_type=season_reg,per_mode_simple=permode)
        personalfouls = []
        pf = json.loads(all_time_records.pf_leaders.get_json())['data']
        for row in pf: 
            if permode == "PerGame":
                personalfouls.append({'Player':row[1],'Career Personal Fouls':str(row[2])[:+3]})
            else:
                personalfouls.append({'Player':row[1],'Career Personal Fouls':row[2]})
        st.table(personalfouls)
        st.markdown("""
        <style>
        table td:nth-child(1) {
            display: none
        }
        table th:nth-child(1) {
            display: none
        }
        </style>
        """, unsafe_allow_html=True)
    else: 
        st.write('') 
    if type_of_record == "Turnovers":
        all_time_records = alltimeleadersgrids.AllTimeLeadersGrids(season_type=season_reg,per_mode_simple=permode)
        tov = []
        turnovers = json.loads(all_time_records.tov_leaders.get_json())['data']
        for row in turnovers: 
            if permode == "PerGame":
                tov.append({'Player':row[1],'Career Turnovers':str(row[2])[:+3]})
            else:
                tov.append({'Player':row[1],'Career Turnovers':row[2]})
        st.table(tov)
        st.markdown("""
        <style>
        table td:nth-child(1) {
            display: none
        }
        table th:nth-child(1) {
            display: none
        }
        </style>
        """, unsafe_allow_html=True)
    else: 
        st.write('') 
elif page == 'NBA Award and Chapionship History':
    st.title('NBA Award History')
    st.subheader('Please select between the following NBA Awards and Winners')
    history = st.selectbox(
        '',
        ('','Finals Matchups', 'All-NBA Teams', 'Award History'))

    if history == "Finals Matchups":
        finals = []
        with open ('nba_champions.csv', 'r') as read_obj:
            csv_reader = reader(read_obj)
            for row in csv_reader:
                finals.append({"Year":row[0],"League":row[1],"Champion":row[2],"Runner-Up":row[3],"Finals MVP":row[4]})
            st.table(finals)
            st.markdown("""
            <style>
            table td:nth-child(1) {
                display: none
            }
            table th:nth-child(1) {
                display: none
            }
            </style>
            """, unsafe_allow_html=True)
    else:
        st.write('')
            
    if history == "All-NBA Teams":
        allnba = []
        with open ('allnba.csv', 'r') as read_obj:
            csv_reader = reader(read_obj)
            for row in csv_reader: 
                allnba.append({"Year":row[0],"League":row[1],"Team":row[2],"Center":row[3], "Forward":row[4], "Forward ":row[5],"Guard":row[6],"Guard ":row[7]})
        st.table(allnba)
        st.markdown("""
        <style>
        table td:nth-child(1) {
            display: none
        }
        table th:nth-child(1) {
            display: none
        }
        </style>
        """, unsafe_allow_html=True)
    else: 
        st.write('')

    if history == "Award History":
        st.write("* recognizes unofficial ROY winners from newspaper writers.")
        awards = []
        with open ('awards.csv', 'r') as read_obj:
            csv_reader = reader(read_obj)
            for row in csv_reader: 
                awards.append({"Year":row[0],"MVP":row[4]," ":row[5],"ROY":row[7],"  ":row[8],"DPOY":row[10],'   ':row[11],"6MOY":row[13],"    ":row[14],"Coach":row[1],"":row[2],"MIP":row[16],"      ":row[17]})
        st.table(awards)
        st.markdown("""
        <style>
        table td:nth-child(1) {
            display: none
        }
        table th:nth-child(1) {
            display: none
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.write('')
elif page == 'Draft History':
    st.title('Draft History')

    players = []
    
    years = []
    for year in range (2020,1946, -1):
        years.append(str(year))

    years.insert(0, "")

    st.subheader('Please Choose a Season to View Draft Recap')
    jonnyissexy = st.selectbox(
        '',
        years)

    if jonnyissexy != '':
        draft_history = json.loads(drafthistory.DraftHistory(league_id='',season_year_nullable=jonnyissexy).get_json())['resultSets'][0]['rowSet']
        for row in draft_history:
            if row[2] == jonnyissexy: 
                players.append({"Player":row[1], "Round":row[3], "Pick in Round":row[4], "City":row[8], "Team":row[9], "College/Other":row[11]})

        st.markdown("""
        <style>
        table td:nth-child(1) {
            display: none
        }
        table th:nth-child(1) {
            display: none
        }
        </style>
        """, unsafe_allow_html=True)

        st.table(players)
elif page == 'League Standings':
    st.title("League Standings")

    years = []
    for year in range (2020,1969, -1):
        years.append(str(year) + "-" + (str(year+1)[-2:]))

    st.subheader('Note: NBA.com Only Provides Regular Season Standings Dating Back to 1970-71. Some Data is Only Available After 2002-03 Season')
    jonnyissexy = st.selectbox(
        '',
        years)
    
    st.subheader('Please choose between League Wide, Eastern Conference, or Western Conference')
    conference_type = st.selectbox(
        '',
        ('League Wide', 'East', 'West'))

    st.write('Indicators:')
    st.write('Clinched - ', 'E: east,', 'W: west,', 'NW: northwest,', 'P: pacific,', 'SW: southwest,', 'A: atlantic,', 'C: central,', 'SE: southeast')
    st.write('Misc - ', 'X: earned playoff berth,', 'O: eliminated from playoffs,', 'PI: play-in game')

    #build empty dictionary
    teams = []

    standings_league = json.loads(leaguestandings.LeagueStandings(season=jonnyissexy).get_json())['resultSets'][0]['rowSet']
    for row in standings_league: 
        if row[5] == conference_type:
            teams.append({'Team':row[3] + " " + row[4], 'Conference': row[5], 'Record':row[16], 'Win %':str(round(row[14]*100)) + "%", 'Home Record':row[17], 'Away Record':row[18], 'Last 10': row[19], 'Playoff Seed':row[7],'Clinched':row[8], 'PPG':row[56],'Opp PPG':row[57], 'Point Diff.':row[58],'Conference Record': row[6],  'Longest Winning Streak':row[29], 'Longest Losing Streak':row[30]})
        elif conference_type == "League Wide":
            teams.append({'Team':row[3] + " " + row[4], 'Conference': row[5], 'Record':row[16], 'Win %':str(round(row[14]*100)) + "%", 'Home Record':row[17], 'Away Record':row[18], 'Last 10': row[19], 'Playoff Seed':row[7], 'Clinched':row[8], 'PPG':row[56],'Opp PPG':row[57], 'Point Diff.':row[58],'Conference Record': row[6],  'Longest Winning Streak':row[29], 'Longest Losing Streak':row[30]})

    newlist = sorted(teams, key=lambda k: k['Win %'], reverse=True)

    st.markdown("""
    <style>
    table td:nth-child(1) {
        display: none
    }
    table th:nth-child(1) {
        display: none
    }
    </style>
    """, unsafe_allow_html=True)

    st.table(newlist)
else: 
    st.title('What can you do on NBA Unicorn?')
    st.subheader('Using the drop down menu on the left, you can view scores, contract sitatuations, player information, stats, and shotcharts. You can also see NBA history, draft history, and current league standings.')
    st.title('Who made this?')
    st.subheader('Made by Josh and Jonny with help from Noah')
    st.title('Resources Used')
    st.write('Contract Data Courtesy of basketballreference.com')
    st.write('Other information courtesy of NBA_API by Swar')
    st.title('TTP')
