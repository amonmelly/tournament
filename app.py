import streamlit as st
import hydralit_components as hc
import pandas as pd
import sqlite3

st.set_page_config(layout='wide')


def connection():
    return sqlite3.connect('tournament.db')


st.title('Pool Tournament')
menu_data=[{'label':'Fixtures'},{'label':'Table'},{'label':'Update Fixture'}]
menu_id=hc.nav_bar(menu_definition=menu_data)
if menu_id=='Fixtures':
    conn = connection()
    query = """
    SELECT games.game_id,players.name,player_2.player_name,games.status,games.round
    FROM games
    LEFT JOIN players ON players.id = games.player1_id
    LEFT JOIN player_2 ON games.player2_id = player_2.id;
"""
    df = pd.read_sql(query, conn)
    df.columns = ['Game Id','Player 1','Player 2','Status','Game Round']
    conn.close()
    round_ = st.radio('Filter By', ['Round','Individual'], horizontal=True,)
    if round_ == 'Round':
        round_list = list(df['Game Round'].unique())
        s_round = st.selectbox('Choose Round',round_list)
        df_display = df[df['Game Round']==s_round]
    else:
        individual_list = list(df['Player 1'].unique())
        s_individual = st.selectbox('Select Name',individual_list)
        df_display = df[(df['Player 1']==s_individual) | (df['Player 2']==s_individual)]
    st.dataframe(df_display, hide_index=True, use_container_width=True)
elif menu_id == 'Update Fixture':
    st.subheader('Game Update Window')
    conn = connection()
    query = """
    SELECT games.game_id,players.name,player_2.player_name,games.status,games.round
    FROM games
    LEFT JOIN players ON players.id = games.player1_id
    LEFT JOIN player_2 ON games.player2_id = player_2.id;"""
    
    player_query = """
    SELECT id,name,points,games_played,remaining,wins,lost
    FROM players;"""
    
    df_players = pd.read_sql(player_query, conn)
    df = pd.read_sql(query, conn)
    
    df.columns = ['Game Id','Player 1','Player 2','Status','Game Round']
    df['fixtures'] = df['Player 1'] + ' vs ' +df['Player 2']
    fixtures = list(df['fixtures'])
    
    fixture = st.selectbox('Select Fixture',fixtures)
    winner = st.radio('Winner?',fixture.split(' vs '), horizontal=True)
    if st.button('Submit'):
        
        game_id = int(df[df['fixtures'] == fixture]['Game Id'].values[0])
        winner_name = winner
        winner_id = int(df_players[df_players['name'] == winner_name]['id'].values[0])
        for l in fixture.split(' vs '):
            if l == winner_name:
                continue
            else:
                looser = l
                
        game_status = df[df['fixtures'] == fixture]['Status'].values[0]
        if game_status == 'Played':
            st.error('Fixture Already Updated')
        else:
            cursor = conn.cursor()
            update_games = '''
            UPDATE games
            SET status = ?,winner_id = ?
            WHERE game_id = ?
            '''
            
            update_winner = '''
            UPDATE players
            SET points = ?,games_played = ?,remaining = ?,wins = ?
            WHERE name = ?
            '''
            w_p = int(df_players[df_players['name'] == winner_name]['points'].values[0])+3
            w_g = int(df_players[df_players['name'] == winner_name]['games_played'].values[0])+1
            w_r = int(df_players[df_players['name'] == winner_name]['remaining'].values[0])-1
            w_w = int(df_players[df_players['name'] == winner_name]['wins'].values[0])+1
            
            update_looser = '''
            UPDATE players
            SET games_played = ?,remaining = ?,lost = ?
            WHERE name = ?
            '''
            l_g = int(df_players[df_players['name'] == looser]['games_played'].values[0])+1
            l_r = int(df_players[df_players['name'] == looser]['remaining'].values[0])-1
            l_l = int(df_players[df_players['name'] == looser]['lost'].values[0])+1
            
            cursor.execute(update_games, ("Played", winner_id, game_id))
            cursor.execute(update_winner, (w_p,w_g,w_r,w_w, winner_name))
            cursor.execute(update_looser, (l_g,l_r,l_l, looser))
            
            conn.commit()
            conn.close()
            st.success('Updated Successfully')
else:
    conn = connection()
    query = """
    SELECT name,points,games_played,remaining,wins,lost
    FROM players;"""
    
    df_table = pd.read_sql(query, conn)
    df_table.columns = ['Name','Points','Played','Remaining','Wins','Lost']
    st.dataframe(df_table.sort_values(by='Points',ascending=False),hide_index=True,use_container_width=True)
