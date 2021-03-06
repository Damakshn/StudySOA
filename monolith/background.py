from celery import Celery
from stravalib import Client
from monolith.database import db, User, Run

celery = Celery(__name__, backend="rpc://", broker="amqp://")


_APP = None


def activity2run(user, activity):
    run = Run()
    run.runner = user
    run.strava_id = activity.id
    run.name = activity.name
    run.distance = activity.distance
    run.elapsed_time = activity.elapsed_time.total_seconds()
    run.average_speed = activity.average_speed
    run.average_heartrate = activity.average_heartrate
    run.total_elevation_gain = activity.total_elevation_gain
    run.start_date = activity.start_date
    return run


@celery.task
def fetch_all_runs():
    global _APP
    if _APP is None:
        from monolith.app import create_app
        # db.init_app(app)
        _APP = create_app()
    # else:
        # app = _APP

    runs_fetched = {}

    with _APP.app_context():
        q = db.session.query(User)
        for user in q:
            if user.strava_token is None:
                continue
            runs_fetched[user.id] = fetch_runs(user)

    return runs_fetched


def fetch_runs(user):
    client = Client(access_token=user.strava_token)
    runs = 0
    for activity in client.get_activities(limit=10):
        if activity.type != "Run":
            continue
        q = db.session.query(Run).filter(Run.strava_id == activity.id)
        run = q.first()
        if run is None:
            db.session.add(activity2run(user, activity))
            runs += 1
    db.session.commit()
    return runs
