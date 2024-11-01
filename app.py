import streamlit as st
import hydralit_components as hc
import pandas as pd
import connection


st.set_page_config(layout='wide')
st.title('Pool Tournament')
menu_data=[{'label':'Fixtures'},{'label':'Table'},{'label':'Update Fixture'}]
menu_id=hc.nav_bar(menu_definition=menu_data)
  
if menu_id=='Fixtures':
    conn = connection.connection()
    query = """
    SELECT games.game_id,players.name,copy_players.name,games.status,games.scores
    FROM games
    LEFT JOIN players ON players.player_id = games.player_1_id
    LEFT JOIN copy_players ON games.player_2_id = copy_players.player_id;
"""
    df = pd.read_sql(query, conn)
    df.columns = ['Game Id','Player 1','Player 2','Status','Scores']
    conn.close()
    individual_list = list(df['Player 1'].unique())
    s_individual = st.selectbox('Select Name',individual_list)
    df_display = df[(df['Player 1']==s_individual) | (df['Player 2']==s_individual)]
    st.dataframe(df_display, hide_index=True, use_container_width=True)
elif menu_id == 'Update Fixture':
    st.subheader('Game Update Window')
    conn = connection.connection()
    query = """
    SELECT games.game_id,players.name,copy_players.name,games.status
    FROM games
    LEFT JOIN players ON players.player_id = games.player_1_id
    LEFT JOIN copy_players ON games.player_2_id = copy_players.player_id;"""
    
    player_query = """
    SELECT player_id,name,points,games_played,remaining,wins,lost,difference
    FROM players;"""
    
    df_players = pd.read_sql(player_query, conn)
    df = pd.read_sql(query, conn)
    
    df.columns = ['Game Id','Player 1','Player 2','Status']
    df['fixtures'] = df['Player 1'] + ' vs ' +df['Player 2']
    f = df[df['Status'] != 'Played']
    player_filter = st.selectbox('Select Player',list(df_players['name']))

    fixtures = f[(f['Player 1']==player_filter) | (f['Player 2']==player_filter)]
    
    fixture = st.selectbox('Select Fixture',list(fixtures['fixtures']))
    winner = st.radio('Winner?',fixture.split(' vs '), horizontal=True)
    looser_score = st.number_input('Looser Score:', min_value=0, max_value=1)
    if looser_score == 0:
        l_score = -2
        w_score = 2
    else:
        l_score = -1
        w_score = 1
    if st.button('Submit'):
        
        game_id = int(df[df['fixtures'] == fixture]['Game Id'].values[0])
        winner_name = winner
        winner_id = int(df_players[df_players['name'] == winner_name]['player_id'].values[0])
        for i,l in enumerate(fixture.split(' vs ')):
            if l == winner_name:
                if i == 0:
                    if looser_score == 0:
                        score_text = '2,0'
                    else:
                        score_text = '2,1'
                else:
                    if looser_score == 0:
                        score_text = '0,2'
                    else:
                        score_text = '1,2'
            else:
                looser = l
                
        game_status = df[df['fixtures'] == fixture]['Status'].values[0]
        if game_status == 'Played':
            st.error('Fixture Already Updated')
        else:
            cursor = conn.cursor()
            update_games = """
            UPDATE games
            SET status = %s,winner_id = %s,scores = %s
            WHERE game_id = %s
            """
            
            update_winner = '''
            UPDATE players
            SET points = %s,games_played = %s,remaining = %s,wins = %s,difference = %s
            WHERE name = %s
            '''
            w_p = int(df_players[df_players['name'] == winner_name]['points'].values[0])+3
            w_g = int(df_players[df_players['name'] == winner_name]['games_played'].values[0])+1
            w_r = int(df_players[df_players['name'] == winner_name]['remaining'].values[0])-1
            w_w = int(df_players[df_players['name'] == winner_name]['wins'].values[0])+1
            ws_d = int(df_players[df_players['name'] == winner_name]['difference'].values[0])+w_score
            
            update_looser = '''
            UPDATE players
            SET games_played = %s,remaining = %s,lost = %s,difference = %s
            WHERE name = %s
            '''
            l_g = int(df_players[df_players['name'] == looser]['games_played'].values[0])+1
            l_r = int(df_players[df_players['name'] == looser]['remaining'].values[0])-1
            l_l = int(df_players[df_players['name'] == looser]['lost'].values[0])+1
            ls_d = int(df_players[df_players['name'] == looser]['difference'].values[0])+l_score
            
            cursor.execute(update_games, ("Played", winner_id, score_text,game_id))
            cursor.execute(update_winner, (w_p,w_g,w_r,w_w, ws_d,winner_name))
            cursor.execute(update_looser, (l_g,l_r,l_l,ls_d,looser))
            
            conn.commit()
            conn.close()
            st.success('Updated Successfully')
else:
    conn = connection.connection()
    query = """
    SELECT name,points,difference,remaining,wins,lost
    FROM players;"""
    
    df_table = pd.read_sql(query, conn)
    df_table.columns = ['Name','Points','Score Difference','Remaining','Wins','Lost']
    st.dataframe(df_table.sort_values(by=['Points','Score Difference','Name'],ascending=[False,False,True]),hide_index=True,use_container_width=True)
