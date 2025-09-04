from spaceeval import Space_Model

event_path = '/home/c_yeung/workspace6/python/openstarlab/spaceEval/testing/soccer/event'
home_tracking_path = '/home/c_yeung/workspace6/python/openstarlab/spaceEval/testing/soccer/home_tracking'
away_tracking_path = '/home/c_yeung/workspace6/python/openstarlab/spaceEval/testing/soccer/away_tracking'
out_path = '/home/c_yeung/workspace6/python/openstarlab/spaceEval/testing/soccer'

model = Space_Model(space_model='soccer_OBSO',
            event_data=event_path,
            tracking_home=home_tracking_path,
            tracking_away=away_tracking_path,
            testing_mode=True,
            out_path=out_path)

model.get_obso()


