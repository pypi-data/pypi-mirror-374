from spaceeval import Space_Model

event_id = 8
events_data = '/home/c_yeung/workspace6/python/openstarlab/spaceEval/testing/soccer/event/event_data_10502.csv'
tracking_home = '/home/c_yeung/workspace6/python/openstarlab/spaceEval/testing/soccer/home_tracking/home_tracking_10502.csv'
tracking_away = '/home/c_yeung/workspace6/python/openstarlab/spaceEval/testing/soccer/away_tracking/away_tracking_10502.csv'
ppcf= '/home/c_yeung/workspace6/python/openstarlab/spaceEval/testing/soccer/obso/10502_PPCF_dict.npy'
out_path = '/home/c_yeung/workspace6/python/openstarlab/spaceEval/testing/soccer'
model = Space_Model(space_model='soccer_OBSO')

model.vis_obso(event_id=event_id, 
               events_data=events_data, 
               tracking_home=tracking_home, 
               tracking_away=tracking_away, 
               PPCF=ppcf,
               out_path=out_path
               )